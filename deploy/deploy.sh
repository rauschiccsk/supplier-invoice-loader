#!/bin/bash
# -*- coding: utf-8 -*-
#===============================================================================
# Supplier Invoice Loader - Deployment Script for Linux/Mac
# Version: 2.0.0
#
# This script automates the deployment of Supplier Invoice Loader
# for a new customer installation or update of existing installation.
#
# Usage:
#   ./deploy.sh new CUSTOMER_NAME     # New installation
#   ./deploy.sh update                # Update existing
#   ./deploy.sh check                 # Check prerequisites
#   ./deploy.sh backup                # Backup current installation
#===============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
DEPLOYMENT_LOG="${PROJECT_ROOT}/deployment.log"
PYTHON_MIN_VERSION="3.8"
REQUIRED_SPACE_MB=500

#===============================================================================
# Utility Functions
#===============================================================================

log() {
    local level=$1
    shift
    local message="$@"
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')

    case $level in
        INFO)
            echo -e "${BLUE}[INFO]${NC} $message"
            ;;
        SUCCESS)
            echo -e "${GREEN}[SUCCESS]${NC} $message"
            ;;
        WARNING)
            echo -e "${YELLOW}[WARNING]${NC} $message"
            ;;
        ERROR)
            echo -e "${RED}[ERROR]${NC} $message"
            ;;
    esac

    echo "[$timestamp] [$level] $message" >> "$DEPLOYMENT_LOG"
}

check_command() {
    if ! command -v $1 &> /dev/null; then
        return 1
    fi
    return 0
}

check_python_version() {
    if ! check_command python3; then
        return 1
    fi

    local version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
    local required=$1

    if [ "$(printf '%s\n' "$required" "$version" | sort -V | head -n1)" = "$required" ]; then
        return 0
    else
        return 1
    fi
}

check_disk_space() {
    local required_mb=$1
    local available_mb

    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        available_mb=$(df -m . | awk 'NR==2 {print $4}')
    else
        # Linux
        available_mb=$(df -m . | awk 'NR==2 {print $4}')
    fi

    if [ "$available_mb" -lt "$required_mb" ]; then
        return 1
    fi
    return 0
}

create_backup() {
    local backup_name="backup_$(date +%Y%m%d_%H%M%S)"
    local backup_dir="${PROJECT_ROOT}/${backup_name}"

    log INFO "Creating backup: $backup_dir"

    mkdir -p "$backup_dir"

    # Backup critical files
    [ -f "${PROJECT_ROOT}/config_customer.py" ] && cp "${PROJECT_ROOT}/config_customer.py" "$backup_dir/"
    [ -f "${PROJECT_ROOT}/invoices.db" ] && cp "${PROJECT_ROOT}/invoices.db" "$backup_dir/"
    [ -f "${PROJECT_ROOT}/.env" ] && cp "${PROJECT_ROOT}/.env" "$backup_dir/"
    [ -d "${PROJECT_ROOT}/logs" ] && cp -r "${PROJECT_ROOT}/logs" "$backup_dir/"

    # Create backup info
    cat > "$backup_dir/backup_info.txt" << EOF
Backup created: $(date)
Version: $(git describe --tags --always 2>/dev/null || echo "unknown")
Customer: $(python3 -c "from config_customer import CUSTOMER_NAME; print(CUSTOMER_NAME)" 2>/dev/null || echo "unknown")
EOF

    log SUCCESS "Backup created: $backup_dir"
    echo "$backup_dir"
}

#===============================================================================
# Prerequisites Check
#===============================================================================

check_prerequisites() {
    log INFO "Checking prerequisites..."

    local all_ok=true

    # Check Python
    if check_python_version "$PYTHON_MIN_VERSION"; then
        log SUCCESS "Python 3.8+ found"
    else
        log ERROR "Python 3.8+ not found or version too old"
        all_ok=false
    fi

    # Check pip
    if check_command pip3; then
        log SUCCESS "pip3 found"
    else
        log ERROR "pip3 not found"
        all_ok=false
    fi

    # Check git
    if check_command git; then
        log SUCCESS "git found"
    else
        log WARNING "git not found (optional but recommended)"
    fi

    # Check disk space
    if check_disk_space $REQUIRED_SPACE_MB; then
        log SUCCESS "Sufficient disk space available"
    else
        log ERROR "Insufficient disk space (need ${REQUIRED_SPACE_MB}MB)"
        all_ok=false
    fi

    # Check SQLite
    if check_command sqlite3; then
        log SUCCESS "SQLite3 found"
    else
        log WARNING "SQLite3 not found (optional for manual DB operations)"
    fi

    if [ "$all_ok" = true ]; then
        log SUCCESS "All prerequisites met"
        return 0
    else
        log ERROR "Prerequisites check failed"
        return 1
    fi
}

