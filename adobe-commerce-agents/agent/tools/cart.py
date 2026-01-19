from langchain_core.tools import tool
from services.magento import MagentoService
from typing import Optional

@tool
def create_cart_tool() -> str:
    """
    Create a new empty guest cart.
    Returns the Cart ID.
    """
    service = MagentoService()
    try:
        cart_id = service.create_empty_cart()
        return f"Cart created successfully. Cart ID: {cart_id}"
    except Exception as e:
        return f"Error creating cart: {str(e)}"

@tool
def add_to_cart_tool(cart_id: str, sku: str, quantity: float = 1.0) -> str:
    """
    Add a product to the cart.
    Args:
        cart_id: The ID of the cart.
        sku: The SKU of the product to add.
        quantity: The quantity to add (default 1).
    """
    service = MagentoService()
    try:
        service.add_products_to_cart(cart_id, quantity, sku)
        return f"Added {quantity} of {sku} to cart {cart_id}."
    except Exception as e:
        return f"Error adding to cart: {str(e)}"

@tool
def view_cart_tool(cart_id: str, token: Optional[str] = None) -> str:
    """
    View the contents of a cart.
    Args:
        cart_id: The ID of the cart.
        token: Optional customer token if the user is logged in.
    """
    service = MagentoService(token=token)
    try:
        result = service.get_cart(cart_id)
        cart = result.get('cart', {})
        items = cart.get('items', [])

        if not items:
            return "Cart is empty."

        output = [f"Cart ID: {cart.get('id')}"]
        for item in items:
            p_name = item['product']['name']
            qty = item['quantity']
            price = item['product']['price_range']['minimum_price']['regular_price']['value']
            output.append(f"- {p_name} (Qty: {qty}) @ {price}")

        grand_total = cart.get('prices', {}).get('grand_total', {}).get('value')
        output.append(f"Total: {grand_total}")
        return "\n".join(output)
    except Exception as e:
        return f"Error viewing cart: {str(e)}"

@tool
def merge_carts_tool(source_cart_id: str, destination_cart_id: str, token: str) -> str:
    """
    Merge a guest cart into a customer cart.
    Args:
        source_cart_id: The guest cart ID.
        destination_cart_id: The customer cart ID.
        token: The customer's auth token.
    """
    service = MagentoService(token=token)
    try:
        service.merge_carts(source_cart_id, destination_cart_id)
        return "Carts merged successfully."
    except Exception as e:
        return f"Error merging carts: {str(e)}"

@tool
def get_customer_cart_tool(token: str) -> str:
    """
    Get the cart ID for the logged-in user.
    Args:
        token: The customer's auth token.
    Returns: The customer's Cart ID.
    """
    service = MagentoService(token=token)
    try:
        cart_id = service.get_customer_cart()
        return f"Customer Cart ID: {cart_id}"
    except Exception as e:
        return f"Error retrieving customer cart: {str(e)}"
