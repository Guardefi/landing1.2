const { validationResult } = require('express-validator');
const Logger = require('../../utils/helpers/logger');

const logger = new Logger('ValidationMiddleware');

/**
 * Express middleware for handling validation errors
 */
const validationMiddleware = (req, res, next) => {
  const errors = validationResult(req);
  
  if (!errors.isEmpty()) {
    logger.warn('Validation failed:', {
      path: req.path,
      method: req.method,
      errors: errors.array(),
      userId: req.user?.id || 'anonymous'
    });
    
    return res.status(400).json({
      success: false,
      error: 'Validation failed',
      details: errors.array().map(error => ({
        field: error.param,
        message: error.msg,
        value: error.value,
        location: error.location
      }))
    });
  }
  
  next();
};

module.exports = validationMiddleware; 