#===============================================================================
# Virtual Environment Setup
#===============================================================================

setup_venv() {
    log INFO "Setting up Python virtual environment..."

    if [ -d "${PROJECT_ROOT}/venv" ]; then
        log WARNING "Virtual environment already exists"
        read -p "Recreate virtual environment? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "${PROJECT_ROOT}/venv"
        else
            log INFO "Using existing virtual environment"
            return 0
        fi
    fi

    python3 -m venv "${PROJECT_ROOT}/venv"

    # Activate venv
    source "${PROJECT_ROOT}/venv/bin/activate"

    # Upgrade pip
    pip install --upgrade pip

    log SUCCESS "Virtual environment created"
}

#===============================================================================
# Dependencies Installation
#===============================================================================

install_dependencies() {
    log INFO "Installing Python dependencies..."

    # Activate venv if not already
    if [ -z "$VIRTUAL_ENV" ]; then
        source "${PROJECT_ROOT}/venv/bin/activate"
    fi

    # Install requirements
    pip install -r "${PROJECT_ROOT}/requirements.txt"

    # Install additional tools
    pip install python-dotenv

    log SUCCESS "Dependencies installed"
}

#===============================================================================
# Configuration Setup
#===============================================================================

setup_configuration() {
    local customer_name=$1

    log INFO "Setting up configuration for customer: $customer_name"

    # Check if config_customer.py exists
    if [ -f "${PROJECT_ROOT}/config_customer.py" ]; then
        log WARNING "config_customer.py already exists"
        read -p "Overwrite existing configuration? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            log INFO "Keeping existing configuration"
            return 0
        fi
        # Backup existing config
        cp "${PROJECT_ROOT}/config_customer.py" "${PROJECT_ROOT}/config_customer.py.backup"
    fi

    # Copy template
    cp "${PROJECT_ROOT}/config_template.py" "${PROJECT_ROOT}/config_customer.py"

    # Update customer name in config
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/CUSTOMER_NAME_HERE/$customer_name/g" "${PROJECT_ROOT}/config_customer.py"
        sed -i '' "s/Customer Company Name s.r.o./$customer_name s.r.o./g" "${PROJECT_ROOT}/config_customer.py"
    else
        # Linux
        sed -i "s/CUSTOMER_NAME_HERE/$customer_name/g" "${PROJECT_ROOT}/config_customer.py"
        sed -i "s/Customer Company Name s.r.o./$customer_name s.r.o./g" "${PROJECT_ROOT}/config_customer.py"
    fi

    log SUCCESS "Configuration template created"
    log WARNING "Please edit config_customer.py with actual values!"
}

#===============================================================================
# Environment Variables Setup
#===============================================================================

setup_environment() {
    log INFO "Setting up environment variables..."

    if [ -f "${PROJECT_ROOT}/.env" ]; then
        log WARNING ".env file already exists"
    else
        # Copy template
        if [ -f "${PROJECT_ROOT}/.env.example" ]; then
            cp "${PROJECT_ROOT}/.env.example" "${PROJECT_ROOT}/.env"
            log SUCCESS ".env file created from template"
        else
            # Create basic .env
            cat > "${PROJECT_ROOT}/.env" << 'EOF'
# Supplier Invoice Loader - Environment Variables
# Generated by deployment script

# API Security
LS_API_KEY=CHANGE_ME_$(openssl rand -hex 16)

# Email Configuration
SMTP_USER=
SMTP_PASSWORD=

# NEX Genesis API (optional, can be in config)
# NEX_API_KEY=

# Logging
LOG_LEVEL=INFO

# Storage (optional, defaults in config)
# LS_STORAGE_PATH=/opt/supplier_invoices
EOF
            log SUCCESS ".env file created"
        fi

        log WARNING "Please edit .env file with actual values!"
    fi

    # Set permissions
    chmod 600 "${PROJECT_ROOT}/.env"
}

#===============================================================================
# Database Setup
#===============================================================================

setup_database() {
    log INFO "Setting up database..."

    # Activate venv
    source "${PROJECT_ROOT}/venv/bin/activate"

    # Check if database exists
    if [ -f "${PROJECT_ROOT}/invoices.db" ]; then
        log WARNING "Database already exists"

        # Check if migration needed
        python3 "${PROJECT_ROOT}/migrate_v2.py" --check

        read -p "Run database migration? (y/N): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            python3 "${PROJECT_ROOT}/migrate_v2.py"
        fi
    else
        # Initialize new database
        python3 -c "import database; database.init_database()"
        log SUCCESS "Database initialized"
    fi
}

#===============================================================================
# Storage Directories Setup
#===============================================================================

