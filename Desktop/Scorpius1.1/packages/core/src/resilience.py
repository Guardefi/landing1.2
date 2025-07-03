"""
Async Resilience Module for Scorpius Enterprise Platform
Implements circuit breakers, retry logic, and failure handling patterns.
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, Optional, TypeVar, Union, List
from dataclasses import dataclass, field
from enum import Enum
from functools import wraps
from contextlib import asynccontextmanager

import pybreaker
from tenacity import (
    AsyncRetrying, 
    retry_if_exception_type, 
    stop_after_attempt, 
    wait_exponential,
    wait_random_exponential,
    before_sleep_log,
    after_log
)

logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitBreakerState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_attempts: int = 3
    min_wait: float = 1.0
    max_wait: float = 60.0
    exponential_base: float = 2.0
    jitter: bool = True
    retry_on_exceptions: tuple = (Exception,)
    stop_on_exceptions: tuple = ()


@dataclass
class CircuitBreakerConfig:
    """Configuration for circuit breaker behavior"""
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: tuple = (Exception,)
    name: Optional[str] = None


@dataclass
class ResilienceStats:
    """Statistics for resilience patterns"""
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    retries_attempted: int = 0
    circuit_breaker_trips: int = 0
    last_failure_time: Optional[float] = None
    last_success_time: Optional[float] = None


class AsyncCircuitBreaker:
    """
    Async-aware circuit breaker implementation
    """
    
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.name = config.name or f"cb_{id(self)}"
        
        # Create pybreaker instance
        self._breaker = pybreaker.CircuitBreaker(
            failure_threshold=config.failure_threshold,
            recovery_timeout=config.recovery_timeout,
            expected_exception=config.expected_exception,
            name=self.name
        )
        
        self.stats = ResilienceStats()
        
        # Add listeners
        self._breaker.add_listener(self._on_failure)
        self._breaker.add_listener(self._on_success)
        self._breaker.add_listener(self._on_state_change)
    
    async def __call__(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        try:
            self.stats.total_calls += 1
            
            # Use pybreaker's call method (it handles async functions)
            result = await self._breaker.call(func, *args, **kwargs)
            
            self.stats.successful_calls += 1
            self.stats.last_success_time = time.time()
            
            return result
            
        except pybreaker.CircuitBreakerError as e:
            self.stats.circuit_breaker_trips += 1
            logger.warning(f"Circuit breaker {self.name} is open: {e}")
            raise
        except Exception as e:
            self.stats.failed_calls += 1
            self.stats.last_failure_time = time.time()
            logger.error(f"Function failed in circuit breaker {self.name}: {e}")
            raise
    
    def _on_failure(self, cb, exception):
        """Called when a failure occurs"""
        logger.warning(f"Circuit breaker {self.name} recorded failure: {exception}")
    
    def _on_success(self, cb):
        """Called when a success occurs"""
        logger.debug(f"Circuit breaker {self.name} recorded success")
    
    def _on_state_change(self, cb, old_state, new_state):
        """Called when circuit breaker state changes"""
        logger.info(f"Circuit breaker {self.name} state changed: {old_state} -> {new_state}")
    
    @property
    def state(self) -> CircuitBreakerState:
        """Get current circuit breaker state"""
        state_map = {
            pybreaker.STATE_CLOSED: CircuitBreakerState.CLOSED,
            pybreaker.STATE_OPEN: CircuitBreakerState.OPEN,
            pybreaker.STATE_HALF_OPEN: CircuitBreakerState.HALF_OPEN
        }
        return state_map.get(self._breaker.current_state, CircuitBreakerState.CLOSED)
    
    def reset(self):
        """Reset circuit breaker to closed state"""
        self._breaker.reset()
        logger.info(f"Circuit breaker {self.name} reset")


class AsyncRetrier:
    """
    Async retry mechanism with exponential backoff and jitter
    """
    
    def __init__(self, config: RetryConfig):
        self.config = config
        self.stats = ResilienceStats()
    
    async def __call__(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """Execute function with retry logic"""
        # Configure retry behavior
        retry_config = {
            'stop': stop_after_attempt(self.config.max_attempts),
            'retry': retry_if_exception_type(self.config.retry_on_exceptions),
            'before_sleep': before_sleep_log(logger, logging.WARNING),
            'after': after_log(logger, logging.INFO),
        }
        
        # Choose wait strategy based on jitter configuration
        if self.config.jitter:
            retry_config['wait'] = wait_random_exponential(
                multiplier=1,
                max=self.config.max_wait,
                exp_base=self.config.exponential_base
            )
        else:
            retry_config['wait'] = wait_exponential(
                multiplier=self.config.min_wait,
                max=self.config.max_wait,
                exp_base=self.config.exponential_base
            )
        
        # Execute with retry
        async for attempt in AsyncRetrying(**retry_config):
            with attempt:
                try:
                    self.stats.total_calls += 1
                    result = await func(*args, **kwargs)
                    self.stats.successful_calls += 1
                    self.stats.last_success_time = time.time()
                    return result
                    
                except self.config.stop_on_exceptions as e:
                    # Don't retry on these exceptions
                    self.stats.failed_calls += 1
                    self.stats.last_failure_time = time.time()
                    logger.error(f"Non-retryable exception: {e}")
                    raise
                    
                except Exception as e:
                    self.stats.retries_attempted += 1
                    self.stats.last_failure_time = time.time()
                    
                    if attempt.retry_state.attempt_number >= self.config.max_attempts:
                        self.stats.failed_calls += 1
                        logger.error(f"Max retries ({self.config.max_attempts}) exceeded for function")
                        raise
                    
                    logger.warning(f"Attempt {attempt.retry_state.attempt_number} failed: {e}")
                    raise


class ResilientAsyncClient:
    """
    A resilient async client that combines circuit breaker and retry patterns
    """
    
    def __init__(
        self, 
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
        name: str = "resilient_client"
    ):
        self.name = name
        
        # Initialize components
        self.retry_config = retry_config or RetryConfig()
        self.cb_config = circuit_breaker_config or CircuitBreakerConfig(name=f"{name}_cb")
        
        self.retrier = AsyncRetrier(self.retry_config)
        self.circuit_breaker = AsyncCircuitBreaker(self.cb_config)
        
        self.global_stats = ResilienceStats()
    
    async def execute(self, func: Callable[..., Any], *args, **kwargs) -> Any:
        """
        Execute a function with both circuit breaker and retry protection
        """
        start_time = time.time()
        
        try:
            # Wrap function with retry logic first, then circuit breaker
            async def retry_wrapped():
                return await self.retrier(func, *args, **kwargs)
            
            result = await self.circuit_breaker(retry_wrapped)
            
            execution_time = time.time() - start_time
            logger.debug(f"Function executed successfully in {execution_time:.2f}s")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Function failed after {execution_time:.2f}s: {e}")
            
            # Update global stats
            self.global_stats.total_calls += 1
            self.global_stats.failed_calls += 1
            self.global_stats.last_failure_time = time.time()
            
            raise
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the resilient client"""
        return {
            "name": self.name,
            "circuit_breaker": {
                "state": self.circuit_breaker.state.value,
                "stats": self.circuit_breaker.stats.__dict__
            },
            "retrier": {
                "stats": self.retrier.stats.__dict__
            },
            "global_stats": self.global_stats.__dict__
        }


