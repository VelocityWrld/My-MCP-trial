# backend enabling my server to LLM

import asyncio
import json
import os
from mcp.client.sse import sse_client
from mcp import ClientSession
from openai import OpenAI
# configuration
OPEN_API_KEY = os.environ.get("OPEN_API_KEY")
MCP_SERVER_URL = os.environ.get("MCP_SERVER_URL")

client = OpenAI(api_key=OPEN_API_KEY)
# the main function
async def main():
  async with sse_client(MCP_SERVER_URL) as (read, write):
    async with ClientSession(read, write) as session:
      await session.initialize()
# tool discovery
tool_result = await session.list_tools()
   
    openai_tools = [
      {
        "type":"function",
        "function":{
          "name":tool.name,
          "description":tool.description,
          "parameters":tool.inputSchema
        }
      }
      for tool in tools_result.tools
    ]
# the conversation
messages = [
      {"roles":"system","content":"You are a helpful assistant with access to tools."} #instruction to LLM before conversation starts
      {"roles":"user","content":"What is 1 USD in NGN? Also lookup IP 8.8.8.8"}
  ]
# the agent loop
while True:
  response = client.chat.completions.create(
    model="gpt-4",
    messages=messages,
    tools=openai_tools
  )
  
  message = response.choices[0].message
  
  if message.tool_calls:
    messages.append(message)
    
    for tool_call in message.tool_calls:
      args = json.loads(tool_call.function.arguments)
      
      result = await session.call_tool(
        tool_call.function.name, args
      )
      
      messages.append({
        "role":"tool"
        "tool_call_id":tool_call.id,
        "content":result.content[0].text
      })
  else:
    print("System:", message.content)
    break

asyncio.run(main())