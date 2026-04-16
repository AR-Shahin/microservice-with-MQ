import json
import pika
import os
import threading
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database Setup
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@postgres-db:5432/notification_db")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class NotificationLog(Base):
    __tablename__ = "notification_logs"
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer)
    user_id = Column(Integer)
    message = Column(Text)

Base.metadata.create_all(bind=engine)

# RabbitMQ Consumer Logic
def consume_messages():
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
        channel = connection.channel()

        channel.exchange_declare(exchange='order_exchange', exchange_type='direct')
        result = channel.queue_declare(queue='', exclusive=True)
        queue_name = result.method.queue

        channel.queue_bind(exchange='order_exchange', queue=queue_name, routing_key='order_created')

        def callback(ch, method, properties, body):
            order = json.loads(body)
            print(f" [x] Notification Service received: {order}")
            
            # Save to Database
            db = SessionLocal()
            log = NotificationLog(
                order_id=order['id'],
                user_id=order['user_id'],
                message=f"Notification sent for Order #{order['id']}"
            )
            db.add(log)
            db.commit()
            db.close()
            print(f" [x] Notification logged to PostgreSQL for Order {order['id']}")

        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
        print(' [*] Notification Service waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        print(f"Error in RabbitMQ Consumer: {e}")

# Start consumer in a separate thread
threading.Thread(target=consume_messages, daemon=True).start()

@app.get("/")
def read_root():
    return {"message": "Notification Service is running"}

@app.get("/logs")
def get_logs():
    db = SessionLocal()
    logs = db.query(NotificationLog).all()
    db.close()
    return logs