# Decorator for easy application of resilience patterns
def resilient(
    retry_config: Optional[RetryConfig] = None,
    circuit_breaker_config: Optional[CircuitBreakerConfig] = None,
    client_name: Optional[str] = None
):
    """
    Decorator to make async functions resilient
    
    Usage:
        @resilient(
            retry_config=RetryConfig(max_attempts=3),
            circuit_breaker_config=CircuitBreakerConfig(failure_threshold=5)
        )
        async def my_function():
            # Your async code here
            pass
    """
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        name = client_name or f"resilient_{func.__name__}"
        client = ResilientAsyncClient(retry_config, circuit_breaker_config, name)
        
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await client.execute(func, *args, **kwargs)
        
        # Attach client for inspection
        wrapper._resilience_client = client
        return wrapper
    
    return decorator


# Predefined configurations for common scenarios
class ResilienceConfigs:
    """Predefined resilience configurations for common scenarios"""
    
    # Database operations
    DATABASE = {
        'retry_config': RetryConfig(
            max_attempts=3,
            min_wait=0.5,
            max_wait=10.0,
            retry_on_exceptions=(ConnectionError, TimeoutError)
        ),
        'circuit_breaker_config': CircuitBreakerConfig(
            failure_threshold=5,
            recovery_timeout=30,
            expected_exception=(ConnectionError, TimeoutError)
        )
    }
    
    # External API calls
    EXTERNAL_API = {
        'retry_config': RetryConfig(
            max_attempts=5,
            min_wait=1.0,
            max_wait=30.0,
            retry_on_exceptions=(ConnectionError, TimeoutError, OSError)
        ),
        'circuit_breaker_config': CircuitBreakerConfig(
            failure_threshold=10,
            recovery_timeout=60,
            expected_exception=(ConnectionError, TimeoutError, OSError)
        )
    }
    
    # Internal microservice calls
    MICROSERVICE = {
        'retry_config': RetryConfig(
            max_attempts=3,
            min_wait=0.2,
            max_wait=5.0,
            retry_on_exceptions=(ConnectionError, TimeoutError)
        ),
        'circuit_breaker_config': CircuitBreakerConfig(
            failure_threshold=3,
            recovery_timeout=20,
            expected_exception=(ConnectionError, TimeoutError)
        )
    }
    
    # Blockchain/Web3 operations
    BLOCKCHAIN = {
        'retry_config': RetryConfig(
            max_attempts=5,
            min_wait=2.0,
            max_wait=60.0,
            retry_on_exceptions=(ConnectionError, TimeoutError, ValueError)
        ),
        'circuit_breaker_config': CircuitBreakerConfig(
            failure_threshold=7,
            recovery_timeout=120,
            expected_exception=(ConnectionError, TimeoutError)
        )
    }


