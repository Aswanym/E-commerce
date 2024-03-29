# Generated by Django 3.2.7 on 2021-10-28 08:52

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('admin_panel', '0010_remove_offers_startdate'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='category',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='admin_panel.category'),
            preserve_default=False,
        ),
        migrations.CreateModel(
            name='category_offers',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('offername', models.CharField(max_length=200)),
                ('dis_percentage', models.IntegerField()),
                ('is_avail', models.BooleanField(default=True, null=True)),
                ('enddate', models.DateField()),
                ('category', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='admin_panel.category')),
            ],
        ),
    ]
