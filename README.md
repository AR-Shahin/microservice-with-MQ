# Microservices Learning Ecosystem

This project is a polyglot microservices system designed for learning architectural patterns.

## 🚀 Services
1. **Order Service (Laravel 11)**: Port 8000 (MySQL)
2. **Inventory Service (Express.js)**: Port 3000 (MongoDB)
3. **Notification Service (FastAPI)**: Port 8001 (PostgreSQL)
4. **RabbitMQ**: Port 15672 (Management UI)

## 🛠️ How to Run
1. Ensure you have Docker and Docker Compose installed.
2. Clone this repository.
3. Run the following command in the root directory:
   ```bash
   docker-compose up --build
   ```
4. Wait for all containers to start.

## 🧪 Testing the Workflow
1. **Place an Order**: Send a POST request to Laravel.
   ```bash
   curl -X POST http://localhost:8000/api/orders \
     -H "Content-Type: application/json" \
     -d '{"product_id": 123, "quantity": 1, "user_id": 1}'
   ```
2. **Check Inventory**: The Express service should have decreased stock.
   ```bash
   curl http://localhost:3000/inventory
   ```
3. **Check Notifications**: The FastAPI service should have logged a notification.
   ```bash
   curl http://localhost:8001/logs
   ```
4. **RabbitMQ Dashboard**: Visit `http://localhost:15672` (User: `guest`, Pass: `guest`) to see message flows.

## 📈 Large-Scale Evolution (Learning Roadmap)
To make this project "Large Scale", follow these gradual steps:

1. **Phase 1: API Gateway**: Add a **Kong** or **Nginx** Gateway to handle all incoming requests at a single entry point.
2. **Phase 2: Service Discovery**: Implement **Consul** or **Eureka** so services find each other dynamically.
3. **Phase 3: Distributed Tracing**: Integrate **Jaeger** or **Zipkin** to trace a single request across all three services using Correlation IDs.
4. **Phase 4: Circuit Breaker**: Add a circuit breaker pattern (e.g., in Express) to handle cases where RabbitMQ or the DB is slow.
5. **Phase 5: Event Sourcing**: Instead of just "updating stock", store every stock change as an immutable event in the Database.
6. **Phase 6: Monitoring**: Use **Prometheus** and **Grafana** to monitor CPU/Memory and Queue depth.

## 💾 persistence (Volumes)
All databases are configured with named volumes in `docker-compose.yml`:
- `mysql_data`: Persists Order data.
- `mongo_data`: Persists Inventory levels.
- `postgres_data`: Persists Notification history.
- `rabbitmq_data`: (Optional, can be added for persistent queues).
