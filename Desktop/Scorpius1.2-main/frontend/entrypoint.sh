#!/bin/sh

# Set environment variables
export PORT=${PORT:-80}
export VITE_PORT=${VITE_PORT:-80}
export VITE_HMR_PORT=${VITE_HMR_PORT:-24678}

# Start nginx
nginx -g "daemon off;"
