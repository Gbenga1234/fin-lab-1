from rest_framework import viewsets
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Transaction
from .serializers import TransactionSerializer
from .tasks import process_transaction


@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    return Response({'status': 'ok'})


class TransactionViewSet(viewsets.ModelViewSet):
    serializer_class = TransactionSerializer

    def get_queryset(self):
        return Transaction.objects.filter(owner=self.request.user).order_by('-created_at')

    def perform_create(self, serializer):
        transaction = serializer.save(owner=self.request.user)
        process_transaction.delay(transaction.id)
