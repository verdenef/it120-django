"""
Textbee SMS Gateway Service Client.

Handles secure communication with the Textbee REST API (https://api.textbee.dev)
to dispatch SMS messages without leaking credentials or allowing unhandled network
exceptions to bubble up into 500 errors.
"""

from dataclasses import dataclass
import logging
from typing import Any, Dict, Optional

from django.conf import settings
import requests

logger = logging.getLogger(__name__)


@dataclass
class TextbeeResult:
    """Structured result returned by Textbee service operations."""

    success: bool
    message_id: Optional[str] = None
    error_message: Optional[str] = None
    status_code: Optional[int] = None
    raw_response: Optional[Dict[str, Any]] = None


def send_sms(
    recipient: str,
    message: str,
    api_key: Optional[str] = None,
    device_id: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: int = 10,
) -> TextbeeResult:
    """
    Send an SMS message via the Textbee REST API gateway.

    Args:
        recipient: Phone number of the recipient (e.g. +639171234567).
        message: Body of the text message.
        api_key: Textbee API key (defaults to settings.TEXTBEE_API_KEY).
        device_id: Optional Android device ID (defaults to settings.TEXTBEE_DEVICE_ID).
        base_url: Base endpoint URL (defaults to settings.TEXTBEE_BASE_URL).
        timeout: Request timeout in seconds (default: 10).

    Returns:
        TextbeeResult with delivery outcome, status code, and parsed details.
    """
    if api_key is None:
        api_key = getattr(settings, "TEXTBEE_API_KEY", "") if settings.configured else ""
    if device_id is None:
        device_id = getattr(settings, "TEXTBEE_DEVICE_ID", "") if settings.configured else ""
    if base_url is None:
        base_url = (
            getattr(settings, "TEXTBEE_BASE_URL", "https://api.textbee.dev/api/v1")
            if settings.configured
            else "https://api.textbee.dev/api/v1"
        )

    api_key = (api_key or "").strip()
    device_id = (device_id or "").strip()
    base_url = (base_url or "").strip().rstrip("/")

    if not api_key:
        return TextbeeResult(
            success=False,
            error_message="Textbee API key is not configured. Please check your .env settings.",
        )

    if not recipient or not recipient.strip():
        return TextbeeResult(
            success=False,
            error_message="Recipient phone number cannot be empty.",
        )

    if not message or not message.strip():
        return TextbeeResult(
            success=False,
            error_message="SMS message content cannot be empty.",
        )

    endpoint = f"{base_url}/gateway/send-sms"
    payload: Dict[str, Any] = {
        "recipients": [recipient.strip()],
        "message": message,
    }
    if device_id:
        payload["deviceId"] = device_id

    headers = {
        "x-api-key": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(endpoint, json=payload, headers=headers, timeout=timeout)
        try:
            data = response.json()
        except Exception:
            data = {}

        if response.status_code in (200, 201):
            batch_id = (
                data.get("smsBatchId")
                or data.get("_id")
                or data.get("id")
                or data.get("batchId")
            )
            return TextbeeResult(
                success=True,
                message_id=str(batch_id) if batch_id is not None else None,
                status_code=response.status_code,
                raw_response=data,
            )

        if response.status_code == 401:
            return TextbeeResult(
                success=False,
                status_code=401,
                error_message="Authentication failed: Invalid Textbee API key.",
                raw_response=data,
            )

        if response.status_code == 429:
            return TextbeeResult(
                success=False,
                status_code=429,
                error_message="Rate limit exceeded or insufficient credits.",
                raw_response=data,
            )

        error_detail = (
            data.get("message")
            or data.get("error")
            or f"Gateway returned HTTP {response.status_code}."
        )
        return TextbeeResult(
            success=False,
            status_code=response.status_code,
            error_message=str(error_detail),
            raw_response=data,
        )

    except requests.exceptions.Timeout:
        logger.warning("Textbee gateway request timed out after %s seconds", timeout)
        return TextbeeResult(
            success=False,
            error_message="The request to Textbee gateway timed out. Please try again.",
        )
    except requests.exceptions.ConnectionError:
        logger.warning("Failed to connect to Textbee gateway at %s", endpoint)
        return TextbeeResult(
            success=False,
            error_message="Unable to reach Textbee gateway. Please check internet connectivity.",
        )
    except requests.exceptions.RequestException as exc:
        logger.error("Textbee request exception: %s", exc.__class__.__name__)
        return TextbeeResult(
            success=False,
            error_message=f"Network error communicating with Textbee gateway: {exc.__class__.__name__}",
        )
    except Exception as exc:
        logger.error("Unexpected error in Textbee service: %s", exc.__class__.__name__)
        return TextbeeResult(
            success=False,
            error_message=f"Unexpected error: {exc.__class__.__name__}",
        )
