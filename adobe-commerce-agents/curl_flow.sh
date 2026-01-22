#!/bin/bash

# Base URL
BASE_URL="http://127.0.0.1:5000"

echo "1. Health Check"
curl -X GET "$BASE_URL/api/health"
echo -e "\n\n"

echo "2. Chat: Product Discovery (Deep Agent)"
curl -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "I need a new laptop for work, budget around $1500",
    "history": []
  }'
echo -e "\n\n"

echo "3. Chat: Add to Cart (Deep Agent)"
curl -X POST "$BASE_URL/api/chat" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add that laptop to my cart",
    "history": [
        {"role": "user", "content": "I need a new laptop for work, budget around $1500"},
        {"role": "assistant", "content": "I found a MacBook Pro M3 for $1499. Would you like to add it to your cart?"}
    ]
  }'
echo -e "\n\n"

echo "4. Debug: Direct Catalog Search"
curl -X POST "$BASE_URL/api/debug/catalog" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Search for wireless headphones"
  }'
echo -e "\n\n"
