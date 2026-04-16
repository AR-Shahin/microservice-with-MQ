const express = require('express');
const mongoose = require('mongoose');
const amqp = require('amqplib');
require('dotenv').config();

const app = express();
app.use(express.json());

const PORT = 3000;
const MONGO_URI = process.env.MONGO_URI || 'mongodb://mongodb:27017/inventory_db';
const RABBIT_URL = process.env.RABBIT_URL || 'amqp://guest:guest@rabbitmq:5672';

// MongoDB Model
const Inventory = mongoose.model('Inventory', {
    productId: Number,
    stock: Number
});

async function connectRabbit() {
    try {
        const connection = await amqp.connect(RABBIT_URL);
        const channel = await connection.createChannel();
        
        await channel.assertExchange('order_exchange', 'direct', { durable: false });
        const q = await channel.assertQueue('', { exclusive: true });
        
        console.log(" [*] Waiting for messages in %s. To exit press CTRL+C", q.queue);
        channel.bindQueue(q.queue, 'order_exchange', 'order_created');

        channel.consume(q.queue, async (msg) => {
            if (msg.content) {
                const order = JSON.parse(msg.content.toString());
                console.log(" [x] Received Order:", order);
                
                // Logic: Decrease stock in MongoDB
                const stockItem = await Inventory.findOne({ productId: order.product_id });
                if (stockItem) {
                    stockItem.stock -= order.quantity;
                    await stockItem.save();
                    console.log(`Inventory updated for Product ${order.product_id}. New stock: ${stockItem.stock}`);
                } else {
                    console.log(`Product ${order.product_id} not found in inventory.`);
                }
            }
        }, { noAck: true });
    } catch (error) {
        console.error("Error connecting to RabbitMQ:", error);
    }
}

mongoose.connect(MONGO_URI)
    .then(() => {
        console.log("Connected to MongoDB");
        // Seed some data for demo
        Inventory.updateOne({ productId: 123 }, { stock: 100 }, { upsert: true }).exec();
        connectRabbit();
    })
    .catch(err => console.error("MongoDB connection error:", err));

app.get('/inventory', async (req, res) => {
    const items = await Inventory.find();
    res.json(items);
});

app.listen(PORT, () => {
    console.log(`Inventory service running on port ${PORT}`);
});
