"""LLM Service for AI reasoning and tool calling."""

import json
from typing import Any, Dict, List, Optional, AsyncGenerator
from app.config import settings
from app.models.tool import TOOL_DEFINITIONS
from app.services.model_router import model_router, ModelTier


class LLMService:
    """Service for interacting with LLM providers."""

    def __init__(self):
        self.openai_client = None
        self.anthropic_client = None
        self.model_router = model_router
        self._init_clients()

    def _init_clients(self) -> None:
        """Initialize LLM clients."""
        if settings.openai_api_key:
            try:
                from openai import AsyncOpenAI

                self.openai_client = AsyncOpenAI(api_key=settings.openai_api_key)
            except ImportError:
                pass

        if settings.anthropic_api_key:
            try:
                from anthropic import AsyncAnthropic

                self.anthropic_client = AsyncAnthropic(api_key=settings.anthropic_api_key)
            except ImportError:
                pass

    def get_system_prompt(self) -> str:
        """Get the system prompt for Kevin AI."""
        return """You are Kevin AI, a virtual AI software engineer assistant. You help users with software development tasks including:

- Understanding and navigating code
- Writing and editing code
- Running shell commands
- Managing git repositories
- Searching the web for documentation
- Automating browser interactions
- Managing tasks and todos

You have access to various tools to accomplish these tasks. Use them wisely and efficiently.

Core Principles:
1. Be thorough and persistent - complete tasks fully
2. Use tools to explore and understand before making changes
3. Always read files before editing them
4. Test your changes when possible
5. Communicate clearly with the user
6. Break complex tasks into smaller steps using the todo list

When working on tasks:
1. First understand the request fully
2. Create a plan using the todo_write tool
3. Execute the plan step by step
4. Update todo status as you progress
5. Report completion to the user

Be concise in your responses. Focus on actions and results rather than explanations."""

    async def chat_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
        stream: bool = False,
        session_id: Optional[str] = None,
        force_tier: Optional[ModelTier] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Get a chat completion from the LLM with intelligent model routing."""
        tools = tools or TOOL_DEFINITIONS

        # Get the last user message for task classification
        last_user_message = ""
        for msg in reversed(messages):
            if msg.get("role") == "user":
                last_user_message = msg.get("content", "")
                break

        # Use model router to select appropriate model if not specified
        if model is None:
            selected_model, tier, category = self.model_router.select_model(
                message=last_user_message,
                context=context,
                force_tier=force_tier,
            )
            model = selected_model
            max_tokens = self.model_router.get_max_tokens_for_tier(tier)
        else:
            max_tokens = settings.max_tokens

        # Add system prompt if not present
        if not messages or messages[0].get("role") != "system":
            messages = [{"role": "system", "content": self.get_system_prompt()}] + messages

        if self.openai_client and "gpt" in model.lower():
            result = await self._openai_completion(messages, tools, model, stream, max_tokens)
        elif self.anthropic_client and "claude" in model.lower():
            result = await self._anthropic_completion(messages, tools, model, stream, max_tokens)
        else:
            # Fallback to mock response for demo
            result = self._mock_completion(messages)

        # Track usage if session_id provided and cost tracking enabled
        if session_id and settings.enable_cost_tracking:
            input_tokens = result.get("usage", {}).get("input_tokens", 0)
            output_tokens = result.get("usage", {}).get("output_tokens", 0)
            if input_tokens or output_tokens:
                self.model_router.track_usage(session_id, model, input_tokens, output_tokens)

        # Add model info to result
        result["model_used"] = model

        return result

    async def _openai_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        model: str,
        _stream: bool,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get completion from OpenAI."""
        try:
            response = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                tool_choice="auto",
                max_tokens=max_tokens or settings.max_tokens,
                temperature=settings.temperature,
            )

            message = response.choices[0].message

            result: Dict[str, Any] = {
                "role": "assistant",
                "content": message.content or "",
            }

            if message.tool_calls:
                result["tool_calls"] = [
                    {
                        "id": tc.id,
                        "type": "function",
                        "function": {
                            "name": tc.function.name,
                            "arguments": tc.function.arguments,
                        },
                    }
                    for tc in message.tool_calls
                ]

            # Add usage information for cost tracking
            if response.usage:
                result["usage"] = {
                    "input_tokens": response.usage.prompt_tokens,
                    "output_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                }

            return result
        except Exception as e:
            return {"role": "assistant", "content": f"Error: {str(e)}"}

    async def _anthropic_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        model: str,
        _stream: bool,
        max_tokens: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Get completion from Anthropic."""
        try:
            # Convert tools to Anthropic format
            anthropic_tools = []
            for tool in tools:
                if tool.get("type") == "function":
                    func = tool["function"]
                    anthropic_tools.append(
                        {
                            "name": func["name"],
                            "description": func["description"],
                            "input_schema": func["parameters"],
                        }
                    )

            # Extract system message
            system_content = ""
            chat_messages = []
            for msg in messages:
                if msg["role"] == "system":
                    system_content = msg["content"]
                else:
                    chat_messages.append(msg)

            response = await self.anthropic_client.messages.create(
                model=model,
                max_tokens=max_tokens or settings.max_tokens,
                system=system_content,
                messages=chat_messages,
                tools=anthropic_tools,
            )

            # Convert response to standard format
            result: Dict[str, Any] = {"role": "assistant", "content": ""}

            tool_calls = []
            for block in response.content:
                if block.type == "text":
                    result["content"] = block.text
                elif block.type == "tool_use":
                    tool_calls.append(
                        {
                            "id": block.id,
                            "type": "function",
                            "function": {
                                "name": block.name,
                                "arguments": json.dumps(block.input),
                            },
                        }
                    )

            if tool_calls:
                result["tool_calls"] = tool_calls

            # Add usage information for cost tracking
            if response.usage:
                result["usage"] = {
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                    "total_tokens": response.usage.input_tokens + response.usage.output_tokens,
                }

            return result
        except Exception as e:
            return {"role": "assistant", "content": f"Error: {str(e)}"}

    def _mock_completion(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Mock completion for demo/testing."""
        last_message = messages[-1].get("content", "") if messages else ""

        # Simple response logic for demo
        if "hello" in last_message.lower():
            return {
                "role": "assistant",
                "content": "Hello! I'm Kevin AI, your virtual software engineer. How can I help you today?",
            }
        elif "todo" in last_message.lower() or "task" in last_message.lower():
            return {
                "role": "assistant",
                "content": "I'll help you manage your tasks.",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "function": {
                            "name": "todo_write",
                            "arguments": json.dumps(
                                {
                                    "todos": [
                                        {"content": "Analyze the request", "status": "in_progress"},
                                        {"content": "Create implementation plan", "status": "pending"},
                                    ]
                                }
                            ),
                        },
                    }
                ],
            }
        else:
            return {
                "role": "assistant",
                "content": f"I understand you want help with: {last_message[:100]}. Let me assist you with that. Note: For full functionality, please configure an API key (OpenAI or Anthropic) in the .env file.",
            }

    async def stream_completion(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        model: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream a chat completion."""
        model = model or settings.default_model

        if self.openai_client and "gpt" in model.lower():
            async for chunk in self._stream_openai(messages, tools, model):
                yield chunk
        else:
            # Non-streaming fallback
            response = await self.chat_completion(messages, tools, model)
            yield json.dumps(response)

    async def _stream_openai(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]],
        model: str,
    ) -> AsyncGenerator[str, None]:
        """Stream from OpenAI."""
        try:
            stream = await self.openai_client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools or TOOL_DEFINITIONS,
                tool_choice="auto",
                max_tokens=settings.max_tokens,
                temperature=settings.temperature,
                stream=True,
            )

            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    yield chunk.choices[0].delta.content
        except Exception as e:
            yield f"Error: {str(e)}"
