# Generated by Django 3.2.16 on 2022-12-01 21:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sns_main', '0006_auto_20221201_2025'),
    ]

    operations = [
        migrations.AlterField(
            model_name='messagecard',
            name='head_image',
            field=models.ImageField(blank=True, upload_to='images/1973161845690074611/'),
        ),
    ]
