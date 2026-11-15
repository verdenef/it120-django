"""
Service layer for sms_app.

Integrates external gateway providers such as Textbee.
"""

from .textbee import TextbeeResult, send_sms

__all__ = ["TextbeeResult", "send_sms"]
