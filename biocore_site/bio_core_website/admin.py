from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, Category, Element, Manufacturer

admin.site.register(Category)
admin.site.register(Element)
admin.site.register(Manufacturer)

class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ("Дополнительная информация", {
            "fields": ("gender", "weight", "height", "age")
        }),
    )