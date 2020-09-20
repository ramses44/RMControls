from django.forms import Form, CharField, TextInput, ChoiceField, Select, URLField, URLInput
from .models import Provider, UNITS


class AddFolder(Form):
    title = CharField(widget=TextInput({
                'class': 'form-control',
                'placeholder': 'Введите название папки'
            }))


class AddMaterial(Form):
    title = CharField(widget=TextInput({
                'class': 'form-control',
                'placeholder': 'Введите название Материала'
            }))

    provider = ChoiceField(widget=Select({
        'class': 'form-control',
    }), choices=map(lambda x: (x.id, x.title,), Provider.objects.all()), label="Поставщик")

    units = ChoiceField(widget=Select({
        'class': 'form-control',
    }), choices=[[x] * 2 for x in UNITS], label="Единицы измерения")

    url = URLField(widget=URLInput({
        'class': 'form-control'
    }), label="URL изображения", required=False)






