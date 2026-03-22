from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),

    # Django built-in auth
    path('accounts/', include('django.contrib.auth.urls')),

    # ⭐ CONNECT YOUR APP (THIS FIXES EVERYTHING)
    path('', include('finance.urls')),
]

# Media files (uploads)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)