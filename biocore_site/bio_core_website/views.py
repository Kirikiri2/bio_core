from django.shortcuts import render, get_object_or_404
from .models import Category, Element
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from .forms import ProfileEditForm
from django.contrib import messages


@login_required
def profile_view(request):
    user = request.user
    
    context = {
        'user': user
    }
    return render(request, 'bio_core_website/profile.html', context)

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