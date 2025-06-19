from django.urls import path
from . import views
from .views import profile_view, edit_profile

app_name = 'bio_core_website'  # Пространство имен приложения

urlpatterns = [
    path('', views.home, name='home'),  # Главная страница
    path('category/<int:category_id>/', views.category_elements, name='category_elements'),
    path('element/<int:pk>/', views.element_detail, name='element_detail'),
    path('profile/', profile_view, name='profile'),
    path('profile/edit/', edit_profile, name='edit_profile'),
]