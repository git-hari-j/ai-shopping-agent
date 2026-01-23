import logging
import json
from typing import Any, Dict, List
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

# Configure structured logging
logger = logging.getLogger("universal_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

class UniversalCallbackHandler(BaseCallbackHandler):
    """
    Callback handler to log all interactions:
    - User Input
    - Supervisor/Agent Reasoning
    - Tool Calls
    - Tool Outputs
    """

    def on_llm_start(self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any) -> None:
        """Run when LLM starts running."""
        # logger.info(f"LLM Start: Prompts: {prompts}")
        pass

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends running."""
        for generations in response.generations:
            for gen in generations:
                if gen.message and isinstance(gen.message, AIMessage):
                    content = gen.message.content
                    tool_calls = gen.message.tool_calls
                    if tool_calls:
                        for tc in tool_calls:
                            logger.info(f"Reasoning/Action: Agent decided to call tool '{tc['name']}' with args: {tc['args']}")
                    else:
                         logger.info(f"Reasoning/Response: {content}")

    def on_tool_start(self, serialized: Dict[str, Any], input_str: str, **kwargs: Any) -> None:
        """Run when tool starts running."""
        tool_name = serialized.get("name")
        logger.info(f"Tool Call Start: {tool_name} with input: {input_str}")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Run when tool ends running."""
        logger.info(f"Tool Call Result: {output}")

    def on_chain_start(self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain starts running."""
        # This can be noisy, but useful for tracing graph nodes
        if "messages" in inputs:
             # Identify if this is a user input
             last_msg = inputs["messages"][-1]
             if isinstance(last_msg, HumanMessage):
                 logger.info(f"User Input: {last_msg.content}")

def log_interaction(event_type: str, details: Any):
    """Manual logging helper"""
    logger.info(f"Event: {event_type} | Details: {json.dumps(details, default=str)}")
