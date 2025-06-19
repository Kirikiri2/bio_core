from django.contrib import admin
from .models import (
    Category, 
    Manufacturer, 
    Element,
    ProductVariant,
    CustomUser,
    UserAnalysis
)

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Manufacturer)
class ManufacturerAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'website')
    search_fields = ('name', 'country')

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    autocomplete_fields = ['manufacturer']

@admin.register(Element)
class ElementAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_manufacturers', 'min_normal_value', 'max_normal_value')
    list_filter = ('category',)
    search_fields = ('name', 'description')
    filter_horizontal = ('manufacturers',)
    inlines = [ProductVariantInline]
    
    def get_manufacturers(self, obj):
        return ", ".join([m.name for m in obj.manufacturers.all()])
    get_manufacturers.short_description = "Производители"

@admin.register(ProductVariant)
class ProductVariantAdmin(admin.ModelAdmin):
    list_display = ('element', 'manufacturer', 'dosage', 'price')
    list_filter = ('manufacturer', 'element__category')
    autocomplete_fields = ['element', 'manufacturer']

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'get_full_name', 'age', 'gender')
    list_filter = ('gender',)
    search_fields = ('username', 'email', 'first_name', 'last_name')

@admin.register(UserAnalysis)
class UserAnalysisAdmin(admin.ModelAdmin):
    list_display = ('user', 'uploaded_at')
    list_filter = ('uploaded_at',)
    filter_horizontal = ('recommended_variants',)
    raw_id_fields = ('user',)