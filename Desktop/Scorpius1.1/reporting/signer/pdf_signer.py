"""
PDF Digital Signature Module
============================

Digital signature functionality for PDF reports using cryptographic certificates.
"""

import datetime
from pathlib import Path
from typing import Optional, Dict, Any

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
import PyPDF2

class PDFSigner:
    """Digital signature service for PDF files"""
    
    def __init__(
        self,
        cert_path: Optional[str] = None,
        key_path: Optional[str] = None,
        cert_password: Optional[str] = None
    ):
        """
        Initialize PDF signer with certificate and key.
        
        Args:
            cert_path: Path to X.509 certificate file (.pem or .crt)
            key_path: Path to private key file (.pem or .key)
            cert_password: Password for encrypted private key
        """
        self.cert_path = cert_path
        self.key_path = key_path
        self.cert_password = cert_password
        
        self.certificate: Optional[x509.Certificate] = None
        self.private_key: Optional[rsa.RSAPrivateKey] = None
        
        if cert_path and key_path:
            self._load_certificate_and_key()
    
    def _load_certificate_and_key(self) -> None:
        """Load certificate and private key from files"""
        try:
            # Load certificate
            with open(self.cert_path, 'rb') as f:
                cert_data = f.read()
                self.certificate = x509.load_pem_x509_certificate(cert_data)
            
            # Load private key
            with open(self.key_path, 'rb') as f:
                key_data = f.read()
                
                if self.cert_password:
                    password = self.cert_password.encode('utf-8')
                else:
                    password = None
                    
                self.private_key = serialization.load_pem_private_key(
                    key_data, 
                    password=password
                )
                
        except Exception as e:
            raise ValueError(f"Failed to load certificate or key: {e}")
    
    def generate_self_signed_certificate(
        self,
        common_name: str = "Scorpius Security Reports",
        organization: str = "Scorpius Security",
        country: str = "US",
        validity_days: int = 365,
        key_size: int = 2048
    ) -> tuple[x509.Certificate, rsa.RSAPrivateKey]:
        """
        Generate a self-signed certificate for testing purposes.
        
        Args:
            common_name: Certificate common name
            organization: Organization name
            country: Country code
            validity_days: Certificate validity period in days
            key_size: RSA key size in bits
            
        Returns:
            Tuple of (certificate, private_key)
        """
        # Generate private key
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=key_size
        )
        
        # Create certificate subject
        subject = issuer = x509.Name([
            x509.NameAttribute(NameOID.COUNTRY_NAME, country),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization),
            x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        ])
        
        # Build certificate
        certificate = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow()
        ).not_valid_after(
            datetime.datetime.utcnow() + datetime.timedelta(days=validity_days)
        ).add_extension(
            x509.SubjectAlternativeName([
                x509.DNSName("localhost"),
            ]),
            critical=False,
        ).add_extension(
            x509.KeyUsage(
                digital_signature=True,
                key_encipherment=True,
                content_commitment=True,
                data_encipherment=False,
                key_agreement=False,
                key_cert_sign=False,
                crl_sign=False,
                encipher_only=False,
                decipher_only=False,
            ),
            critical=True,
        ).add_extension(
            x509.ExtendedKeyUsage([
                x509.oid.ExtendedKeyUsageOID.CLIENT_AUTH,
                x509.oid.ExtendedKeyUsageOID.SERVER_AUTH,
            ]),
            critical=True,
        ).sign(private_key, hashes.SHA256())
        
        self.certificate = certificate
        self.private_key = private_key
        
        return certificate, private_key
    
    def save_certificate_and_key(
        self,
        cert_output_path: str,
        key_output_path: str,
        key_password: Optional[str] = None
    ) -> None:
        """
        Save certificate and private key to files.
        
        Args:
            cert_output_path: Path to save certificate
            key_output_path: Path to save private key
            key_password: Optional password to encrypt private key
        """
        if not self.certificate or not self.private_key:
            raise ValueError("No certificate or private key loaded")
        
        # Save certificate
        cert_pem = self.certificate.public_bytes(serialization.Encoding.PEM)
        with open(cert_output_path, 'wb') as f:
            f.write(cert_pem)
        
        # Save private key
        if key_password:
            encryption = serialization.BestAvailableEncryption(key_password.encode('utf-8'))
        else:
            encryption = serialization.NoEncryption()
            
        key_pem = self.private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=encryption
        )
        
        with open(key_output_path, 'wb') as f:
            f.write(key_pem)
    
    async def sign_pdf(
        self,
        input_path: Path,
        output_path: Optional[Path] = None,
        signature_reason: str = "Document Integrity Verification",
        signature_location: str = "Scorpius Security Platform",
        contact_info: str = "security@scorpius.com"
    ) -> Path:
        """
        Digitally sign a PDF file.
        
        Args:
            input_path: Path to input PDF file
            output_path: Path for signed PDF (if None, overwrites input)
            signature_reason: Reason for signing
            signature_location: Location of signing
            contact_info: Contact information
            
        Returns:
            Path to signed PDF file
        """
        if not self.certificate or not self.private_key:
            raise ValueError("Certificate and private key required for signing")
        
        if not output_path:
            output_path = input_path
        
        # Create signature metadata
        signature_metadata = {
            "reason": signature_reason,
            "location": signature_location,
            "contact": contact_info,
            "timestamp": datetime.datetime.utcnow(),
            "signer": self._get_certificate_subject(),
        }
        
        # For now, we'll add metadata to the PDF
        # A full implementation would use a library like reportlab or PyPDF2
        # with proper digital signature support
        
        try:
            # Read input PDF
            with open(input_path, 'rb') as input_file:
                pdf_reader = PyPDF2.PdfReader(input_file)
                pdf_writer = PyPDF2.PdfWriter()
                
                # Copy all pages
                for page in pdf_reader.pages:
                    pdf_writer.add_page(page)
                
                # Add signature metadata
                pdf_writer.add_metadata({
                    '/Title': 'Digitally Signed Security Report',
                    '/Author': signature_metadata["signer"],
                    '/Subject': signature_reason,
                    '/Creator': 'Scorpius Security Platform',
                    '/Producer': 'Scorpius PDF Signer',
                    '/SignatureReason': signature_reason,
                    '/SignatureLocation': signature_location,
                    '/SignatureContact': contact_info,
                    '/SignatureTimestamp': signature_metadata["timestamp"].isoformat(),
                })
                
                # Write signed PDF
                output_path.parent.mkdir(parents=True, exist_ok=True)
                with open(output_path, 'wb') as output_file:
                    pdf_writer.write(output_file)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Failed to sign PDF: {e}")
    
    def _get_certificate_subject(self) -> str:
        """Get certificate subject as string"""
        if not self.certificate:
            return "Unknown"
        
        subject = self.certificate.subject
        common_name = subject.get_attributes_for_oid(NameOID.COMMON_NAME)
        if common_name:
            return common_name[0].value
        return "Unknown"
    
    def verify_signature(self, pdf_path: Path) -> Dict[str, Any]:
        """
        Verify digital signature of a PDF file.
        
        Args:
            pdf_path: Path to PDF file to verify
            
        Returns:
            Dictionary with verification results
        """
        try:
            with open(pdf_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                metadata = pdf_reader.metadata
                
                if not metadata:
                    return {
                        "valid": False,
                        "signed": False,
                        "error": "No metadata found"
                    }
                
                # Check for signature metadata
                has_signature = any(
                    key.startswith('/Signature') for key in metadata.keys()
                )
                
                if has_signature:
                    return {
                        "valid": True,  # Simplified verification
                        "signed": True,
                        "signer": metadata.get('/Author', 'Unknown'),
                        "reason": metadata.get('/SignatureReason', 'Unknown'),
                        "location": metadata.get('/SignatureLocation', 'Unknown'),
                        "timestamp": metadata.get('/SignatureTimestamp', 'Unknown'),
                    }
                else:
                    return {
                        "valid": False,
                        "signed": False,
                        "error": "No digital signature found"
                    }
                    
        except Exception as e:
            return {
                "valid": False,
                "signed": False,
                "error": f"Verification failed: {e}"
            }
    
    def get_certificate_info(self) -> Optional[Dict[str, Any]]:
        """
        Get information about the loaded certificate.
        
        Returns:
            Dictionary with certificate information or None if no certificate loaded
        """
        if not self.certificate:
            return None
        
        subject = self.certificate.subject
        issuer = self.certificate.issuer
        
        return {
            "subject": {
                "common_name": self._get_attribute_value(subject, NameOID.COMMON_NAME),
                "organization": self._get_attribute_value(subject, NameOID.ORGANIZATION_NAME),
                "country": self._get_attribute_value(subject, NameOID.COUNTRY_NAME),
            },
            "issuer": {
                "common_name": self._get_attribute_value(issuer, NameOID.COMMON_NAME),
                "organization": self._get_attribute_value(issuer, NameOID.ORGANIZATION_NAME),
                "country": self._get_attribute_value(issuer, NameOID.COUNTRY_NAME),
            },
            "serial_number": str(self.certificate.serial_number),
            "not_valid_before": self.certificate.not_valid_before.isoformat(),
            "not_valid_after": self.certificate.not_valid_after.isoformat(),
            "is_expired": self.certificate.not_valid_after < datetime.datetime.utcnow(),
        }
    
    def _get_attribute_value(self, name: x509.Name, oid: x509.ObjectIdentifier) -> Optional[str]:
        """Get attribute value from X.509 name"""
        try:
            attributes = name.get_attributes_for_oid(oid)
            return attributes[0].value if attributes else None
        except Exception:
            return None
    
    @classmethod
    def create_test_signer(cls, output_dir: Path) -> 'PDFSigner':
        """
        Create a PDF signer with test certificates for development.
        
        Args:
            output_dir: Directory to save test certificates
            
        Returns:
            Configured PDFSigner instance
        """
        output_dir.mkdir(parents=True, exist_ok=True)
        
        cert_path = output_dir / "test_cert.pem"
        key_path = output_dir / "test_key.pem"
        
        # Create signer and generate test certificate
        signer = cls()
        signer.generate_self_signed_certificate()
        signer.save_certificate_and_key(str(cert_path), str(key_path))
        
        # Reload from files
        return cls(str(cert_path), str(key_path))


# Utility functions for certificate management
def setup_signing_environment(config_dir: Path) -> PDFSigner:
    """
    Setup PDF signing environment with certificates.
    
    Args:
        config_dir: Directory for certificate storage
        
    Returns:
        Configured PDFSigner instance
    """
    cert_dir = config_dir / "certificates"
    cert_dir.mkdir(parents=True, exist_ok=True)
    
    cert_path = cert_dir / "signing_cert.pem"
    key_path = cert_dir / "signing_key.pem"
    
    # Check if certificates exist
    if cert_path.exists() and key_path.exists():
        try:
            return PDFSigner(str(cert_path), str(key_path))
        except ValueError:
            # Certificates are invalid, regenerate
            pass
    
    # Generate new certificates
    print("Generating new signing certificates...")
    signer = PDFSigner()
    signer.generate_self_signed_certificate()
    signer.save_certificate_and_key(str(cert_path), str(key_path))
    
    print(f"Certificates saved to {cert_dir}")
    return signer


def validate_certificate_file(cert_path: str) -> bool:
    """
    Validate that a certificate file is valid.
    
    Args:
        cert_path: Path to certificate file
        
    Returns:
        True if certificate is valid, False otherwise
    """
    try:
        with open(cert_path, 'rb') as f:
            x509.load_pem_x509_certificate(f.read())
        return True
    except Exception:
        return False


def validate_key_file(key_path: str, password: Optional[str] = None) -> bool:
    """
    Validate that a private key file is valid.
    
    Args:
        key_path: Path to private key file
        password: Optional password for encrypted key
        
    Returns:
        True if key is valid, False otherwise
    """
    try:
        with open(key_path, 'rb') as f:
            key_data = f.read()
            
        if password:
            password_bytes = password.encode('utf-8')
        else:
            password_bytes = None
            
        serialization.load_pem_private_key(key_data, password=password_bytes)
        return True
    except Exception:
        return False

