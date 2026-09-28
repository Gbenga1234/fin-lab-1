from rest_framework import serializers

from accounts.models import Account

from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    source_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())
    destination_account = serializers.PrimaryKeyRelatedField(queryset=Account.objects.all())

    class Meta:
        model = Transaction
        fields = [
            'id', 'reference', 'source_account', 'destination_account', 'amount',
            'currency', 'status', 'failure_reason', 'created_at', 'updated_at',
        ]
        read_only_fields = ['currency', 'status', 'failure_reason', 'created_at', 'updated_at']

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError('Transfer amount must be greater than zero.')
        return value

    def validate(self, attrs):
        request_user = self.context['request'].user
        source = attrs['source_account']
        destination = attrs['destination_account']

        if source.owner_id != request_user.id:
            raise serializers.ValidationError({'source_account': 'You do not own this account.'})
        if source.pk == destination.pk:
            raise serializers.ValidationError({'destination_account': 'Choose a different account.'})
        if source.currency != destination.currency:
            raise serializers.ValidationError('Transfers between different currencies are not supported.')
        if source.status != Account.Status.ACTIVE or destination.status != Account.Status.ACTIVE:
            raise serializers.ValidationError('Both accounts must be active.')

        attrs['currency'] = source.currency
        return attrs
