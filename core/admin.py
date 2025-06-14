from django.contrib import admin
from .models import UserSession, BotMessage

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('whatsapp_id', 'user_type', 'current_state', 'is_authenticated', 'last_activity')
    list_filter = ('user_type', 'current_state', 'is_authenticated')
    search_fields = ('whatsapp_id',)
    readonly_fields = ('created_at', 'last_activity')

@admin.register(BotMessage)
class BotMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'message_type', 'timestamp')
    list_filter = ('message_type',)
    search_fields = ('session__whatsapp_id', 'message_content')
    readonly_fields = ('timestamp',)
