#!/bin/bash
# Scorpius Vulnerability Scanner Setup Script
# Enterprise-grade deployment with Docker and simulation capabilities

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCORPIUS_VERSION="1.0.0"
DOCKER_COMPOSE_VERSION="2.21.0"
PYTHON_VERSION="3.11"

echo -e "${BLUE}🦂 Scorpius Vulnerability Scanner Enterprise Setup${NC}"
echo -e "${BLUE}Version: $SCORPIUS_VERSION${NC}"
echo "=================================================="

# Function to print status messages
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
check_root() {
    if [[ $EUID -eq 0 ]]; then
        print_error "This script should not be run as root for security reasons"
        exit 1
    fi
}

# Check system requirements
check_requirements() {
    print_status "Checking system requirements..."
    
    # Check OS
    if [[ "$OSTYPE" != "linux-gnu"* ]] && [[ "$OSTYPE" != "darwin"* ]]; then
        print_error "Unsupported operating system: $OSTYPE"
        print_error "Scorpius supports Linux and macOS"
        exit 1
    fi
    
    # Check available memory (minimum 8GB recommended)
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        MEMORY_KB=$(grep MemTotal /proc/meminfo | awk '{print $2}')
        MEMORY_GB=$((MEMORY_KB / 1024 / 1024))
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        MEMORY_BYTES=$(sysctl -n hw.memsize)
        MEMORY_GB=$((MEMORY_BYTES / 1024 / 1024 / 1024))
    fi
    
    if [[ $MEMORY_GB -lt 8 ]]; then
        print_warning "System has ${MEMORY_GB}GB RAM. Minimum 8GB recommended for optimal performance"
    fi
    
    # Check disk space (minimum 20GB recommended)
    DISK_SPACE=$(df -BG . | awk 'NR==2 {print $4}' | sed 's/G//')
    if [[ $DISK_SPACE -lt 20 ]]; then
        print_warning "Available disk space: ${DISK_SPACE}GB. Minimum 20GB recommended"
    fi
    
    print_status "System requirements check completed"
}

# Install Docker if not present
install_docker() {
    if ! command -v docker &> /dev/null; then
        print_status "Installing Docker..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Install Docker on Linux
            curl -fsSL https://get.docker.com -o get-docker.sh
            sh get-docker.sh
            rm get-docker.sh
            
            # Add user to docker group
            sudo usermod -aG docker $USER
            print_warning "Please log out and log back in for Docker group changes to take effect"
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            print_error "Please install Docker Desktop for Mac manually from https://docker.com"
            exit 1
        fi
    else
        print_status "Docker is already installed"
        docker --version
    fi
}

# Install Docker Compose if not present
install_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        print_status "Installing Docker Compose..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo curl -L "https://github.com/docker/compose/releases/download/v${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
            sudo chmod +x /usr/local/bin/docker-compose
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            print_status "Docker Compose should be included with Docker Desktop"
        fi
    else
        print_status "Docker Compose is already installed"
        docker-compose --version
    fi
}

# Install Python if not present
install_python() {
    if ! command -v python3 &> /dev/null; then
        print_status "Installing Python $PYTHON_VERSION..."
        
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            sudo apt-get update
            sudo apt-get install -y python3 python3-pip python3-venv
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            if command -v brew &> /dev/null; then
                brew install python@3.11
            else
                print_error "Please install Homebrew or Python manually"
                exit 1
            fi
        fi
    else
        print_status "Python is already installed"
        python3 --version
    fi
}

# Create Python virtual environment
setup_python_env() {
    print_status "Setting up Python virtual environment..."
    
    if [[ ! -d "venv" ]]; then
        python3 -m venv venv
    fi
    
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    
    print_status "Python environment setup completed"
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    
    mkdir -p contracts
    mkdir -p reports
    mkdir -p logs
    mkdir -p simulation_results
    mkdir -p config
    mkdir -p exploits
    
    print_status "Directory structure created"
}

# Generate configuration files
generate_config() {
    print_status "Generating configuration files..."
    
    # Create .env file
    if [[ ! -f ".env" ]]; then
        cat > .env << EOF
# Scorpius Configuration
SCORPIUS_ENV=development
SCORPIUS_API_KEY=scorpius-api-token-change-me
SCORPIUS_SECRET_KEY=change-me-to-a-secure-secret-key

# Database
DATABASE_URL=postgresql://scorpius:scorpius_secure_pass@localhost:5432/scorpius

# Redis
REDIS_URL=redis://:scorpius_redis_pass@localhost:6379/0

# Docker
COMPOSE_PROJECT_NAME=scorpius

# External Services
MYTHX_API_KEY=your-mythx-api-key-here
MAINNET_FORK_URL=https://mainnet.infura.io/v3/your-infura-key

# Monitoring
ENABLE_MONITORING=false
GRAFANA_ADMIN_PASSWORD=admin
PROMETHEUS_RETENTION=15d

# Storage
ENABLE_IPFS=false
ENABLE_MINIO=false
MINIO_ROOT_USER=scorpius
MINIO_ROOT_PASSWORD=scorpius_minio_pass
EOF
        print_status "Created .env configuration file"
        print_warning "Please update the .env file with your specific configuration"
    fi
    
    # Create logging configuration
    if [[ ! -f "config/logging.yaml" ]]; then
        mkdir -p config
        cat > config/logging.yaml << EOF
version: 1
disable_existing_loggers: false

formatters:
  standard:
    format: '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
  detailed:
    format: '%(asctime)s [%(levelname)s] %(name)s:%(lineno)d: %(message)s'

handlers:
  console:
    class: logging.StreamHandler
    level: INFO
    formatter: standard
    stream: ext://sys.stdout
  
  file:
    class: logging.handlers.RotatingFileHandler
    level: DEBUG
    formatter: detailed
    filename: logs/scorpius.log
    maxBytes: 10485760  # 10MB
    backupCount: 5

loggers:
  scorpius:
    level: DEBUG
    handlers: [console, file]
    propagate: false

root:
  level: INFO
  handlers: [console]
EOF
        print_status "Created logging configuration"
    fi
}

