from django.shortcuts import render, redirect
from .models import *
from .forms import *


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
                  dict(title=f'Каталог{ ": " + root.title if root.id else ""}', root=root, path=path))


def add_folder(request, parent):
    message = ('none', '')
    path = get_path(parent)

    if request.method == 'POST':
        form = AddFolder(request.POST)
        if form.is_valid():
            f = Folder()
            f.title = form.data['title']
            f.parent_id = parent
            f.save()
            message = ('success', 'Папка успешно сохранена')
        else:
            message = ('error', 'Ошибка отправки формы!')

    form = AddFolder()

    context = {
        'form': form,
        'message': message,
        'title': 'Добавить папку',
        'additional': True,
        'path': path
    }

    return render(request, 'main/add.html', context)


def add_material(request, parent):
    message = ('none', '')
    path = get_path(parent)

    if request.method == 'POST':
        form = AddMaterial(request.POST)
        if form.is_valid():
            f = AbsMaterial()
            f.title = form.data['title']
            f.units = form.data['units']
            f.provider_id = form.data['provider']
            if form.data['url']:
                f.picture_url = form.data['url']
            f.parent_id = parent
            f.save()
            message = ('success', 'Данные о материале успешно сохранены')
        else:
            message = ('error', 'Ошибка отправки формы!')

    form = AddMaterial()

    context = {
        'form': form,
        'message': message,
        'title': 'Добавить материал',
        'additional': True,
        'path': path
    }

    return render(request, 'main/add.html', context)
