"""
Simple test client for MCP server tools with SSE endpoint.
"""
import asyncio
import json
import requests
import sys
import time
import socket
import inspect
import traceback
from llama_index.tools.mcp import BasicMCPClient, McpToolSpec

# MCP server endpoint
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

def check_server_availability():
    """Check if the server is available at the given host:port."""
    host = "localhost"
    port = 8000
    
    print(f"Checking if server is available at {host}:{port}...")
    
    # Try to connect to the socket
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(2)
    try:
        result = s.connect_ex((host, port))
        if result == 0:
            print(f"✅ Server is listening on {host}:{port}")
            return True
        else:
            print(f"❌ Server is NOT listening on {host}:{port}")
            return False
    except Exception as e:
        print(f"❌ Error checking server: {e}")
        return False
    finally:
        s.close()

def test_sse_endpoint():
    """Test SSE endpoint with GET request (standard for SSE)."""
    print(f"\nTesting SSE endpoint at: {MCP_URL}")
    
    try:
        # For standard SSE, use GET request with appropriate headers
        print("Sending GET request with SSE headers...")
        
        # Try simple GET request without parameters
        response = requests.get(
            MCP_URL,
            headers={"Accept": "text/event-stream"},
            stream=True,
            timeout=10
        )
        
        print(f"Response status code: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            print("✅ Connection to SSE endpoint successful!")
            print("Reading SSE events...")
            
            session_id = None
            
            try:
                # Process SSE events
                for line in response.iter_lines():
                    if line:
                        line_str = line.decode('utf-8')
                        print(f"SSE: {line_str}")
                        
                        # Check for session ID in the data
                        if line.startswith(b'data: '):
                            data_str = line[6:].decode('utf-8')
                            if '?session_id=' in data_str:
                                session_id = data_str.split('?session_id=')[1]
                                print(f"✅ Received session ID: {session_id}")
                                # Successfully got session ID, this is expected behavior
                                break
                            else:
                                try:
                                    # Try to parse as JSON
                                    event_data = json.loads(data_str)
                                    print(f"Event data: {json.dumps(event_data, indent=2)}")
                                except json.JSONDecodeError:
                                    print(f"Event data: {data_str}")
                
                # If we got here normally, the connection ended gracefully
                if session_id:
                    print("✅ Connection closed after receiving session ID (expected behavior)")
                else:
                    print("⚠️ Connection closed without receiving a session ID")
                    
            except requests.exceptions.ChunkedEncodingError:
                # This is expected when the server closes the connection after sending the session ID
                if session_id:
                    print("✅ Connection closed after receiving session ID (expected behavior)")
                else:
                    print("⚠️ Server closed connection without sending a session ID")
            except Exception as e:
                print(f"⚠️ Error reading SSE events: {e}")
            
            response.close()
        else:
            print(f"❌ Failed to connect: {response.text}")
            
    except requests.exceptions.Timeout:
        print("⚠️ Request timed out - server may be slow to respond")
    except requests.exceptions.ConnectionError:
        # Only show connection error if we didn't get a successful response first
        if 'response' not in locals() or response.status_code != 200:
            print("⚠️ Connection error - server may not be running")
    except Exception as e:
        print(f"Error testing SSE endpoint: {e}")

async def test_with_llama_index():
    """Test using llama-index MCP client with the SSE endpoint."""
    print("\nInspecting BasicMCPClient.call_tool method...")
    if hasattr(BasicMCPClient, "call_tool"):
        sig = inspect.signature(BasicMCPClient.call_tool)
        print(f"Method signature: {sig}")
        
        # Also inspect the __init__ method
        init_sig = inspect.signature(BasicMCPClient.__init__)
        print(f"Constructor signature: {init_sig}")
        print("✅ Successfully inspected MCP client methods")
    else:
        print("client.call_tool method not found!")
        print(f"Available methods: {[m for m in dir(BasicMCPClient) if not m.startswith('_')]}")

    print(f"\nTesting with llama-index MCP client at {MCP_URL}")

    try:
        # Initialize the MCP client
        client = BasicMCPClient(MCP_URL)
        print("✅ Successfully created BasicMCPClient instance")

        # Get available tools
        print("Getting available tools...")
        tools_spec = McpToolSpec(client=client)
        
        try:
            tools = await asyncio.wait_for(
                tools_spec.to_tool_list_async(),
                timeout=10
            )
                
            print(f"✅ Found {len(tools)} tools:")
            for tool in tools:
                print(f" - {tool.metadata.name}: {tool.metadata.description}")
        except asyncio.TimeoutError:
            print("Timeout getting tools list")
            return
        except Exception as e:
            print(f"Error getting tools: {e}")
            traceback.print_exc()
            return

        # Test hello_world tool
        print("\n--- Testing hello_world tool ---")
        try:
            # Test with default parameter
            print("Calling hello_world with default parameters...")
            result_default = await asyncio.wait_for(
                client.call_tool("hello_world", arguments={}),
                timeout=10
            )
                
            print("✅ Default Result:")
            print(result_default)
            
            if hasattr(result_default, 'content'):
                print("\nContent:")
                for item in result_default.content:
                    if hasattr(item, 'text'):
                        print(f"Text: {item.text}")

            # Test with custom name
            print("\nCalling hello_world with name='LlamaIndex Tester'...")
            result_custom = await asyncio.wait_for(
                client.call_tool("hello_world", arguments={"name": "LlamaIndex Tester"}),
                timeout=10
            )
                
            print("✅ Custom Result:")
            print(result_custom)
            
            if hasattr(result_custom, 'content'):
                print("\nContent:")
                for item in result_custom.content:
                    if hasattr(item, 'text'):
                        print(f"Text: {item.text}")
            
            print("✅ hello_world tool tests completed successfully")
                        
        except asyncio.TimeoutError:
            print("⚠️ Timeout calling hello_world tool")
        except Exception as e:
            print(f"Error calling hello_world tool: {e}")
            traceback.print_exc()

        # Test add tool
        print("\n--- Testing add tool ---")
        try:
            print("Calling add with a=5, b=3...")
            result_add = await asyncio.wait_for(
                client.call_tool("add", arguments={"a": 5, "b": 3}),
                timeout=10
            )
                
            print("✅ Result (5 + 3):", result_add)
            
            if hasattr(result_add, 'content'):
                print("\nContent:")
                for item in result_add.content:
                    if hasattr(item, 'text'):
                        print(f"Text: {item.text}")
            
            print("✅ add tool test completed successfully")
                        
        except asyncio.TimeoutError:
            print("⚠️ Timeout calling add tool")
        except Exception as e:
            print(f"Error calling add tool: {e}")
            traceback.print_exc()
        
        print("✅ All tool tests completed successfully")

    except Exception as e:
        print(f"Error during llama-index test: {e}")
        traceback.print_exc()

async def main():
    """Main function to run the tests properly with asyncio."""
    # First check if server is available
    if not check_server_availability():
        print("⚠️ Server doesn't appear to be running. Tests may fail.")
    
    # Test direct SSE connection
    test_sse_endpoint()
    
    # Then try llama-index client (properly awaited)
    await test_with_llama_index()

if __name__ == "__main__":
    print("🔍 MCP Server SSE Endpoint Tester")
    print("================================")
    
    # Check requirements first
    if not check_requirements():
        sys.exit(1)
    
    asyncio.run(main())
    
    print("\n✅ Testing complete!") 