#!/bin/bash

# PostgreSQL Database Setup Script for Resumify
# Run this script to set up the database

echo "Setting up PostgreSQL database for Resumify..."

# Check if PostgreSQL is running
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "Error: PostgreSQL is not running. Please start PostgreSQL first."
    exit 1
fi

# Prompt for PostgreSQL superuser password
read -sp "Enter PostgreSQL superuser (postgres) password: " POSTGRES_PASSWORD
echo ""

# Create database
PGPASSWORD=$POSTGRES_PASSWORD psql -U postgres -h localhost -c "CREATE DATABASE resumify_db;" 2>/dev/null

if [ $? -eq 0 ]; then
    echo "✓ Database 'resumify_db' created successfully!"
else
    echo "Database might already exist or there was an error. Continuing..."
fi

# Set environment variables for Django
export DB_NAME=resumify_db
export DB_USER=postgres
export DB_PASSWORD=$POSTGRES_PASSWORD
export DB_HOST=localhost
export DB_PORT=5432

echo ""
echo "Database setup complete!"
echo "To use these credentials, run:"
echo "  export DB_PASSWORD='$POSTGRES_PASSWORD'"
echo "  cd backend && source venv/bin/activate && python manage.py migrate"

