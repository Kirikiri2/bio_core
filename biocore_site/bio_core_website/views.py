from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from django.db.models import Prefetch
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from .models import Category, Element, Vitamin, Consultation, VitaminLevel, UserBMI, PromoVideo
from .forms import ProfileEditForm, ConsultationForm, SearchForm
from django.http import HttpResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from datetime import datetime

def test_cache(request):
    # Тест низкоуровневого кэширования
    cache.set('test_key', 'test_value', timeout=60)
    cached_value = cache.get('test_key', 'default_value')
    
    # Тест кэширования страницы
    return HttpResponse(
        f"Low-level cache test: {cached_value}<br>"
        f"Server time: {datetime.now()}"
    )

@cache_page(60)  # Кэшировать на 1 минуту
def cached_page(request):
    return HttpResponse(f"This page is cached. Time: {datetime.now()}")
@login_required
def consultation_view(request):
    cache_key = f'user_{request.user.id}_vitamins'
    vitamins = cache.get(cache_key)
    
    if not vitamins:
        vitamins = Vitamin.objects.select_related('element').only(
            'id', 'name', 'min_normal', 'max_normal', 'unit', 
            'danger_high_level', 'high_level_message', 'element__id'
        )
        cache.set(cache_key, vitamins, 60*60*24)  # Кэш на 24 часа

    if request.method == 'POST':
        form = ConsultationForm(request.POST, vitamins=vitamins)
        if form.is_valid():
            try:
                with transaction.atomic():
                    consultation = Consultation.objects.create(
                        user=request.user,
                        notes=form.cleaned_data['notes']
                    )
                    
                    vitamin_levels = [
                        VitaminLevel(
                            consultation=consultation,
                            vitamin_id=vitamin.id,
                            value=form.cleaned_data[f'vitamin_{vitamin.id}']
                        )
                        for vitamin in vitamins
                    ]
                    VitaminLevel.objects.bulk_create(vitamin_levels)
                    
                    # Сохраняем только ID для сессии
                    request.session['consultation_id'] = consultation.id
                    messages.success(request, 'Данные консультации сохранены!')
                    return redirect('bio_core_website:consultation_results')
            
            except Exception as e:
                messages.error(request, f'Ошибка при сохранении данных: {e}')
    else:
        form = ConsultationForm(vitamins=vitamins)
    
    return render(request, 'bio_core_website/consultation.html', {
        'form': form,
        'vitamins': vitamins
    })

@login_required
@cache_page(60*15)  # Кэшируем на 15 минут
def consultation_results(request):
    consultation_id = request.session.get('consultation_id')
    if not consultation_id:
        return redirect('bio_core_website:consultation')
    
    consultation = get_object_or_404(Consultation, id=consultation_id)
    levels = consultation.vitamin_levels.select_related('vitamin')
    
    deficient_elements = []
    excess_vitamins = []
    
    for level in levels:
        if level.value < level.vitamin.min_normal and level.vitamin.element:
            deficient_elements.append(level.vitamin.element)
        elif level.vitamin.danger_high_level and level.value > level.vitamin.max_normal:
            excess_vitamins.append({
                'vitamin': level.vitamin,
                'value': level.value,
                'message': level.vitamin.high_level_message
            })
    
    return render(request, 'bio_core_website/consultation_results.html', {
        'elements': deficient_elements,
        'excess_vitamins': excess_vitamins
    })

@login_required
def consultation_history(request):
    consultations = request.user.consultations.select_related('user').prefetch_related(
        Prefetch('vitamin_levels', queryset=VitaminLevel.objects.select_related('vitamin')))
    
    vitamins = Vitamin.objects.only('id', 'name', 'unit', 'min_normal', 'max_normal')
    chart_data = {}
    
    for vitamin in vitamins:
        levels = VitaminLevel.objects.filter(
            vitamin=vitamin,
            consultation__user=request.user
        ).only('value', 'consultation__date').order_by('consultation__date')
        
        chart_data[vitamin.name] = {
            'dates': [l.consultation.date.strftime('%Y-%m-%d') for l in levels],
            'values': [l.value for l in levels],
            'unit': vitamin.unit,
            'min_normal': vitamin.min_normal,
            'max_normal': vitamin.max_normal
        }
    
    return render(request, 'bio_core_website/consultation_history.html', {
        'consultations': consultations[:10],  # Ограничиваем количество
        'chart_data': chart_data
    })

@login_required
def profile_view(request):
    user = request.user
    bmi_data = None
    
    if user.weight and user.height:
        bmi = UserBMI.calculate_bmi(user.weight, user.height)
        category = UserBMI.get_bmi_category(bmi)
        bmi_data = {
            'value': round(bmi, 1),
            'category': category,
            'history': user.bmi_history.only('date', 'weight', 'height', 'bmi', 'category')[:10]
        }
    
    return render(request, 'bio_core_website/profile.html', {
        'user': user,
        'bmi_data': bmi_data
    })

@cache_page(60*60)  # Кэшируем на 1 час
def home(request):
    categories = Category.objects.only('id', 'name', 'image')[:2]
    return render(request, 'bio_core_website/home.html', {
        'categories': categories
    })

@cache_page(60*60)  # Кэшируем на 1 час
def category_elements(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    elements = category.elements.select_related('category').only(
        'id', 'name', 'category__name', 'image'
    )
    return render(request, 'bio_core_website/category_elements.html', {
        'category': category,
        'elements': elements
    })

@cache_page(60*60*24)  # Кэшируем на 24 часа
def element_detail(request, pk):
    element = get_object_or_404(
        Element.objects.select_related('category')
                       .prefetch_related('manufacturers')
                       .only('name', 'description', 'image', 'usage', 'category__name'),
        id=pk
    )
    return render(request, 'bio_core_website/element_detail.html', {
        'element': element
    })

@cache_page(60*60)  # Кэшируем на 1 час
def catalog_view(request):
    categories = Category.objects.prefetch_related(
        Prefetch('elements', queryset=Element.objects.only('id', 'name', 'image', 'category__name'))
    ).only('id', 'name', 'image')
    
    return render(request, 'bio_core_website/catalog.html', {
        'categories': categories,
        'title': 'Каталог элементов'
    })

@cache_page(60*60*24)  # Кэшируем на 24 часа
def about_view(request):
    promo_video = PromoVideo.objects.filter(is_active=True).only('title', 'video_file').first()
    return render(request, 'bio_core_website/about.html', {
        'title': 'О компании',
        'promo_video': promo_video
    })

def search_element(request):
    form = SearchForm()
    results = None
    query = None
    
    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Element.objects.filter(name__icontains=query).only(
                'id', 'name', 'category__name', 'image'
            )[:20]  # Ограничиваем результаты
    
    return render(request, 'bio_core_website/search_results.html', {
        'form': form,
        'results': results,
        'query': query
    })
@login_required
def edit_profile(request):
    if request.method == 'POST':
        form = ProfileEditForm(
            request.POST,
            request.FILES,
            instance=request.user
        )
        if form.is_valid():
            # Обработка удаления аватара
            if form.cleaned_data.get('delete_avatar') and request.user.avatar:
                request.user.avatar.delete(save=False)
                request.user.avatar = None
            
            form.save()
            messages.success(request, 'Профиль успешно обновлен!')
            return redirect('bio_core_website:profile')
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'bio_core_website/edit_profile.html', {'form': form})