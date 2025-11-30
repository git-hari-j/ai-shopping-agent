from .graph import app
from langchain_core.messages import HumanMessage

async def run_agent(user_input: str, chat_history: list = []):
    """
    Run the agent with the given input.
    """
    # Convert simple chat history to LangChain messages if needed
    messages = [HumanMessage(content=user_input)]

    # Run the graph
    inputs = {"messages": messages, "cart_items": [], "current_step": "discovery"}
    result = await app.ainvoke(inputs)

    # Extract response
    last_msg = result['messages'][-1]
    return last_msg.content
