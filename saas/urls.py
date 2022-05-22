from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf import settings
urlpatterns = [
    path('admin/', admin.site.urls),
    path('installation/',include('installation.urls')),
    path('', include('manager.urls')),
]

urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
handler400 ='errors.views.error_400'
handler403 ='errors.views.error_403'
handler404 ='errors.views.error_404'
handler500='errors.views.error_500'