# AI Shopping Agent API - CURL Commands

This document provides ready-to-use CURL commands for interacting with the AI Shopping Agent API.

## Base URL
`http://localhost:5000`

## 1. Health Check
Verify the API is running.

```bash
curl -X GET http://localhost:5000/api/health
```

## 2. Authentication

### Register a New User
Replace the values with your desired credentials.

```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Response:** You will get a JSON response containing `token`. Copy this token for subsequent requests.

### Login
If you already have an account.

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "securepassword123"
  }'
```

**Response:** JSON with `token`.

## 3. User Profile
**Requires Token.** Replace `YOUR_TOKEN_HERE` with the token received from login/register.

```bash
curl -X GET http://localhost:5000/api/auth/profile \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 4. Product Recommendation (with LLM)
**Requires Token.**
Search for a product. Set `use_nlp` to `true` to use the LLM to refine the query.

```bash
curl -X POST http://localhost:5000/api/auth/recommend \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product": "cheap gaming laptop under 1000",
    "budget": 1000,
    "use_nlp": true
  }'
```

## 5. Favorites
**Requires Token.**

### Add Favorite
```bash
curl -X POST http://localhost:5000/api/favorites \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Example Laptop",
    "product_url": "https://example.com/product/123",
    "price": 999.99,
    "platform": "Amazon"
  }'
```

### Get Favorites
```bash
curl -X GET http://localhost:5000/api/favorites \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 6. Price Alerts
**Requires Token.**

### Create Alert
```bash
curl -X POST http://localhost:5000/api/price-alerts \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Example Laptop",
    "product_url": "https://example.com/product/123",
    "target_price": 900.00
  }'
```

### Get Alerts
```bash
curl -X GET http://localhost:5000/api/price-alerts \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```
