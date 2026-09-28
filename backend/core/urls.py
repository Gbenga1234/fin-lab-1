from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import TransactionViewSet, health_check

router = DefaultRouter()
router.register('transactions', TransactionViewSet, basename='transaction')

urlpatterns = [
    path('health/', health_check, name='health-check'),
    path('', include(router.urls)),
]
