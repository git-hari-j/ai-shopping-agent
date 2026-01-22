# Agents

This file describes the responsibility of each agent in the system.

## Supervisor
**Role:** Orchestrator.
**Function:** Analyzes user input and routes control to the specific agent best suited to handle the request.

## Catalog Agent
**Role:** Product Expert.
**Capabilities:**
- Search for products by keyword.
- Retrieve detailed product information (price, description, stock) by SKU.

## Cart Agent
**Role:** Shopping Assistant.
**Capabilities:**
- Create new guest carts.
- Add items to the cart.
- View current cart contents and totals.
- Merge a guest cart into a customer cart upon login.

## Account Agent
**Role:** Identity Manager.
**Capabilities:**
- Log in existing customers (retrieve Bearer token).
- Register new customers.

## Checkout Agent
**Role:** Cashier.
**Capabilities:**
- Set shipping address.
- Set billing address.
- Select shipping method.
- Select payment method.
- Place the final order.
