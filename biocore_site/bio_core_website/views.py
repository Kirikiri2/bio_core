from django.shortcuts import render, get_object_or_404, redirect
from .models import Category, Element, Vitamin, Consultation, VitaminLevel, UserBMI
from django.contrib.auth.decorators import login_required
from .forms import ProfileEditForm, ConsultationForm
from django.contrib import messages
from django.db import transaction

@login_required
def consultation_view(request):
    vitamins = Vitamin.objects.all()
    
    if request.method == 'POST':
        form = ConsultationForm(request.POST, vitamins=vitamins)
        if form.is_valid():
            try:
                with transaction.atomic():
                    consultation = Consultation.objects.create(
                        user=request.user,
                        notes=form.cleaned_data['notes']
                    )
                    
                    deficient_vitamins = []
                    excess_vitamins = []
                    
                    for vitamin in vitamins:
                        value = form.cleaned_data[f'vitamin_{vitamin.id}']
                        VitaminLevel.objects.create(
                            consultation=consultation,
                            vitamin=vitamin,
                            value=value
                        )
                        
                        if value < vitamin.min_normal:
                            deficient_vitamins.append(vitamin)
                        elif vitamin.danger_high_level and value > vitamin.max_normal:
                            excess_vitamins.append({
                                'vitamin': vitamin,
                                'value': value,
                                'message': vitamin.high_level_message
                            })
                    
                    # Сохраняем данные в сессии
                    request.session['deficient_vitamins'] = [
                        {'id': v.id, 'name': v.name} for v in deficient_vitamins
                    ]
                    request.session['excess_vitamins'] = excess_vitamins
                    
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
def consultation_results(request):
    deficient_vitamins = request.session.get('deficient_vitamins', [])
    excess_vitamins = request.session.get('excess_vitamins', [])
    elements = []
    
    for v in deficient_vitamins:
        try:
            vitamin = Vitamin.objects.get(id=v['id'])
            if vitamin.element:
                elements.append(vitamin.element)
        except Vitamin.DoesNotExist:
            continue
    
    return render(request, 'bio_core_website/consultation_results.html', {
        'elements': elements,
        'excess_vitamins': excess_vitamins
    })


@login_required
def consultation_history(request):
    consultations = request.user.consultations.all().order_by('-date')
    vitamins = Vitamin.objects.all()
    
    # Подготовка данных для графиков
    chart_data = {}
    for vitamin in vitamins:
        levels = VitaminLevel.objects.filter(
            vitamin=vitamin,
            consultation__user=request.user
        ).order_by('consultation__date')
        
        chart_data[vitamin.name] = {
            'dates': [l.consultation.date.strftime('%Y-%m-%d') for l in levels],
            'values': [l.value for l in levels],
            'unit': vitamin.unit,
            'min_normal': vitamin.min_normal,
            'max_normal': vitamin.max_normal
        }
    
    return render(request, 'bio_core_website/consultation_history.html', {
        'consultations': consultations,
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
            'history': user.bmi_history.all().order_by('-date')[:10]
        }
    
    context = {
        'user': user,
        'bmi_data': bmi_data
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