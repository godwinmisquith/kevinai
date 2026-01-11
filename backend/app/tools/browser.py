"""Browser automation tool using Playwright."""

import base64
from typing import Any, Dict, Optional
from app.tools.base import BaseTool


class BrowserTool(BaseTool):
    """Tool for browser automation."""

    name = "browser"
    description = "Automate browser interactions"

    def __init__(self):
        self.browser = None
        self.context = None
        self.pages: Dict[int, Any] = {}
        self.current_tab = 0
        self._initialized = False

    async def _ensure_browser(self) -> None:
        """Ensure browser is initialized."""
        if not self._initialized:
            try:
                from playwright.async_api import async_playwright

                self._playwright = await async_playwright().start()
                self.browser = await self._playwright.chromium.launch(headless=True)
                self.context = await self.browser.new_context(
                    viewport={"width": 1280, "height": 720}
                )
                self._initialized = True
            except Exception as e:
                raise RuntimeError(f"Failed to initialize browser: {e}")

    async def _get_page(self, tab_idx: Optional[int] = None) -> Any:
        """Get or create a page for the given tab index."""
        await self._ensure_browser()

        idx = tab_idx if tab_idx is not None else self.current_tab

        if idx not in self.pages:
            self.pages[idx] = await self.context.new_page()

        self.current_tab = idx
        return self.pages[idx]

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a browser operation."""
        operations = {
            "navigate": self.navigate,
            "click": self.click,
            "type": self.type_text,
            "scroll": self.scroll,
            "screenshot": self.screenshot,
            "view": self.view_page,
            "console": self.get_console,
            "close": self.close_tab,
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        return await operations[operation](**kwargs)

    async def navigate(
        self, url: str, tab_idx: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Navigate to a URL."""
        try:
            page = await self._get_page(tab_idx)
            await page.goto(url, wait_until="domcontentloaded", timeout=30000)

            return {
                "success": True,
                "url": page.url,
                "title": await page.title(),
                "tab_idx": self.current_tab,
            }
        except Exception as e:
            return {"error": str(e)}

    async def click(
        self,
        selector: Optional[str] = None,
        coordinates: Optional[str] = None,
        tab_idx: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Click an element."""
        try:
            page = await self._get_page(tab_idx)

            if selector:
                await page.click(selector, timeout=10000)
            elif coordinates:
                x, y = map(float, coordinates.split(","))
                await page.mouse.click(x, y)
            else:
                return {"error": "Either selector or coordinates required"}

            return {"success": True, "message": "Click performed"}
        except Exception as e:
            return {"error": str(e)}

    async def type_text(
        self,
        content: str,
        selector: Optional[str] = None,
        press_enter: bool = False,
        tab_idx: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Type text into an element."""
        try:
            page = await self._get_page(tab_idx)

            if selector:
                await page.fill(selector, content)
            else:
                await page.keyboard.type(content)

            if press_enter:
                await page.keyboard.press("Enter")

            return {"success": True, "message": f"Typed: {content[:50]}..."}
        except Exception as e:
            return {"error": str(e)}

    async def scroll(
        self,
        direction: str = "down",
        amount: int = 500,
        selector: Optional[str] = None,
        tab_idx: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Scroll the page or an element."""
        try:
            page = await self._get_page(tab_idx)

            delta = amount if direction == "down" else -amount

            if selector:
                element = await page.query_selector(selector)
                if element:
                    await element.evaluate(f"el => el.scrollBy(0, {delta})")
            else:
                await page.mouse.wheel(0, delta)

            return {"success": True, "message": f"Scrolled {direction} by {amount}px"}
        except Exception as e:
            return {"error": str(e)}

    async def screenshot(
        self,
        full_page: bool = False,
        tab_idx: Optional[int] = None,
        path: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Take a screenshot."""
        try:
            page = await self._get_page(tab_idx)

            screenshot_bytes = await page.screenshot(full_page=full_page)

            if path:
                with open(path, "wb") as f:
                    f.write(screenshot_bytes)
                return {"success": True, "path": path}

            # Return base64 encoded screenshot
            return {
                "success": True,
                "screenshot": base64.b64encode(screenshot_bytes).decode("utf-8"),
                "format": "base64",
            }
        except Exception as e:
            return {"error": str(e)}

    async def view_page(
        self, tab_idx: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Get the current page state."""
        try:
            page = await self._get_page(tab_idx)

            # Get page info
            url = page.url
            title = await page.title()

            # Get simplified HTML structure
            html = await page.content()

            # Take a screenshot
            screenshot_bytes = await page.screenshot()
            screenshot_b64 = base64.b64encode(screenshot_bytes).decode("utf-8")

            return {
                "url": url,
                "title": title,
                "html_length": len(html),
                "screenshot": screenshot_b64,
                "tab_idx": self.current_tab,
            }
        except Exception as e:
            return {"error": str(e)}

    async def get_console(
        self,
        code: Optional[str] = None,
        tab_idx: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Execute JavaScript in the browser console."""
        try:
            page = await self._get_page(tab_idx)

            if code:
                result = await page.evaluate(code)
                return {"success": True, "result": result}

            return {"success": True, "message": "Console ready"}
        except Exception as e:
            return {"error": str(e)}

    async def close_tab(
        self, tab_idx: Optional[int] = None, **kwargs: Any
    ) -> Dict[str, Any]:
        """Close a browser tab."""
        try:
            idx = tab_idx if tab_idx is not None else self.current_tab

            if idx in self.pages:
                await self.pages[idx].close()
                del self.pages[idx]

            return {"success": True, "message": f"Tab {idx} closed"}
        except Exception as e:
            return {"error": str(e)}

    async def close(self) -> None:
        """Close the browser."""
        if self.browser:
            await self.browser.close()
        if hasattr(self, "_playwright"):
            await self._playwright.stop()
        self._initialized = False
