import asyncio
import json


class GitHubMCPClient: 
    def __init__(self, token: str, debug: bool = False):
        self.token = token
        self.process = None
        self.request_id = 0
        self.debug = debug
        
    async def start(self):
        """Runs GitHub MCP server in docker"""
        self.process = await asyncio.create_subprocess_exec(
            "docker", "run", "-i", "--rm",
            "-e", f"GITHUB_PERSONAL_ACCESS_TOKEN={self.token}",
            "ghcr.io/github/github-mcp-server",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("GitHub MCP server running in docker")
        
        await self._initialize()
        
    async def _initialize(self):
        init_request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "gemini-github-agent",
                    "version": "1.0.0"
                }
            }
        }
        
        response = await self._send_request(init_request)
        if self.debug:
            print(f"MCP initialized: {response.get('result', {}).get('serverInfo', {})}")
        
        initialized = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        await self._send_notification(initialized)
        
    def _next_id(self):
        self.request_id += 1
        return self.request_id
        
    async def _send_request(self, request: dict) -> dict:
        request_json = json.dumps(request) + "\n"
        
        if self.debug:
            print(f"\n Request: {request['method']}")
            if 'params' in request:
                print(f"  Params: {json.dumps(request['params'], indent=2)}")
        
        self.process.stdin.write(request_json.encode())
        await self.process.stdin.drain()
        
        response_line = await self.process.stdout.readline()
        if not response_line:
            raise Exception("MCP server didn't respond")
        
        response = json.loads(response_line.decode())
        
        if self.debug:
            if 'error' in response:
                print(f"Error: {response['error']}")
            elif 'result' in response:
                result_preview = str(response['result'])[:200]
                print(f"Result: {result_preview}...")
        
        return response
        
    async def _send_notification(self, notification: dict):
        notification_json = json.dumps(notification) + "\n"
        self.process.stdin.write(notification_json.encode())
        await self.process.stdin.drain()
        
    async def call_tool(self, tool_name: str, arguments: dict) -> dict:
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/call",
            "params": {
                "name": tool_name,
                "arguments": arguments
            }
        }
        
        response = await self._send_request(request)
        
        if "error" in response:
            error_msg = response["error"].get("message", "Unknown error")
            print(f"Tool error: {error_msg}")
            return {"error": error_msg}
        
        return response.get("result", {})
    
    async def list_tools(self) -> list:
        request = {
            "jsonrpc": "2.0",
            "id": self._next_id(),
            "method": "tools/list"
        }
        
        response = await self._send_request(request)
        return response.get("result", {}).get("tools", [])
    
    async def stop(self):
        """Stopping GitHub MCP server container from docker"""
        if self.process:
            self.process.terminate()
            await self.process.wait()