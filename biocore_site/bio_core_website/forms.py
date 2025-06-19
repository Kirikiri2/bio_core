from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, Vitamin, Manufacturer, Element, UserBMI
from django.core.exceptions import ValidationError

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)
    
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')
    
    def clean_email(self):
        email = self.cleaned_data['email']
        if CustomUser.objects.filter(email=email).exists():
            raise ValidationError("Этот email уже используется")
        return email

class ProfileEditForm(forms.ModelForm):
    delete_avatar = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label="Удалить аватар"
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'first_name', 'last_name', 'email', 'avatar', 'gender', 'weight', 'height', 'age']
        widgets = {
            'avatar': forms.FileInput(attrs={'accept': 'image/*'}),
            'gender': forms.Select(choices=CustomUser.GENDER_CHOICES),
        }
    def save(self, commit=True):
        user = super().save(commit=False)
        
        if commit:
            user.save()
            # Сохраняем историю ИМТ при изменении веса или роста
            if 'weight' in self.changed_data or 'height' in self.changed_data:
                if user.weight and user.height:
                    UserBMI.objects.create(
                        user=user,
                        weight=user.weight,
                        height=user.height
                    )
        
        return user

class ConsultationForm(forms.Form):
    def __init__(self, *args, **kwargs):
        vitamins = kwargs.pop('vitamins', None)
        super().__init__(*args, **kwargs)
        
        if vitamins:
            for vitamin in vitamins:
                self.fields[f'vitamin_{vitamin.id}'] = forms.FloatField(
                    label=f"{vitamin.name} ({vitamin.unit})",
                    widget=forms.NumberInput(attrs={'class': 'form-control'}),
                    required=True
                )
    
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False,
        label="Дополнительные примечания"
    )

class ElementForm(forms.ModelForm):
    manufacturers = forms.ModelMultipleChoiceField(
        queryset=Manufacturer.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    class Meta:
        model = Element
        fields = '__all__'

    def save(self, commit=True):
        instance = super().save(commit)
        if commit:
            instance.manufacturers.clear()
            for manufacturer in self.cleaned_data['manufacturers']:
                ElementManufacturer.objects.create(
                    element=instance,
                    manufacturer=manufacturer,
                    is_main=False  # или логика определения главного производителя
                )
        return instance