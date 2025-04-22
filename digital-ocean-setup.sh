#!/bin/bash
set -e

# Print commands before execution
set -x

# Update system packages
echo "Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Install required packages
echo "Installing required packages..."
sudo apt install -y \
  apt-transport-https \
  ca-certificates \
  curl \
  gnupg \
  lsb-release \
  git \
  ufw

# Install Docker
echo "Installing Docker..."
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
rm get-docker.sh

# Add current user to docker group
sudo usermod -aG docker $USER

# Install Docker Compose
echo "Installing Docker Compose..."
sudo curl -L "https://github.com/docker/compose/releases/download/v2.15.1/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Configure firewall
echo "Configuring firewall..."
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 8000/tcp
sudo ufw allow 8001/tcp
sudo ufw allow 8002/tcp
sudo ufw --force enable

# Create application directory
echo "Creating application directory..."
sudo mkdir -p /app
sudo chown $USER:$USER /app
cd /app

# Create Docker network
echo "Creating Docker network..."
docker network create hmt-network || true

# Create environment file
echo "Creating .env file..."
cat > /app/.env << EOF
# Production environment variables
MONGO_URI=mongodb+srv://tm3995:${DB_PASSWORD}@healthtracker.vc6hwcx.mongodb.net/?retryWrites=true&w=majority&appName=HealthTracker
JWT_SECRET=${JWT_SECRET}
API_KEY=${API_KEY}
NODE_ENV=production
EOF

# Create docker-compose.yml for production
echo "Creating docker-compose.yml..."
cat > /app/docker-compose.yml << EOF
version: '3.8'

services:
  user-service:
    image: ${DOCKERHUB_USERNAME}/health-tracker-user-service:latest
    container_name: hmt-user-service
    restart: always
    environment:
      - MONGO_URI=\${MONGO_URI}
      - JWT_SECRET=\${JWT_SECRET}
      - API_KEY=\${API_KEY}
      - NODE_ENV=production
    ports:
      - "8000:8000"
    networks:
      - hmt-network

  data-service:
    image: ${DOCKERHUB_USERNAME}/health-tracker-data-service:latest
    container_name: hmt-data-service
    restart: always
    environment:
      - MONGO_URI=\${MONGO_URI}
      - USER_SERVICE_URL=http://user-service:8000
      - NODE_ENV=production
    ports:
      - "8001:8000"
    networks:
      - hmt-network
    depends_on:
      - user-service

  analytics-service:
    image: ${DOCKERHUB_USERNAME}/health-tracker-analytics-service:latest
    container_name: hmt-analytics-service
    restart: always
    environment:
      - MONGO_URI=\${MONGO_URI}
      - DATA_SERVICE_URL=http://data-service:8000
      - NODE_ENV=production
    ports:
      - "8002:8000"
    networks:
      - hmt-network
    depends_on:
      - data-service

  frontend:
    image: ${DOCKERHUB_USERNAME}/health-tracker-frontend:latest
    container_name: hmt-frontend
    restart: always
    ports:
      - "80:80"
    networks:
      - hmt-network
    depends_on:
      - user-service
      - data-service
      - analytics-service

networks:
  hmt-network:
    external: true
EOF

# Pull Docker images
echo "Pulling Docker images..."
docker pull ${DOCKERHUB_USERNAME}/health-tracker-user-service:latest
docker pull ${DOCKERHUB_USERNAME}/health-tracker-data-service:latest
docker pull ${DOCKERHUB_USERNAME}/health-tracker-analytics-service:latest
docker pull ${DOCKERHUB_USERNAME}/health-tracker-frontend:latest

# Start the services
echo "Starting services with Docker Compose..."
docker-compose up -d

# Create an Nginx configuration for HTTPS (optional)
echo "Creating Nginx configuration for HTTPS..."
mkdir -p /app/nginx
cat > /app/nginx/nginx.conf << EOF
server {
    listen 80;
    server_name YOUR_DOMAIN.com;
    return 301 https://\$host\$request_uri;
}

server {
    listen 443 ssl;
    server_name YOUR_DOMAIN.com;

    ssl_certificate /etc/nginx/ssl/fullchain.pem;
    ssl_certificate_key /etc/nginx/ssl/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers HIGH:!aNULL:!MD5;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;

    location / {
        proxy_pass http://frontend;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/user/ {
        proxy_pass http://user-service:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/data/ {
        proxy_pass http://data-service:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /api/analytics/ {
        proxy_pass http://analytics-service:8000/;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

echo "Setup completed successfully!"
echo "Your Health Metrics Tracker services are now running:"
echo "User Service: http://YOUR_IP:8000"
echo "Data Service: http://YOUR_IP:8001"
echo "Analytics Service: http://YOUR_IP:8002"
echo "Frontend: http://YOUR_IP"
echo ""
echo "For HTTPS, configure Certbot and update the Nginx configuration."
