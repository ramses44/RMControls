# Generated by Django 3.1.1 on 2020-09-16 19:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='absmaterial',
            name='picture_url',
            field=models.TextField(blank=True, null=True, verbose_name='URL изображения'),
        ),
        migrations.AlterField(
            model_name='absmaterial',
            name='units',
            field=models.CharField(choices=[('м', 'м'), ('м2', 'м2'), ('шт', 'шт'), ('комп.', 'комп.'), ('лист', 'лист')], default='шт', max_length=10, verbose_name='Единицы измерения'),
        ),
        migrations.AlterField(
            model_name='order',
            name='status',
            field=models.IntegerField(choices=[(0, 'Ожидаются материалы'), (1, 'В производстве'), (2, 'Заказ выполнен')], default=0, verbose_name='Статус'),
        ),
        migrations.CreateModel(
            name='Folder',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=20, verbose_name='Имя')),
                ('parent', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='main.folder')),
            ],
            options={
                'verbose_name': 'Папка',
                'verbose_name_plural': 'Папки',
                'db_table': 'folders',
            },
        ),
        migrations.AddField(
            model_name='absmaterial',
            name='parent',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='main.folder'),
        ),
    ]
