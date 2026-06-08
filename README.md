# Vic MCP Server

A simple MCP server with two tools:

- **Currency Converter** - Converts amounts between currencies
- **IP Geolocation** - Returns location and network info for any IP address

## Tools

### convert_currency
Converts an amount from one currency to another using live exchange rates.

**Inputs:**
- amount (number) - the amount to convert
- from_currency (string) - the source currency e.g USD
- to_currency (string) - the target currency e.g NGN

### get_ip_info
Returns locationand network information about an IP address.

**Inputs:**
- ip_address (string) - the IP address to look up

## Tech Stack
- Python
- FastMCP
- Render (hosting)

## Transport
SSE (Server-Sent Events)