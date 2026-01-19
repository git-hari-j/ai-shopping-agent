from langchain_core.tools import tool
from services.magento import MagentoService

@tool
def login_tool(email: str, password: str) -> str:
    """
    Authenticate a user and get a token.
    Args:
        email: User email.
        password: User password.
    Returns: The customer authentication token.
    """
    service = MagentoService()
    try:
        token = service.generate_customer_token(email, password)
        return f"Login successful. Token: {token}"
    except Exception as e:
        return f"Login failed: {str(e)}"

@tool
def register_tool(firstname: str, lastname: str, email: str, password: str) -> str:
    """
    Register a new customer account.
    Args:
        firstname: First name.
        lastname: Last name.
        email: Email address.
        password: Password.
    """
    service = MagentoService()
    try:
        result = service.create_customer(firstname, lastname, email, password)
        customer = result.get('createCustomer', {}).get('customer', {})
        return f"Registration successful for {customer.get('email')}."
    except Exception as e:
        return f"Registration failed: {str(e)}"
