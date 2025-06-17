from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('bio_core_website.urls', namespace='bio_core_website')),
]