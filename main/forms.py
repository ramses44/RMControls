from django.forms import Form, CharField, TextInput, ChoiceField, Select, URLField, \
    URLInput, FloatField, Textarea, BooleanField, CheckboxInput, DateField, DateInput, IntegerField
from .models import UNITS, Order, Manager


class AddFolder(Form):
    title = CharField(widget=TextInput({
        'class': 'form-control',
        'placeholder': 'Введите название папки',
        'id': 'title',
    }))


class AddMaterial(Form):
    title = CharField(widget=TextInput({
        'class': 'form-control',
        'placeholder': 'Введите название Материала',
        'id': 'title',
    }))

    units = ChoiceField(widget=Select({
        'class': 'form-control',
    }), choices=[[x] * 2 for x in UNITS], label="Единицы измерения")

    url = URLField(widget=URLInput({
        'class': 'form-control'
    }), label="URL изображения", required=False)


class CreateOrder(Form):

    number = IntegerField(widget=TextInput({
        'class': 'form-control'
    }), label="№ Заказа")

    manager = ChoiceField(widget=Select({
        'class': 'form-control',
        'placeholder': 'Кто взял заказ (менеджер)'
    }), label="Менеджер", choices=list(map(lambda x: (x.id, x.name), Manager.objects.all())) + [(0, '-')])

    client = CharField(widget=TextInput({
        'class': 'form-control',
        'placeholder': 'ФИО'
    }), label="Заказчик")

    description = CharField(widget=Textarea({
        'class': 'form-control',
        'style': 'height: 60px',
        'placeholder': '...'
    }), label="Описание")

    date = DateField(widget=DateInput({
        'class': 'form-control',
        'type': 'date'
    }), label="Дата заказа")

    prod_date = DateField(widget=DateInput({
        'class': 'form-control',
        'type': 'date'
    }), label="Дата исполнения", required=False)


class EditOnStock(Form):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['for_order'].choices = [(None, '-')] + [(x.id, '№' + x.id.__str__()) for x
                                                            in Order.objects.filter(status=0)]

    for_order = ChoiceField(widget=Select({
        'class': 'form-control',
        'style': 'background-color: aliceblue'
    }), label="Для заказа", required=False)

    count = FloatField(widget=TextInput({
        'class': 'form-control',
        'style': 'background-color: aliceblue'
    }), label="Заказывается")

    details = CharField(widget=Textarea({
        'class': 'form-control',
        'style': 'height: 60px; background-color: aliceblue'
    }), label="Примечание (детали)")

    price = FloatField(widget=TextInput({
        'class': 'form-control',
        'style': 'background-color: aliceblue'
    }), label="Цена")
