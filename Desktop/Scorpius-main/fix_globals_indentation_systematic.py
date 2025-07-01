#!/usr/bin/env python3
"""
Systematic Fix Script: IndentationError on SimilarityEngine
Fixes the broken globals().update({}) pattern in 39 test files
"""

import os
import re
from pathlib import Path

def fix_globals_update_pattern(file_path):
    """Fix the broken globals().update({}) pattern in a file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        original_content = content
        
        # Pattern 1: Fix broken globals().update({}) followed by orphaned dictionary entries
        pattern1 = r'globals\(\)\.update\(\{\}\)\s*\n(\s+)\'SimilarityEngine\': MockSimilarityEngine,\s*\n(\s+)print\(f"Error: \{str\(e\)\}"\)\s*\n(\s+)\'MultiDimensionalComparison\': MockMultiDimensionalComparison,\s*\n(\s+)\'TestClient\': MockTestClient,\s*\n(\s+)print\(f"Error: \{str\(e\)\}"\)'
        
        replacement1 = """globals().update({
    'SimilarityEngine': MockSimilarityEngine,
    'MultiDimensionalComparison': MockMultiDimensionalComparison,
    'TestClient': MockTestClient,
})"""
        
        content = re.sub(pattern1, replacement1, content, flags=re.MULTILINE)
        
        # Pattern 2: Fix any remaining orphaned SimilarityEngine entries
        pattern2 = r'^\s+\'SimilarityEngine\': MockSimilarityEngine,\s*$'
        content = re.sub(pattern2, '', content, flags=re.MULTILINE)
        
        # Pattern 3: Fix any remaining orphaned print statements in globals context
        pattern3 = r'^\s+print\(f"Error: \{str\(e\)\}"\)\s*$'
        content = re.sub(pattern3, '', content, flags=re.MULTILINE)
        
        # Pattern 4: Fix any remaining orphaned mock entries
        pattern4 = r'^\s+\'(MultiDimensionalComparison|TestClient|BytecodeNormalizer)\': Mock\w+,\s*$'
        content = re.sub(pattern4, '', content, flags=re.MULTILINE)
        
        # Pattern 5: Fix empty globals().update({}) calls by adding common mocks
        pattern5 = r'globals\(\)\.update\(\{\}\)'
        replacement5 = """globals().update({
    'SimilarityEngine': MockSimilarityEngine,
    'MultiDimensionalComparison': MockMultiDimensionalComparison,
    'TestClient': MockTestClient,
    'BytecodeNormalizer': MockBytecodeNormalizer,
})"""
        
        content = re.sub(pattern5, replacement5, content)
        
        # Pattern 6: Clean up any multiple consecutive blank lines
        content = re.sub(r'\n\n\n+', '\n\n', content)
        
        # Only write if changes were made
        if content != original_content:
            with open(file_path, 'w', encoding='utf-8', errors='ignore') as f:
                f.write(content)
            return True
        
        return False
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return False

def main():
    """Main execution function"""
    project_root = Path(__file__).parent
    
    # Files with IndentationError on SimilarityEngine (from test results)
    affected_files = [
        "tests/api/test_static_api.py",
        "tests/unit/bytecode/test_api_main.py", 
        "tests/unit/bytecode/test_comparison_engine.py",
        "services/bridge-service/tests/test_bridge-service.py",
        "services/api-gateway/tests/test_api-gateway.py",
        "services/api-gateway/tests/test_routes.py",
        "reporting/tests/test_api_routes.py",
        "reporting/tests/test_diff_engine.py",
        "reporting/tests/test_writer_html.py",
        "packages/core/tests/test_api.py",
        "packages/core/tests/test_mev_bot.py",
        "packages/backend/reporting/tests/test_app.py",
        "backend/honeypot/test_comprehensive.py",
        "backend/mempool/test_api_startup.py",
        "backend/mempool/test_database_api.py",
        "backend/scanner/test_docker_plugins.py",
        "backend/scanner/test_enhanced_scanner.py",
        "backend/scanner/test_plugins.py",
        "backend/wallet_guard/tests/test_wallet_guard.py",
        "backend/utils/tests/test_utils.py",
        "backend/usage_metering/tests/test_api.py",
        "backend/usage_metering/tests/test_integration.py",
        "backend/usage_metering/tests/test_metrics_exporter.py",
        "backend/usage_metering/tests/test_stripe_service.py",
        "backend/usage_metering/tests/test_usage_metering.py",
        "backend/usage_metering/tests/test_usage_tracker.py",
        "backend/time_machine/tests/test_time_machine.py",
        "backend/scanner/tests/test_models.py",
        "backend/scanner/tests/test_scanner.py",
        "backend/scanner/tests/integration/test_enhanced_scanner.py",
        "backend/quantum/tests/test_enterprise.py",
        "backend/quantum/tests/test_quantum.py",
        "backend/middleware/tests/test_middleware.py",
        "backend/mev_bot/tests/test_mev_bot.py",
        "backend/mempool/tests/test_mempool.py",
        "backend/mempool/tests/integration/test_api.py",
        "backend/mempool/tests/unit/test_mempool_monitor.py",
        "backend/honeypot/tests/test_honeypot.py",
        "backend/honeypot/tests/test_risk_level.py",
        "backend/honeypot/tests/test_static_engine.py",
        "backend/decorators/tests/test_decorators.py",
        "backend/Bytecode/tests/test_normalizer.py",
        "backend/bridge/tests/test_bridge.py",
        "backend/auth_proxy/tests/test_auth_proxy.py",
        "backend/audit_trail/tests/test_audit_trail.py",
    ]
    
    print(">> Systematic IndentationError Fix - SimilarityEngine Pattern")
    print("=" * 70)
    
    total_files = len(affected_files)
    processed_files = 0
    fixed_files = 0
    
    for file_path in affected_files:
        full_path = project_root / file_path.replace('/', '\\')
        
        if full_path.exists():
            if fix_globals_update_pattern(full_path):
                print(f"[FIXED] {file_path}")
                fixed_files += 1
            else:
                print(f"[SKIP] {file_path} - No changes needed")
            processed_files += 1
        else:
            print(f"[MISS] {file_path} - File not found")
    
    print(f"\n[SUMMARY] Processed {processed_files}/{total_files} files")
    print(f"[SUMMARY] Fixed {fixed_files} files with IndentationError")
    print(f"[SUMMARY] Success rate: {(fixed_files/processed_files)*100:.1f}%")
    
    return fixed_files

if __name__ == "__main__":
    fixed_count = main()
    print(f"\n[COMPLETE] Fixed {fixed_count} files with SimilarityEngine IndentationError") 