from django.contrib import admin

from .models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('kind', 'recipient', 'transaction', 'read_at', 'created_at')
    list_filter = ('kind', 'read_at')
    search_fields = ('recipient__username', 'message')