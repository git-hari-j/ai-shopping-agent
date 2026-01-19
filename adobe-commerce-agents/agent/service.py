from .graph import app
from langchain_core.messages import HumanMessage

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

    # app.ainvoke returns the final state
    result = await app.ainvoke(inputs)

    # Extract response
    # The result['messages'] contains the full history including the final response
    last_msg = result['messages'][-1]
    return last_msg.content
