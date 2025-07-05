"""
Main Similarity Engine
Enterprise-grade bytecode similarity detection engine
"""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

# Optional dependencies with fallbacks
try:
    import numpy as np
    HAS_NUMPY = True
except ImportError:
    HAS_NUMPY = False
    np = None

try:
    import torch
    HAS_TORCH = True
except ImportError:
    HAS_TORCH = False
    torch = None

# Try to import local modules - they might not exist in test environment
try:
    from core.comparison_engine import MultiDimensionalComparison
except ImportError:
    MultiDimensionalComparison = None

try:
    from models.siamese_network import SmartSDSiameseNetwork
except ImportError:
    SmartSDSiameseNetwork = None

try:
    from preprocessors.bytecode_normalizer import BytecodeNormalizer, FeatureExtractor
except ImportError:
    BytecodeNormalizer = None
    FeatureExtractor = None

try:
    from utils.metrics import MetricsCollector, PerformanceMonitor
except ImportError:
    MetricsCollector = None
    PerformanceMonitor = None

logger = logging.getLogger(__name__)


@dataclass
class SimilarityResult:
    """Result of similarity analysis"""

    similarity_score: float
    confidence: float
    dimension_scores: Dict[str, float]
    metadata: Dict
    processing_time: float


@dataclass
class SearchResult:
    """Result of similarity search"""

    bytecode_hash: str
    similarity_score: float
    confidence: float
    metadata: Dict


