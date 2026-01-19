from langgraph.prebuilt import create_react_agent
from agent.utils import get_llm
from agent.tools.account import login_tool, register_tool

llm = get_llm()

system_prompt = """You are an Account Management Agent.
Your goal is to handle user authentication and registration.
You can log users in (getting a token) or register new accounts.
When a user logs in successfully, make sure to capture the 'token' returned by the tool.
"""

account_agent = create_react_agent(llm, tools=[login_tool, register_tool], prompt=system_prompt)
