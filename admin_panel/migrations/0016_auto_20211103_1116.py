# Generated by Django 3.2.7 on 2021-11-03 05:46

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('order', '0008_alter_orderproduct_options'),
        ('admin_panel', '0015_couponoffer_order_details'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='couponoffer',
            name='order_details',
        ),
        migrations.RemoveField(
            model_name='couponoffer',
            name='user',
        ),
        migrations.CreateModel(
            name='CouponUsed',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_ordered', models.BooleanField(default=False)),
                ('coupon', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.couponoffer')),
                ('order_details', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='order.orderproduct')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
