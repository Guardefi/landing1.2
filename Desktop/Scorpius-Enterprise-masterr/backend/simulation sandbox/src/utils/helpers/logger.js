const winston = require('winston');
const path = require('path');

// Try to import DailyRotateFile, fall back to regular File transport if not available
let DailyRotateFile;
try {
  DailyRotateFile = require('winston-daily-rotate-file');
} catch (error) {
  console.warn('winston-daily-rotate-file not available, using regular file transport');
}

class Logger {
  constructor(component, options = {}) {
    this.component = component;
    this.options = {
      level: process.env.LOG_LEVEL || 'info',
      format: process.env.LOG_FORMAT || 'json',
      maxSize: process.env.LOG_MAX_SIZE || '100m',
      maxFiles: parseInt(process.env.LOG_MAX_FILES || '5'),
      datePattern: process.env.LOG_DATE_PATTERN || 'YYYY-MM-DD',
      ...options
    };

    this.logger = this.createLogger();
  }

  createLogger() {
    const logFormat = winston.format.combine(
      winston.format.timestamp(),
      winston.format.errors({ stack: true }),
      winston.format.printf(({ timestamp, level, message, stack, ...meta }) => {
        const logObject = {
          timestamp,
          level,
          component: this.component,
          message,
          ...meta
        };

        if (stack) {
          logObject.stack = stack;
        }

        return this.options.format === 'json' 
          ? JSON.stringify(logObject)
          : `${timestamp} [${level.toUpperCase()}] ${this.component}: ${message}`;
      })
    );

    const transports = [
      new winston.transports.Console({
        level: this.options.level,
        format: winston.format.combine(
          winston.format.colorize(),
          logFormat
        )
      })
    ];

    // Add file transport if not in test environment
    if (process.env.NODE_ENV !== 'test') {
      if (DailyRotateFile) {
        // Use daily rotate file if available
        transports.push(
          new DailyRotateFile({
            filename: path.join('logs', `${this.component}-%DATE%.log`),
            datePattern: this.options.datePattern,
            maxSize: this.options.maxSize,
            maxFiles: this.options.maxFiles,
            level: this.options.level,
            format: logFormat
          })
        );

        // Separate error log
        transports.push(
          new DailyRotateFile({
            filename: path.join('logs', `${this.component}-error-%DATE%.log`),
            datePattern: this.options.datePattern,
            maxSize: this.options.maxSize,
            maxFiles: this.options.maxFiles,
            level: 'error',
            format: logFormat
          })
        );
      } else {
        // Fall back to regular file transport
        transports.push(
          new winston.transports.File({
            filename: path.join('logs', `${this.component}.log`),
            level: this.options.level,
            format: logFormat
          })
        );

        transports.push(
          new winston.transports.File({
            filename: path.join('logs', `${this.component}-error.log`),
            level: 'error',
            format: logFormat
          })
        );
      }
    }

    return winston.createLogger({
      level: this.options.level,
      format: logFormat,
      transports,
      exceptionHandlers: [
        new winston.transports.File({ filename: path.join('logs', 'exceptions.log') })
      ],
      rejectionHandlers: [
        new winston.transports.File({ filename: path.join('logs', 'rejections.log') })
      ]
    });
  }

  child(metadata) {
    return new Logger(this.component, {
      ...this.options,
      defaultMeta: { ...this.options.defaultMeta, ...metadata }
    });
  }

  debug(message, meta = {}) {
    this.logger.debug(message, meta);
  }

  info(message, meta = {}) {
    this.logger.info(message, meta);
  }

  warn(message, meta = {}) {
    this.logger.warn(message, meta);
  }

  error(message, meta = {}) {
    if (typeof message === 'object' && message.stack) {
      this.logger.error(message.message, { ...meta, stack: message.stack });
    } else {
      this.logger.error(message, meta);
    }
  }

  fatal(message, meta = {}) {
    this.logger.error(`FATAL: ${message}`, { ...meta, fatal: true });
  }

  audit(action, details = {}) {
    this.logger.info(`AUDIT: ${action}`, { 
      ...details, 
      audit: true,
      timestamp: new Date().toISOString()
    });
  }

  security(event, details = {}) {
    this.logger.warn(`SECURITY: ${event}`, { 
      ...details, 
      security: true,
      timestamp: new Date().toISOString()
    });
  }

  performance(metric, value, unit = 'ms', details = {}) {
    this.logger.info(`PERFORMANCE: ${metric}`, {
      ...details,
      performance: true,
      metric,
      value,
      unit,
      timestamp: new Date().toISOString()
    });
  }
}

module.exports = Logger; 