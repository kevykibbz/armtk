from django.contrib import admin
from django.urls import path,include
from django.conf.urls.static import static
from django.conf.urls import url
from django.conf import settings
from django.views.static import serve
urlpatterns = [
    path('admin/', admin.site.urls),
    path('installation/',include('installation.urls')),
    path('', include('manager.urls')),
    url(r'^uploads/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
    url(r'^profiles/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
    url(r'^static/(?P<path>.*)$',serve,{'document_root':settings.STATIC_ROOT}),
]

urlpatterns +=static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
urlpatterns +=static(settings.STATIC_URL,document_root=settings.STATIC_ROOT)

handler400 ='errors.views.error_400'
handler403 ='errors.views.error_403'
handler404 ='errors.views.error_404'
handler500='errors.views.error_500'