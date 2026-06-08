# the actual server logic + tools
from mcp.server.fastmcp import FastMCP
import requests
import os
import uvicorn

mcp = FastMCP("vic-mcp-server") #creating the server instance

@mcp.tool() #this decorator registers the function below as a tool on my server
def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another"""
    url = f"https://api.exchangerate-api.com/v4/latest/{from_currency}"
    response = requests.get(url)
    data = response.json() #api returns data in JSON format
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
    country = data["county_name"]
    org = data["org"]
    return f"IP: {ip_address} | Location: {city}, {country} | Network: {org}"
    
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app = mcp.sse_app()
    uvicorn.run(app, host="0.0.0.0", port=port)