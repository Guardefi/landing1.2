"""
Scorpius Reporting Service - Digital Signature Service
Cryptographic signing for PDF and JSON documents
"""

import os
import json
import logging
import hashlib
import hmac
from typing import Dict, Any, Optional
from datetime import datetime, timezone
import base64

# Cryptographic libraries
try:
    from cryptography.hazmat.primitives import hashes, serialization
    from cryptography.hazmat.primitives.asymmetric import rsa, padding
    from cryptography.hazmat.primitives.serialization import load_pem_private_key, load_pem_public_key
    from cryptography import x509
    CRYPTOGRAPHY_AVAILABLE = True
except ImportError:
    CRYPTOGRAPHY_AVAILABLE = False
    logging.warning("Cryptography library not available. Signature functionality will be limited.")

try:
    import jwt
    JWT_AVAILABLE = True
except ImportError:
    JWT_AVAILABLE = False
    logging.warning("PyJWT not available. JWT signing will be limited.")

from core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SignatureError(Exception):
    """Digital signature error"""
    pass


class SignatureService:
    """Digital signature service for enterprise documents"""
    
    def __init__(self):
        self.settings = settings
        self.private_key = None
        self.public_key = None
        self.certificate = None
        self.initialized = False
    
    async def initialize(self):
        """Initialize signature service with keys and certificates"""
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                logger.warning("Cryptography not available, using mock signatures")
                self.initialized = True
                return
            
            # Load private key
            if os.path.exists(self.settings.SIGNATURE_KEY_PATH):
                with open(self.settings.SIGNATURE_KEY_PATH, 'rb') as key_file:
                    private_key_data = key_file.read()
                    self.private_key = load_pem_private_key(
                        private_key_data,
                        password=None,  # In production, use password-protected keys
                    )
                    logger.info("Private key loaded successfully")
            else:
                # Generate new key pair for development
                await self._generate_key_pair()
            
            # Load certificate
            if os.path.exists(self.settings.SIGNATURE_CERT_PATH):
                with open(self.settings.SIGNATURE_CERT_PATH, 'rb') as cert_file:
                    cert_data = cert_file.read()
                    self.certificate = x509.load_pem_x509_certificate(cert_data)
                    self.public_key = self.certificate.public_key()
                    logger.info("Certificate loaded successfully")
            else:
                # Generate self-signed certificate for development
                await self._generate_self_signed_cert()
            
            self.initialized = True
            logger.info("Signature service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize signature service: {e}")
            # Fall back to mock signatures in case of error
            self.initialized = True
    
    async def _generate_key_pair(self):
        """Generate RSA key pair for development"""
        if not CRYPTOGRAPHY_AVAILABLE:
            return
        
        try:
            # Generate private key
            self.private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048,
            )
            
            # Save private key
            os.makedirs(os.path.dirname(self.settings.SIGNATURE_KEY_PATH), exist_ok=True)
            private_pem = self.private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            
            with open(self.settings.SIGNATURE_KEY_PATH, 'wb') as key_file:
                key_file.write(private_pem)
            
            logger.info("Generated new RSA key pair for development")
            
        except Exception as e:
            logger.error(f"Failed to generate key pair: {e}")
    
    async def _generate_self_signed_cert(self):
        """Generate self-signed certificate for development"""
        if not CRYPTOGRAPHY_AVAILABLE or not self.private_key:
            return
        
        try:
            # Create certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(x509.NameOID.COUNTRY_NAME, "US"),
                x509.NameAttribute(x509.NameOID.STATE_OR_PROVINCE_NAME, "CA"),
                x509.NameAttribute(x509.NameOID.LOCALITY_NAME, "San Francisco"),
                x509.NameAttribute(x509.NameOID.ORGANIZATION_NAME, "Scorpius Enterprise"),
                x509.NameAttribute(x509.NameOID.COMMON_NAME, "Scorpius Reporting Service"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                self.private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow().replace(year=datetime.utcnow().year + 1)
            ).add_extension(
                x509.SubjectAlternativeName([
                    x509.DNSName("localhost"),
                ]),
                critical=False,
            ).sign(self.private_key, hashes.SHA256())
            
            # Save certificate
            os.makedirs(os.path.dirname(self.settings.SIGNATURE_CERT_PATH), exist_ok=True)
            cert_pem = cert.public_bytes(serialization.Encoding.PEM)
            
            with open(self.settings.SIGNATURE_CERT_PATH, 'wb') as cert_file:
                cert_file.write(cert_pem)
            
            self.certificate = cert
            self.public_key = cert.public_key()
            
            logger.info("Generated self-signed certificate for development")
            
        except Exception as e:
            logger.error(f"Failed to generate certificate: {e}")
    
    async def sign_pdf(
        self,
        pdf_content: bytes,
        signer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """
        Sign PDF document
        
        Args:
            pdf_content: PDF content as bytes
            signer_id: ID of the signer
            metadata: Additional metadata to include
            
        Returns:
            Signed PDF content
        """
        if not self.initialized:
            raise SignatureError("Signature service not initialized")
        
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._mock_sign_pdf(pdf_content, signer_id, metadata)
            
            # Calculate PDF hash
            pdf_hash = hashlib.sha256(pdf_content).hexdigest()
            
            # Create signature metadata
            signature_metadata = {
                "document_hash": pdf_hash,
                "signer_id": signer_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "algorithm": "RSA-SHA256",
                "service": "scorpius-reporting"
            }
            
            if metadata:
                signature_metadata.update(metadata)
            
            # Create signature payload
            signature_payload = json.dumps(signature_metadata, sort_keys=True).encode('utf-8')
            
            # Sign the payload
            signature = self.private_key.sign(
                signature_payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Create signed PDF with embedded signature
            signature_info = {
                "signature": base64.b64encode(signature).decode('utf-8'),
                "metadata": signature_metadata,
                "certificate": base64.b64encode(
                    self.certificate.public_bytes(serialization.Encoding.PEM)
                ).decode('utf-8') if self.certificate else None
            }
            
            # Embed signature in PDF (simplified - in production, use proper PDF signing)
            signature_json = json.dumps(signature_info, indent=2)
            signed_pdf = pdf_content + b"\n\n%% SCORPIUS SIGNATURE %%\n" + signature_json.encode('utf-8') + b"\n%% END SIGNATURE %%"
            
            logger.info(f"PDF signed successfully: {len(signed_pdf)} bytes")
            return signed_pdf
            
        except Exception as e:
            logger.error(f"PDF signing error: {e}")
            raise SignatureError(f"Failed to sign PDF: {str(e)}")
    
    async def sign_json(
        self,
        json_content: Dict[str, Any],
        signer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Sign JSON document
        
        Args:
            json_content: JSON content as dictionary
            signer_id: ID of the signer
            metadata: Additional metadata to include
            
        Returns:
            Signed JSON document
        """
        if not self.initialized:
            raise SignatureError("Signature service not initialized")
        
        try:
            if not CRYPTOGRAPHY_AVAILABLE:
                return await self._mock_sign_json(json_content, signer_id, metadata)
            
            # Calculate content hash
            content_str = json.dumps(json_content, sort_keys=True)
            content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
            
            # Create signature metadata
            signature_metadata = {
                "document_hash": content_hash,
                "signer_id": signer_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "algorithm": "RSA-SHA256",
                "service": "scorpius-reporting"
            }
            
            if metadata:
                signature_metadata.update(metadata)
            
            # Create signature payload
            signature_payload = json.dumps(signature_metadata, sort_keys=True).encode('utf-8')
            
            # Sign the payload
            signature = self.private_key.sign(
                signature_payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            # Create signed JSON
            signed_json = {
                "content": json_content,
                "signature": {
                    "value": base64.b64encode(signature).decode('utf-8'),
                    "metadata": signature_metadata,
                    "certificate": base64.b64encode(
                        self.certificate.public_bytes(serialization.Encoding.PEM)
                    ).decode('utf-8') if self.certificate else None
                }
            }
            
            logger.info("JSON signed successfully")
            return signed_json
            
        except Exception as e:
            logger.error(f"JSON signing error: {e}")
            raise SignatureError(f"Failed to sign JSON: {str(e)}")
    
    async def verify_signature(
        self,
        signed_content: Dict[str, Any],
        public_key: Optional[bytes] = None
    ) -> bool:
        """
        Verify document signature
        
        Args:
            signed_content: Signed content with signature
            public_key: Public key for verification (optional)
            
        Returns:
            True if signature is valid, False otherwise
        """
        if not CRYPTOGRAPHY_AVAILABLE:
            return await self._mock_verify_signature(signed_content)
        
        try:
            signature_info = signed_content.get("signature", {})
            if not signature_info:
                return False
            
            # Extract signature components
            signature_value = base64.b64decode(signature_info["value"])
            signature_metadata = signature_info["metadata"]
            
            # Use provided public key or service public key
            verify_key = self.public_key
            if public_key:
                verify_key = load_pem_public_key(public_key)
            
            if not verify_key:
                logger.error("No public key available for verification")
                return False
            
            # Recreate signature payload
            signature_payload = json.dumps(signature_metadata, sort_keys=True).encode('utf-8')
            
            # Verify signature
            verify_key.verify(
                signature_value,
                signature_payload,
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            
            logger.info("Signature verification successful")
            return True
            
        except Exception as e:
            logger.error(f"Signature verification failed: {e}")
            return False
    
    async def get_cert_fingerprint(self) -> str:
        """Get certificate fingerprint"""
        if not self.certificate:
            return "mock_fingerprint_dev"
        
        fingerprint = hashlib.sha256(
            self.certificate.public_bytes(serialization.Encoding.DER)
        ).hexdigest()
        
        return fingerprint
    
    async def _mock_sign_pdf(
        self,
        pdf_content: bytes,
        signer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bytes:
        """Mock PDF signing for development"""
        
        # Create mock signature
        pdf_hash = hashlib.sha256(pdf_content).hexdigest()
        mock_signature = {
            "signature": "mock_signature_" + pdf_hash[:16],
            "metadata": {
                "document_hash": pdf_hash,
                "signer_id": signer_id,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "algorithm": "MOCK-SHA256",
                "service": "scorpius-reporting"
            }
        }
        
        if metadata:
            mock_signature["metadata"].update(metadata)
        
        # Embed mock signature
        signature_json = json.dumps(mock_signature, indent=2)
        signed_pdf = pdf_content + b"\n\n%% SCORPIUS MOCK SIGNATURE %%\n" + signature_json.encode('utf-8') + b"\n%% END SIGNATURE %%"
        
        return signed_pdf
    
    async def _mock_sign_json(
        self,
        json_content: Dict[str, Any],
        signer_id: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Mock JSON signing for development"""
        
        # Create mock signature
        content_str = json.dumps(json_content, sort_keys=True)
        content_hash = hashlib.sha256(content_str.encode('utf-8')).hexdigest()
        
        mock_signature_metadata = {
            "document_hash": content_hash,
            "signer_id": signer_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "algorithm": "MOCK-SHA256",
            "service": "scorpius-reporting"
        }
        
        if metadata:
            mock_signature_metadata.update(metadata)
        
        return {
            "content": json_content,
            "signature": {
                "value": "mock_signature_" + content_hash[:16],
                "metadata": mock_signature_metadata,
                "certificate": None
            }
        }
    
    async def _mock_verify_signature(self, signed_content: Dict[str, Any]) -> bool:
        """Mock signature verification for development"""
        signature_info = signed_content.get("signature", {})
        return signature_info.get("value", "").startswith("mock_signature_")
    
    async def cleanup(self):
        """Cleanup signature service"""
        logger.info("Signature service cleanup completed")
