from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django.db.models import Prefetch

from .forms import AnalysisUploadForm
from .models import Category, Element, UserAnalysis
from .utils import extract_text_from_file, recommend_elements_from_text


def home(request):
    """Главная страница с популярными категориями"""
    featured_categories = Category.objects.all()[:4]
    return render(request, 'bio_core_website/home.html', {
        'categories': featured_categories,
        'title': _('Главная страница')
    })


def category_elements(request, category_id):
    """Список элементов в конкретной категории"""
    category = get_object_or_404(
        Category.objects.prefetch_related(
            Prefetch('elements', queryset=Element.objects.select_related('manufacturer'))
        ), 
        id=category_id
    )
    
    # Пагинация
    paginator = Paginator(category.elements.all(), 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'bio_core_website/category_elements.html', {
        'category': category,
        'page_obj': page_obj,
        'title': f"{_('Категория')}: {category.name}"
    })


def element_detail(request, pk):
    """Детальная страница элемента"""
    element = get_object_or_404(
        Element.objects.select_related('category', 'manufacturer'),
        id=pk
    )
    
    # Получаем элементы из той же категории
    related_elements = Element.objects.filter(
        category=element.category
    ).exclude(id=pk)[:4]
    
    return render(request, 'bio_core_website/element_detail.html', {
        'element': element,
        'related_elements': related_elements,
        'title': element.name
    })


@login_required
def consultation_view(request):
    """Обработка загрузки анализов и консультации"""
    if request.method == 'POST':
        form = AnalysisUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                analysis = form.save(commit=False)
                analysis.user = request.user
                
                text = extract_text_from_file(request.FILES['analysis_file'])
                recommended_elements = recommend_elements_from_text(text)
                
                analysis.save()
                if recommended_elements:
                    analysis.elements_to_take.set(recommended_elements)
                    messages.success(request, _('Анализ успешно обработан!'))
                else:
                    messages.warning(request, _('Не удалось определить рекомендации'))
                
                return redirect('bio_core_website:consultation_result', analysis_id=analysis.id)
                
            except Exception as e:
                messages.error(request, _('Ошибка: {}').format(str(e)))
    else:
        form = AnalysisUploadForm()
    
    return render(request, 'bio_core_website/consultation.html', {'form': form})


@login_required
def consultation_result(request, analysis_id):
    """Отображение результатов консультации"""
    analysis = get_object_or_404(
        UserAnalysis.objects.select_related('user'),
        id=analysis_id,
        user=request.user
    )
    
    recommended_elements = analysis.elements_to_take.select_related('category', 'manufacturer')
    
    return render(request, 'bio_core_website/consultation_result.html', {
        'analysis': analysis,
        'recommended_elements': recommended_elements,
        'title': _('Результаты анализа')
    })