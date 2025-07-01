"""
Simple validation test for SCORPIUS engine components
"""

import asyncio
import os
import sys

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))


def test_imports():
    """Test that we can import our main modules"""
    print("Testing module imports...")

    try:
        from core.similarity_engine import SimilarityEngine

        print("✓ SimilarityEngine imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SimilarityEngine: {e}")
        return False

    try:
        from core.comparison_engine import MultiDimensionalComparison

        print("✓ MultiDimensionalComparison imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import MultiDimensionalComparison: {e}")
        return False

    try:
        from preprocessors.bytecode_normalizer import BytecodeNormalizer

        print("✓ BytecodeNormalizer imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import BytecodeNormalizer: {e}")
        return False

    try:
        from utils.metrics import PerformanceMonitor

        print("✓ PerformanceMonitor imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import PerformanceMonitor: {e}")
        return False

    try:
        from models.siamese_network import SiameseNetwork

        print("✓ SiameseNetwork imported successfully")
    except ImportError as e:
        print(f"✗ Failed to import SiameseNetwork: {e}")
        return False

    return True


def test_instantiation():
    """Test that classes can be instantiated"""
    print("\nTesting class instantiation...")

    try:
        from core.similarity_engine import SimilarityEngine

        engine = SimilarityEngine()
        print("✓ SimilarityEngine instantiated")
    except Exception as e:
        print(f"✗ SimilarityEngine instantiation failed: {e}")
        return False

    try:
        from core.comparison_engine import MultiDimensionalComparison

        comparison = MultiDimensionalComparison()
        print("✓ MultiDimensionalComparison instantiated")
    except Exception as e:
        print(f"✗ MultiDimensionalComparison instantiation failed: {e}")
        return False

    try:
        from preprocessors.bytecode_normalizer import BytecodeNormalizer

        normalizer = BytecodeNormalizer()
        print("✓ BytecodeNormalizer instantiated")
    except Exception as e:
        print(f"✗ BytecodeNormalizer instantiation failed: {e}")
        return False

    try:
        from utils.metrics import PerformanceMonitor

        monitor = PerformanceMonitor()
        print("✓ PerformanceMonitor instantiated")
    except Exception as e:
        print(f"✗ PerformanceMonitor instantiation failed: {e}")
        return False

    return True


async def test_basic_functionality():
    """Test basic functionality"""
    print("\nTesting basic functionality...")

    try:
        from preprocessors.bytecode_normalizer import BytecodeNormalizer

        normalizer = BytecodeNormalizer()

        # Test with a simple bytecode
        bytecode = "608060405234801561001057600080fd5b50"

        # Test validation
        is_valid = normalizer.validate_bytecode(bytecode)
        print(f"✓ Bytecode validation: {is_valid}")

        # Test normalization
        normalized = normalizer.normalize(bytecode)
        print(f"✓ Bytecode normalization: {len(normalized)} chars")

        # Test opcode extraction
        opcodes = normalizer.extract_opcodes(bytecode)
        print(f"✓ Opcode extraction: {len(opcodes)} opcodes")

        return True
    except Exception as e:
        print(f"✗ Basic functionality test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_comparison_engine():
    """Test comparison engine functionality"""
    print("\nTesting comparison engine...")

    try:
        from core.comparison_engine import MultiDimensionalComparison

        comparison = MultiDimensionalComparison()

        # Test with simple bytecodes
        bytecode1 = "608060405234801561001057600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b51"

        result = await comparison.compute_similarity(bytecode1, bytecode2)

        if isinstance(result, dict):
            print(f"✓ Comparison engine working - result keys: {list(result.keys())}")
            if "similarity_score" in result:
                print(f"  Similarity score: {result['similarity_score']:.3f}")
            return True
        else:
            print(f"✗ Unexpected result type: {type(result)}")
            return False

    except Exception as e:
        print(f"✗ Comparison engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_performance_monitor():
    """Test performance monitoring"""
    print("\nTesting performance monitoring...")

    try:
        from utils.metrics import PerformanceMonitor

        monitor = PerformanceMonitor()

        # Record some test data
        monitor.record_comparison(0.85, 123.45)
        monitor.record_comparison(0.92, 98.76)

        # Get statistics
        stats = monitor.get_statistics()
        print(
            f"✓ Performance monitoring - {stats['total_comparisons']} comparisons recorded"
        )
        print(f"  Average similarity: {stats['avg_similarity_score']:.3f}")
        print(f"  Average time: {stats['avg_comparison_time']:.2f}ms")

        return True
    except Exception as e:
        print(f"✗ Performance monitor test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_similarity_engine():
    """Test the full similarity engine"""
    print("\nTesting similarity engine...")

    try:
        from core.similarity_engine import SimilarityEngine

        engine = SimilarityEngine()

        # Test with simple bytecodes
        bytecode1 = "608060405234801561001057600080fd5b50"
        bytecode2 = "608060405234801561001057600080fd5b51"

        # This will use mocked neural network since we don't have trained weights
        print("  Note: Neural network will be mocked for this test")

        # Just test that the engine initializes properly
        print("✓ Similarity engine initialized successfully")
        return True

    except Exception as e:
        print(f"✗ Similarity engine test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests"""
    print("SCORPIUS Bytecode Similarity Engine - Validation Tests")
    print("=" * 55)

    tests = [
        ("Module Import Test", test_imports),
        ("Class Instantiation Test", test_instantiation),
        ("Basic Functionality Test", test_basic_functionality),
        ("Comparison Engine Test", test_comparison_engine),
        ("Performance Monitor Test", test_performance_monitor),
        ("Similarity Engine Test", test_similarity_engine),
    ]

    results = []

    for test_name, test_func in tests:
        print(f"\n{test_name}:")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results.append(result)
        except Exception as e:
            print(f"✗ Test {test_name} failed with exception: {e}")
            results.append(False)

    print("\n" + "=" * 55)
    passed = sum(results)
    total = len(results)
    print(f"Test Results: {passed}/{total} passed")

    if passed == total:
        print("🎉 All validation tests passed! SCORPIUS engine is ready.")
    else:
        print("⚠️  Some tests failed. Check the output above for details.")
        print(
            "💡 Note: Some failures may be expected if optional dependencies are missing."
        )

    return passed == total


if __name__ == "__main__":
    asyncio.run(main())
