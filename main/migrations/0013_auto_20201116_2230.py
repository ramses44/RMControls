# Generated by Django 3.1.1 on 2020-11-16 19:30

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_auto_20201116_2212'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='manager',
            field=models.ForeignKey(blank=True, default=None, null=True, on_delete=django.db.models.deletion.SET_NULL, to='main.manager', verbose_name='Менеджер'),
        ),
    ]
