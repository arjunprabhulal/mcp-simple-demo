# MCP Simple Demo

A simple demonstration of the Model Context Protocol (MCP) with a Python server and client.

## Overview

This project demonstrates a basic implementation of the Model Context Protocol (MCP), which allows AI models to access external tools and data sources. It includes:

- An MCP-compliant server with simple tools
- A client for interacting with the server
- Examples of tool calls and responses

## Repository

The official repository for this project is available at:
[https://github.com/arjunprabhulal/mcp-simple-demo](https://github.com/arjunprabhulal/mcp-simple-demo)

## Installation

### Prerequisites

- Python 3.8+
- pip

### Setup

1. Clone the repository:
```bash
git clone https://github.com/arjunprabhulal/mcp-simple-demo.git
cd mcp-simple-demo
```

2. Install the required packages:
```bash
# Using requirements.txt (recommended)
pip install -r requirements.txt

# Or install packages manually
pip install mcp llama-index llama-index-tools-mcp requests
```

## Server Usage

The server provides MCP-compliant tools that can be accessed by AI models or client applications.

### Starting the Server

```bash
python server.py
```

This starts an MCP server on the default port (8000) with two tools:
- `hello_world`: Returns a greeting message
- `add`: Adds two numbers

### Debugging

To enable debugging logs:

```bash
DEBUG_LEVEL=DEBUG python server.py
```

For full debug mode:

```bash
DEBUG=true DEBUG_LEVEL=DEBUG python server.py
```

## Client Usage

The provided client can interact with the MCP server in both interactive and command-line modes.

### Interactive Mode

```bash
python client.py
```

This starts an interactive session where you can choose commands to execute.

### Command Line Mode

List available tools:
```bash
python client.py tools
```

Call the hello_world tool:
```bash
python client.py hello
python client.py hello "Your Name"
```

Call the add tool:
```bash
python client.py add 5 3
```

## Available Tools

### hello_world

Returns a greeting message.

**Parameters:**
- `name` (optional): The name to greet (default: "World")

**Returns:**
- A JSON object with a message field: `{"message": "Hello, Name!"}`

### add

Adds two numbers.

**Parameters:**
- `a`: First number (integer)
- `b`: Second number (integer)

**Returns:**
- The sum of a and b (integer)

## Protocol Details

The Model Context Protocol (MCP) uses Server-Sent Events (SSE) for establishing connections. The flow works as follows:

1. Client connects to the `/sse` endpoint
2. Server returns a session ID
3. Client uses the session ID to make tool calls via `/messages/?session_id=...`

## Advanced Testing

For more detailed testing of the server, use the test client:

```bash
python test_client.py
```

This performs more comprehensive tests of the MCP connection and available tools.

## Contributions

Contributions to this project are welcome! Please feel free to submit issues or pull requests to the [GitHub repository](https://github.com/arjunprabhulal/mcp-simple-demo).

## References

- [Model Context Protocol Specification](https://github.com/anthropics/anthropic-tools)
- [MCP Python SDK](https://github.com/anthropics/anthropic-tools-python)
- [LlamaIndex MCP Integration](https://docs.llamaindex.ai/en/stable/examples/tools/anthropic_tools/)
- [MCP Simple Demo Repository](https://github.com/arjunprabhulal/mcp-simple-demo) 