<?php

namespace App\Services;

use PhpAmqpLib\Connection\AMQPStreamConnection;
use PhpAmqpLib\Message\AMQPMessage;

class RabbitMQService
{
    public function publish($messageBody)
    {
        try {
            $connection = new AMQPStreamConnection(
                env('RABBITMQ_HOST', 'rabbitmq'),
                env('RABBITMQ_PORT', 5672),
                env('RABBITMQ_USER', 'guest'),
                env('RABBITMQ_PASS', 'guest')
            );
            $channel = $connection->channel();

            $channel->exchange_declare('order_exchange', 'direct', false, false, false);

            $msg = new AMQPMessage(json_encode($messageBody), [
                'content_type' => 'application/json',
                'delivery_mode' => AMQPMessage::DELIVERY_MODE_PERSISTENT
            ]);
            
            $channel->basic_publish($msg, 'order_exchange', 'order_created');

            $channel->close();
            $connection->close();
        } catch (\Exception $e) {
            \Log::error("RabbitMQ Publish Error: " . $e->getMessage());
        }
    }
}
