import logging
import os
from typing import Optional, Dict, Any, List
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from config import settings

logger = logging.getLogger(__name__)

class MagentoService:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the Magento Service.
        If a token is provided, it is used for Authorization header (Customer context).
        Otherwise, Admin/Integration token from settings is used if available, or no auth (for public endpoints).
        """
        self.base_url = settings.MAGENTO_URL.rstrip('/')
        self.graphql_url = f"{self.base_url}/graphql"
        self.token = token

        headers = {}
        if self.token:
            headers['Authorization'] = f"Bearer {self.token}"
        elif settings.MAGENTO_ACCESS_TOKEN:
             headers['Authorization'] = f"Bearer {settings.MAGENTO_ACCESS_TOKEN}"

        self.transport = RequestsHTTPTransport(
            url=self.graphql_url,
            headers=headers,
            verify=True,
            retries=3,
        )
        self.client = Client(transport=self.transport, fetch_schema_from_transport=False)

    def execute_query(self, query_str: str, variable_values: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Helper to execute GraphQL queries."""
        try:
            query = gql(query_str)
            result = self.client.execute(query, variable_values=variable_values)
            return result
        except Exception as e:
            logger.error(f"GraphQL Execution Error: {e}")
            raise

    # -------------------------------------------------------------------------
    # Catalog
    # -------------------------------------------------------------------------
    def search_products(self, search_term: str, page_size: int = 5, current_page: int = 1) -> Dict[str, Any]:
        query = """
        query searchProducts($search: String!, $pageSize: Int!, $currentPage: Int!) {
            products(search: $search, pageSize: $pageSize, currentPage: $currentPage) {
                total_count
                items {
                    sku
                    name
                    price_range {
                        minimum_price {
                            regular_price {
                                value
                                currency
                            }
                        }
                    }
                    small_image {
                        url
                    }
                    url_key
                }
            }
        }
        """
        variables = {"search": search_term, "pageSize": page_size, "currentPage": current_page}
        return self.execute_query(query, variables)

    def get_product_details(self, sku: str) -> Dict[str, Any]:
        query = """
        query getProductDetails($sku: String!) {
            products(filter: {sku: {eq: $sku}}) {
                items {
                    sku
                    name
                    description {
                        html
                    }
                    price_range {
                        minimum_price {
                            regular_price {
                                value
                                currency
                            }
                        }
                    }
                    media_gallery {
                        url
                        label
                    }
                    stock_status
                }
            }
        }
        """
        variables = {"sku": sku}
        return self.execute_query(query, variables)

    # -------------------------------------------------------------------------
    # Cart
    # -------------------------------------------------------------------------
    def create_empty_cart(self) -> str:
        """Creates a guest cart and returns the Masked Cart ID."""
        mutation = """
        mutation {
            createEmptyCart
        }
        """
        result = self.execute_query(mutation)
        return result['createEmptyCart']

    def add_products_to_cart(self, cart_id: str, quantity: float, sku: str) -> Dict[str, Any]:
        mutation = """
        mutation addProductsToCart($cartId: String!, $qty: Float!, $sku: String!) {
            addProductsToCart(
                cartId: $cartId
                cartItems: [
                    {
                        quantity: $qty
                        sku: $sku
                    }
                ]
            ) {
                cart {
                    items {
                        uid
                        product {
                            name
                            sku
                        }
                        quantity
                    }
                    prices {
                        grand_total {
                            value
                            currency
                        }
                    }
                }
            }
        }
        """
        variables = {"cartId": cart_id, "qty": quantity, "sku": sku}
        return self.execute_query(mutation, variables)

    def get_cart(self, cart_id: str) -> Dict[str, Any]:
        query = """
        query getCart($cartId: String!) {
            cart(cart_id: $cartId) {
                id
                email
                items {
                    uid
                    quantity
                    product {
                        name
                        sku
                        price_range {
                            minimum_price {
                                regular_price {
                                    value
                                    currency
                                }
                            }
                        }
                    }
                }
                prices {
                    grand_total {
                        value
                        currency
                    }
                }
                shipping_addresses {
                    firstname
                    lastname
                    city
                    country {
                        code
                    }
                }
            }
        }
        """
        variables = {"cartId": cart_id}
        return self.execute_query(query, variables)

    def merge_carts(self, source_cart_id: str, destination_cart_id: str) -> Dict[str, Any]:
        mutation = """
        mutation mergeCarts($source: String!, $destination: String!) {
            mergeCarts(source_cart_id: $source, destination_cart_id: $destination) {
                id
                items {
                    product {
                        name
                    }
                    quantity
                }
            }
        }
        """
        variables = {"source": source_cart_id, "destination": destination_cart_id}
        return self.execute_query(mutation, variables)

    def get_customer_cart(self) -> str:
        """Retrieves the cart ID for the logged-in customer."""
        query = """
        query {
            customerCart {
                id
            }
        }
        """
        result = self.execute_query(query)
        return result['customerCart']['id']

    # -------------------------------------------------------------------------
    # Customer / Auth
    # -------------------------------------------------------------------------
    def generate_customer_token(self, email: str, password: str) -> str:
        mutation = """
        mutation generateToken($email: String!, $password: String!) {
            generateCustomerToken(email: $email, password: $password) {
                token
            }
        }
        """
        variables = {"email": email, "password": password}
        result = self.execute_query(mutation, variables)
        return result['generateCustomerToken']['token']

    def create_customer(self, firstname: str, lastname: str, email: str, password: str) -> Dict[str, Any]:
        mutation = """
        mutation createCustomer($firstname: String!, $lastname: String!, $email: String!, $password: String!) {
            createCustomer(
                input: {
                    firstname: $firstname
                    lastname: $lastname
                    email: $email
                    password: $password
                }
            ) {
                customer {
                    firstname
                    lastname
                    email
                }
            }
        }
        """
        variables = {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "password": password
        }
        return self.execute_query(mutation, variables)

    # -------------------------------------------------------------------------
    # Checkout
    # -------------------------------------------------------------------------
    def set_shipping_address(self, cart_id: str, address: Dict[str, Any]) -> Dict[str, Any]:
        """
        Address dict should contain: firstname, lastname, street (list), city, region, postcode, country_code, telephone
        """
        mutation = """
        mutation setShipping($cartId: String!, $address: ShippingAddressInput!) {
            setShippingAddressesOnCart(
                input: {
                    cart_id: $cartId
                    shipping_addresses: [$address]
                }
            ) {
                cart {
                    shipping_addresses {
                        firstname
                        lastname
                        available_shipping_methods {
                            carrier_code
                            carrier_title
                            method_code
                            method_title
                            amount {
                                value
                                currency
                            }
                        }
                    }
                }
            }
        }
        """
        # Simplistic address mapping - in real app, detailed validation needed
        shipping_address_input = {
            "customer_address_id": None,
            "address": {
                "firstname": address.get("firstname"),
                "lastname": address.get("lastname"),
                "street": address.get("street", ["123 Main St"]),
                "city": address.get("city"),
                "region": address.get("region", "CA"), # Simplified
                "postcode": address.get("postcode"),
                "country_code": address.get("country_code", "US"),
                "telephone": address.get("telephone", "555-555-5555"),
                "save_in_address_book": False
            }
        }
        variables = {"cartId": cart_id, "address": shipping_address_input}
        return self.execute_query(mutation, variables)

    def set_billing_address(self, cart_id: str, address: Dict[str, Any]) -> Dict[str, Any]:
        mutation = """
        mutation setBilling($cartId: String!, $address: BillingAddressInput!) {
            setBillingAddressOnCart(
                input: {
                    cart_id: $cartId
                    billing_address: $address
                }
            ) {
                cart {
                    billing_address {
                        firstname
                        lastname
                    }
                }
            }
        }
        """
        billing_address_input = {
            "address": {
                "firstname": address.get("firstname"),
                "lastname": address.get("lastname"),
                "street": address.get("street", ["123 Main St"]),
                "city": address.get("city"),
                "region": address.get("region", "CA"),
                "postcode": address.get("postcode"),
                "country_code": address.get("country_code", "US"),
                "telephone": address.get("telephone", "555-555-5555"),
                "save_in_address_book": False
            }
        }
        variables = {"cartId": cart_id, "address": billing_address_input}
        return self.execute_query(mutation, variables)

    def set_shipping_method(self, cart_id: str, carrier_code: str, method_code: str) -> Dict[str, Any]:
        mutation = """
        mutation setShippingMethod($cartId: String!, $carrier: String!, $method: String!) {
            setShippingMethodsOnCart(
                input: {
                    cart_id: $cartId
                    shipping_methods: [
                        {
                            carrier_code: $carrier
                            method_code: $method
                        }
                    ]
                }
            ) {
                cart {
                    shipping_addresses {
                        selected_shipping_method {
                            carrier_title
                            method_title
                            amount {
                                value
                            }
                        }
                    }
                }
            }
        }
        """
        variables = {"cartId": cart_id, "carrier": carrier_code, "method": method_code}
        return self.execute_query(mutation, variables)

    def set_payment_method(self, cart_id: str, code: str = "checkmo") -> Dict[str, Any]:
        mutation = """
        mutation setPaymentMethod($cartId: String!, $code: String!) {
            setPaymentMethodOnCart(
                input: {
                    cart_id: $cartId
                    payment_method: {
                        code: $code
                    }
                }
            ) {
                cart {
                    selected_payment_method {
                        code
                        title
                    }
                }
            }
        }
        """
        variables = {"cartId": cart_id, "code": code}
        return self.execute_query(mutation, variables)

    def place_order(self, cart_id: str) -> Dict[str, Any]:
        mutation = """
        mutation placeOrder($cartId: String!) {
            placeOrder(input: {cart_id: $cartId}) {
                order {
                    order_number
                }
            }
        }
        """
        variables = {"cartId": cart_id}
        return self.execute_query(mutation, variables)
