# Generated by Django 3.2.7 on 2021-10-13 05:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0003_alter_product_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offername', models.IntegerField(blank=True)),
                ('offer', models.IntegerField()),
                ('startdate', models.DateField()),
                ('enddate', models.DateField()),
                ('product', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.product')),
            ],
        ),
    ]
