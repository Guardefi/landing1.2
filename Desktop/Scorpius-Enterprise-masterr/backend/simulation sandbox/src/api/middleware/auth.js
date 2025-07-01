const jwt = require('jsonwebtoken');
const Logger = require('../../utils/helpers/logger');

const logger = new Logger('AuthMiddleware');

/**
 * JWT Authentication Middleware
 */
const authMiddleware = async (req, res, next) => {
  try {
    const token = extractToken(req);
    
    if (!token) {
      return res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'No authentication token provided'
      });
    }

    // Verify JWT token
    const decoded = jwt.verify(token, process.env.JWT_SECRET || 'scorpius-sandbox-secret');
    
    // Add user information to request
    req.user = {
      id: decoded.userId,
      email: decoded.email,
      role: decoded.role || 'user',
      permissions: decoded.permissions || [],
      tokenType: decoded.type || 'access'
    };

    // Log successful authentication
    logger.debug('User authenticated:', {
      userId: req.user.id,
      email: req.user.email,
      role: req.user.role,
      path: req.path,
      method: req.method
    });

    next();

  } catch (error) {
    if (error.name === 'JsonWebTokenError') {
      logger.warn('Invalid JWT token:', { error: error.message, path: req.path });
      return res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Invalid authentication token'
      });
    }

    if (error.name === 'TokenExpiredError') {
      logger.warn('Expired JWT token:', { path: req.path });
      return res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Authentication token has expired'
      });
    }

    logger.error('Authentication error:', error);
    return res.status(500).json({
      success: false,
      error: 'Internal server error',
      message: 'Authentication failed'
    });
  }
};

/**
 * Extract token from request headers
 */
const extractToken = (req) => {
  const authHeader = req.headers.authorization;
  
  if (authHeader && authHeader.startsWith('Bearer ')) {
    return authHeader.substring(7);
  }
  
  // Also check for token in cookies (for web interface)
  if (req.cookies && req.cookies.access_token) {
    return req.cookies.access_token;
  }
  
  return null;
};

/**
 * Role-based authorization middleware
 */
const requireRole = (roles) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Authentication required'
      });
    }

    const userRole = req.user.role;
    const allowedRoles = Array.isArray(roles) ? roles : [roles];

    if (!allowedRoles.includes(userRole)) {
      logger.warn('Insufficient permissions:', {
        userId: req.user.id,
        userRole,
        requiredRoles: allowedRoles,
        path: req.path
      });

      return res.status(403).json({
        success: false,
        error: 'Forbidden',
        message: 'Insufficient permissions'
      });
    }

    next();
  };
};

/**
 * Permission-based authorization middleware
 */
const requirePermission = (permission) => {
  return (req, res, next) => {
    if (!req.user) {
      return res.status(401).json({
        success: false,
        error: 'Unauthorized',
        message: 'Authentication required'
      });
    }

    const userPermissions = req.user.permissions || [];

    if (!userPermissions.includes(permission)) {
      logger.warn('Missing permission:', {
        userId: req.user.id,
        userPermissions,
        requiredPermission: permission,
        path: req.path
      });

      return res.status(403).json({
        success: false,
        error: 'Forbidden',
        message: `Missing required permission: ${permission}`
      });
    }

    next();
  };
};

/**
 * Optional authentication middleware (doesn't fail if no token)
 */
const optionalAuth = async (req, res, next) => {
  try {
    const token = extractToken(req);
    
    if (token) {
      const decoded = jwt.verify(token, process.env.JWT_SECRET || 'scorpius-sandbox-secret');
      req.user = {
        id: decoded.userId,
        email: decoded.email,
        role: decoded.role || 'user',
        permissions: decoded.permissions || []
      };
    }
    
    next();
  } catch (error) {
    // Ignore authentication errors in optional auth
    next();
  }
};

module.exports = authMiddleware;
module.exports.requireRole = requireRole;
module.exports.requirePermission = requirePermission;
module.exports.optionalAuth = optionalAuth; 