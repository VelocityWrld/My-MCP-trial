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
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Could not fetch exchange rates for {from_currency}. Invalid currency code or API unavailable."
        
        data = response.json()
        
        if to_currency not in data["rates"]:
            return f"Error: Currency code {to_currency} not found."
        
        rate = data["rates"][to_currency]
        result = amount * rate
        return f"{amount} {from_currency} = {result:.2f} {to_currency}"
    
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to exchange rate API. Check your internet connection."
    
    except Exception as e:
        return f"Error: Something went wrong — {str(e)}"

@mcp.tool()
def get_ip_info(ip_address: str) -> str:
    """Get location and network information about an IP address"""
    try:
        url = f"https://ipapi.co/{ip_address}/json/"
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            return f"Error: Could not fetch info for IP {ip_address}. API unavailable."
        
        data = response.json()
        
        if "error" in data:
            return f"Error: {data.get('reason', 'Invalid IP address.')}"
        
        city = data.get("city", "Unknown")
        country = data.get("country_name", "Unknown")
        org = data.get("org", "Unknown")
        
        return f"IP: {ip_address} | Location: {city}, {country} | Network: {org}"
    
    except requests.exceptions.Timeout:
        return "Error: Request timed out. Please try again."
    
    except requests.exceptions.ConnectionError:
        return "Error: Could not connect to IP lookup API. Check your internet connection."
    
    except Exception as e:
        return f"Error: Something went wrong — {str(e)}"

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