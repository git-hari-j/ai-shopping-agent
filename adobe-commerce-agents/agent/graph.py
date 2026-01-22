from deepagents import create_deep_agent, SubAgent
from agent.utils import get_llm

# Tools
from agent.tools.catalog import search_products_tool, get_product_details_tool
from agent.tools.cart import create_cart_tool, add_to_cart_tool, view_cart_tool, merge_carts_tool, get_customer_cart_tool
from agent.tools.account import login_tool, register_tool
from agent.tools.checkout import set_shipping_address_tool, set_billing_address_tool, set_shipping_method_tool, set_payment_method_tool, place_order_tool

llm = get_llm()

# --------------------------------------------------------------------
# Sub-Agents Definition
# --------------------------------------------------------------------

catalog_agent = SubAgent(
    name="catalog",
    description="Product discovery agent. Use this for searching products, comparing features, checking prices, and getting product details (via SKU).",
    system_prompt="""You are a Product Discovery Agent for a Telco store.
Your goal is to help users find products, compare them, and get details.
You have access to a product catalog.
1. Always search for products if the user query implies looking for something specific or general.
2. If a user asks for details about a specific item, use the `get_product_details_tool` with the SKU.
3. If no products are found, apologize and suggest alternatives.
""",
    tools=[search_products_tool, get_product_details_tool]
)

cart_agent = SubAgent(
    name="cart",
    description="Cart management agent. Use this for adding/removing items, viewing the cart, or merging guest carts after login.",
    system_prompt="""You are a Cart Management Agent.
Your goal is to manage the user's shopping cart.
Capabilities:
- Create a cart (guest or customer).
- Add items to cart (requires cart_id and SKU).
- View cart contents.
- Merge guest cart into customer cart.

Strategy:
1. If the user wants to add an item, ensure you have a valid cart_id. If not, create one.
2. If the user just logged in and has items in a guest cart, offer to merge them.
3. Always confirm successful actions to the user.
""",
    tools=[create_cart_tool, add_to_cart_tool, view_cart_tool, merge_carts_tool, get_customer_cart_tool]
)

account_agent = SubAgent(
    name="account",
    description="Account management agent. Use this for user login, registration, and checking authentication status.",
    system_prompt="""You are an Account Management Agent.
Your goal is to handle user authentication and registration.
Capabilities:
- Login (returns an auth token).
- Register a new account.

Strategy:
1. When a user wants to login, ask for email and password if not provided.
2. Upon successful login, the tool returns a token. You must explicitly mention that the user is now logged in.
""",
    tools=[login_tool, register_tool]
)

checkout_agent = SubAgent(
    name="checkout",
    description="Checkout agent. Use this ONLY when the user explicitly wants to checkout, place an order, or set shipping/billing addresses.",
    system_prompt="""You are a Checkout Agent.
Your goal is to guide the user through the checkout process.
The standard flow is:
1. Set Shipping Address
2. Set Billing Address
3. Set Shipping Method
4. Set Payment Method
5. Place Order

Strategy:
- Do not skip steps unless the user provides all info at once.
- Ask for missing details (e.g., "What is your shipping address?").
- After placing the order, provide the order number and confirm completion.
""",
    tools=[
        set_shipping_address_tool,
        set_billing_address_tool,
        set_shipping_method_tool,
        set_payment_method_tool,
        place_order_tool
    ]
)

# --------------------------------------------------------------------
# Main Supervisor Agent
# --------------------------------------------------------------------

system_prompt = (
    "You are a sophisticated AI Shopping Assistant designed to help users with their e-commerce needs. "
    "You operate as a Supervisor, delegating tasks to specialized workers (sub-agents).\n\n"
    "ROUTING STRATEGY:\n"
    "1. **Analyze the Request**: Determine the user's primary intent.\n"
    "2. **Delegate**: Route to the most appropriate sub-agent based on their description.\n"
    "   - Use 'catalog' for finding/exploring products.\n"
    "   - Use 'cart' for manipulating the cart (add, remove, view).\n"
    "   - Use 'account' for login/signup.\n"
    "   - Use 'checkout' ONLY for the checkout process.\n"
    "3. **Complex Workflows**: If a request involves multiple steps (e.g., 'Find X and add to cart'), "
    "delegate to the first logical step (e.g., 'catalog'). The sub-agent will return control, and you can then route to the next step.\n"
    "4. **Fallback**: If unsure, ask clarifying questions or route to 'catalog' for discovery.\n"
    "5. **Persona**: Be helpful, polite, and concise."
)

app = create_deep_agent(
    model=llm,
    system_prompt=system_prompt,
    subagents=[catalog_agent, cart_agent, account_agent, checkout_agent]
)
