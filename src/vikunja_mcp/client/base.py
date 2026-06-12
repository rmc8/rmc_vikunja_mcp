"""Base class for the Vikunja API client."""

from typing import Any, Self

import httpx


class VikunjaClientBase:
    """Core class containing the transport configuration and request runner."""

    base_url: str
    token: str
    headers: dict[str, str]
    client: httpx.AsyncClient

    def __init__(self, base_url: str, token: str) -> None:
        # Normalise the URL: strip trailing slash, ensure /api/v1 suffix.
        base_url = base_url.rstrip("/")
        if not base_url.endswith("/api/v1"):
            self.base_url = f"{base_url}/api/v1"
        else:
            self.base_url = base_url

        self.token = token
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }
        self.client = httpx.AsyncClient(
            headers=self.headers, timeout=30.0
        )

    async def close(self) -> None:
        """Close the underlying HTTP transport."""
        await self.client.aclose()

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: object,
        exc_val: object,
        exc_tb: object,
    ) -> None:
        await self.close()

    async def _request(
        self, method: str, path: str, **kwargs: Any
    ) -> Any:
        """Send an HTTP request and return the parsed JSON body.

        Args:
            method: HTTP method (``GET``, ``POST``, ``PUT``, ``DELETE``).
            path:   API path relative to ``/api/v1/``.
            **kwargs: Forwarded to :meth:`httpx.AsyncClient.request`.
        """
        url = f"{self.base_url}/{path.lstrip('/')}"
        try:
            response = await self.client.request(method, url, **kwargs)
            response.raise_for_status()
            if response.status_code == 204:
                return {}
            return response.json()
        except httpx.HTTPStatusError as e:
            try:
                error_detail = e.response.json()
                message = error_detail.get("message", str(e))
            except Exception:
                message = e.response.text or str(e)
            raise ValueError(
                f"Vikunja API Error ({e.response.status_code}): {message}"
            ) from e
        except httpx.RequestError as e:
            raise ConnectionError(
                f"Failed to connect to Vikunja server: {e}"
            ) from e
