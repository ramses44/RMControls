# Generated by Django 3.1.1 on 2020-11-02 15:55

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0004_auto_20201027_2132'),
    ]

    operations = [
        migrations.AlterField(
            model_name='order',
            name='order_date',
            field=models.DateField(default=datetime.date(2020, 11, 2), verbose_name='Дата приёма'),
        ),
    ]
