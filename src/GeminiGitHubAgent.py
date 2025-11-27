from google import genai
from google.genai import types
from GitHubMCPClient import GitHubMCPClient


class GeminiGitHubAgent:
    def __init__(self, mcp_client: GitHubMCPClient, GEN_API_KEY: str, MODEL_ID: str):
        self.mcp_client = mcp_client
        self.client = genai.Client(api_key=GEN_API_KEY)
        self.MODEL_ID = MODEL_ID
        self.tools = []
        
    def _clean_schema(self, schema: dict) -> dict:
        if not isinstance(schema, dict):
            return schema
        
        cleaned = {}
        for key, value in schema.items():
            if key in ["additionalProperties", "additional_properties", "$schema", "$id", "$ref"]:
                continue
            
            if isinstance(value, dict):
                cleaned[key] = self._clean_schema(value)
            elif isinstance(value, list):
                cleaned[key] = [self._clean_schema(item) if isinstance(item, dict) else item for item in value]
            else:
                cleaned[key] = value
        
        return cleaned
    
    async def initialize(self):
        mcp_tools = await self.mcp_client.list_tools()
        
        self.tools = []
        for tool in mcp_tools:
            input_schema = tool.get("inputSchema", {})
            cleaned_schema = self._clean_schema(input_schema)
            
            if "properties" not in cleaned_schema:
                cleaned_schema = {
                    "type": "object",
                    "properties": {},
                    "required": []
                }
            
            try:
                gemini_tool = types.FunctionDeclaration(
                    name=tool["name"],
                    description=tool.get("description", "No description"),
                    parameters=cleaned_schema
                )
                self.tools.append(gemini_tool)
            except Exception as e:
                print(f"Skip tool {tool['name']}: {e}")
        
        print(f"Agent initialized with {len(self.tools)} tools")
        
    async def execute_task(self, task: str) -> str:
        """Execută o sarcină folosind Gemini și MCP tools."""
        
        try:
            response = self.client.models.generate_content(
                model=self.MODEL_ID,
                contents=task,
                config=types.GenerateContentConfig(
                    tools=[types.Tool(function_declarations=self.tools)],
                    temperature=0.7
                )
            )
        except Exception as e:
            return f"An error occured while generating content: {e}"
        
        conversation_history = [
            types.Content(
                role="user",
                parts=[types.Part(text=task)]
            )
        ]
        
        max_iterations = 10
        iteration = 0
        
        while iteration < max_iterations:
            iteration += 1
            print(f"\n--- Iteration {iteration} ---")
            
            if not response.candidates or not response.candidates[0].content.parts:
                print("No response from model")
                break
                
            part = response.candidates[0].content.parts[0]
            
            if hasattr(part, "text") and part.text:
                print(f"Response: {part.text[:100]}...")
                return part.text
            
            if hasattr(part, "function_call") and part.function_call:
                function_call = part.function_call
                print(f"Called tool: {function_call.name}")
                print(f"  Arguments: {dict(function_call.args)}")
                
                try:
                    result = await self.mcp_client.call_tool(
                        function_call.name,
                        dict(function_call.args)
                    )
                    
                    print(f"Tool result: {str(result)[:200]}...")
                except Exception as e:
                    result = {"error": str(e)}
                    print(f"Tool error: {e}")
                
                conversation_history.append(
                    types.Content(
                        role="model",
                        parts=[part]
                    )
                )
                
                conversation_history.append(
                    types.Content(
                        role="user",
                        parts=[types.Part.from_function_response(
                            name=function_call.name,
                            response=result
                        )]
                    )
                )
                
                try:
                    response = self.client.models.generate_content(
                        model=self.MODEL_ID,
                        contents=conversation_history,
                        config=types.GenerateContentConfig(
                            tools=[types.Tool(function_declarations=self.tools)],
                            temperature=0.7
                        )
                    )
                except Exception as e:
                    return f"An error ocurred during conversation: {e}"
            else:
                print("Error, stopping")
                break
        
        if response.candidates and response.candidates[0].content.parts:
            last_part = response.candidates[0].content.parts[0]
            if hasattr(last_part, "text"):
                return last_part.text
        
        return "Iteration limit reached!"