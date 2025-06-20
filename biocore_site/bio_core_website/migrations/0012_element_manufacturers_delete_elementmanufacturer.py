# Generated by Django 5.2 on 2025-06-19 19:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bio_core_website', '0011_alter_elementmanufacturer_element_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='element',
            name='manufacturers',
            field=models.ManyToManyField(blank=True, related_name='elements', to='bio_core_website.manufacturer', verbose_name='Производители'),
        ),
        migrations.DeleteModel(
            name='ElementManufacturer',
        ),
    ]
