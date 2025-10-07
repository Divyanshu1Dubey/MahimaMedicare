#!/bin/bash

# Automated deployment script for Mahima Medicare
# This script handles the complete deployment process

set -e  # Exit on any error

echo "🚀 Starting Mahima Medicare deployment..."

# Configuration
PROJECT_DIR="/var/www/mahima-medicare"
VENV_DIR="$PROJECT_DIR/venv"
BACKUP_DIR="/var/backups/mahima-medicare"
LOG_FILE="/var/log/mahima-medicare-deploy.log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}❌ Error: $1${NC}" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}✅ $1${NC}" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}⚠️  $1${NC}" | tee -a "$LOG_FILE"
}

# Function to backup database
backup_database() {
    log "Creating database backup..."
    mkdir -p "$BACKUP_DIR"

    if [ -f "$PROJECT_DIR/db.sqlite3" ]; then
        cp "$PROJECT_DIR/db.sqlite3" "$BACKUP_DIR/db_backup_$(date +%Y%m%d_%H%M%S).sqlite3"
        success "Database backed up successfully"
    else
        warning "No existing database found to backup"
    fi
}

# Function to export data before deployment
export_data() {
    log "Exporting essential data..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    if python export_data.py; then
        success "Data exported successfully"
    else
        warning "Data export failed or no data to export"
    fi
}

# Function to clean up unnecessary files
cleanup_files() {
    log "Cleaning up unnecessary files..."
    cd "$PROJECT_DIR"

    # Remove test files
    find . -name "*test*.py" -not -path "./venv/*" -delete
    find . -name "*TEST*.py" -not -path "./venv/*" -delete

    # Remove documentation files (except README.md)
    find . -name "*.md" -not -name "README.md" -not -path "./venv/*" -delete

    # Remove Python cache
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name "*.pyc" -delete

    # Remove build and deployment scripts
    rm -f build.sh deploy_*.sh setup_*.bat install_*.bat fix_*.bat update_*.bat *.ps1

    # Remove HTML test files
    rm -f test-*.html

    success "Cleanup completed"
}

# Function to pull latest code
pull_code() {
    log "Pulling latest code from repository..."
    cd "$PROJECT_DIR"

    if git pull origin main; then
        success "Code updated successfully"
    else
        error "Failed to pull latest code"
        exit 1
    fi
}

# Function to install/update dependencies
install_dependencies() {
    log "Installing/updating dependencies..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    if pip install -r requirements.txt; then
        success "Dependencies installed successfully"
    else
        error "Failed to install dependencies"
        exit 1
    fi
}

# Function to run migrations
run_migrations() {
    log "Running database migrations..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    python manage.py makemigrations
    python manage.py migrate

    success "Migrations completed"
}

# Function to import data after migrations
import_data() {
    log "Importing essential data..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    # Find the most recent backup directory
    BACKUP_DIRS=($(ls -dt data_backup_* 2>/dev/null || true))

    if [ ${#BACKUP_DIRS[@]} -gt 0 ]; then
        python import_data.py "${BACKUP_DIRS[0]}"
        success "Data imported successfully"
    else
        warning "No data backup found to import"
    fi
}

# Function to collect static files
collect_static() {
    log "Collecting static files..."
    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    python manage.py collectstatic --noinput
    success "Static files collected"
}

# Function to restart Gunicorn
restart_gunicorn() {
    log "Restarting Gunicorn..."

    # Kill existing Gunicorn processes
    pkill -f gunicorn || true
    sleep 2

    cd "$PROJECT_DIR"
    source "$VENV_DIR/bin/activate"

    # Start Gunicorn in background
    nohup gunicorn --config gunicorn.conf.py healthstack.wsgi:application &

    sleep 5

    if pgrep -f gunicorn > /dev/null; then
        success "Gunicorn started successfully"
    else
        error "Failed to start Gunicorn"
        exit 1
    fi
}

# Function to verify deployment
verify_deployment() {
    log "Verifying deployment..."

    # Check if Gunicorn is running
    if pgrep -f gunicorn > /dev/null; then
        success "Gunicorn is running"
    else
        error "Gunicorn is not running"
        return 1
    fi

    # Check if the application is responding
    if curl -f -s http://localhost:8000 > /dev/null; then
        success "Application is responding"
    else
        warning "Application may not be responding on port 8000"
    fi
}

# Main deployment process
main() {
    log "=== Starting deployment process ==="

    # Backup current state
    backup_database
    export_data

    # Update code and dependencies
    pull_code
    cleanup_files
    install_dependencies

    # Database updates
    run_migrations
    import_data

    # Static files and restart
    collect_static
    restart_gunicorn

    # Verify everything is working
    verify_deployment

    success "=== Deployment completed successfully! ==="
    log "Application is now running at http://mahimamedicare.com"
}

# Run main function
main "$@"
