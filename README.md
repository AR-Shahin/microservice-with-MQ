# Microservices Learning System (Hybrid Setup)

This project is now configured as a **Hybrid Architecture**:
- **Laravel**: Running natively on your Mac.
- **Express & FastAPI**: Dockerized.
- **RabbitMQ**: Dockerized.
- **MySQL**: Global Local MySQL (on your Mac).

## 🗄️ Database Setup
Create three databases in your local MySQL:
1. `ms_laravel`
2. `ms_express`
3. `ms_fastapi`

## 🚀 How to Run

### 1. Start Docker Services (MQ, Express, FastAPI)
Run this in the root directory:
```bash
docker-compose up --build
```
*Wait for RabbitMQ and the services to start.*

### 2. Start Laravel Service (Order Service)
Run these commands on your Mac:
```bash
cd order-service
composer install
php artisan migrate:fresh
php artisan serve --port=8000
```

## 🧪 Testing the Pipeline

1. **Register & Login** in Laravel:
   ```bash
   curl -X POST http://localhost:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{"name": "Alice", "email": "alice@example.com", "password": "password", "role": "user"}'
   ```
2. **Place an Order** (Published to RabbitMQ):
   ```bash
   curl -X POST http://localhost:8000/api/orders \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"product_id": 123, "quantity": 5}'
   ```
3. **Verify Inventory** (Express - MySQL):
   ```bash
   curl http://localhost:3000/inventory
   ```
4. **Verify Notifications** (FastAPI - MySQL):
   ```bash
   curl http://localhost:8001/logs
   ```

## 🔗 Connection Map
- **Laravel (Host)** -> **DB (Host: 127.0.0.1)** & **MQ (Docker: 127.0.0.1:5672)**
- **Express (Docker)** -> **DB (Host: host.docker.internal)** & **MQ (Docker: rabbitmq)**
- **FastAPI (Docker)** -> **DB (Host: host.docker.internal)** & **MQ (Docker: rabbitmq)**
