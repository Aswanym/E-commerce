# Generated by Django 3.2.7 on 2021-11-09 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0019_auto_20211109_2113'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='category_offer_price',
            field=models.FloatField(default=0, null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='offer_price',
            field=models.FloatField(default=0, null=True),
        ),
    ]
