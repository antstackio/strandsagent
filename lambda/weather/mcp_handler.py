import json
from typing import Dict, Any, List, Optional
from weather_agent_handler import handler as weather_handler

class MCPServer:
    """MCP Server implementation for weather queries"""
    def __init__(self):
        self.tools = self._define_tools()
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available MCP tools"""
        return [
            {
                "name": "get_weather_forecast",
                "description": "Get weather forecast for a specific location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "location": {
                            "type": "string",
                            "description": "Location for weather forecast (city, zip code, etc.)"
                        }
                    },
                    "required": ["location"]
                }
            },
        ]
    def handle_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle incoming MCP requests"""
        tool_name = request.get("name")
        if tool_name == "get_weather_forecast":
            return self._handle_weather_request(request)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _handle_weather_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle weather forecast requests"""
        location = request["arguments"]["location"]
        # Call the weather agent handler
        response = weather_handler({"prompt": f"Get weather forecast for {location}"}, None)
        print(response)
        return {"response": response}
    
    def handle_tool_list(self) -> Dict[str, Any]:
        """Handle tool list requests"""
        return {"tools": self.tools}
    
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization requests"""
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "serverInfo": {
                "name": "database-agent",
                "version": "1.0.0"
            }
        }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process incoming requests"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self.handle_initialize(params)
            elif method == "tools/list":
                result = self.handle_tool_list()
            elif method == "tools/call":
                result = self.handle_request(params)
            else:
                raise ValueError(f"Unknown method: {method}")
            
            return {
                "jsonrpc": "2.0",
                "result": result,
                "id": request_id
            }
            
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                },
                "id": request_id
            }

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Lambda handler function"""
    print(event)
    mcp_server = MCPServer()
    if isinstance(event.get("body"), str):
        body = json.loads(event["body"])
    else:
        body = event
    
    return mcp_server.process_request(body)