# Build Docker images
build_images() {
    print_status "Building Docker images..."
    
    # Build plugin images
    docker-compose build slither mythril manticore mythx ethereum-sim
    
    # Build main application
    docker-compose build scorpius-main
    
    print_status "Docker images built successfully"
}

# Initialize database
init_database() {
    print_status "Initializing database..."
    
    # Start database services
    docker-compose up -d postgres redis
    
    # Wait for database to be ready
    sleep 10
    
    # Run database migrations (placeholder)
    # docker-compose exec scorpius-main python -m alembic upgrade head
    
    print_status "Database initialized"
}

# Setup monitoring (optional)
setup_monitoring() {
    read -p "Do you want to enable monitoring (ELK stack + Grafana)? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setting up monitoring stack..."
        
        # Update .env file
        sed -i 's/ENABLE_MONITORING=false/ENABLE_MONITORING=true/' .env
        
        # Start monitoring services
        docker-compose --profile monitoring up -d
        
        print_status "Monitoring stack started"
        print_status "Grafana: http://localhost:3000 (admin/admin)"
        print_status "Kibana: http://localhost:5601"
        print_status "Prometheus: http://localhost:9090"
    fi
}

# Setup storage (optional)
setup_storage() {
    read -p "Do you want to enable distributed storage (IPFS + MinIO)? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setting up storage services..."
        
        # Update .env file
        sed -i 's/ENABLE_IPFS=false/ENABLE_IPFS=true/' .env
        sed -i 's/ENABLE_MINIO=false/ENABLE_MINIO=true/' .env
        
        # Start storage services
        docker-compose --profile storage up -d
        
        print_status "Storage services started"
        print_status "MinIO Console: http://localhost:9001"
        print_status "IPFS Gateway: http://localhost:8081"
    fi
}

# Start core services
start_services() {
    print_status "Starting core Scorpius services..."
    
    # Start core services
    docker-compose up -d scorpius-main postgres redis
    
    # Wait for services to be ready
    sleep 15
    
    # Health check
    if curl -f http://localhost:8080/health &> /dev/null; then
        print_status "✅ Scorpius API is running at http://localhost:8080"
        print_status "✅ API Documentation: http://localhost:8080/docs"
    else
        print_error "❌ Failed to start Scorpius API"
        print_error "Check logs with: docker-compose logs scorpius-main"
    fi
}

# Run security hardening
security_hardening() {
    print_status "Applying security hardening..."
    
    # Set proper file permissions
    chmod 600 .env
    chmod 755 setup.sh
    
    # Create security configuration
    cat > config/security.yaml << EOF
# Security Configuration
api:
  rate_limiting:
    enabled: true
    requests_per_minute: 100
  
  authentication:
    token_expiry: 3600
    require_https: false  # Set to true in production
  
sandbox:
  network_isolation: true
  resource_limits:
    memory: "4g"
    cpu: "2"
  
docker:
  security_options:
    - "no-new-privileges:true"
    - "apparmor:docker-default"
EOF
    
    print_status "Security hardening completed"
}

# Print final instructions
print_instructions() {
    echo
    echo -e "${GREEN}🎉 Scorpius Vulnerability Scanner Enterprise Setup Complete!${NC}"
    echo "=============================================================="
    echo
    echo -e "${BLUE}Quick Start:${NC}"
    echo "1. Update configuration: nano .env"
    echo "2. Start all services: docker-compose up -d"
    echo "3. Access API docs: http://localhost:8080/docs"
    echo
    echo -e "${BLUE}Available Services:${NC}"
    echo "• API Server: http://localhost:8080"
    echo "• PostgreSQL: localhost:5432"
    echo "• Redis: localhost:6379"
    echo
    echo -e "${BLUE}Plugin Management:${NC}"
    echo "• Initialize plugins: docker-compose --profile plugins up -d"
    echo "• Simulation environment: docker-compose --profile simulation up -d"
    echo
    echo -e "${BLUE}Useful Commands:${NC}"
    echo "• View logs: docker-compose logs -f"
    echo "• Stop services: docker-compose down"
    echo "• Update images: docker-compose pull && docker-compose up -d"
    echo
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "1. Configure your API keys in .env file"
    echo "2. Read the documentation in docs/"
    echo "3. Run your first scan!"
    echo
    print_warning "Remember to change default passwords in production!"
}

# Main execution
main() {
    check_root
    check_requirements
    install_docker
    install_docker_compose
    install_python
    setup_python_env
    create_directories
    generate_config
    build_images
    init_database
    security_hardening
    
    # Optional components
    setup_monitoring
    setup_storage
    
    start_services
    print_instructions
}

# Run main function
main "$@"
