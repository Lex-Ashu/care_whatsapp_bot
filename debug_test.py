#!/usr/bin/env python3

import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

token = os.getenv('WHATSAPP_ACCESS_TOKEN')
print(f'Token: {token[:20]}...')

url = 'https://graph.facebook.com/v22.0/651347521403933/messages'
headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

payload = {
    'messaging_product': 'whatsapp',
    'to': '918767341918',
    'type': 'template',
    'template': {
        'name': 'hello_world',
        'language': {
            'code': 'en_US'
        }
    }
}

print(f'URL: {url}')
print(f'Headers: {headers}')
print(f'Payload: {payload}')

response = requests.post(url, json=payload, headers=headers)
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')