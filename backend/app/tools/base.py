"""Base tool class."""

from abc import ABC, abstractmethod
from typing import Any, Dict
import time


class BaseTool(ABC):
    """Base class for all tools."""

    name: str = "base_tool"
    description: str = "Base tool"

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute the tool with given parameters."""
        pass

    async def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Run the tool and measure execution time."""
        start_time = time.time()
        try:
            result = await self.execute(**kwargs)
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": True,
                "result": result,
                "execution_time_ms": execution_time,
            }
        except Exception as e:
            execution_time = (time.time() - start_time) * 1000
            return {
                "success": False,
                "error": str(e),
                "execution_time_ms": execution_time,
            }