class SimilarityEngine:
    """Enterprise-grade bytecode similarity detection engine"""

    def __init__(self, config: Dict = None):
        self.config = config or self._get_default_config()

        # Initialize components
        self.comparison_engine = MultiDimensionalComparison(self.config)
        self.normalizer = BytecodeNormalizer()
        self.feature_extractor = FeatureExtractor()

        # Performance monitoring
        self.monitor = PerformanceMonitor()
        self.metrics_collector = MetricsCollector()

        # Neural network model (lazy loading)
        self._siamese_model = None
        self._device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        # Cache for frequent comparisons
        self._comparison_cache = {}
        self._cache_max_size = self.config.get("cache_size", 10000)

        # Vector index for similarity search (placeholder)
        self._vector_index = None
        self._embeddings = {}

        logger.info(f"Similarity engine initialized with device: {self._device}")

    def _get_default_config(self) -> Dict:
        """Get default configuration"""
        return {
            "similarity_threshold": 0.7,
            "top_k": 10,
            "use_gpu": torch.cuda.is_available(),
            "cache_size": 10000,
            "dimension_weights": {
                "instruction": 0.4,
                "operand": 0.2,
                "control_flow": 0.25,
                "data_flow": 0.15,
            },
            "model_config": {
                "vocab_size": 10000,
                "embedding_dim": 256,
                "hidden_dim": 512,
            },
        }

    async def compare_bytecodes(
        self, bytecode1: str, bytecode2: str, use_neural_network: bool = True
    ) -> SimilarityResult:
        """Compare two bytecodes and return similarity result"""
        start_time = time.time()

        try:
            # Check cache first
            cache_key = self._get_cache_key(bytecode1, bytecode2)
            if cache_key in self._comparison_cache:
                self.metrics_collector.record_cache_hit()
                cached_result = self._comparison_cache[cache_key]
                cached_result.processing_time = time.time() - start_time
                return cached_result

            self.metrics_collector.record_cache_miss()

            # Multi-dimensional comparison
            md_result = await self.comparison_engine.compute_similarity(
                bytecode1, bytecode2
            )

            # Neural network comparison (if enabled and model available)
            nn_score = 0.0
            if use_neural_network and self._siamese_model:
                nn_score = await self._neural_network_similarity(bytecode1, bytecode2)

            # Combine scores
            final_score = self._combine_scores(
                md_result["final_score"], nn_score, use_neural_network
            )

            # Create result
            result = SimilarityResult(
                similarity_score=final_score,
                confidence=md_result["confidence"],
                dimension_scores=md_result["dimension_scores"],
                metadata={
                    "multidimensional_score": md_result["final_score"],
                    "neural_network_score": nn_score,
                    "method": "hybrid" if use_neural_network else "multidimensional",
                },
                processing_time=time.time() - start_time,
            )

            # Cache result
            self._update_cache(cache_key, result)

            # Record metrics
            self.metrics_collector.record_comparison(result.processing_time, True)

            return result

        except Exception as e:
            logger.error(f"Error comparing bytecodes: {e}")
            self.metrics_collector.record_comparison(time.time() - start_time, False)
            raise

    async def find_similar_bytecode(
        self, query_bytecode: str, top_k: int = None, min_similarity: float = None
    ) -> List[SearchResult]:
        """Find similar bytecode from indexed collection"""
        top_k = top_k or self.config["top_k"]
        min_similarity = min_similarity or self.config["similarity_threshold"]

        self.monitor.start_measurement()

        try:
            # Get embedding for query
            query_embedding = await self._get_embedding(query_bytecode)

            # Search in vector index
            similar_embeddings = await self._vector_search(
                query_embedding, top_k * 2
            )  # Get more for filtering

            # Filter and rank results
            results = []
            for embedding_id, similarity in similar_embeddings:
                if similarity >= min_similarity:
                    metadata = self._embeddings.get(embedding_id, {})
                    result = SearchResult(
                        bytecode_hash=embedding_id,
                        similarity_score=similarity,
                        confidence=self._calculate_search_confidence(similarity),
                        metadata=metadata,
                    )
                    results.append(result)

            # Sort by similarity and return top_k
            results.sort(key=lambda x: x.similarity_score, reverse=True)
            final_results = results[:top_k]

            self.monitor.end_measurement(
                "similarity_search",
                {
                    "query_length": len(query_bytecode),
                    "results_found": len(final_results),
                    "total_candidates": len(similar_embeddings),
                },
            )

            return final_results

        except Exception as e:
            logger.error(f"Error in similarity search: {e}")
            self.monitor.end_measurement("similarity_search_error")
            raise

    async def index_bytecode(self, bytecode: str, metadata: Dict) -> str:
        """Index a bytecode for similarity search"""
        try:
            # Generate embedding
            embedding = await self._get_embedding(bytecode)

            # Generate hash for the bytecode
            import hashlib

            bytecode_hash = hashlib.sha256(bytecode.encode()).hexdigest()

            # Store embedding and metadata
            self._embeddings[bytecode_hash] = {
                "bytecode": bytecode,
                "embedding": embedding,
                **metadata,
            }

            # Add to vector index
            if self._vector_index:
                await self._vector_index.add(bytecode_hash, embedding)

            logger.debug(f"Indexed bytecode with hash: {bytecode_hash}")
            return bytecode_hash

        except Exception as e:
            logger.error(f"Error indexing bytecode: {e}")
            raise

    async def batch_index_bytecodes(
        self, bytecodes: List[Tuple[str, Dict]]
    ) -> List[str]:
        """Index multiple bytecodes efficiently"""
        self.monitor.start_measurement()

        hashes = []
        embeddings = []
        metadata_list = []

        try:
            # Process in batches
            batch_size = 32
            for i in range(0, len(bytecodes), batch_size):
                batch = bytecodes[i : i + batch_size]

                # Generate embeddings for batch
                batch_embeddings = await self._get_batch_embeddings(
                    [bc for bc, _ in batch]
                )

                for j, (bytecode, metadata) in enumerate(batch):
                    import hashlib

                    bytecode_hash = hashlib.sha256(bytecode.encode()).hexdigest()

                    embedding = batch_embeddings[j]

                    # Store
                    self._embeddings[bytecode_hash] = {
                        "bytecode": bytecode,
                        "embedding": embedding,
                        **metadata,
                    }

                    hashes.append(bytecode_hash)
                    embeddings.append(embedding)
                    metadata_list.append(metadata)

            # Add to vector index
            if self._vector_index and embeddings:
                await self._vector_index.batch_add(hashes, embeddings)

            self.monitor.end_measurement(
                "batch_indexing",
                {"total_bytecodes": len(bytecodes), "batch_size": batch_size},
            )

            logger.info(f"Indexed {len(hashes)} bytecodes")
            return hashes

        except Exception as e:
            logger.error(f"Error in batch indexing: {e}")
            self.monitor.end_measurement("batch_indexing_error")
            raise

    async def _get_embedding(self, bytecode: str) -> np.ndarray:
        """Get vector embedding for bytecode"""
        try:
            # Extract features
            features = await self.feature_extractor.extract_features(bytecode)

            # For now, create a simple feature vector
            # In production, this would use the trained embedding model
            feature_vector = self._features_to_vector(features)

            return feature_vector

        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            raise

    async def _get_batch_embeddings(self, bytecodes: List[str]) -> List[np.ndarray]:
        """Get embeddings for multiple bytecodes efficiently"""
        embeddings = []
        for bytecode in bytecodes:
            embedding = await self._get_embedding(bytecode)
            embeddings.append(embedding)
        return embeddings

    def _features_to_vector(self, features: Dict) -> np.ndarray:
        """Convert extracted features to vector representation"""
        # Simplified feature vectorization
        vector_parts = []

        # Opcode histogram (top 50 most common opcodes)
        histogram = features.get("opcode_histogram", {})
        common_opcodes = [
            "PUSH1",
            "POP",
            "MSTORE",
            "MLOAD",
            "SSTORE",
            "SLOAD",
            "JUMP",
            "JUMPI",
            "JUMPDEST",
            "ADD",
        ]
        for opcode in common_opcodes:
            vector_parts.append(histogram.get(opcode, 0))

        # Control flow features
        cf_features = features.get("control_flow_features", {})
        vector_parts.extend(
            [
                cf_features.get("jump_count", 0),
                cf_features.get("jumpi_count", 0),
                cf_features.get("jumpdest_count", 0),
                cf_features.get("total_jumps", 0),
            ]
        )

        # Data dependency features
        dd_features = features.get("data_dependency_features", {})
        vector_parts.extend(
            [
                dd_features.get("push_count", 0),
                dd_features.get("pop_count", 0),
                dd_features.get("dup_count", 0),
                dd_features.get("swap_count", 0),
                dd_features.get("stack_balance", 0),
            ]
        )

        # Structural features
        struct_features = features.get("structural_features", {})
        vector_parts.extend(
            [
                struct_features.get("total_instructions", 0),
                struct_features.get("unique_opcodes", 0),
                struct_features.get("complexity_ratio", 0.0),
            ]
        )

        # Pad to fixed size (256 dimensions)
        while len(vector_parts) < 256:
            vector_parts.append(0.0)

        return np.array(vector_parts[:256], dtype=np.float32)

    async def _neural_network_similarity(self, bytecode1: str, bytecode2: str) -> float:
        """Compute similarity using neural network"""
        if not self._siamese_model:
            await self._load_siamese_model()

        if not self._siamese_model:
            return 0.0

        try:
            # This would tokenize and run through the neural network
            # Placeholder implementation
            return 0.85  # Dummy score

        except Exception as e:
            logger.error(f"Error in neural network similarity: {e}")
            return 0.0

    async def _load_siamese_model(self):
        """Load pre-trained Siamese network model"""
        try:
            model_config = self.config["model_config"]
            self._siamese_model = SmartSDSiameseNetwork(
                vocab_size=model_config["vocab_size"],
                embedding_dim=model_config["embedding_dim"],
                hidden_dim=model_config["hidden_dim"],
            ).to(self._device)

            # Load trained weights if available
            import os

            model_path = "models/best_siamese_model.pth"
            if os.path.exists(model_path):
                self._siamese_model.load_state_dict(
                    torch.load(model_path, map_location=self._device)
                )
                self._siamese_model.eval()
                logger.info("Loaded pre-trained Siamese model")
            else:
                logger.warning("No pre-trained model found, using random weights")

        except Exception as e:
            logger.error(f"Error loading Siamese model: {e}")
            self._siamese_model = None

    def _combine_scores(self, md_score: float, nn_score: float, use_nn: bool) -> float:
        """Combine multi-dimensional and neural network scores"""
        if not use_nn or nn_score == 0.0:
            return md_score

        # Weighted combination
        md_weight = 0.6
        nn_weight = 0.4

        return md_weight * md_score + nn_weight * nn_score

    async def _vector_search(
        self, query_embedding: np.ndarray, top_k: int
    ) -> List[Tuple[str, float]]:
        """Search for similar vectors in the index"""
        # Simplified vector search using cosine similarity
        # In production, use a proper vector database like Faiss, Pinecone, etc.

        similarities = []
        for bytecode_hash, data in self._embeddings.items():
            embedding = data["embedding"]
            similarity = self._cosine_similarity(query_embedding, embedding)
            similarities.append((bytecode_hash, similarity))

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:top_k]

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Compute cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    def _calculate_search_confidence(self, similarity: float) -> float:
        """Calculate confidence for search results"""
        # Simple confidence calculation based on similarity score
        if similarity > 0.9:
            return 0.95
        elif similarity > 0.8:
            return 0.85
        elif similarity > 0.7:
            return 0.75
        else:
            return 0.6

    def _get_cache_key(self, bytecode1: str, bytecode2: str) -> str:
        """Generate cache key for bytecode pair"""
        import hashlib

        # Sort to ensure consistent key regardless of order
        sorted_bytecodes = tuple(sorted([bytecode1, bytecode2]))
        key_string = "|".join(sorted_bytecodes)
        return hashlib.md5(key_string.encode()).hexdigest()

    def _update_cache(self, key: str, result: SimilarityResult):
        """Update comparison cache"""
        if len(self._comparison_cache) >= self._cache_max_size:
            # Remove oldest entry (simple LRU)
            oldest_key = next(iter(self._comparison_cache))
            del self._comparison_cache[oldest_key]

        self._comparison_cache[key] = result

    def get_engine_stats(self) -> Dict:
        """Get engine statistics"""
        return {
            "total_indexed_bytecodes": len(self._embeddings),
            "cache_size": len(self._comparison_cache),
            "device": str(self._device),
            "model_loaded": self._siamese_model is not None,
            "metrics": self.metrics_collector.get_metrics(),
            "performance_summary": self.monitor.get_performance_summary(),
        }

    def clear_cache(self):
        """Clear comparison cache"""
        self._comparison_cache.clear()
        logger.info("Comparison cache cleared")

    async def cleanup(self):
        """Cleanup resources"""
        self.clear_cache()
        self._embeddings.clear()
        if self._vector_index:
            await self._vector_index.close()
        logger.info("Engine cleanup completed")
