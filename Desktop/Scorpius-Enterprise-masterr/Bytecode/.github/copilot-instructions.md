# SCORPIUS Bytecode Similarity Engine - Copilot Instructions

<!-- Use this file to provide workspace-specific custom instructions to Copilot. For more details, visit https://code.visualstudio.com/docs/copilot/copilot-customization#_use-a-githubcopilotinstructionsmd-file -->

## Project Overview

This is an enterprise-grade bytecode similarity detection engine for smart contract analysis. The project implements state-of-the-art machine learning techniques including:

- **Multi-dimensional comparison** using SeByte-inspired Jaccard similarity (85.46% recall)
- **Siamese neural networks** with attention mechanisms (98.37% accuracy)
- **Advanced bytecode normalization** for compilation noise reduction
- **Vector-based similarity search** with embedding indexing

## Architecture Guidelines

### Code Organization
- `core/` - Main similarity engine and comparison logic
- `models/` - Neural network implementations (Siamese networks, attention mechanisms)
- `preprocessors/` - Bytecode normalization and feature extraction
- `utils/` - Performance monitoring, metrics, and utilities
- `api/` - FastAPI REST endpoints
- `scripts/` - Training scripts and evaluation tools
- `configs/` - YAML configuration files

### Key Design Patterns
1. **Async/Await**: Use async programming for I/O operations and model inference
2. **Factory Pattern**: For creating different similarity computation engines
3. **Strategy Pattern**: For different normalization and comparison strategies
4. **Observer Pattern**: For performance monitoring and metrics collection

### Dependencies and Technologies
- **PyTorch**: For neural network models and GPU acceleration
- **FastAPI**: For REST API endpoints
- **scikit-learn**: For traditional ML metrics and preprocessing
- **numpy**: For numerical computations and vector operations
- **asyncio**: For asynchronous processing

## Coding Standards

### Python Best Practices
- Follow PEP 8 style guidelines
- Use type hints for all function parameters and return values
- Document all classes and methods with comprehensive docstrings
- Use dataclasses for structured data objects
- Implement proper error handling with custom exceptions

### Performance Considerations
- Use batch processing for multiple comparisons
- Implement caching for frequently compared bytecodes
- Leverage GPU acceleration when available
- Monitor memory usage for large-scale processing

### EVM Bytecode Specifics
- Handle all EVM opcodes correctly (PUSH1-PUSH32, DUP1-DUP16, SWAP1-SWAP16)
- Parse bytecode instruction sequences with proper operand handling
- Normalize compilation artifacts while preserving semantic meaning
- Extract control flow and data flow patterns

## Testing Guidelines

### Unit Tests
- Test each component in isolation
- Mock external dependencies (vector databases, GPU operations)
- Use parametrized tests for different bytecode patterns
- Verify numerical accuracy of similarity calculations

### Integration Tests
- Test complete similarity comparison workflows
- Validate API endpoints with real bytecode examples
- Test training pipeline with synthetic data
- Benchmark performance with various dataset sizes

### Test Data
- Use real smart contract bytecodes from Ethereum
- Include edge cases (empty bytecode, malformed input)
- Test with similar contracts (same source, different optimization)
- Test with dissimilar contracts

## Security Considerations

### Input Validation
- Validate hex strings for bytecode input
- Sanitize file paths and configuration values
- Implement rate limiting for API endpoints
- Validate vector dimensions and model inputs

### API Security
- Use authentication tokens for API access
- Implement CORS policies appropriately
- Log security-relevant events
- Validate request sizes and formats

## Machine Learning Guidelines

### Model Training
- Use stratified splitting for balanced datasets
- Implement early stopping to prevent overfitting
- Track comprehensive metrics (precision, recall, F1, AUC)
- Save model checkpoints regularly

### Feature Engineering
- Extract semantic features from bytecode patterns
- Normalize features consistently across train/test
- Handle variable-length sequences properly
- Document feature extraction rationale

### Model Evaluation
- Use cross-validation for robust evaluation
- Test on held-out datasets
- Analyze failure cases and edge conditions
- Compare against baseline methods

## Configuration Management

### YAML Configurations
- Use hierarchical configuration structure
- Provide sensible defaults for all parameters
- Document configuration options thoroughly
- Support environment-specific overrides

### Model Hyperparameters
- Use configuration files for all hyperparameters
- Support hyperparameter tuning workflows
- Version control configuration changes
- Document parameter sensitivity

## Documentation

### Code Documentation
- Write clear, comprehensive docstrings
- Include usage examples in docstrings
- Document algorithm choices and trade-offs
- Maintain up-to-date README files

### API Documentation
- Use OpenAPI/Swagger for REST API documentation
- Provide request/response examples
- Document error codes and handling
- Include performance characteristics

## Deployment Guidelines

### Production Readiness
- Implement health checks for all services
- Use structured logging with appropriate levels
- Monitor resource usage (CPU, memory, GPU)
- Implement graceful shutdown procedures

### Scalability
- Design for horizontal scaling
- Use connection pooling for databases
- Implement circuit breakers for external services
- Cache frequently accessed data

## Research Foundation

This implementation is based on cutting-edge research:
- **SeByte**: Multi-dimensional semantic bytecode similarity
- **SmartSD**: Siamese networks with attention for smart contracts
- **CEBin**: Hybrid comparison frameworks
- **ETHBMC**: Large-scale bytecode analysis techniques

When extending the system, reference recent academic literature and maintain consistency with proven approaches.