# Global resilience manager
class ResilienceManager:
    """Global manager for resilience patterns"""
    
    def __init__(self):
        self.clients: Dict[str, ResilientAsyncClient] = {}
    
    def get_client(
        self, 
        name: str,
        retry_config: Optional[RetryConfig] = None,
        circuit_breaker_config: Optional[CircuitBreakerConfig] = None
    ) -> ResilientAsyncClient:
        """Get or create a resilient client"""
        if name not in self.clients:
            self.clients[name] = ResilientAsyncClient(
                retry_config=retry_config,
                circuit_breaker_config=circuit_breaker_config,
                name=name
            )
        return self.clients[name]
    
    def get_health_report(self) -> Dict[str, Any]:
        """Get health report for all clients"""
        return {
            client_name: client.get_health_status()
            for client_name, client in self.clients.items()
        }
    
    def reset_all_circuit_breakers(self):
        """Reset all circuit breakers"""
        for client in self.clients.values():
            client.circuit_breaker.reset()
        logger.info("All circuit breakers reset")


# Global instance
resilience_manager = ResilienceManager()


# Convenience functions
async def execute_with_resilience(
    func: Callable[..., Any],
    *args,
    client_name: str = "default",
    config_preset: str = None,
    **kwargs
) -> Any:
    """Execute a function with resilience patterns"""
    # Get configuration from preset
    config = {}
    if config_preset and hasattr(ResilienceConfigs, config_preset.upper()):
        config = getattr(ResilienceConfigs, config_preset.upper())
    
    client = resilience_manager.get_client(
        client_name,
        retry_config=config.get('retry_config'),
        circuit_breaker_config=config.get('circuit_breaker_config')
    )
    
    return await client.execute(func, *args, **kwargs)
