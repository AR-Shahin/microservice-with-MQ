<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use App\Services\RabbitMQService;

class OrderController extends Controller
{
    protected $mqService;

    public function __construct(RabbitMQService $mqService)
    {
        $this->mqService = $mqService;
    }

    public function store(Request $request)
    {
        // Simulating order storage in MySQL
        $order = [
            'id' => rand(100, 999),
            'product_id' => $request->product_id,
            'quantity' => $request->quantity,
            'user_id' => $request->user_id,
            'status' => 'pending'
        ];

        // Publish to RabbitMQ
        $this->mqService->publish($order);

        return response()->json([
            'message' => 'Order placed and message published to RabbitMQ!',
            'order' => $order
        ], 201);
    }
}
