from django.db import models
from django.utils import timezone

# Дополнить потом!!!
UNITS = [
    "м",
    "м²",
    "шт",
    "комп.",
    "лист",
]


class Provider(models.Model):
    title = models.CharField("Название поставщика", max_length=20)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Поставщик"
        verbose_name_plural = "Поставщики"
        db_table = "providers"


class Folder(models.Model):

    title = models.CharField("Имя", max_length=20)
    parent = models.ForeignKey('self', models.CASCADE, null=True, blank=True)

    def __str__(self):
        path = []
        current = self
        while current.parent:
            path.append(current.title)
        path.append(current.title)

        return "/".join(path[::-1])

    class Meta:
        verbose_name = "Папка"
        verbose_name_plural = "Папки"
        db_table = "folders"


class Material(models.Model):

    material = models.ForeignKey('AbsMaterial', models.PROTECT, verbose_name="Материал")
    count = models.FloatField("Кол-во")
    for_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Для заказа")
    status = models.IntegerField("Статус",
                                 choices=[(0, "Ожидается"), (1, "На складе"), (2, "В производстве")], default=0)
    details = models.CharField("Детали", blank=True, null=True, max_length=100)
    price = models.FloatField("Цена", blank=True, null=True)

    def __str__(self):
        return self.material.title + " - " + str(self.count) + self.material.units

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Склад"
        db_table = "stock"


class AbsMaterial(models.Model):

    title = models.CharField("Наименование", max_length=20)
    provider = models.ForeignKey(Provider, models.CASCADE, verbose_name="Поставщик")
    units = models.CharField("Единицы измерения", choices=map(lambda x: (x, x, ), UNITS), max_length=10, default="шт")
    parent = models.ForeignKey(Folder, models.CASCADE, null=True, verbose_name="Папка")
    picture_url = models.TextField("URL изображения", null=True, blank=True)

    def __str__(self):
        path = []
        current = self
        while current.parent:
            path.append(current.title)
        path.append(current.title)

        return "/".join(path[::-1])

    def get_last_price(self):
        last = Material.objects.filter(material_id=self.id).last()
        return last.price if last else None

    def get_remainder(self) -> Material:
        free = Material.objects.filter(material=self, for_order__isnull=True)
        return free[0] if free else None

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        db_table = "abs-materials"


class Order(models.Model):

    description = models.CharField("Описание", max_length=50)
    client = models.CharField("Заказчик", max_length=50)
    order_date = models.DateField("Дата приёма", default=timezone.now().date())
    status = models.IntegerField("Статус", default=0, choices=[
        (0, "Ожидаются материалы"),
        (1, "В производстве"),
        (2, "Заказ выполнен")
    ])
    prod_date = models.DateField("Дата исполнения", blank=True, null=True)

    def __str__(self):
        return self.description

    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"
        db_table = "orders"


class Task(models.Model):

    material = models.ForeignKey(AbsMaterial, models.PROTECT, verbose_name="Материал")
    count = models.FloatField("Кол-во")

    def __str__(self):
        return self.material.title + " - " + str(self.count) + self.material.units + " - Task"

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Для нового заказа"
        db_table = "tasks"


class CompletedMaterial(models.Model):

    material = models.ForeignKey('AbsMaterial', models.PROTECT, verbose_name="Материал")
    count = models.FloatField("Кол-во")
    for_order = models.ForeignKey('Order', on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Для заказа")
    details = models.CharField("Детали", blank=True, null=True, max_length=100)
    price = models.FloatField("Цена", blank=True, null=True)

    def __str__(self):
        return self.material.title + " - " + str(self.count) + self.material.units

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Завершённые"
        db_table = "completed"

