from langgraph.prebuilt import create_react_agent
from agent.utils import get_llm
from agent.tools.cart import create_cart_tool, add_to_cart_tool, view_cart_tool, merge_carts_tool, get_customer_cart_tool

llm = get_llm()

system_prompt = """You are a Cart Management Agent.
Your goal is to manage the user's shopping cart.
You can create a cart, add items, view the cart, and merge carts.
When adding items, ensure you have the cart_id and SKU.
If the user is a guest, they might need a new cart first (create_cart_tool).
If they just logged in, they might want to merge their guest cart. To do this, you first need to get their customer cart ID (get_customer_cart_tool) and then use the guest cart ID as source.
Always confirm the action to the user.
"""

cart_agent = create_react_agent(llm, tools=[create_cart_tool, add_to_cart_tool, view_cart_tool, merge_carts_tool, get_customer_cart_tool], prompt=system_prompt)
