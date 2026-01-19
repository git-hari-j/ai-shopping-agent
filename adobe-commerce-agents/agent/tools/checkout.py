from langchain_core.tools import tool
from services.magento import MagentoService
from typing import Optional, Dict

@tool
def set_shipping_address_tool(cart_id: str, firstname: str, lastname: str, street: str, city: str, postcode: str, telephone: str, region: str = "CA", country_code: str = "US", token: Optional[str] = None) -> str:
    """
    Set the shipping address for the cart.
    Args:
        cart_id: The cart ID.
        firstname: First name.
        lastname: Last name.
        street: Street address.
        city: City.
        postcode: Zip/Postal code.
        telephone: Phone number.
        region: Region/State code (default CA).
        country_code: Country code (default US).
        token: Optional customer token.
    """
    service = MagentoService(token=token)
    address = {
        "firstname": firstname,
        "lastname": lastname,
        "street": [street],
        "city": city,
        "postcode": postcode,
        "telephone": telephone,
        "region": region,
        "country_code": country_code
    }
    try:
        result = service.set_shipping_address(cart_id, address)
        methods = result['setShippingAddressesOnCart']['cart']['shipping_addresses'][0]['available_shipping_methods']
        method_str = ", ".join([f"{m['carrier_code']}_{m['method_code']} ({m['amount']['value']})" for m in methods])
        return f"Shipping address set. Available methods: {method_str}"
    except Exception as e:
        return f"Error setting shipping address: {str(e)}"

@tool
def set_billing_address_tool(cart_id: str, firstname: str, lastname: str, street: str, city: str, postcode: str, telephone: str, region: str = "CA", country_code: str = "US", token: Optional[str] = None) -> str:
    """
    Set the billing address for the cart. Same args as shipping.
    """
    service = MagentoService(token=token)
    address = {
        "firstname": firstname,
        "lastname": lastname,
        "street": [street],
        "city": city,
        "postcode": postcode,
        "telephone": telephone,
        "region": region,
        "country_code": country_code
    }
    try:
        service.set_billing_address(cart_id, address)
        return "Billing address set successfully."
    except Exception as e:
        return f"Error setting billing address: {str(e)}"

@tool
def set_shipping_method_tool(cart_id: str, carrier_code: str, method_code: str, token: Optional[str] = None) -> str:
    """
    Set the shipping method.
    Args:
        cart_id: Cart ID.
        carrier_code: The carrier code (e.g., 'flatrate').
        method_code: The method code (e.g., 'flatrate').
        token: Optional customer token.
    """
    service = MagentoService(token=token)
    try:
        service.set_shipping_method(cart_id, carrier_code, method_code)
        return "Shipping method set successfully."
    except Exception as e:
        return f"Error setting shipping method: {str(e)}"

@tool
def set_payment_method_tool(cart_id: str, method_code: str = "checkmo", token: Optional[str] = None) -> str:
    """
    Set the payment method.
    Args:
        cart_id: Cart ID.
        method_code: Payment method code (default 'checkmo').
        token: Optional customer token.
    """
    service = MagentoService(token=token)
    try:
        service.set_payment_method(cart_id, method_code)
        return "Payment method set successfully."
    except Exception as e:
        return f"Error setting payment method: {str(e)}"

@tool
def place_order_tool(cart_id: str, token: Optional[str] = None) -> str:
    """
    Place the order.
    Args:
        cart_id: Cart ID.
        token: Optional customer token.
    Returns: The order number.
    """
    service = MagentoService(token=token)
    try:
        result = service.place_order(cart_id)
        order_number = result['placeOrder']['order']['order_number']
        return f"Order placed successfully! Order Number: {order_number}"
    except Exception as e:
        return f"Error placing order: {str(e)}"
