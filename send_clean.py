#!/usr/bin/env python3
"""
Clean WhatsApp message sender - bypasses Django completely
Uses the exact same format as the working curl command
"""

import requests
import sys
import os
from dotenv import load_dotenv

def send_whatsapp_message(phone_number, template_name="hello_world", language_code="en_US"):
    """
    Send WhatsApp template message using the exact same format as working curl command
    """
    # Load environment variables
    load_dotenv()
    

    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '651347521403933')
    
    if not access_token:
        print("Error: WHATSAPP_ACCESS_TOKEN not found in .env file")
        return False
    
    # Exact URL format from working curl command
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    
    # Exact headers from working curl command
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    # Exact payload format from working curl command
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "template",
        "template": {
            "name": template_name,
            "language": {
                "code": language_code
            }
        }
    }
    
    print(f"Sending to: {phone_number}")
    print(f"URL: {url}")
    print(f"Token (first 20 chars): {access_token[:20]}...")
    print(f"Payload: {payload}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send message. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

def send_text_message(phone_number, message_text):
    """
    Send WhatsApp text message
    """
    # Load environment variables
    load_dotenv()
    

    access_token = os.getenv('WHATSAPP_ACCESS_TOKEN')
    phone_number_id = os.getenv('WHATSAPP_PHONE_NUMBER_ID', '651347521403933')
    
    if not access_token:
        print("Error: WHATSAPP_ACCESS_TOKEN not found in .env file")
        return False
    
    url = f"https://graph.facebook.com/v22.0/{phone_number_id}/messages"
    
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": phone_number,
        "type": "text",
        "text": {
            "body": message_text
        }
    }
    
    print(f"Sending text to: {phone_number}")
    print(f"Message: {message_text}")
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ Text message sent successfully!")
            return True
        else:
            print(f"❌ Failed to send text message. Status: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        return False

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 send_clean.py <phone_number>                    # Send hello_world template")
        print("  python3 send_clean.py <phone_number> template <name>    # Send specific template")
        print("  python3 send_clean.py <phone_number> text <message>     # Send text message")
        print("")
        print("Examples:")
        print("  python3 send_clean.py 918767341918")
        print("  python3 send_clean.py 918767341918 template hello_world")
        print("  python3 send_clean.py 918767341918 text 'Hello from CARE Bot!'")
        sys.exit(1)
    
    phone_number = sys.argv[1]
    

    phone_number = phone_number.replace("+", "").replace(" ", "")
    
    if len(sys.argv) == 2:
        # Default: send hello_world template
        send_whatsapp_message(phone_number)
    elif len(sys.argv) >= 3:
        message_type = sys.argv[2]
        
        if message_type == "template":
            template_name = sys.argv[3] if len(sys.argv) > 3 else "hello_world"
            send_whatsapp_message(phone_number, template_name)
        elif message_type == "text":
            if len(sys.argv) < 4:
                print("Error: Text message requires message content")
                sys.exit(1)
            message_text = sys.argv[3]
            send_text_message(phone_number, message_text)
        else:
            print(f"Unknown message type: {message_type}. Use 'template' or 'text'")
            sys.exit(1)