# Generated by Django 3.2.16 on 2022-12-01 20:25

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('sns_main', '0005_alter_user_username'),
    ]

    operations = [
        migrations.RenameField(
            model_name='reply',
            old_name='massage',
            new_name='message',
        ),
        migrations.AlterField(
            model_name='messagecard',
            name='head_image',
            field=models.ImageField(blank=True, upload_to='images/-6628161637832400557/'),
        ),
    ]