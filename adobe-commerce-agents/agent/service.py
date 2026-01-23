from .graph import app
from langchain_core.messages import HumanMessage
from .logger import UniversalCallbackHandler, logger

async def run_agent(user_input: str, chat_history: list = []):
    """
    Run the agent with the given input.
    """
    # In a real app, you would deserialize chat_history into HumanMessage/AIMessage objects
    # For now, we just take the new user input
    messages = [HumanMessage(content=user_input)]

    # Run the graph
    # We only provide keys that are part of the StateSchema
    inputs = {"messages": messages}

    # Configure callbacks
    config = {"callbacks": [UniversalCallbackHandler()]}

    logger.info(f"--- Starting Interaction: {user_input} ---")

    # app.ainvoke returns the final state
    result = await app.ainvoke(inputs, config=config)

    # Extract response
    # The result['messages'] contains the full history including the final response
    last_msg = result['messages'][-1]

    logger.info(f"--- Interaction Complete. Final Response: {last_msg.content} ---")

    return last_msg.content
