#!/usr/bin/env python

import os
import requests
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_whatsapp_token():
    """
    Check if the WhatsApp API token is valid by making a request to the Meta Graph API
    """
    access_token = os.environ.get('WHATSAPP_ACCESS_TOKEN', '')
    phone_number_id = os.environ.get('WHATSAPP_PHONE_NUMBER_ID', '')
    api_version = 'v18.0'
    
    if not access_token or not phone_number_id:
        print("Error: WhatsApp API credentials not found in environment variables.")
        return False
    
    url = f"https://graph.facebook.com/{api_version}/{phone_number_id}"
    params = {
        'fields': 'name,status,phone_numbers',
        'access_token': access_token
    }
    
    try:
        response = requests.get(url, params=params)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("✅ WhatsApp API token is valid!")
            return True
        else:
            print("❌ WhatsApp API token is invalid or expired.")
            return False
    except Exception as e:
        print(f"Error checking token: {str(e)}")
        return False

if __name__ == "__main__":
    check_whatsapp_token()