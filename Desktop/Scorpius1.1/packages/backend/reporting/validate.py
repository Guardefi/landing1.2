#!/usr/bin/env python3
"""
Scorpius Reporting Service - Validation Script
Test that the service can be imported and basic functionality works
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all modules can be imported"""
    print("Testing imports...")
    
    try:
        from models import ReportStatus, PDFReportRequest, SARIFReportRequest
        print("✓ Models imported successfully")
    except Exception as e:
        print(f"✗ Models import failed: {e}")
        return False
    
    try:
        from services.pdf_generator import PDFGenerator
        print("✓ PDF Generator imported successfully")
    except Exception as e:
        print(f"✗ PDF Generator import failed: {e}")
        return False
    
    try:
        from services.sarif_generator import SARIFGenerator
        print("✓ SARIF Generator imported successfully")
    except Exception as e:
        print(f"✗ SARIF Generator import failed: {e}")
        return False
    
    try:
        from services.signature_service import SignatureService
        print("✓ Signature Service imported successfully")
    except Exception as e:
        print(f"✗ Signature Service import failed: {e}")
        return False
    
    try:
        from services.audit_service import AuditService
        print("✓ Audit Service imported successfully")
    except Exception as e:
        print(f"✗ Audit Service import failed: {e}")
        return False
    
    try:
        from services.qldb_service import QLDBService
        print("✓ QLDB Service imported successfully")
    except Exception as e:
        print(f"✗ QLDB Service import failed: {e}")
        return False
    
    return True

def test_service_creation():
    """Test that services can be created"""
    print("\nTesting service creation...")
    
    try:
        from services.pdf_generator import PDFGenerator
        pdf_gen = PDFGenerator()
        print("✓ PDF Generator created successfully")
    except Exception as e:
        print(f"✗ PDF Generator creation failed: {e}")
        return False
    
    try:
        from services.sarif_generator import SARIFGenerator
        sarif_gen = SARIFGenerator()
        print("✓ SARIF Generator created successfully")
    except Exception as e:
        print(f"✗ SARIF Generator creation failed: {e}")
        return False
    
    try:
        from services.signature_service import SignatureService
        sig_service = SignatureService()
        print("✓ Signature Service created successfully")
    except Exception as e:
        print(f"✗ Signature Service creation failed: {e}")
        return False
    
    return True

def test_models():
    """Test that models work correctly"""
    print("\nTesting models...")
    
    try:
        from models import PDFReportRequest, ScanResult, ToolInfo, SARIFReportRequest
        
        # Test PDF request
        pdf_request = PDFReportRequest(
            title="Test Report",
            data={"test": "data"},
            template="default"
        )
        print("✓ PDF Request model works")
        
        # Test SARIF request
        scan_result = ScanResult(
            rule_id="TEST-001",
            level="error",
            message="Test finding"
        )
        
        tool_info = ToolInfo(
            name="Test Tool",
            version="1.0.0"
        )
        
        sarif_request = SARIFReportRequest(
            title="Test SARIF",
            scan_results=[scan_result],
            tool_info=tool_info
        )
        print("✓ SARIF Request model works")
        
    except Exception as e:
        print(f"✗ Model validation failed: {e}")
        return False
    
    return True

def main():
    """Main validation function"""
    print("Scorpius Reporting Service - Validation")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test service creation
    if not test_service_creation():
        success = False
    
    # Test models
    if not test_models():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All validation tests passed!")
        print("The Scorpius Reporting Service is ready to use.")
        return 0
    else:
        print("✗ Some validation tests failed!")
        print("Please check the errors above and fix the issues.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
