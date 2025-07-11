#!/usr/bin/env python3
import requests
import json

# Direct token from your curl command
token = 'EAFYi1HZB6eFQBPBIGeuwarpTvf1zzkzyK07cCJECkZCeRLNcoW6xzET7K7tYyWcWyhRPNZA6u2BIK3GCPDF4rSb4SVFxUaJaCHv8CJ5HYbJRAynTQZCog6iQze6XkvHgHHsJbpWPfLagqMfHmnMtknrwOcjsVRp2GL5ap4kCj7iPVbBYH0ssxlyzVgUHiHlPvdlOWWgIkNnUppqeTLQRtXVZA5jSzh57pcxk2OadmrDMJIgZDZD'

print(f'Token prefix: {token[:20]}')

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

response = requests.post(url, headers=headers, json=payload)
print(f'Status: {response.status_code}')
print(f'Response: {response.text}')

if response.status_code == 200:
    print('✅ Message sent successfully!')
else:
    print('❌ Failed to send message')