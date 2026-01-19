from langgraph.prebuilt import create_react_agent
from agent.utils import get_llm
from agent.tools.catalog import search_products_tool, get_product_details_tool

llm = get_llm()

system_prompt = """You are a Product Discovery Agent for a Telco store.
Your goal is to help users find products, compare them, and get details.
You have access to a product catalog.
Always search for products if the user query implies looking for something.
If a user asks for details, use the SKU to fetch them.
"""

catalog_agent = create_react_agent(llm, tools=[search_products_tool, get_product_details_tool], prompt=system_prompt)
