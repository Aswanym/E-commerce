# Generated by Django 3.2.7 on 2021-10-28 08:13

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('order', '0007_auto_20211016_1404'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='orderproduct',
            options={'ordering': ['-created_at']},
        ),
    ]
