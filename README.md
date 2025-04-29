# TheEnd: Final Project – Spring 2025

[![log github events](https://github.com/software-students-spring2025/5-final-theend/actions/workflows/event-logger.yml/badge.svg)](https://github.com/software-students-spring2025/5-final-theend/actions/workflows/event-logger.yml)

---

## 🧠 Project Overview

**TheEnd** A web platform where users log and view their health metrics — like sleep, nutrition, and exercise.

---

## ⚙️ Architecture Overview

This system is composed of three primary services:

1. **User Service**  
   Manages authentication, login/signup, and user profile data.

2. **Data Service**  
   Collects, stores, and retrieves sleep, nutrition, and exercise logs.

3. **Analytics Service**  
   Provides insights and visual summaries of the collected health data.

All services are Dockerized and communicate via REST APIs.

---

## 👥 Team Members

- [Naseem Uddin](https://github.com/naseem-student)
- [Tarini Mathur](https://github.com/tmathur2005)
- [Giulia Carvalho](https://github.com/giulia-carvalho)
- [Jibril Wague](https://github.com/Jibril1010)

---

## 🐳 DockerHub Container Images

- [User Service](https://hub.docker.com/r/yourdockerhubusername/user-service)
- [Data Service](https://hub.docker.com/r/yourdockerhubusername/data-service)
- [Analytics Service](https://hub.docker.com/r/yourdockerhubusername/analytics-service)

---

## 🚀 Getting Started

### Prerequisites

- Python 3.12+
- Docker & Docker Compose
- Git

### Setup Instructions

1. **Clone the Repository**

```bash
git clone https://github.com/software-students-spring2025/5-final-theend.git
cd 5-final-theend
```

2. **Install pip files and requirements**
```bash
pip install -r requirements.txt
```

3. **Configure Environment Variables**

Copy the sample .env.example to .env and edit the values:

```bash
cp .env.example .env
```

Replace placeholder values with your actual configuration.

4. **Build and Run with Docker Compose**

```bash
docker-compose up --build
```

5. **Access the Application**

Upon running the Docker Compose command above, you will be given a link in your terminal.

It should look something like this:
```bash
http://localhost:5000
```

Upon clicking the link, you will be redirected to the web application.

You're all set to begin tracking your health data. Welcome to TheEnd!
