# Generated by Django 3.2.7 on 2021-10-11 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0002_auto_20210922_1841'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='stock',
            field=models.PositiveIntegerField(),
        ),
    ]
