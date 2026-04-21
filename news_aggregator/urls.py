from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.news import views as news_views

handler404 = 'apps.news.views.custom_404'
handler500 = 'apps.news.views.custom_500'

urlpatterns = [

    path('admin/', admin.site.urls),  
    path('', include('apps.news.urls')),
    path('accounts/', include('apps.accounts.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
