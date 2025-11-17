"""Sophos Central Alerts API client.

This module provides the AlertsAPI class for managing alerts including
listing, filtering, and performing actions on alerts.
"""

from typing import Any

from pysophoscentralapi.api.common.models import (
    Alert,
    AlertActionRequest,
    AlertFilters,
)
from pysophoscentralapi.core.client import HTTPClient
from pysophoscentralapi.core.models import PaginatedResponse
from pysophoscentralapi.core.pagination import Paginator, create_paginator


class AlertsAPI:
    """Sophos Central Alerts API client.

    Provides methods for managing alerts including listing, filtering,
    and performing actions.

    Attributes:
        http_client: HTTP client for making API requests
        base_path: Base URL path for alerts API

    Example:
        >>> async with HTTPClient(base_url, auth) as client:
        ...     alerts_api = AlertsAPI(client)
        ...     alerts = await alerts_api.list_alerts()
        ...     for alert in alerts.items:
        ...         print(f"{alert.severity}: {alert.description}")
    """

    def __init__(self, http_client: HTTPClient) -> None:
        """Initialize the Alerts API client.

        Args:
            http_client: HTTP client for API requests
        """
        self.http_client = http_client
        self.base_path = "/common/v1"

    async def list_alerts(
        self,
        filters: AlertFilters | None = None,
    ) -> PaginatedResponse[Alert]:
        """List alerts with optional filtering.

        Args:
            filters: Optional filters to apply to the listing

        Returns:
            Paginated response containing alerts

        Raises:
            ValidationError: If parameters are invalid
            APIError: If API returns an error

        Example:
            >>> from datetime import datetime, timedelta
            >>> filters = AlertFilters(
            ...     severity=["high", "critical"],
            ...     product=["endpoint"],
            ...     from_date=datetime.now() - timedelta(days=7)
            ... )
            >>> result = await api.list_alerts(filters)
            >>> print(f"Found {len(result.items)} alerts")
        """
        if filters is None:
            filters = AlertFilters()

        params = filters.to_params()
        response = await self.http_client.get(f"{self.base_path}/alerts", params)

        # Parse items as Alert models
        items = [Alert(**item) for item in response.get("items", [])]

        return PaginatedResponse[Alert](
            items=items,
            pages=response["pages"],
        )

    async def get_alert(self, alert_id: str) -> Alert:
        """Get a specific alert by ID.

        Args:
            alert_id: The alert ID

        Returns:
            Alert information

        Raises:
            ResourceNotFoundError: If alert not found
            APIError: If API returns an error

        Example:
            >>> alert = await api.get_alert("alert-123")
            >>> print(f"{alert.severity}: {alert.description}")
        """
        response = await self.http_client.get(f"{self.base_path}/alerts/{alert_id}")
        return Alert(**response)

    async def perform_action(
        self,
        alert_id: str,
        action: str,
        message: str | None = None,
    ) -> dict[str, Any]:
        """Perform an action on an alert.

        Args:
            alert_id: The alert ID
            action: Action to perform (e.g., "acknowledge", "clearThreat")
            message: Optional message explaining the action

        Returns:
            Action result

        Raises:
            ValidationError: If action is invalid
            ResourceNotFoundError: If alert not found
            APIError: If API returns an error

        Example:
            >>> result = await api.perform_action(
            ...     "alert-123",
            ...     "acknowledge",
            ...     message="Investigating"
            ... )
        """
        request = AlertActionRequest(action=action, message=message)
        return await self.http_client.post(
            f"{self.base_path}/alerts/{alert_id}/actions",
            json=request.model_dump(by_alias=True, exclude_none=True),
        )

    def paginate_alerts(
        self,
        filters: AlertFilters | None = None,
        max_pages: int | None = None,
    ) -> Paginator[Alert]:
        """Create a paginator for alerts.

        This allows iterating through all alerts across multiple pages.

        Args:
            filters: Optional filters to apply
            max_pages: Maximum number of pages to fetch

        Returns:
            Paginator instance for iterating through alerts

        Example:
            >>> paginator = api.paginate_alerts(
            ...     filters=AlertFilters(severity=["high", "critical"])
            ... )
            >>> async for alert in paginator.iter_items():
            ...     print(f"{alert.severity}: {alert.description}")
        """
        if filters is None:
            filters = AlertFilters()

        async def fetch_page(page_key: str | None) -> PaginatedResponse[Alert]:
            if page_key:
                filters.page_from_key = page_key
            return await self.list_alerts(filters)

        return create_paginator(
            fetch_page,
            page_size=filters.page_size,
            max_pages=max_pages,
        )
