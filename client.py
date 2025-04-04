"""
Simple MCP client to interact with the SimpleServer.
"""
import asyncio
import json
import sys
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# MCP server configuration
MCP_URL = "http://localhost:8000/sse"

def check_requirements():
    """Check if all required packages are installed."""
    try:
        import llama_index
        return True
    except ImportError:
        print("Error: Required packages not installed.")
        print("Install with: pip install llama-index llama-index-tools-mcp")
        return False

async def call_hello_world(name=None):
    """Call the hello_world tool."""
    try:
        # Create client
        client = BasicMCPClient(MCP_URL)
        print(f"Connecting to MCP server at {MCP_URL}...")
        
        # Set up parameters
        args = {"name": name} if name else {}
        
        # Call the tool
        print(f"Calling hello_world tool{' with name: ' + name if name else ''}...")
        result = await asyncio.wait_for(
            client.call_tool("hello_world", arguments=args),
            timeout=10
        )
        
        # Extract and display the text content
        if hasattr(result, 'content'):
            for item in result.content:
                if hasattr(item, 'text'):
                    try:
                        # Try to parse as JSON if possible
                        data = json.loads(item.text)
                        return data
                    except json.JSONDecodeError:
                        # Otherwise return the raw text
                        return item.text
        
        # Fallback to returning the full result
        return result
        
    except Exception as e:
        print(f"Error calling hello_world: {e}")
        return None

async def call_add(a, b):
    """Call the add tool."""
    try:
        # Create client
        client = BasicMCPClient(MCP_URL)
        print(f"Connecting to MCP server at {MCP_URL}...")
        
        # Call the tool
        print(f"Calling add tool with a={a}, b={b}...")
        result = await asyncio.wait_for(
            client.call_tool("add", arguments={"a": a, "b": b}),
            timeout=10
        )
        
        # Extract and display the text content
        if hasattr(result, 'content'):
            for item in result.content:
                if hasattr(item, 'text'):
                    try:
                        # Try to parse as int if possible
                        return int(item.text)
                    except ValueError:
                        # Otherwise return the raw text
                        return item.text
        
        # Fallback to returning the full result
        return result
        
    except Exception as e:
        print(f"Error calling add: {e}")
        return None

async def list_tools():
    """List all available tools on the server."""
    try:
        # Create client
        client = BasicMCPClient(MCP_URL)
        print(f"Connecting to MCP server at {MCP_URL}...")
        
        # Get available tools
        tools_spec = McpToolSpec(client=client)
        tools = await asyncio.wait_for(
            tools_spec.to_tool_list_async(),
            timeout=10
        )
        
        # Return tool info
        return [
            {"name": tool.metadata.name, "description": tool.metadata.description}
            for tool in tools
        ]
        
    except Exception as e:
        print(f"Error listing tools: {e}")
        return []

async def interactive_mode():
    """Run an interactive session with the MCP server."""
    print("🔍 MCP Client Interactive Mode")
    print("=============================")
    print("Type 'exit' to quit, 'tools' to list available tools")
    
    while True:
        command = input("\nEnter command (hello, add, tools, exit): ").strip().lower()
        
        if command == "exit":
            print("Goodbye!")
            break
            
        elif command == "tools":
            tools = await list_tools()
            print("\nAvailable tools:")
            for tool in tools:
                print(f" - {tool['name']}: {tool['description']}")
                
        elif command == "hello":
            name = input("Enter name (or press Enter for default): ").strip()
            name = name if name else None
            
            result = await call_hello_world(name)
            print("\nResult:", result)
            
        elif command == "add":
            try:
                a = int(input("Enter first number: ").strip())
                b = int(input("Enter second number: ").strip())
                
                result = await call_add(a, b)
                print("\nResult:", result)
            except ValueError:
                print("Error: Please enter valid numbers")
                
        else:
            print("Unknown command. Available commands: hello, add, tools, exit")

async def main():
    """Main function that processes command line arguments."""
    if len(sys.argv) < 2:
        # No arguments, run interactive mode
        await interactive_mode()
        return
        
    command = sys.argv[1].lower()
    
    if command == "tools":
        # List available tools
        tools = await list_tools()
        print("\nAvailable tools:")
        for tool in tools:
            print(f" - {tool['name']}: {tool['description']}")
            
    elif command == "hello":
        # Call hello_world tool
        name = sys.argv[2] if len(sys.argv) > 2 else None
        result = await call_hello_world(name)
        print(result)
        
    elif command == "add":
        # Call add tool
        if len(sys.argv) < 4:
            print("Usage: python client.py add <number1> <number2>")
            return
            
        try:
            a = int(sys.argv[2])
            b = int(sys.argv[3])
            result = await call_add(a, b)
            print(result)
        except ValueError:
            print("Error: Please provide valid numbers")
            
    else:
        print(f"Unknown command: {command}")
        print("Available commands: hello, add, tools")

if __name__ == "__main__":
    # Check requirements first
    if not check_requirements():
        sys.exit(1)
    
    # Run the client
    asyncio.run(main()) 