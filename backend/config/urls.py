from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('identity.urls')),
    path('api/', include('core.urls')),
    path('api/accounts/', include('accounts.urls')),
    path('api/notifications/', include('notifications.urls')),
]
