# Microservices Learning Ecosystem (Auth Edition)

This system now includes **Auth (Sanctum)** in the Order Service (Laravel).

## 🚀 Services
1. **Order Service (Laravel 11)**: Port 8000 (MySQL + Sanctum)
2. **Inventory Service (Express.js)**: Port 3000 (MongoDB)
3. **Notification Service (FastAPI)**: Port 8001 (PostgreSQL)

## 🔐 Auth Workflow
The Order Service handles user registration and login.
- **Roles**: `user` and `admin`.
- **Token**: Bearer token via Laravel Sanctum.

## 🧪 Testing the New Flow

1. **Register a User**:
   ```bash
   curl -X POST http://localhost:8000/api/register \
     -H "Content-Type: application/json" \
     -d '{"name": "John Doe", "email": "john@example.com", "password": "password123", "role": "user"}'
   ```
   *Copy the `access_token` from the response.*

2. **Place an Order (Authenticated)**:
   ```bash
   curl -X POST http://localhost:8000/api/orders \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -H "Content-Type: application/json" \
     -d '{"product_id": 123, "quantity": 2}'
   ```

3. **Admin Check**: Register as `admin` to see the role-based logic in `GET /api/orders`.

## 📈 Evolution
- The `OrderController` now automatically attaches the authenticated user's ID to the RabbitMQ message.
- The Inventory and Notification services will receive the `user_id`, `user_email`, and `user_role` in the event payload.
