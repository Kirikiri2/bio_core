from django.urls import path
from django.utils.translation import gettext_lazy as _
from . import views

app_name = 'bio_core_website'

urlpatterns = [
    # Главная страница
    path('', views.home, name='home'),
    
    # Категории и элементы
    path(
        'categories/<int:category_id>/', 
        views.category_elements, 
        name='category_elements'
    ),
    path(
        'elements/<int:pk>/', 
        views.element_detail, 
        name='element_detail'
    ),
    
    # Система консультаций
    path(
        'consultation/',
        views.consultation_view,
        name='consultation'
    ),
    path(
        'consultation/result/<int:analysis_id>/',
        views.consultation_result,
        name='consultation_result'
    ),
    
]