from django.shortcuts import render, redirect, HttpResponse
from django.http import HttpResponseBadRequest, JsonResponse
from .models import *
from .forms import *
from django.core.exceptions import PermissionDenied, ObjectDoesNotExist
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict

ON_PAGE = 1


def superuser_required(func):
    """Limit view to superusers only."""

    def _inner(request, *args, **kwargs):
        if not request.user.is_superuser:
            raise PermissionDenied
        return func(request, *args, **kwargs)

    return _inner


def ajax_required(f):
    """AJAX request required decorator"""

    def wrap(request, *args, **kwargs):
        if not request.is_ajax():
            return HttpResponseBadRequest()
        return f(request, *args, **kwargs)

    wrap.__doc__ = f.__doc__
    wrap.__name__ = f.__name__
    return wrap


def get_path(oid):
    root = Folder.objects.get(id=oid)
    path = []
    current = root
    while current.parent:
        path.append((current.title, current.id,))
        current = current.parent
    path.append((current.title, current.id,))

    return path[::-1]


def index(request):
    return redirect('/catalog/0')


def catalog(request, oid):
    path = get_path(oid)
    root = Folder.objects.get(id=oid)

    return render(request, 'main/catalog.html',
                  dict(title=f'Каталог{": " + root.title if root.id else ""}', root=root, path=path,
                       user_type='admin' if request.user.is_superuser else 'user' if request.user.is_authenticated else 'guest'))


def get_units(request, mid):
    return HttpResponse(AbsMaterial.objects.get(id=mid).units)


def get_order_list(request):
    return JsonResponse({'data': [x.id for x in Order.objects.filter(status__in=(0, 1,))][::-1]})


def get_last_price(request, mid):
    return HttpResponse(AbsMaterial.objects.get(id=mid).get_last_price())


def join_materials(mid):
    mats = Material.objects.filter(material_id=mid)

    for i, m1 in enumerate(mats):
        for m2 in mats[i + 1:]:
            if m1.price == m2.price and m1.details == m2.details and \
                    m1.for_order == m2.for_order and m1.status == m2.status:
                m1.count += m2.count
                m2.delete()
                m1.save()
                join_materials(mid)
                break


def add_remainder(mid, count, price):
    Material(material_id=mid, count=round(count, 2), for_order=None, details='Остаток', price=round(price, 2)).save()
    join_materials(mid)


@xframe_options_exempt
@superuser_required
def add_folder(request, parent):
    res = 'none'
    path = get_path(parent)
    f = None

    if request.method == 'POST':
        form = AddFolder(request.POST)
        if form.is_valid():
            f = Folder()
            f.title = form.data['title']
            f.parent_id = parent
            f.save()
            res = 'success'
        else:
            res = 'error'
    else:
        form = AddFolder()

    context = {
        'form': form,
        'result': res,
        'title': 'Добавить папку',
        'additional': True,
        'path': path,
    }

    return render(request, 'main/add.html', context)


@xframe_options_exempt
@superuser_required
def add_material(request, parent):
    res = 'none'
    path = get_path(parent)
    f = None

    if request.method == 'POST':
        form = AddMaterial(request.POST)
        if form.is_valid():
            f = AbsMaterial()
            f.title = form.data['title']
            f.units = form.data['units']
            if form.data['url']:
                f.picture_url = form.data['url']
            f.parent_id = parent
            f.save()
            res = 'success'
        else:
            res = 'error'
    else:
        form = AddMaterial()

    context = {
        'form': form,
        'result': res,
        'title': 'Добавить материал',
        'additional': True,
        'path': path,
    }

    return render(request, 'main/add.html', context)


@superuser_required
def del_folder(request, fid):
    folder = Folder.objects.get(id=fid)
    folder.delete()

    return HttpResponse('success')


@superuser_required
def del_material(request, mid):
    mat = AbsMaterial.objects.get(id=mid)
    mat.delete()

    return HttpResponse('success')


@xframe_options_exempt
@superuser_required
def edit_folder(request, fid):
    folder = Folder.objects.get(id=fid)

    res = 'none'
    path = get_path(folder.parent_id)

    if request.method == 'POST':
        form = AddFolder(request.POST)
        if form.is_valid():
            folder.title = form.data['title']
            folder.save()
            res = 'success'
        else:
            res = 'error'
    else:
        form = AddFolder({'title': folder.title})

    context = {
        'form': form,
        'result': res,
        'title': 'Переименовать папку',
        'additional': True,
        'path': path,
    }

    return render(request, 'main/add.html', context)


