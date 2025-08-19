#!/bin/bash

# PostgreSQL Database Setup Script for Kragentic Telephony Project
# Run with sudo privileges

echo "Setting up PostgreSQL database for Kragentic Telephony Project..."

# Check if PostgreSQL is installed
if ! command -v psql &> /dev/null; then
    echo "PostgreSQL not found. Installing..."
    sudo apt update
    sudo apt install -y postgresql postgresql-contrib
fi

# Start PostgreSQL service
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Create database and user
sudo -u postgres psql -c "CREATE DATABASE kragentic_telephony;"
sudo -u postgres psql -c "CREATE USER kragentic WITH PASSWORD 'kragentic123';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE kragentic_telephony TO kragentic;"
sudo -u postgres psql -c "ALTER DATABASE kragentic_telephony OWNER TO kragentic;"

# Configure PostgreSQL to listen on all interfaces
sudo sed -i "s/#listen_addresses = 'localhost'/listen_addresses = '*'/g" /etc/postgresql/*/main/postgresql.conf
sudo sh -c "echo 'host all all 0.0.0.0/0 md5' >> /etc/postgresql/*/main/pg_hba.conf"

# Restart PostgreSQL
sudo systemctl restart postgresql

echo "PostgreSQL setup complete!"
echo "Database: kragentic_telephony"
echo "User: kragentic"
echo "Password: kragentic123"
echo "Host: localhost"
echo "Port: 5432"

# Run migrations
cd kragentic_telephony
mix deps.get
mix ecto.create
mix ecto.migrate
mix run priv/repo/seeds.exs

echo "Database migrations and seeding complete!"
