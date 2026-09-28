from django.contrib import admin

from .models import Account


@admin.register(Account)
class AccountAdmin(admin.ModelAdmin):
    list_display = ('account_number', 'owner', 'currency', 'balance', 'status', 'created_at')
    list_filter = ('currency', 'status')
    search_fields = ('account_number', 'owner__username')