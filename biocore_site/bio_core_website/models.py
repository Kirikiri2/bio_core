from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Category(models.Model):
    """Модель категорий элементов"""
    name = models.CharField(
        max_length=100, 
        unique=True, 
        verbose_name=_("Категория"),
        help_text=_("Название категории элементов (например, Витамины, Минералы)")
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_("URL-адрес"),
        help_text=_("Автоматически создается при сохранении")
    )

    class Meta:
        verbose_name = _("Категория")
        verbose_name_plural = _("Категории")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Manufacturer(models.Model):
    """Модель производителей добавок"""
    name = models.CharField(
        max_length=200, 
        unique=True, 
        verbose_name=_("Производитель")
    )
    country = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        verbose_name=_("Страна производителя")
    )
    website = models.URLField(
        blank=True, 
        null=True, 
        verbose_name=_("Официальный сайт")
    )
    description = models.TextField(
        verbose_name=_("Описание производителя"),
        blank=True,
        null=True
    )

    class Meta:
        verbose_name = _("Производитель")
        verbose_name_plural = _("Производители")
        ordering = ['name']

    def __str__(self):
        return self.name


class Element(models.Model):
    """Модель элементов/добавок с множеством производителей"""
    name = models.CharField(
        max_length=100, 
        verbose_name=_("Название элемента")
    )
    category = models.ForeignKey(
        Category, 
        on_delete=models.CASCADE, 
        related_name="elements", 
        verbose_name=_("Категория")
    )
    description = models.TextField(
        verbose_name=_("Описание"), 
        blank=True, 
        null=True
    )
    image = models.ImageField(
        upload_to='product_images/', 
        blank=True, 
        null=True, 
        verbose_name=_("Изображение")
    )
    usage = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Способ применения и дозировка")
    )
    manufacturers = models.ManyToManyField(
        Manufacturer,
        related_name="elements",
        verbose_name=_("Производители"),
        blank=True
    )
    min_normal_value = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name=_("Минимальное нормальное значение")
    )
    max_normal_value = models.FloatField(
        null=True, 
        blank=True, 
        verbose_name=_("Максимальное нормальное значение")
    )
    measurement_unit = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        verbose_name=_("Единица измерения"),
        help_text=_("нг/мл, мкг, мг и т.д.")
    )

    class Meta:
        verbose_name = _("Элемент")
        verbose_name_plural = _("Элементы")
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['category']),
        ]

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    def get_manufacturers_list(self):
        return ", ".join([m.name for m in self.manufacturers.all()])


class ProductVariant(models.Model):
    """Модель вариантов продукта от разных производителей"""
    element = models.ForeignKey(
        Element,
        on_delete=models.CASCADE,
        related_name='variants',
        verbose_name=_("Базовый элемент")
    )
    manufacturer = models.ForeignKey(
        Manufacturer,
        on_delete=models.CASCADE,
        verbose_name=_("Производитель")
    )
    dosage = models.CharField(
        max_length=50,
        verbose_name=_("Дозировка"),
        help_text=_("500mg, 1000IU и т.д.")
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Цена")
    )
    sku = models.CharField(
        max_length=50,
        unique=True,
        blank=True,
        null=True,
        verbose_name=_("Артикул")
    )

    class Meta:
        verbose_name = _("Вариант продукта")
        verbose_name_plural = _("Варианты продуктов")
        unique_together = ('element', 'manufacturer', 'dosage')

    def __str__(self):
        return f"{self.element.name} ({self.dosage}) by {self.manufacturer.name}"


class CustomUser(AbstractUser):
    """Расширенная модель пользователя с дополнительными полями"""
    class GenderChoices(models.TextChoices):
        MALE = 'M', _('Мужской')
        FEMALE = 'F', _('Женский')
        OTHER = 'O', _('Другой')

    gender = models.CharField(
        max_length=1, 
        choices=GenderChoices.choices, 
        verbose_name=_("Пол"),
        blank=True,
        null=True
    )
    weight = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("Вес (кг)"),
        help_text=_("Введите ваш вес в килограммах")
    )
    height = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        verbose_name=_("Рост (см)"),
        help_text=_("Введите ваш рост в сантиметрах")
    )
    age = models.PositiveIntegerField(
        null=True, 
        blank=True, 
        verbose_name=_("Возраст"),
        help_text=_("Введите ваш возраст")
    )
    health_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name=_("Заметки о здоровье"),
        help_text=_("Хронические заболевания, аллергии и т.д.")
    )

    class Meta:
        verbose_name = _("Пользователь")
        verbose_name_plural = _("Пользователи")

    def __str__(self):
        return self.get_full_name() or self.username


class UserAnalysis(models.Model):
    """Модель для хранения анализов пользователей и рекомендаций"""
    user = models.ForeignKey(
        CustomUser, 
        on_delete=models.CASCADE, 
        related_name="analyses", 
        verbose_name=_("Пользователь")
    )
    analysis_file = models.FileField(
        upload_to='user_analyses/%Y/%m/%d/', 
        verbose_name=_("Файл с анализами"),
        help_text=_("Загрузите файл с результатами ваших анализов"),
        blank=True,
        null=True
    )
    analysis_data = models.JSONField(
        verbose_name=_("Данные анализов"),
        help_text=_("Структурированные данные анализов"),
        blank=True,
        null=True
    )
    uploaded_at = models.DateTimeField(
        auto_now_add=True, 
        verbose_name=_("Дата загрузки")
    )
    recommended_variants = models.ManyToManyField(
        ProductVariant,
        blank=True,
        verbose_name=_("Рекомендуемые варианты"),
        help_text=_("Конкретные продукты от производителей")
    )
    notes = models.TextField(
        blank=True, 
        null=True, 
        verbose_name=_("Примечания и рекомендации"),
        help_text=_("Дополнительные заметки по результатам анализа")
    )

    class Meta:
        verbose_name = _("Анализ пользователя")
        verbose_name_plural = _("Анализы пользователей")
        ordering = ['-uploaded_at']
        get_latest_by = 'uploaded_at'

    def __str__(self):
        return _("Анализ {user} от {date}").format(
            user=self.user.get_full_name() or self.user.username,
            date=self.uploaded_at.strftime('%d.%m.%Y')
        )