from django.db import models
from django.contrib.auth.models import AbstractUser


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")

    def __str__(self):
        return self.name


class Manufacturer(models.Model):
    name = models.CharField(max_length=200, unique=True, verbose_name="Производитель")
    country = models.CharField(max_length=100, blank=True, null=True, verbose_name="Страна")
    website = models.URLField(blank=True, null=True, verbose_name="Сайт")

    def __str__(self):
        return self.name


class Element(models.Model):
    name = models.CharField(max_length=100, verbose_name="Элемент")
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="elements", verbose_name="Категория")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Изображение")
    usage = models.TextField(blank=True, null=True, verbose_name="Способ применения")
    manufacturer = models.ForeignKey(Manufacturer,on_delete=models.SET_NULL,null=True,blank=True,related_name="elements",verbose_name="Производитель")

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, verbose_name="Пол")
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Вес (кг)")
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name="Рост (см)")
    age = models.PositiveIntegerField(null=True, blank=True, verbose_name="Возраст")

    def __str__(self):
        return self.username
