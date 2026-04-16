<?php

namespace App\Http\Controllers\Api;

use App\Http\Controllers\Controller;
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
        $request->validate([
            'product_id' => 'required|integer',
            'quantity' => 'required|integer|min:1'
        ]);

        $user = $request->user();

        // Simulating order storage
        $order = [
            'id' => rand(1000, 9999),
            'product_id' => $request->product_id,
            'quantity' => $request->quantity,
            'user_id' => $user->id,
            'user_email' => $user->email,
            'user_role' => $user->role,
            'status' => 'placed'
        ];

        // Publish to RabbitMQ
        $this->mqService->publish($order);

        return response()->json([
            'message' => 'Order created successfully and broadcasted!',
            'order' => $order
        ], 201);
    }

    public function index(Request $request)
    {
        if ($request->user()->isAdmin()) {
            return response()->json(['message' => 'Admin viewing all orders (simulated)']);
        }

        return response()->json(['message' => 'User viewing their own orders (simulated)']);
    }
}
