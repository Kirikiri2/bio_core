from django.shortcuts import render, get_object_or_404
from .models import Category, Element

def home(request):
    categories = Category.objects.all()[:2]
    return render(request, 'bio_core_website/home.html', {'categories': categories})

def category_elements(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    elements = category.elements.all()
    return render(request, 'bio_core_website/category_elements.html', {
        'category': category,
        'elements': elements
    })
def element_detail(request, pk):
    element = get_object_or_404(Element, id=pk)
    return render(request, 'bio_core_website/element_detail.html', {
        'element': element
    })