"""User operations for the Vikunja client."""

from vikunja_mcp.client.base import VikunjaClientBase
from vikunja_mcp.models import User


class UserMixin(VikunjaClientBase):
    """Mixin for user-related endpoints."""

    async def get_user_info(self) -> User:
        """Return the authenticated user's profile.

        Useful as a connectivity / auth-token health check.
        """
        data = await self._request("GET", "user")
        return User.model_validate(data)

    async def search_users(self, query: str) -> list[User]:
        """Search for users by username or email fragment.

        Args:
            query: Search term matched against username and email.
        """
        params = {"search": query}
        data = await self._request("GET", "users", params=params)
        return [User.model_validate(item) for item in data]
