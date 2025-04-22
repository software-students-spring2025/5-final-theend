# frontend/Dockerfile
# Python image
FROM python:3.11-slim

# set working directory
WORKDIR /app

# install OS-level dependencies
RUN apt-get update \
  && apt-get install -y --no-install-recommends curl \
  && rm -rf /var/lib/apt/lists/*

# install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# copy application source
COPY . .

# exposing Flask port
EXPOSE 5000

# health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# launch the Flask dashboard
CMD ["python", "dashboard_app.py"]