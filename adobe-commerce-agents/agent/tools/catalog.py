from langchain_core.tools import tool
from services.magento import MagentoService
from typing import Optional

@tool
def search_products_tool(query: str, page: int = 1) -> str:
    """
    Search for products in the catalog.
    Args:
        query: The search term (e.g., "running shoes").
        page: The page number for pagination (default is 1).
    """
    service = MagentoService()
    try:
        result = service.search_products(query, current_page=page)
        items = result.get('products', {}).get('items', [])
        if not items:
            return "No products found."

        output = []
        for item in items:
            price = item['price_range']['minimum_price']['regular_price']['value']
            currency = item['price_range']['minimum_price']['regular_price']['currency']
            output.append(f"Name: {item['name']}, SKU: {item['sku']}, Price: {price} {currency}")
        return "\n".join(output)
    except Exception as e:
        return f"Error searching products: {str(e)}"

@tool
def get_product_details_tool(sku: str) -> str:
    """
    Get detailed information about a specific product.
    Args:
        sku: The unique SKU of the product.
    """
    service = MagentoService()
    try:
        result = service.get_product_details(sku)
        items = result.get('products', {}).get('items', [])
        if not items:
            return "Product not found."

        item = items[0]
        desc = item.get('description', {}).get('html', 'No description')
        price = item['price_range']['minimum_price']['regular_price']['value']
        stock = item.get('stock_status', 'UNKNOWN')

        return f"Name: {item['name']}\nSKU: {item['sku']}\nPrice: {price}\nStock: {stock}\nDescription: {desc}"
    except Exception as e:
        return f"Error getting product details: {str(e)}"
