import asyncio
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from crawl4ai import AsyncWebCrawler
from patchright.async_api import async_playwright
import json
import logging
from config import settings

logger = logging.getLogger(__name__)

# Constants
MAGENTO_URL = "https://demo-fklvc3a-qslkp4psgn6ta.us-4.magentosite.cloud/"

@tool
async def search_products(query: str) -> List[Dict[str, Any]]:
    """
    Search for products on the Magento demo store using Crawl4AI.
    Returns a list of products with names, prices, and URLs.
    """
    if settings.DEBUG:
        logger.debug(f"Tool 'search_products' called with query: {query}")

    search_url = f"{MAGENTO_URL}/catalogsearch/result/?q={query.replace(' ', '+')}"

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=search_url)

        if not result.success:
            logger.error(f"Crawl failed: {result.error_message}")
            return []

        if settings.DEBUG:
            logger.debug(f"Crawl result length: {len(result.markdown)}")

        return [{"text_content": result.markdown[:2000]}]

@tool
async def add_to_cart(product_url: str, quantity: int = 1) -> str:
    """
    Add a product to the cart.
    """
    if settings.DEBUG:
        logger.debug(f"Tool 'add_to_cart' called for {product_url} qty={quantity}")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(product_url)
            # Generic Magento selectors - might need adjustment for specific demo theme
            await page.fill('#qty', str(quantity))
            await page.click('#product-addtocart-button')
            await page.wait_for_selector('.message-success')
            return "Product added to cart successfully."
        except Exception as e:
            logger.error(f"Add to cart failed: {e}", exc_info=True)
            return f"Failed to add to cart: {str(e)}"
        finally:
            await browser.close()

@tool
async def view_cart() -> str:
    """
    View current cart contents.
    """
    if settings.DEBUG:
        logger.debug(f"Tool 'view_cart' called")

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        try:
            await page.goto(f"{MAGENTO_URL}/checkout/cart/")
            # Extract cart items logic here
            content = await page.content()
            return "Cart is currently empty (Mock response - session persistence needed)"
        finally:
            await browser.close()
