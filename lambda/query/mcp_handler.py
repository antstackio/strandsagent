import json
from typing import Dict, Any, List, Optional
from query_agent_handler import (
    analyze_business_request, 
    generate_business_insights,
    execute_revenue_query,
    execute_product_query,
    execute_customer_query
)

class MCPServer:
    """MCP Server implementation for database queries"""
    
    def __init__(self):
        self.tools = self._define_tools()
    
    def _define_tools(self) -> List[Dict[str, Any]]:
        """Define available MCP tools"""
        return [
            {
                "name": "query_business_data",
                "description": "Query business data and get AI-powered insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language query about business data"
                        }
                    },
                    "required": ["query"]
                }
            },
            {
                "name": "get_revenue_summary",
                "description": "Get revenue summary for a specific time period",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format",
                            "format": "date"
                        }
                    }
                }
            },
            {
                "name": "get_product_performance",
                "description": "Get product sales performance data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format",
                            "format": "date"
                        },
                        "category": {
                            "type": "string",
                            "description": "Product category to filter by"
                        }
                    }
                }
            },
            {
                "name": "get_customer_orders",
                "description": "Get customer order data",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "start_date": {
                            "type": "string",
                            "description": "Start date in YYYY-MM-DD format",
                            "format": "date"
                        },
                        "min_amount": {
                            "type": "number",
                            "description": "Minimum order amount to filter by"
                        }
                    }
                }
            }
        ]
    
    def handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle MCP initialize request"""
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
    
    def handle_tools_list(self) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {"tools": self.tools}
    
    def handle_tools_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            if tool_name == "query_business_data":
                query = arguments.get("query", "Show me a business performance summary")
                query_results = analyze_business_request(query)
                insights = generate_business_insights(query_results, query)
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": insights
                        }
                    ]
                }
            
            elif tool_name == "get_revenue_summary":
                data = execute_revenue_query(arguments.get("start_date"))
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(data, indent=2, default=str)
                        }
                    ]
                }
            
            elif tool_name == "get_product_performance":
                data = execute_product_query(
                    arguments.get("start_date"),
                    arguments.get("category")
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(data, indent=2, default=str)
                        }
                    ]
                }
            
            elif tool_name == "get_customer_orders":
                data = execute_customer_query(
                    arguments.get("start_date"),
                    arguments.get("min_amount")
                )
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": json.dumps(data, indent=2, default=str)
                        }
                    ]
                }
            
            else:
                raise ValueError(f"Unknown tool: {tool_name}")
                
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error executing {tool_name}: {str(e)}"
                    }
                ],
                "isError": True
            }
    
    def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Process MCP JSON-RPC request"""
        method = request.get("method")
        params = request.get("params", {})
        request_id = request.get("id")
        
        try:
            if method == "initialize":
                result = self.handle_initialize(params)
            elif method == "tools/list":
                result = self.handle_tools_list()
            elif method == "tools/call":
                result = self.handle_tools_call(params)
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

def handler(event: Dict[str, Any], context) -> Dict[str, Any]:
    """Lambda handler for MCP protocol"""
    
    try:
        # Parse request body
        if isinstance(event.get("body"), str):
            body = json.loads(event["body"])
        else:
            body = event
        
        # Check if this is an MCP request
        if "jsonrpc" in body:
            # Handle MCP protocol
            mcp_server = MCPServer()
            response_body = mcp_server.process_request(body)
        else:
            # Fallback to original handler for backward compatibility
            from query_agent_handler import agentic_handler
            return agentic_handler(event, context)
        
        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps(response_body)
        }
        
    except Exception as e:
        print(f"Handler error: {str(e)}")
        return {
            "statusCode": 200,  # MCP expects 200 even for errors
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*"
            },
            "body": json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": f"Internal error: {str(e)}"
                },
                "id": None
            })
        }
