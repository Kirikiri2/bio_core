from django import forms
from .models import CustomUser

class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['first_name', 'last_name', 'email', 'gender', 'weight', 'height', 'age']
        widgets = {
            'gender': forms.Select(choices=CustomUser.GENDER_CHOICES),
        }
        labels = {
            'first_name': 'Имя',
            'last_name': 'Фамилия',
            'email': 'Email',
            'gender': 'Пол',
            'weight': 'Вес (кг)',
            'height': 'Рост (см)',
            'age': 'Возраст',
        }