import logging

import httpx

from services.hubspot_integration_service.app.core.config import settings

logger = logging.getLogger(__name__)


class HubSpotClient:
    """Client for communicating with the HubSpot CRM API."""

    def __init__(self) -> None:
        self.base_url = settings.hubspot_api_base_url.rstrip("/")
        self.access_token = settings.hubspot_access_token

    async def get_contacts(self) -> list[dict]:
        """Retrieve all contacts from HubSpot using pagination."""
        if not self.access_token:
            raise RuntimeError("HUBSPOT_ACCESS_TOKEN is not configured")

        url = f"{self.base_url}/crm/v3/objects/contacts"

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
        }

        params = {
            "limit": 100,
            "properties": "email,firstname,lastname,createdate,lastmodifieddate",
        }

        contacts: list[dict] = []

        async with httpx.AsyncClient(timeout=30.0) as client:
            while True:
                try:
                    response = await client.get(
                        url,
                        headers=headers,
                        params=params,
                    )
                    response.raise_for_status()
                except httpx.HTTPStatusError as exc:
                    status_code = exc.response.status_code

                    if status_code == 401 or status_code == 403:
                        logger.error(
                            "HubSpot authentication or permission error: HTTP %s",
                            status_code,
                        )
                    elif status_code == 429:
                        logger.error("HubSpot rate limit reached: HTTP 429")
                    elif status_code >= 500:
                        logger.error(
                            "HubSpot server error: HTTP %s",
                            status_code,
                        )
                    else:
                        logger.error(
                            "HubSpot API request failed: HTTP %s",
                            status_code,
                        )

                    raise
                except httpx.RequestError:
                    logger.exception("Unable to connect to the HubSpot API")
                    raise

                payload = response.json()

                for item in payload.get("results", []):
                    properties = item.get("properties", {})

                    contacts.append(
                        {
                            "hubspot_id": item["id"],
                            "email": properties.get("email"),
                            "firstname": properties.get("firstname"),
                            "lastname": properties.get("lastname"),
                            "created_at": properties.get("createdate"),
                            "updated_at": properties.get("lastmodifieddate"),
                        }
                    )

                next_page = payload.get("paging", {}).get("next", {})
                after = next_page.get("after")

                if not after:
                    break

                params["after"] = after

        return contacts
