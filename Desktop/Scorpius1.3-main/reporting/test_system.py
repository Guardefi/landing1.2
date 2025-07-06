#!/usr/bin/env python3
"""
Test script for the Scorpius Reporting System
"""

import asyncio
import sys
from pathlib import Path

# Add the reporting directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_basic_functionality():
    """Test basic functionality of the reporting system"""
    
    print("🚀 Testing Scorpius Enterprise Reporting System")
    print("=" * 50)
    
    # Test model imports
    try:
        from models import ScanResult, VulnerabilityFinding, SeverityLevel, FindingType, VulnerabilityCategory
        print("✅ Models imported successfully")
    except Exception as e:
        print(f"❌ Failed to import models: {e}")
        return
    
    # Test generator import
    try:
        from generator import ReportGenerator
        print("✅ Generator imported successfully")
    except Exception as e:
        print(f"❌ Failed to import generator: {e}")
        return
    
    # Test theme system
    try:
        from themes import ThemeManager
        theme_mgr = ThemeManager()
        themes = theme_mgr.list_themes()
        print(f"✅ Theme system loaded with {len(themes)} themes: {', '.join(themes)}")
    except Exception as e:
        print(f"❌ Failed to load theme system: {e}")
        return
    
    # Test validators
    try:
        from validators import validate_scan_result, validate_vulnerability
        print("✅ Validators loaded successfully")
    except Exception as e:
        print(f"❌ Failed to load validators: {e}")
        return
    
    # Create sample data
    try:
        sample_vulnerability = VulnerabilityFinding(
            id="TEST_001",
            title="Test Reentrancy Vulnerability",
            severity=SeverityLevel.HIGH,
            category=VulnerabilityCategory.REENTRANCY,
            type=FindingType.REENTRANCY,
            description="This is a test vulnerability for demonstration purposes.",
            confidence=0.8,  # Float between 0.0 and 1.0
            impact="Potential fund drain through reentrancy attack.",
            recommendation="Implement checks-effects-interactions pattern or use OpenZeppelin's ReentrancyGuard.",
            # Optional location fields
            contract_name="TestContract",
            function_name="withdraw",
            line_number=42
        )
        
        sample_scan = ScanResult(
            scan_id="TEST_SCAN_001",
            project_name="TestContract",
            project_version="1.0.0",
            vulnerabilities=[sample_vulnerability]
        )
        
        print("✅ Sample data created successfully")
        
        # Validate the data
        if validate_scan_result(sample_scan):
            print("✅ Sample scan result validation passed")
        else:
            print("❌ Sample scan result validation failed")
            
        if validate_vulnerability(sample_vulnerability):
            print("✅ Sample vulnerability validation passed")
        else:
            print("❌ Sample vulnerability validation failed")
            
    except Exception as e:
        print(f"❌ Failed to create sample data: {e}")
        return
    
    # Test report generation
    try:
        generator = ReportGenerator()
        
        # Test different output formats
        output_dir = Path("test_reports")
        output_dir.mkdir(exist_ok=True)
        
        print("\n📊 Testing report generation...")
        
        # Generate full audit report with multiple formats
        audit_results = await generator.generate_full_audit_report(
            scan_result=sample_scan,
            formats=["json", "html"]
        )
        print(f"✅ Audit reports generated: {list(audit_results.keys())}")
        
        print(f"\n🎉 All reports generated successfully in {output_dir}")
        
    except Exception as e:
        print(f"❌ Failed to generate reports: {e}")
        import traceback
        traceback.print_exc()
        return
    
    print("\n🎯 All tests passed! The Scorpius Reporting System is working correctly.")
    print(f"📁 Test reports are available in: {output_dir.absolute()}")


if __name__ == "__main__":
    asyncio.run(test_basic_functionality())
