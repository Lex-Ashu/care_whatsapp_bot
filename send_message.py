#!/usr/bin/env python

import os
import sys
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "care_im_bot.settings")
django.setup()

from whatsapp_bot.client import WhatsAppClient

def send_whatsapp_template_message(to_number, template_name="hello_world", language_code="en_US"):
    """
    Send a WhatsApp template message to a specific number
    
    Args:
        to_number: The recipient's phone number (with country code, no + symbol)
        template_name: The name of the template to send (default: hello_world)
        language_code: The language code for the template (default: en_US)
    """
    try:
    
        if not to_number.isdigit():
            to_number = to_number.replace("+", "")
            
        client = WhatsAppClient()
        response = client.send_template_message(to_number, template_name, language_code)
        print(f"Template message sent successfully to {to_number}")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"Error sending template message: {str(e)}")
        return False

def send_whatsapp_text_message(to_number, message):
    """
    Send a WhatsApp text message to a specific number
    
    Args:
        to_number: The recipient's phone number (with country code, no + symbol)
        message: The message text to send
    """
    try:
    
        if not to_number.isdigit():
            to_number = to_number.replace("+", "")
            
        client = WhatsAppClient()
        response = client.send_message(to_number, message)
        print(f"Text message sent successfully to {to_number}")
        print(f"Response: {response}")
        return True
    except Exception as e:
        print(f"Error sending text message: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python send_message.py <phone_number> [message_type] [message/template_name]")
        print("Examples:")
        print("  python send_message.py 918767341918 template hello_world")
        print("  python send_message.py 918767341918 text 'Hello from CARE Bot!'")
        print("  python send_message.py 918767341918  # Sends hello_world template by default")
        sys.exit(1)
        
    phone_number = sys.argv[1]
    
    # Default to template message with hello_world
    if len(sys.argv) == 2:
        send_whatsapp_template_message(phone_number)
    elif len(sys.argv) >= 3:
        message_type = sys.argv[2]
        if message_type == "template":
            template_name = sys.argv[3] if len(sys.argv) > 3 else "hello_world"
            send_whatsapp_template_message(phone_number, template_name)
        elif message_type == "text":
            if len(sys.argv) < 4:
                print("Error: Text message requires message content")
                sys.exit(1)
            message = sys.argv[3]
            send_whatsapp_text_message(phone_number, message)
        else:
            print(f"Unknown message type: {message_type}. Use 'template' or 'text'")
            sys.exit(1)