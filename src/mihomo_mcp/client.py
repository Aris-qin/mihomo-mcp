"""Async httpx client wrapping mihomo external-controller REST API."""

from __future__ import annotations

import json
from typing import Any

import httpx


class MihomoError(RuntimeError):
    """mihomo returned an error or was unreachable.

    Attributes:
        message: short description of what failed
        hint: actionable suggestion for the user (e.g. "is mihomo running?")
        status_code: HTTP status code if applicable, else None
    """

    def __init__(self, message: str, hint: str = "", status_code: int | None = None) -> None:
        super().__init__(message)
        self.message = message
        self.hint = hint
        self.status_code = status_code

    def to_dict(self) -> dict:
        return {
            "error": self.message,
            "hint": self.hint,
            "status_code": self.status_code,
        }


class MihomoClient:
    """Thin async wrapper around the mihomo external-controller REST API.

    All methods return parsed JSON. Methods raise MihomoError on any failure,
    with a friendly hint. The underlying httpx client is a single shared
    connection pool — reuse the instance across tool calls.
    """

    def __init__(
        self,
        host: str = "127.0.0.1",
        port: int = 9090,
        secret: str = "",
        timeout: float = 10.0,
    ) -> None:
        self.base = f"http://{host}:{port}"
        headers = {"Authorization": f"Bearer {secret}"} if secret else {}
        self._client = httpx.AsyncClient(
            base_url=self.base,
            headers=headers,
            timeout=timeout,
        )

    async def close(self) -> None:
        await self._client.aclose()

    async def __aenter__(self) -> MihomoClient:
        return self

    async def __aexit__(self, *exc: Any) -> None:
        await self.close()

    # ---- internal ----

    async def _request(self, method: str, path: str, **kwargs: Any) -> Any:
        try:
            resp = await self._client.request(method, path, **kwargs)
        except httpx.ConnectError as e:
            raise MihomoError(
                f"cannot connect to mihomo at {self.base}",
                hint="is mihomo running? check `systemctl status mihomo` or `ps aux | grep mihomo`",
            ) from e
        except httpx.TimeoutException as e:
            raise MihomoError(
                f"mihomo at {self.base} timed out",
                hint="mihomo is slow or overloaded; try a higher MIHOMO_TIMEOUT",
            ) from e
        except httpx.HTTPError as e:
            raise MihomoError(f"http error: {e}", hint="check mihomo logs") from e

        if resp.status_code == 204:
            return None
        if resp.status_code >= 400:
            try:
                detail = resp.json().get("message") or resp.text
            except json.JSONDecodeError:
                detail = resp.text
            hint = ""
            if "Forbidden" in detail or "403" in detail:
                hint = "subscription may be expired or external-controller-secret is wrong"
            elif "not exist" in detail:
                hint = "check the proxy/group name — case-sensitive"
            raise MihomoError(
                f"mihomo api {method} {path}: {detail}",
                hint=hint,
                status_code=resp.status_code,
            )

        if not resp.content:
            return None
        try:
            return resp.json()
        except json.JSONDecodeError:
            return resp.text

    # ---- version ----

    async def version(self) -> dict:
        return await self._request("GET", "/version")

    # ---- proxies ----

    async def list_proxies(self) -> dict:
        return await self._request("GET", "/proxies")

    async def get_proxy(self, name: str) -> dict:
        return await self._request("GET", f"/proxies/{name}")

    async def select_proxy(self, name: str, group: str) -> dict:
        return await self._request("PUT", f"/proxies/{group}", json={"name": name})

    async def test_proxy_delay(self, name: str, url: str, timeout_ms: int = 5000) -> dict:
        return await self._request(
            "GET",
            f"/proxies/{name}/delay",
            params={"url": url, "timeout": timeout_ms},
        )

    # ---- providers ----

    async def list_providers(self) -> dict:
        return await self._request("GET", "/providers/proxies")

    async def get_provider(self, name: str) -> dict:
        return await self._request("GET", f"/providers/proxies/{name}")

    async def healthcheck_provider(self, name: str) -> dict:
        return await self._request("GET", f"/providers/proxies/{name}/healthcheck")

    async def update_provider_url(self, name: str, url: str) -> dict:
        """Update provider's subscription URL. The URL is forwarded to mihomo
        and not persisted by this client."""
        return await self._request("PUT", f"/providers/proxies/{name}", json={"url": url})

    # ---- configs ----

    async def get_configs(self) -> dict:
        return await self._request("GET", "/configs")

    async def patch_configs(self, patch: dict) -> dict:
        return await self._request("PATCH", "/configs", json=patch)

    # ---- connections ----

    async def list_connections(self) -> dict:
        return await self._request("GET", "/connections")

    async def close_all_connections(self) -> dict:
        return await self._request("DELETE", "/connections")
