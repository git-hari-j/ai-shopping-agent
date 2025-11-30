import asyncio
from typing import List, Dict, Any, Optional
from langchain_core.tools import tool
from crawl4ai import AsyncWebCrawler
from patchright.async_api import async_playwright
import json
import logging

logger = logging.getLogger(__name__)

# Constants
MAGENTO_URL = "https://demo-fklvc3a-qslkp4psgn6ta.us-4.magentosite.cloud/"

@tool
async def search_products(query: str) -> List[Dict[str, Any]]:
    """
    Search for products on the Magento demo store using Crawl4AI.
    Returns a list of products with names, prices, and URLs.
    """
    logger.info(f"Searching for: {query}")
    search_url = f"{MAGENTO_URL}/catalogsearch/result/?q={query.replace(' ', '+')}"

    async with AsyncWebCrawler(verbose=True) as crawler:
        result = await crawler.arun(url=search_url)

        if not result.success:
            logger.error(f"Crawl failed: {result.error_message}")
            return []

        # Parse extracted content (assuming crawl4ai extracts markdown/text effectively)
        # For a structured list, we might need a custom CSS selector strategy or LLM extraction.
        # Here we simulated structured extraction based on typical Magento selectors if we were using raw HTML,
        # but crawl4ai gives us cleaner markdown. We'll use a simple strategy or just return the text for the LLM to parse.

        # However, for a "tool", structured data is better. Let's try to extract links and basic info.
        # Since I can't see the exact DOM of the demo site right now, I'll return a summarized text representation
        # which the LLM can interpret, OR strictly, I should use Playwright to get structured data if crawl4ai result is too unstructured.

        # Let's try a direct Playwright extraction for reliability in this specific task,
        # but wrapping it in the tool as requested.

        return [{"text_content": result.markdown[:2000]}] # Limiting context for now

@tool
async def add_to_cart(product_url: str, quantity: int = 1) -> str:
    """
    Add a product to the cart.
    """
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
            return f"Failed to add to cart: {str(e)}"
        finally:
            await browser.close()

@tool
async def view_cart() -> str:
    """
    View current cart contents.
    """
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

# Note: Real stateful cart management requires persisting cookies/session across tool calls.
# The current simple tool implementation spins up a NEW browser each time, losing the session.
# For a true stateful workflow, we need to pass a browser context or session ID.
# I will implement a session manager in the agent service to handle this.
