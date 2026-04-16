import json
import pika
import os
import threading
import time
from fastapi import FastAPI
from sqlalchemy import create_engine, Column, Integer, String, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

app = FastAPI()

# Database Setup (MySQL)
# Example: mysql+pymysql://root:root@host.docker.internal:3306/ms_fastapi
DATABASE_URL = os.getenv("DATABASE_URL", "mysql+pymysql://root:root@host.docker.internal:3306/ms_fastapi")

while True:
    try:
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
        print("Connected to MySQL (MS_FASTAPI)")
        break
    except Exception as e:
        print(f"Waiting for MySQL... {e}")
        time.sleep(5)

# RabbitMQ Consumer Logic
def consume_messages():
    while True:
        try:
            connection = pika.BlockingConnection(pika.ConnectionParameters(host='rabbitmq'))
            channel = connection.channel()

            channel.exchange_declare(exchange='order_exchange', exchange_type='direct')
            result = channel.queue_declare(queue='', exclusive=True)
            queue_name = result.method.queue

            channel.queue_bind(exchange='order_exchange', queue=queue_name, routing_key='order_created')

            def callback(ch, method, properties, body):
                order = json.loads(body)
                print(f" [x] Received Order in Notification: {order}")
                
                db = SessionLocal()
                log = NotificationLog(
                    order_id=order['id'],
                    user_id=order['user_id'],
                    message=f"Notification sent for Order #{order['id']} to {order['user_email']}"
                )
                db.add(log)
                db.commit()
                db.close()

            channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)
            print(' [*] Notification Service waiting for messages...')
            channel.start_consuming()
        except Exception as e:
            print(f"RabbitMQ Connection Error: {e}. Retrying...")
            time.sleep(5)

threading.Thread(target=consume_messages, daemon=True).start()

@app.get("/")
def read_root():
    return {"message": "Notification Service (FastAPI) is running with MySQL"}

@app.get("/logs")
def get_logs():
    db = SessionLocal()
    logs = db.query(NotificationLog).all()
    db.close()
    return logs
