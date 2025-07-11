#!/usr/bin/env python3
import os
import django


os.environ.setdefault("DJANGO_SETTINGS_MODULE", "care_im_bot.settings")
django.setup()

from django.conf import settings

print(f'Token from Django settings: {settings.WHATSAPP_BUSINESS_API["ACCESS_TOKEN"][:20]}...')
print(f'Direct env var: {os.environ.get("WHATSAPP_ACCESS_TOKEN", "NOT_FOUND")[:20]}...')
print(f'Phone number from Django: {settings.WHATSAPP_BUSINESS_API["PHONE_NUMBER_ID"]}')
print(f'API version from Django: {settings.WHATSAPP_BUSINESS_API["API_VERSION"]}')