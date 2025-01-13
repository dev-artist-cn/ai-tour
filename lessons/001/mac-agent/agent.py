import asyncio
import json
import os
from typing import Optional
from contextlib import AsyncExitStack

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

class Agent:
    def __init__(self):
        # Initialize session and client objects
        self.session: Optional[ClientSession] = None
        self.exit_stack = AsyncExitStack()
        self.openai = OpenAI()

    async def connect_to_server(self, server_script_path: str):
        """Connect to an MCP server
        
        Args:
            server_script_path: Path to the server script (.py or .js)
        """
        is_python = server_script_path.endswith('.py')
        is_js = server_script_path.endswith('.js')
        if not (is_python or is_js):
            raise ValueError("Server script must be a .py or .js file")
            
        command = "python" if is_python else "node"
        server_params = StdioServerParameters(
            command=command,
            args=[server_script_path],
            env=None
        )
        
        stdio_transport = await self.exit_stack.enter_async_context(stdio_client(server_params))
        self.stdio, self.write = stdio_transport
        self.session = await self.exit_stack.enter_async_context(ClientSession(self.stdio, self.write))
        
        await self.session.initialize()
        
        # List available tools
        response = await self.session.list_tools()
        tools = response.tools
        print("\nConnected to server with tools:", [tool.name for tool in tools])

    async def process_query(self, query: str) -> str:
        """Process a query using LLM and available tools"""
        messages = [
            {
                "role": "user",
                "content": query
            }
        ]

        response = await self.session.list_tools()
        available_tools = [{ 
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": tool.inputSchema['type'],
                    "properties": {
                        k: {
                            "type": v['type'],
                            "description": v['title']
                        } for k,v in tool.inputSchema['properties'].items()
                    },
                    "required": tool.inputSchema['required']
                }
            }
        } for tool in response.tools]

        # Initial LLM API call
        response = self.openai.chat.completions.create(
            model=os.getenv("OPENAI_MODEL"),
            messages=messages,
            tools=available_tools
        )

        # Process response and handle tool calls
        final_text = []

        message = response.choices[0].message
        if len(message.content) > 0:
            final_text.append(message.content)
        elif len(message.tool_calls) > 0:
            tool_name = message.tool_calls[0].function.name
            tool_args = json.loads(message.tool_calls[0].function.arguments)
            
            final_text.append(f"[Calling tool {tool_name} with args {tool_args}]")
            # Execute tool call
            result = await self.session.call_tool(tool_name, tool_args)
            # print("Tool result:", result)

            # Continue conversation with tool results
            if hasattr(message, 'content') and message.content:
                messages.append({
                    "role": "assistant",
                    "content": message.content
                })
            messages.append({
                "role": "tool", 
                "content": result.content
            })
            

        return "\n".join(final_text)

    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMac Agent Started!")
        print("Type your queries or 'quit' to exit.")
        
        while True:
            try:
                query = input("\nQuery: ").strip()
                
                if query.lower() == 'quit':
                    break
                    
                response = await self.process_query(query)
                print("\n" + response)
                    
            except Exception as e:
                print(f"\nError: {str(e)}")
    
    async def cleanup(self):
        """Clean up resources"""
        await self.exit_stack.aclose()

async def main():        
    client = Agent()
    try:
        print("Connecting to server: ", "server.py")
        await client.connect_to_server("server.py")
        print("Connected to server!")
        await client.chat_loop()
    finally:
        await client.cleanup()

if __name__ == "__main__":
    import sys
    asyncio.run(main())