@xframe_options_exempt
@superuser_required
def edit_material(request, mid):
    res = 'none'
    mat = AbsMaterial.objects.get(id=mid)
    path = get_path(mat.parent_id)

    if request.method == 'POST':
        form = AddMaterial(request.POST)
        if form.is_valid():
            mat.title = form.data['title']
            mat.units = form.data['units']
            if form.data['url']:
                mat.picture_url = form.data['url']
            mat.save()
            res = 'success'
        else:
            res = 'error'
    else:
        form = AddMaterial({
            'title': mat.title,
            'units': mat.units,
            'url': mat.picture_url
        })

    context = {
        'form': form,
        'result': res,
        'title': 'Редактировать материал',
        'additional': True,
        'path': path,
    }

    return render(request, 'main/add.html', context)


def stock(request):
    mats = Material.objects.filter(status__in=(0, 1, 2))
    return render(request, 'main/stock.html', context={
        'stock': mats, 'title': 'Склад', 'all': AbsMaterial.objects.all(),
        'filters': request.GET.get('filters', {})})


def add_to_stock(request, mid):
    task = Material.objects.get(id=mid)
    rem = task.material.get_remainder()
    remainder = round(float(request.GET['remainder_used']), 2)
    need = task.count
    count = round(float(request.GET['count']), 2)
    free = count + remainder - need
    fo = int(request.GET['for_order'])
    det = request.GET['details']
    price = round(float(request.GET['price']), 2)
    amid = task.material_id

    if need > remainder:
        Material(material_id=amid, count=need - remainder if free >= 0 else count, for_order_id=fo, details=det,
                 price=price).save()

    if remainder:
        Material(material_id=amid, count=remainder, for_order_id=fo, details=det, price=price,
                 status=rem.status).save()

        rem.count -= remainder
        if rem.count <= 0:
            rem.delete()
        else:
            rem.save()

    join_materials(amid)

    if free < 0:
        task.count = -free
        task.save()
    elif free == 0:
        task.delete()
    else:
        add_remainder(amid, free, price)
        task.delete()

    return HttpResponse(status=200)


# @ajax_required
@superuser_required
def add_task(request, mid, count, price, for_order):
    price = round(float(price.replace(',', '.')), 2)
    for_order = int(for_order)
    if count == '0':
        return HttpResponseBadRequest()
    Material(material_id=mid, count=round(float(count.replace(',', '.')), 2), price=price if price else None,
             for_order_id=for_order if for_order else None, status=-1).save()
    return HttpResponse(status=200)


@xframe_options_exempt
def create_order(request, additional=0):
    res = None
    ad = ''

    if request.method == 'POST':
        form = CreateOrder(request.POST)
        if form.is_valid():
            try:
                Order.objects.get(id=form.data['number'])
                res = 'error'
            except Order.DoesNotExist:
                o = Order(id=form.data['number'], client=form.data['client'],
                          description=form.data['description'],
                          order_date=form.data.get('date', None), prod_date=form.data.get('prod_date', None))
                if int(form.data['manager']):
                    o.manager_id = int(form.data['manager'])
                o.save()
                res = 'success'
                ad = str(o.id)
        else:
            res = 'error'
    else:
        form = CreateOrder()

    context = {
        'form': form,
        'result': res,
        'addit': ad,
        'title': 'Создать заказ',
        'additional': bool(additional)
    }

    return render(request, 'main/create-order.html', context)


@xframe_options_exempt
def order(request, oid, additional=0):
    o = Order.objects.get(id=oid)
    return render(request, 'main/order.html', context={
        'title': f'Заказ №{oid}', 'order': o, 'additional': additional,
        'cost': sum(map(lambda x: (
            x.price * x.count if x.price else x.material.get_last_price() if x.material.get_last_price() else 0),
                        o.material_set.all()))})


@login_required
def confirm_stock_material(request, mid):
    """On stock"""

    mat = Material.objects.get(id=mid)
    mat.status += 1
    mat.save()

    join_materials(mat.material_id)

    return HttpResponse(status=200)


@login_required
def delete_stock_material(request, mid):
    """On stock"""

    Material.objects.get(id=mid).delete()
    return HttpResponse(status=200)


@login_required
@xframe_options_exempt
def edit_stock_material(request, mid, nid):
    mat = Material.objects.get(id=mid)
    amat = AbsMaterial.objects.get(id=nid)
    res = ''

    if request.method == 'POST':
        form = EditOnStock(request.POST)
        if form.is_valid():

            mat.material_id = nid
            if form.data.get('for_order', None):
                mat.for_order_id = form.data['for_order']
            else:
                mat.for_order = None

            mat.details = form.data['details']
            mat.count = round(float(form.data['count']), 2)
            mat.price = round(float(form.data['price']), 2)

            mat.save()
            res = 'success'
        else:
            res = 'error'
    else:
        form = EditOnStock(model_to_dict(mat))

    context = {
        'form': form,
        'result': res,
        'title': 'Изменить ' + mat.material.title + ' на складе',
        'additional': True,
        'last_price': AbsMaterial.objects.get(id=nid).get_last_price(),
        'units': amat.units
    }

    return render(request, 'main/edit-on-stock.html', context=context)


