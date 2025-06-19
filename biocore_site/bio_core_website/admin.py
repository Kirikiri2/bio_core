from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Element, Manufacturer, Vitamin, Consultation, VitaminLevel

admin.site.register(Category)
admin.site.register(Element)
admin.site.register(Manufacturer)
admin.site.register(Vitamin)
admin.site.register(Consultation)
admin.site.register(VitaminLevel)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительная информация", {
            "fields": ("gender", "weight", "height", "age")
        }),
    )