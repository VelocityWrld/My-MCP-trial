from mcp.server.fastmcp import FastMCP
from mcp.server.sse import SseServerTransport
from fastapi import FastAPI, Request
from starlette.routing import Mount
import requests
import os
import uvicorn

mcp = FastMCP("vic-mcp-server")

@mcp.tool()
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another"""
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)
    data = response.json()
    rate = data["rates"][to_currency]
    result = amount * rate
    return f"{amount} {from_currency} = {result:.2f} {to_currency}"

@mcp.tool()
def get_ip_info(ip_address: str) -> str:
    """Get location and network information about an IP address"""
    url = f"https://ipapi.co/{ip_address}/json/"
    response = requests.get(url)
    data = response.json()
    city = data["city"]
    country = data["country_name"]
    org = data["org"]
    return f"IP: {ip_address} | Location: {city}, {country} | Network: {org}"

app = FastAPI()
sse = SseServerTransport("/messages/")
app.router.routes.append(Mount("/messages", app=sse.handle_post_message))

@app.get("/sse")
async def handle_sse(request: Request):
    async with sse.connect_sse(request.scope, request.receive, request._send) as (read, write):
        await mcp._mcp_server.run(read, write, mcp._mcp_server.create_initialization_options())

@app.get("/")
def root():
    return {"status": "MCP server is running"}

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)