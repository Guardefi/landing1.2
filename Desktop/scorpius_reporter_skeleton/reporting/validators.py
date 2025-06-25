"""
Enterprise Reporting Validators
==============================

Validation functions and classes for scan results, configuration, and report data.
"""

import hashlib
import re
from typing import Any, Dict, List, Union

try:
    from cerberus import Validator
    CERBERUS_AVAILABLE = True
except ImportError:
    CERBERUS_AVAILABLE = False
    
try:
    from jsonschema import validate
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False

from models import ScanResult, VulnerabilityFinding, SeverityLevel, FindingType


class ScanResultValidator:
    """Validator for ScanResult objects"""
    
    def __init__(self):
        self.schema = {
            "scan_id": {"type": "string", "required": True, "minlength": 1},
            "target_info": {"type": "dict", "required": True},
            "metadata": {"type": "dict", "required": True},
            "findings": {"type": "list", "required": True},
            "summary": {"type": "dict", "required": True},
            "execution_time": {"type": "float", "required": True, "min": 0},
            "timestamp": {"type": "datetime", "required": True},
            "version": {"type": "string", "required": True}
        }
        if CERBERUS_AVAILABLE:
            self.validator = Validator(self.schema)
        else:
            self.validator = None
    
    def validate_scan_result(self, scan_result: Union[Dict, ScanResult]) -> bool:
        """Validate a scan result object or dictionary"""
        if isinstance(scan_result, ScanResult):
            # Convert Pydantic model to dict for validation
            scan_data = scan_result.dict()
        else:
            scan_data = scan_result
        
        if self.validator:
            return self.validator.validate(scan_data)
        else:
            # Basic validation without Cerberus
            required_fields = ["scan_id", "target_info", "metadata", "findings", "summary"]
            return all(field in scan_data for field in required_fields)
    
    def get_validation_errors(self) -> List[str]:
        """Get validation errors from last validation"""
        if self.validator and self.validator.errors:
            return list(self.validator.errors.keys())
        return []


class VulnerabilityValidator:
    """Validator for vulnerability findings"""
    
    def __init__(self):
        self.severity_levels = [level.value for level in SeverityLevel]
        self.finding_types = [ftype.value for ftype in FindingType]
    
    def validate_finding(self, finding: Union[Dict, VulnerabilityFinding]) -> bool:
        """Validate a vulnerability finding"""
        if isinstance(finding, VulnerabilityFinding):
            finding_data = finding.dict()
        else:
            finding_data = finding
        
        # Required fields
        required_fields = ["id", "title", "severity", "type", "description"]
        for field in required_fields:
            if field not in finding_data or not finding_data[field]:
                return False
        
        # Validate severity
        if finding_data["severity"] not in self.severity_levels:
            return False
        
        # Validate type
        if finding_data["type"] not in self.finding_types:
            return False
        
        # Validate score range
        if "cvss_score" in finding_data:
            score = finding_data["cvss_score"]
            if score is not None and (score < 0 or score > 10):
                return False
        
        return True
    
    def validate_findings_list(self, findings: List[Union[Dict, VulnerabilityFinding]]) -> bool:
        """Validate a list of findings"""
        return all(self.validate_finding(finding) for finding in findings)


class ConfigValidator:
    """Validator for configuration settings"""
    
    @staticmethod
    def validate_database_config(config: Dict[str, Any]) -> bool:
        """Validate database configuration"""
        required_fields = ["host", "port", "database", "username"]
        return all(field in config for field in required_fields)
    
    @staticmethod
    def validate_redis_config(config: Dict[str, Any]) -> bool:
        """Validate Redis configuration"""
        required_fields = ["host", "port"]
        return all(field in config for field in required_fields)
    
    @staticmethod
    def validate_security_config(config: Dict[str, Any]) -> bool:
        """Validate security configuration"""
        if "secret_key" not in config:
            return False
        
        # Check secret key length
        if len(config["secret_key"]) < 32:
            return False
        
        return True


class DataIntegrityValidator:
    """Validator for data integrity and checksums"""
    
    @staticmethod
    def calculate_checksum(data: Union[str, bytes], algorithm: str = "sha256") -> str:
        """Calculate checksum for data"""
        if isinstance(data, str):
            data = data.encode('utf-8')
        
        hash_func = getattr(hashlib, algorithm)()
        hash_func.update(data)
        return hash_func.hexdigest()
    
    @staticmethod
    def verify_checksum(data: Union[str, bytes], expected_checksum: str, algorithm: str = "sha256") -> bool:
        """Verify data checksum"""
        actual_checksum = DataIntegrityValidator.calculate_checksum(data, algorithm)
        return actual_checksum.lower() == expected_checksum.lower()
    
    @staticmethod
    def validate_file_integrity(file_path: str, expected_checksum: str, algorithm: str = "sha256") -> bool:
        """Validate file integrity using checksum"""
        try:
            with open(file_path, 'rb') as f:
                content = f.read()
            return DataIntegrityValidator.verify_checksum(content, expected_checksum, algorithm)
        except Exception:
            return False


