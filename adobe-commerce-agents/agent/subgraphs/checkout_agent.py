from langgraph.prebuilt import create_react_agent
from agent.utils import get_llm
from agent.tools.checkout import set_shipping_address_tool, set_billing_address_tool, set_shipping_method_tool, set_payment_method_tool, place_order_tool

llm = get_llm()

system_prompt = """You are a Checkout Agent.
Your goal is to guide the user through the checkout process.
The steps are usually:
1. Set Shipping Address
2. Set Billing Address
3. Set Shipping Method
4. Set Payment Method
5. Place Order
You must perform these steps in order.
Ask the user for necessary details (address, etc.) if not provided.
Finalize the order and provide the order number.
"""

checkout_agent = create_react_agent(llm, tools=[
    set_shipping_address_tool,
    set_billing_address_tool,
    set_shipping_method_tool,
    set_payment_method_tool,
    place_order_tool
], prompt=system_prompt)
