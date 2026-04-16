const express = require('express');
const mysql = require('mysql2/promise');
const amqp = require('amqplib');
require('dotenv').config();

const app = express();
app.use(express.json());

const PORT = 3000;
const DB_CONFIG = {
    host: process.env.DB_HOST || 'host.docker.internal',
    user: process.env.DB_USER || 'root',
    password: process.env.DB_PASSWORD || 'root',
    database: process.env.DB_NAME || 'ms_express'
};
const RABBIT_URL = process.env.RABBIT_URL || 'amqp://guest:guest@rabbitmq:5672';

let connection;

async function initDB() {
    try {
        connection = await mysql.createConnection(DB_CONFIG);
        console.log("Connected to MySQL (MS_EXPRESS)");
        
        // Create table if not exists
        await connection.execute(`
            CREATE TABLE IF NOT EXISTS inventory (
                id INT AUTO_INCREMENT PRIMARY KEY,
                product_id INT UNIQUE,
                stock INT
            )
        `);
        
        // Seed data
        await connection.execute('INSERT IGNORE INTO inventory (product_id, stock) VALUES (123, 100)');
    } catch (err) {
        console.error("MySQL Connection Error:", err);
        setTimeout(initDB, 5000);
    }
}

async function connectRabbit() {
    try {
        const conn = await amqp.connect(RABBIT_URL);
        const channel = await conn.createChannel();
        
        await channel.assertExchange('order_exchange', 'direct', { durable: false });
        const q = await channel.assertQueue('', { exclusive: true });
        
        channel.bindQueue(q.queue, 'order_exchange', 'order_created');

        channel.consume(q.queue, async (msg) => {
            if (msg.content) {
                const order = JSON.parse(msg.content.toString());
                console.log(" [x] Received Order:", order);
                
                // Logic: Decrease stock in MySQL
                const [rows] = await connection.execute('SELECT stock FROM inventory WHERE product_id = ?', [order.product_id]);
                if (rows.length > 0) {
                    const newStock = rows[0].stock - order.quantity;
                    await connection.execute('UPDATE inventory SET stock = ? WHERE product_id = ?', [newStock, order.product_id]);
                    console.log(`Inventory updated. Product ${order.product_id} new stock: ${newStock}`);
                }
            }
        }, { noAck: true });
    } catch (error) {
        console.error("RabbitMQ Connection Error:", error);
        setTimeout(connectRabbit, 5000);
    }
}

initDB().then(connectRabbit);

app.get('/inventory', async (req, res) => {
    const [rows] = await connection.execute('SELECT * FROM inventory');
    res.json(rows);
});

app.listen(PORT, () => {
    console.log(`Inventory service (Express) running on port ${PORT}`);
});