setup_storage() {
    log INFO "Setting up storage directories..."

    # Get storage path from config
    local storage_path=$(python3 -c "from config_customer import PDF_DIR; print(PDF_DIR.parent)" 2>/dev/null || echo "/opt/supplier_invoices")

    # Create directories
    mkdir -p "$storage_path/PDF"
    mkdir -p "$storage_path/XML"

    # Set permissions
    chmod 755 "$storage_path"
    chmod 755 "$storage_path/PDF"
    chmod 755 "$storage_path/XML"

    log SUCCESS "Storage directories created: $storage_path"
}

#===============================================================================
# Service Installation
#===============================================================================

install_service() {
    log INFO "Installing as system service..."

    local service_name="supplier-invoice-loader"
    local service_file="/etc/systemd/system/${service_name}.service"

    # Create service file
    sudo tee "$service_file" > /dev/null << EOF
[Unit]
Description=Supplier Invoice Loader
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$PROJECT_ROOT
Environment="PATH=$PROJECT_ROOT/venv/bin"
ExecStart=$PROJECT_ROOT/venv/bin/python $PROJECT_ROOT/main.py
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

    # Reload systemd
    sudo systemctl daemon-reload

    # Enable service
    sudo systemctl enable "$service_name"

    log SUCCESS "Service installed: $service_name"
    log INFO "Start with: sudo systemctl start $service_name"
    log INFO "Check status: sudo systemctl status $service_name"
    log INFO "View logs: sudo journalctl -u $service_name -f"
}

#===============================================================================
# Test Installation
#===============================================================================

test_installation() {
    log INFO "Testing installation..."

    # Activate venv
    source "${PROJECT_ROOT}/venv/bin/activate"

    # Test imports
    if python3 -c "import main, database, config" 2>/dev/null; then
        log SUCCESS "Python imports successful"
    else
        log ERROR "Python imports failed"
        return 1
    fi

    # Test API
    log INFO "Starting test server (press Ctrl+C to stop)..."
    timeout 5 python3 "${PROJECT_ROOT}/main.py" &
    local pid=$!

    sleep 3

    # Test health endpoint
    if curl -s http://localhost:8000/health | grep -q "healthy"; then
        log SUCCESS "API test successful"
    else
        log ERROR "API test failed"
    fi

    kill $pid 2>/dev/null || true

    return 0
}

#===============================================================================
# Main Deployment Functions
#===============================================================================

deploy_new() {
    local customer_name=$1

    if [ -z "$customer_name" ]; then
        log ERROR "Customer name required for new deployment"
        echo "Usage: $0 new CUSTOMER_NAME"
        exit 1
    fi

    log INFO "Starting new deployment for: $customer_name"

    # Run all setup steps
    check_prerequisites || exit 1
    setup_venv
    install_dependencies
    setup_configuration "$customer_name"
    setup_environment
    setup_database
    setup_storage

    # Optional: Install as service
    read -p "Install as system service? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        install_service
    fi

    # Test
    test_installation

    log SUCCESS "Deployment complete!"
    log INFO "Next steps:"
    log INFO "1. Edit config_customer.py with actual values"
    log INFO "2. Edit .env with API keys and SMTP credentials"
    log INFO "3. Configure n8n workflow"
    log INFO "4. Start service or run: python main.py"
}

deploy_update() {
    log INFO "Starting update deployment..."

    # Create backup first
    backup_dir=$(create_backup)

    # Check prerequisites
    check_prerequisites || exit 1

    # Update code
    if check_command git; then
        log INFO "Pulling latest code..."
        git pull origin v2.0-multi-customer
    fi

    # Update dependencies
    source "${PROJECT_ROOT}/venv/bin/activate"
    pip install -r "${PROJECT_ROOT}/requirements.txt"

    # Check for migrations
    python3 "${PROJECT_ROOT}/migrate_v2.py" --check

    log SUCCESS "Update complete!"
    log INFO "Backup saved to: $backup_dir"
}

#===============================================================================
# Main Script
#===============================================================================

main() {
    echo "=========================================="
    echo "Supplier Invoice Loader - Deployment Tool"
    echo "Version 2.0.0"
    echo "=========================================="
    echo

    case "${1:-}" in
        new)
            deploy_new "$2"
            ;;
        update)
            deploy_update
            ;;
        check)
            check_prerequisites
            ;;
        backup)
            create_backup
            ;;
        test)
            test_installation
            ;;
        *)
            echo "Usage: $0 {new CUSTOMER_NAME|update|check|backup|test}"
            echo
            echo "Commands:"
            echo "  new CUSTOMER_NAME - New customer deployment"
            echo "  update           - Update existing deployment"
            echo "  check            - Check prerequisites"
            echo "  backup           - Create backup"
            echo "  test             - Test installation"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"