from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinLengthValidator
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="Категория")
    image = models.ImageField(
        upload_to='category_images/',
        blank=True,
        null=True,
        verbose_name="Изображение категории"
    )

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
    category = models.ForeignKey('Category', on_delete=models.CASCADE,related_name="elements",  verbose_name="Категория")
    description = models.TextField(verbose_name="Описание", blank=True, null=True)
    image = models.ImageField(upload_to='product_images/', blank=True, null=True, verbose_name="Изображение")
    usage = models.TextField(blank=True, null=True, verbose_name="Способ применения")
    
    # Изменяем на ManyToManyField
    manufacturers = models.ManyToManyField(
        Manufacturer,
        verbose_name="Производители",
        blank=True,
        help_text="Выберите одного или нескольких производителей"
    )

    def __str__(self):
        return f"{self.name} ({self.category.name})"


class CustomUser(AbstractUser):
    GENDER_CHOICES = [
        ('M', 'Мужской'),
        ('F', 'Женский'),
    ]

    avatar = models.ImageField(
        upload_to='avatars/',
        blank=True,
        null=True,
        verbose_name="Аватар",
        default='avatars/default.jpg'
    )
    gender = models.CharField(
        max_length=1,
        choices=GENDER_CHOICES,
        verbose_name="Пол",
        blank=True,
        null=True
    )
    weight = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Вес (кг)"
    )
    height = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="Рост (см)"
    )
    age = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="Возраст"
    )
    email = models.EmailField(
        unique=True,
        verbose_name="Email"
    )
    username = models.CharField(
        max_length=30,
        unique=True,
        verbose_name="Имя пользователя",
        validators=[MinLengthValidator(4)]
    )

    def __str__(self):
        return self.username
    
class Vitamin(models.Model):
    name = models.CharField(max_length=100, verbose_name="Витамин/Элемент")
    element = models.OneToOneField(Element, on_delete=models.CASCADE, related_name='vitamin_data', null=True, blank=True)
    min_normal = models.FloatField(verbose_name="Минимальная норма")
    max_normal = models.FloatField(verbose_name="Максимальная норма")
    unit = models.CharField(max_length=20, verbose_name="Единица измерения")
    danger_high_level = models.BooleanField(
        default=True,
        verbose_name="Предупреждать о высоком уровне"
    )
    high_level_message = models.TextField(
        default="Проконсультируйтесь со специалистом",
        verbose_name="Сообщение при высоком уровне"
    )

    def __str__(self):
        return self.name

class Consultation(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='consultations')
    date = models.DateTimeField(auto_now_add=True, verbose_name="Дата консультации")
    notes = models.TextField(blank=True, null=True, verbose_name="Примечания")

    def __str__(self):
        return f"Консультация {self.user.username} от {self.date.strftime('%Y-%m-%d')}"

class VitaminLevel(models.Model):
    consultation = models.ForeignKey(Consultation, on_delete=models.CASCADE, related_name='vitamin_levels')
    vitamin = models.ForeignKey(Vitamin, on_delete=models.CASCADE)
    value = models.FloatField(validators=[MinValueValidator(0)], verbose_name="Уровень")
    
    class Meta:
        unique_together = ('consultation', 'vitamin')

    def __str__(self):
        return f"{self.vitamin.name}: {self.value} {self.vitamin.unit}"
    
class UserBMI(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='bmi_history')
    date = models.DateTimeField(auto_now_add=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2)  # в кг
    height = models.DecimalField(max_digits=5, decimal_places=2)  # в см
    bmi = models.DecimalField(max_digits=5, decimal_places=2)
    category = models.CharField(max_length=50)

    @classmethod
    def calculate_bmi(cls, weight, height):
        # Рост переводим из см в м
        height_m = height / 100
        bmi = weight / (height_m ** 2)
        return bmi

    @classmethod
    def get_bmi_category(cls, bmi):
        if bmi < 18.5:
            return "Недостаточный вес"
        elif 18.5 <= bmi < 25:
            return "Нормальный вес"
        elif 25 <= bmi < 30:
            return "Избыточный вес"
        else:
            return "Ожирение"

    def save(self, *args, **kwargs):
        self.bmi = self.calculate_bmi(self.weight, self.height)
        self.category = self.get_bmi_category(self.bmi)
        super().save(*args, **kwargs)