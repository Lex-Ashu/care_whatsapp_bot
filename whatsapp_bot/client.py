import requests
import logging
from django.conf import settings
from utils.rate_limiter import rate_limited
from utils.constants import WhatsAppAPI

logger = logging.getLogger('whatsapp_bot')

class WhatsAppClient:
    
    def __init__(self):
        self.access_token = settings.WHATSAPP_BUSINESS_API['ACCESS_TOKEN']
        self.phone_number_id = settings.WHATSAPP_BUSINESS_API['PHONE_NUMBER_ID']
        self.api_version = settings.WHATSAPP_BUSINESS_API['API_VERSION']
        self.base_url = settings.WHATSAPP_BUSINESS_API['BASE_URL']
        self.headers = {
            'Authorization': f'Bearer {self.access_token}',
            'Content-Type': 'application/json',
        }

    @rate_limited('whatsapp_send')
    def send_message(self, to_phone_number, message_text):

        if len(message_text) > WhatsAppAPI.MAX_TEXT_LENGTH:
            error_msg = f"Message text exceeds maximum length of {WhatsAppAPI.MAX_TEXT_LENGTH} characters"
            logger.error(error_msg)
            raise ValueError(error_msg)
            
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone_number,
                "type": WhatsAppAPI.MESSAGE_TYPE_TEXT,
                "text": {
                    "body": message_text
                }
            }
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Message sent successfully to {to_phone_number}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending message to {to_phone_number}: {str(e)}")
            raise

    @rate_limited('whatsapp_send')
    def send_template_message(self, to_phone_number, template_name, language_code="en"):
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone_number,
                "type": WhatsAppAPI.MESSAGE_TYPE_TEMPLATE,
                "template": {
                    "name": template_name,
                    "language": {
                        "code": language_code
                    }
                }
            }
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Template message sent to {to_phone_number}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending template message to {to_phone_number}: {str(e)}")
            raise

    @rate_limited('whatsapp_send')
    def send_interactive_message(self, to_phone_number, message_text, buttons):

        if len(message_text) > WhatsAppAPI.MAX_TEXT_LENGTH:
            error_msg = f"Message text exceeds maximum length of {WhatsAppAPI.MAX_TEXT_LENGTH} characters"
            logger.error(error_msg)
            raise ValueError(error_msg)
            

        if len(buttons) > WhatsAppAPI.MAX_BUTTONS:
            logger.warning(f"More than {WhatsAppAPI.MAX_BUTTONS} buttons provided, truncating to {WhatsAppAPI.MAX_BUTTONS}")
            buttons = buttons[:WhatsAppAPI.MAX_BUTTONS]
            
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            interactive_buttons = []
            for i, button in enumerate(buttons):
                interactive_buttons.append({
                    "type": "reply",
                    "reply": {
                        "id": f"btn_{i}_{button['id']}",
                        "title": button['title']
                    }
                })
            payload = {
                "messaging_product": "whatsapp",
                "to": to_phone_number,
                "type": WhatsAppAPI.MESSAGE_TYPE_INTERACTIVE,
                "interactive": {
                    "type": "button",
                    "body": {
                        "text": message_text
                    },
                    "action": {
                        "buttons": interactive_buttons
                    }
                }
            }
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.info(f"Interactive message sent to {to_phone_number}")
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error sending interactive message to {to_phone_number}: {str(e)}")
            raise

    @rate_limited('whatsapp_status')
    def mark_message_as_read(self, message_id):

        if not message_id:
            logger.warning("Attempted to mark message as read with empty message_id")
            return False
            
        try:
            url = f"{self.base_url}/{self.phone_number_id}/messages"
            payload = {
                "messaging_product": "whatsapp",
                "status": "read",
                "message_id": message_id
            }
            response = requests.post(url, json=payload, headers=self.headers)
            response.raise_for_status()
            logger.debug(f"Message {message_id} marked as read")
            return True
        except requests.exceptions.RequestException as e:
            logger.error(f"Error marking message as read: {str(e)}")
            return False
