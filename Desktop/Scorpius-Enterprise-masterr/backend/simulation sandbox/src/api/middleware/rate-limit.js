const rateLimit = require('express-rate-limit');
const RedisStore = require('rate-limit-redis');
const Redis = require('ioredis');
const Logger = require('../../utils/helpers/logger');

const logger = new Logger('RateLimitMiddleware');

// Create Redis client for rate limiting (if Redis is available)
let redisClient;
if (process.env.REDIS_URL) {
  try {
    redisClient = new Redis(process.env.REDIS_URL);
    logger.info('Connected to Redis for rate limiting');
  } catch (error) {
    logger.warn('Failed to connect to Redis, using memory store for rate limiting:', error.message);
  }
}

/**
 * Create rate limit middleware with configurable options
 */
const createRateLimiter = (options = {}) => {
  const defaultOptions = {
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100, // limit each IP to 100 requests per windowMs
    message: {
      success: false,
      error: 'Too many requests',
      message: 'Rate limit exceeded. Please try again later.',
      retryAfter: Math.ceil(options.windowMs / 1000) || 900
    },
    standardHeaders: true, // Return rate limit info in the `RateLimit-*` headers
    legacyHeaders: false, // Disable the `X-RateLimit-*` headers
    // Use Redis store if available, otherwise use memory store
    store: redisClient ? new RedisStore({
      sendCommand: (...args) => redisClient.call(...args),
      prefix: 'rate_limit:',
    }) : undefined,
    handler: (req, res) => {
      logger.warn('Rate limit exceeded:', {
        ip: req.ip,
        path: req.path,
        method: req.method,
        userId: req.user?.id || 'anonymous',
        userAgent: req.get('User-Agent')
      });
      
      res.status(429).json(defaultOptions.message);
    },
    skip: (req) => {
      // Skip rate limiting for health checks in development
      if (process.env.NODE_ENV === 'development' && req.path.includes('/health')) {
        return true;
      }
      return false;
    },
    keyGenerator: (req) => {
      // Use user ID if authenticated, otherwise use IP
      return req.user?.id || req.ip;
    }
  };

  return rateLimit({
    ...defaultOptions,
    ...options
  });
};

// Pre-configured rate limiters for different endpoints
const rateLimiters = {
  // General API rate limit
  general: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 100 // 100 requests per 15 minutes
  }),
  
  // Strict rate limit for resource-intensive operations
  strict: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 10 // 10 requests per 15 minutes
  }),
  
  // Authentication rate limit
  auth: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5, // 5 login attempts per 15 minutes
    skipSuccessfulRequests: true,
    message: {
      success: false,
      error: 'Too many authentication attempts',
      message: 'Account temporarily locked due to too many failed login attempts',
      retryAfter: 900
    }
  }),
  
  // Simulation creation rate limit
  simulation: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 20 // 20 simulations per 15 minutes
  }),
  
  // Contract deployment rate limit
  deployment: createRateLimiter({
    windowMs: 15 * 60 * 1000, // 15 minutes
    max: 5 // 5 deployments per 15 minutes
  })
};

module.exports = createRateLimiter;
module.exports.rateLimiters = rateLimiters; 