from rest_framework import serializers

from .models import Account


class AccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = Account
        fields = ['id', 'account_number', 'currency', 'balance', 'status', 'created_at']
        read_only_fields = ['id', 'account_number', 'balance', 'status', 'created_at']