@ajax_required
def get_all_materials(request):
    return JsonResponse({'data': [{x.id: x.title} for x in AbsMaterial.objects.all()]})


def tasks(request):
    tsks = Material.objects.filter(status=-1)
    return render(request, 'main/tasks.html',
                  context={'title': 'Формирование заказа', 'tasks': tsks, 'filters': request.GET.get('filters', {})})


def tasks_search(request, text):
    tsks = filter(lambda x: text.lower() in x.material.title.lower(), Material.objects.filter(status=-1))
    return render(request, 'main/tasks-search.html',
                  context={'title': 'ФЗ поиск: ' + text, 'tasks': list(tsks), 'text': text,
                           'filters': request.GET.get('filters', {})})


@xframe_options_exempt
def edit_order(request, oid, additional=0):
    res = None
    ad = ''
    o = Order.objects.get(id=oid)

    if request.method == 'POST':
        form = CreateOrder(request.POST)
        print(form.errors)
        if form.is_valid():
            o.client = form.data['client']
            print(int(form.data['manager']))
            if int(form.data['manager']):
                o.manager_id = int(form.data['manager'])
            else:
                o.manager = None
            o.description = form.data['description']
            o.order_date = form.data.get('date', None)
            o.prod_date = form.data['prod_date'] if form.data['prod_date'] else None
            o.save()
            res = 'success'
            ad = str(oid)
        else:
            res = 'error'
    else:
        form = CreateOrder(
            dict(number=oid, client=o.client, manager=o.manager_id if o.manager_id else 0, description=o.description,
                 date=o.order_date.__str__(), prod_date=o.prod_date.__str__()))

    context = {
        'form': form,
        'result': res,
        'addit': ad,
        'title': 'Изменить заказ №' + str(oid),
        'additional': bool(additional)
    }

    return render(request, 'main/edit-order.html', context)


def catalog_search(request, text):
    return render(request, 'main/catalog-search.html', context={
        'materials': filter(lambda x: text.lower() in x.title.lower(), AbsMaterial.objects.all()),
        'folders': list(filter(lambda x: text.lower() in x.title.lower(), Folder.objects.all())),
        'title': 'Поиск по каталогу: ' + text,
        'text': text,
        'filters': request.GET.get('filters', {})
    })


def stock_search(request, text):
    return render(request, 'main/stock-search.html', context={
        'stock': filter(lambda x: text.lower() in x.material.title.lower(),
                        Material.objects.filter(status__in=(0, 1, 2))),
        'title': 'Поиск на складе: ' + text,
        'all': AbsMaterial.objects.all(),
        'text': text,
        'filters': request.GET.get('filters', {})
    })


def mark_arrival(request, mid, count, price):
    try:
        count = round(float(count.replace(',', '.')), 2)
        price = round(float(price.replace(',', '.')), 2)
        mat = Material.objects.filter(status=0, material_id=mid)[0]

        if count > mat.count:
            mat.status = 1
            mat.save()
            return mark_arrival(request, mid, count - mat.count, price)

        else:
            if count == mat.count:
                mat.status = 1
                if price:
                    mat.price = price
            else:
                Material(material_id=mid, count=count, for_order_id=mat.for_order_id, details=mat.details, status=1,
                         price=price).save()
                mat.count -= count

            mat.save()

            join_materials(mid)

            return HttpResponse(status=200)
    except IndexError:
        add_remainder(mid, round(float(count.replace(',', '.')), 2), round(float(price.replace(',', '.')), 2))
        return HttpResponse(status=200)
    except TypeError:
        return HttpResponseBadRequest()


def archive(request, page=1, for_order=None):
    mats = Material.objects.filter(status=3, for_order_id=for_order) if for_order else Material.objects.filter(status=3)
    mats = mats[::-1]

    return render(request, 'main/archive.html', context={
        'materials': mats[ON_PAGE * (page - 1):ON_PAGE * page], 'title': 'Архив материалов', 'page': page,
        'is_last': len(mats) <= ON_PAGE * page, 'orders': Order.objects.filter(status=2), 'for_order': for_order})


def archive_search(request, text, page=1, for_order=None):
    mats = Material.objects.filter(status=3, for_order_id=for_order) if for_order else Material.objects.filter(status=3)
    mats = list(filter(lambda x: text.lower() in x.material.title.lower(), mats))[::-1]

    return render(request, 'main/archive-search.html', context={
        'materials': mats[ON_PAGE * (page - 1):ON_PAGE * page], 'title': 'Поиск по архиву: ' + text, 'page': page,
        'is_last': len(mats) <= ON_PAGE * page, 'orders': Order.objects.filter(status=2),
        'text': text, 'for_order': for_order})


def orders(request):
    return render(request, 'main/orders.html', context={'title': 'Все заказы', 'orders': Order.objects.all()})


def test(request):
    add_remainder(10, 0.5, 63.9)
    return HttpResponse(status=200)
