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


class Manager(models.Model):
    name = models.CharField("Менеджер", max_length=50)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Менеджер"
        verbose_name_plural = "Менеджеры"
        db_table = "managers"


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
                                 choices=[(-1, "Не заказано"), (0, "Ожидается"), (1, "На складе"),
                                          (2, "В производстве"), (3, "Реализовано")], default=0)
    details = models.CharField("Детали", blank=True, null=True, max_length=100)
    price = models.FloatField("Цена", blank=True, null=True)

    def __str__(self):
        return self.material.title + " - " + str(self.count) + self.material.units

    def save(self, *args, **kwargs):
        self.count = round(self.count, 2)
        self.price = round(self.price, 2)
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Склад"
        db_table = "stock"


class AbsMaterial(models.Model):

    title = models.CharField("Наименование", max_length=20)
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
        last = Material.objects.filter(material_id=self.id, price__isnull=False).last()
        return round(last.price, 2) if last else None

    def get_remainder(self) -> Material:
        free = Material.objects.filter(material=self, for_order__isnull=True, status__in=(0, 1))
        return free[0] if free else None

    class Meta:
        verbose_name = "Материал"
        verbose_name_plural = "Материалы"
        db_table = "abs-materials"


class Order(models.Model):

    description = models.CharField("Описание", max_length=50)
    manager = models.ForeignKey(Manager, models.SET_NULL, null=True, blank=True, verbose_name="Менеджер", default=None)
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



