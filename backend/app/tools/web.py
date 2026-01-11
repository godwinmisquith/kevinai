"""Web search and content fetching tools."""

import asyncio
from typing import Any, Dict, List
import httpx
from app.tools.base import BaseTool


class WebTool(BaseTool):
    """Tool for web search and content fetching."""

    name = "web"
    description = "Search the web and fetch content"

    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=30.0,
            follow_redirects=True,
            headers={
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            },
        )

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a web operation."""
        if operation == "search":
            return await self.search(**kwargs)
        elif operation == "get_contents":
            return await self.get_contents(**kwargs)
        else:
            return {"error": f"Unknown operation: {operation}"}

    async def search(
        self,
        query: str,
        num_results: int = 5,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Search the web using DuckDuckGo."""
        try:
            # Use DuckDuckGo HTML search
            url = "https://html.duckduckgo.com/html/"
            data = {"q": query}

            response = await self.client.post(url, data=data)
            response.raise_for_status()

            # Parse results (simplified)
            html = response.text
            results = []

            # Extract result links and titles (basic parsing)
            import re

            # Find result blocks
            result_pattern = r'<a rel="nofollow" class="result__a" href="([^"]+)"[^>]*>([^<]+)</a>'
            matches = re.findall(result_pattern, html)

            for i, (link, title) in enumerate(matches[:num_results]):
                results.append(
                    {
                        "title": title.strip(),
                        "url": link,
                        "snippet": "",
                    }
                )

            return {
                "query": query,
                "results": results,
                "count": len(results),
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_contents(
        self, urls: List[str], **kwargs: Any
    ) -> Dict[str, Any]:
        """Fetch content from URLs."""
        results = []

        async def fetch_url(url: str) -> Dict[str, Any]:
            try:
                response = await self.client.get(url)
                response.raise_for_status()

                content_type = response.headers.get("content-type", "")

                if "text/html" in content_type:
                    # Extract text from HTML
                    html = response.text
                    text = self._extract_text(html)
                    return {
                        "url": url,
                        "success": True,
                        "content": text[:10000],  # Limit content
                        "content_type": content_type,
                    }
                elif "application/json" in content_type:
                    return {
                        "url": url,
                        "success": True,
                        "content": response.text[:10000],
                        "content_type": content_type,
                    }
                else:
                    return {
                        "url": url,
                        "success": True,
                        "content": f"Binary content ({content_type})",
                        "content_type": content_type,
                    }
            except Exception as e:
                return {"url": url, "success": False, "error": str(e)}

        # Fetch all URLs concurrently
        tasks = [fetch_url(url) for url in urls[:10]]  # Limit to 10 URLs
        results = await asyncio.gather(*tasks)

        return {"results": list(results)}

    def _extract_text(self, html: str) -> str:
        """Extract text from HTML."""
        import re

        # Remove script and style elements
        html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL)
        html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)

        # Remove HTML tags
        text = re.sub(r"<[^>]+>", " ", html)

        # Clean up whitespace
        text = re.sub(r"\s+", " ", text)
        text = text.strip()

        return text

    async def close(self) -> None:
        """Close the HTTP client."""
        await self.client.aclose()