class ContractAddressValidator:
    """Validator for smart contract addresses and identifiers"""
    
    @staticmethod
    def validate_ethereum_address(address: str) -> bool:
        """Validate Ethereum address format"""
        if not address:
            return False
        
        # Remove 0x prefix if present
        if address.startswith('0x'):
            address = address[2:]
        
        # Check length and hex format
        if len(address) != 40:
            return False
        
        try:
            int(address, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_contract_bytecode(bytecode: str) -> bool:
        """Validate contract bytecode format"""
        if not bytecode:
            return False
        
        # Remove 0x prefix if present
        if bytecode.startswith('0x'):
            bytecode = bytecode[2:]
        
        # Check if it's valid hex
        try:
            int(bytecode, 16)
            return True
        except ValueError:
            return False
    
    @staticmethod
    def validate_transaction_hash(tx_hash: str) -> bool:
        """Validate transaction hash format"""
        if not tx_hash:
            return False
        
        # Remove 0x prefix if present
        if tx_hash.startswith('0x'):
            tx_hash = tx_hash[2:]
        
        # Check length and hex format (64 characters for sha256)
        if len(tx_hash) != 64:
            return False
        
        try:
            int(tx_hash, 16)
            return True
        except ValueError:
            return False


class ReportFormatValidator:
    """Validator for report format specifications"""
    
    SUPPORTED_FORMATS = ["pdf", "html", "json", "csv", "sarif", "markdown"]
    
    @staticmethod
    def validate_format(format_name: str) -> bool:
        """Validate report format"""
        return format_name.lower() in ReportFormatValidator.SUPPORTED_FORMATS
    
    @staticmethod
    def validate_template_name(template_name: str) -> bool:
        """Validate template name format"""
        # Allow alphanumeric, underscore, hyphen
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, template_name))
    
    @staticmethod
    def validate_theme_name(theme_name: str) -> bool:
        """Validate theme name format"""
        # Allow alphanumeric, underscore, hyphen
        pattern = r'^[a-zA-Z0-9_-]+$'
        return bool(re.match(pattern, theme_name))


class JSONSchemaValidator:
    """JSON Schema validator for structured data"""
    
    # SARIF v2.1.0 schema subset
    SARIF_SCHEMA = {
        "type": "object",
        "properties": {
            "version": {"type": "string", "const": "2.1.0"},
            "runs": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "tool": {"type": "object"},
                        "results": {"type": "array"}
                    },
                    "required": ["tool", "results"]
                }
            }
        },
        "required": ["version", "runs"]
    }
    
    @staticmethod
    def validate_sarif(data: Dict[str, Any]) -> bool:
        """Validate SARIF format data"""
        if not JSONSCHEMA_AVAILABLE:
            # Basic validation without jsonschema
            return (
                isinstance(data, dict) and
                "version" in data and
                "runs" in data and
                isinstance(data["runs"], list)
            )
        
        try:
            validate(instance=data, schema=JSONSchemaValidator.SARIF_SCHEMA)
            return True
        except Exception:
            return False
    
    @staticmethod
    def validate_json_schema(data: Dict[str, Any], schema: Dict[str, Any]) -> bool:
        """Validate data against a JSON schema"""
        if not JSONSCHEMA_AVAILABLE:
            return True  # Skip validation if jsonschema not available
        
        try:
            validate(instance=data, schema=schema)
            return True
        except Exception:
            return False


class InputSanitizer:
    """Input sanitization utilities"""
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """Sanitize filename to prevent path traversal"""
        # Remove directory separators and other dangerous characters
        sanitized = re.sub(r'[<>:"/\\|?*]', '_', filename)
        sanitized = re.sub(r'\.\.', '_', sanitized)
        return sanitized.strip('.')
    
    @staticmethod
    def sanitize_html(html_content: str) -> str:
        """Basic HTML sanitization (remove scripts, etc.)"""
        # Remove script tags and their content
        html_content = re.sub(r'<script\b[^<]*(?:(?!<\/script>)<[^<]*)*<\/script>', '', html_content, flags=re.IGNORECASE)
        
        # Remove potentially dangerous attributes
        html_content = re.sub(r'\s*on\w+\s*=\s*["\'][^"\']*["\']', '', html_content, flags=re.IGNORECASE)
        
        return html_content
    
    @staticmethod
    def validate_sql_input(input_string: str) -> bool:
        """Check for potential SQL injection patterns"""
        dangerous_patterns = [
            r'\b(drop|delete|truncate|alter|create|insert|update)\b',
            r'[;\'"\\]',
            r'--',
            r'/\*.*\*/',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, input_string, re.IGNORECASE):
                return False
        
        return True


# Validator instances for common use
scan_validator = ScanResultValidator()
vulnerability_validator = VulnerabilityValidator()
config_validator = ConfigValidator()
integrity_validator = DataIntegrityValidator()
address_validator = ContractAddressValidator()
format_validator = ReportFormatValidator()
schema_validator = JSONSchemaValidator()
sanitizer = InputSanitizer()


def validate_scan_result(scan_result: Union[Dict, ScanResult]) -> bool:
    """Convenience function for scan result validation"""
    return scan_validator.validate_scan_result(scan_result)


def validate_vulnerability(finding: Union[Dict, VulnerabilityFinding]) -> bool:
    """Convenience function for vulnerability validation"""
    return vulnerability_validator.validate_finding(finding)


def validate_ethereum_address(address: str) -> bool:
    """Convenience function for Ethereum address validation"""
    return address_validator.validate_ethereum_address(address)


def validate_report_format(format_name: str) -> bool:
    """Convenience function for report format validation"""
    return format_validator.validate_format(format_name)


def sanitize_user_input(user_input: str) -> str:
    """Sanitize user input for safe processing"""
    # Basic sanitization
    sanitized = sanitizer.sanitize_html(user_input)
    return sanitized.strip()