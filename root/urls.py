
from django.contrib import admin
from django.urls import path,include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('authsystem.urls')),
    path('api/payments/',include('payments.urls')),
    path('api/ai/',include('chatapp.urls')),
    path('social/',include('social_auth.urls')),

    
]
