# -*- coding: utf-8 -*-

from django import forms
from django.forms import ModelForm
from django.db.models import Q
from django.shortcuts import render, redirect, get_list_or_404, get_object_or_404
from django.views.generic.list import ListView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.core.urlresolvers import reverse_lazy
from gen.models import *
from mdv_u.utils import FloatField2


class CopySpecForm(forms.Form):
    title = 'Копирование содержимого спецификации'
    DestSpecId = forms.ModelChoiceField(label='Выберите спецификацию в которую будем копировать',
                                        queryset=Spec.objects.all().order_by('name'), empty_label=None)
    NumOfCopies = forms.IntegerField(label='Количество копий', required=True, initial=1)


def show_CopySpecForm(request, s_id):
    if request.method == 'POST':
        form = CopySpecForm(request.POST)
        if form.is_valid():
            DestSpecId = form.cleaned_data['DestSpecId']
            NumOfCopies = form.cleaned_data['NumOfCopies']
            if NumOfCopies > 0:
                Src = ItemList.objects.filter(spec=s_id)
                Dest = ItemList.objects.filter(spec=DestSpecId)
                for k in Src:
                    # проверяем есть ли компонент с таким id целевой спецификации
                    try:
                        destitem = Dest.get(item__pk=k.item.pk)
                        #если есть, то увеличиваем количество
                        destitem.numAll = destitem.numAll + k.numAll * NumOfCopies
                        destitem.numPod = destitem.numPod + k.numPod * NumOfCopies
                        destitem.numNad = destitem.numNad + k.numNad * NumOfCopies
                        destitem.save()
                    except ItemList.DoesNotExist:
                        #в противном случае добавляем такойже компонент и копируем его количество
                        p = ItemList(item=k.item, spec=DestSpecId, numAll=k.numAll * NumOfCopies,
                                     numPod=k.numPod * NumOfCopies, numNad=k.numNad * NumOfCopies,
                                     isHydroIsp=k.isHydroIsp)
                        p.save()
            return redirect('show_Proj')
    else:
        form = CopySpecForm()
    return render(request, 'copyspec.html', {'form': form})


def show_SQL(request):
    from django.db import connection, transaction

    cursor = connection.cursor()

    # Data modifying operation - commit required
    #cursor.execute("DROP TABLE gen_item")
    #transaction.commit_unless_managed()
    return redirect('show_Proj')


def ChangeNumItems(request, s_id, l_id):
    p = ItemList.objects.get(pk=l_id)
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            numPod = form.cleaned_data['numPod']
            numNad = form.cleaned_data['numNad']
            isHydro = form.cleaned_data['isHydro']
            numAll = numNad + numPod
            if numAll > 0:
                p.numAll = numAll
                p.numPod = numPod
                p.numNad = numNad
                p.isHydroIsp = isHydro
                p.save()
            return redirect('show_ProjItems', s_id)
    data = {'numPod': p.numPod,
            'numNad': p.numNad,
            'isHydro': p.isHydroIsp}
    form = AddItemForm(data)
    d = p.item
    return render(request, 'additem.html', {'form': form, 'd': d})


def DelItem(request, s_id, l_id):
    l = ItemList.objects.get(pk=l_id)
    l.delete()
    return redirect('show_ProjItems', s_id)


class AddItemForm(forms.Form):
    title = 'Добавть деталь в спецификацию'
    #    numAll=FloatField2(label='Всего',required=True,initial=0)
    numNad = FloatField2(label='Надземная установка', required=True, initial=0)
    numPod = FloatField2(label='Подземная установка', required=True, initial=0)
    isHydro = forms.BooleanField(label='Учитывать в гидроиспытаниях', required=True, initial=True)


#    def clean(self):
#        cleaned_data=super(AddItemForm, self).clean()
#        numAll=float(cleaned_data.get("numAll"))
#        numPod=float(cleaned_data.get("numPod"))
#        numNad=float(cleaned_data.get("numNad"))
#        if abs(numAll-(numPod+numNad))>0.00001:
#            cleaned_data["numAll"]=numPod+numNad
#            raise forms.ValidationError("Общее количество должно совпадать с суммой подземной и надземной части")
#        return cleaned_data

def show_AddItemForm(request, s_id, d_id):
    if request.method == 'POST':
        form = AddItemForm(request.POST)
        if form.is_valid():
            numPod = form.cleaned_data['numPod']
            numNad = form.cleaned_data['numNad']
            isHydro = form.cleaned_data['isHydro']
            numAll = numNad + numPod
            if numAll > 0:
                s = Spec.objects.get(pk=s_id)
                d = Item.objects.get(pk=d_id)
                p = ItemList(item=d, spec=s, numAll=numAll, numPod=numPod, numNad=numNad, isHydroIsp=isHydro)
                p.save()
            return redirect('show_ProjItems', s_id)
    else:
        form = AddItemForm()
    d = Item.objects.get(pk=d_id)
    return render(request, 'additem.html', {'form': form, 'd': d})


def show_ProjItems(request, id):
    # Вью для показа спецификации проекта
    filter_type = int(request.session.get('filter_type', 0))
    if filter_type > 0:
        i = Item.objects.filter(type__id=filter_type).order_by('name')
    else:
        i = Item.objects.all().order_by('name')
    filter_dy = int(request.session.get('filter_dy', 0))
    if filter_dy > 0:
        if len(DYD[filter_dy]) > 1:
            a, b = DYD[filter_dy]
            i = i.filter(Q(dy=filter_dy) | Q(d=a) | Q(d=b))
        else:
            i = i.filter(Q(dy=filter_dy) | Q(d=DYD[filter_dy][0]))
    s = Spec.objects.get(pk=id)
    p = ItemList.objects.filter(spec=s).order_by('item__name')
    i_types = ItemType.objects.all()
    form = {}
    form['title'] = s.name
    return render(request, 'projitem.html',
                  {'p': p, 'i': i, 'spec_id': id, 's': s, 'it': i_types, 'ady': ALL_Dy, 'ftype': filter_type,
                   'fdy': filter_dy, 'form': form})


def ItemsFilterType(request, s_id, t_id):
    if t_id == 0:
        del request.session['filter_type']
    else:
        request.session['filter_type'] = t_id
    return redirect('show_ProjItems', s_id)


def ItemsFilterDY(request, s_id, dy_id):
    if dy_id == 0:
        del request.session['filter_dy']
    else:
        request.session['filter_dy'] = dy_id
    return redirect('show_ProjItems', s_id)


class ProjForm(ModelForm):
    title = 'Выбор проекта'

    class Meta:
        model = Spec
        exclude=()


def show_Proj(request, id=None):
    if request.method == 'POST':
        form = ProjForm(request.POST)
        if form.is_valid():
            form.save()
            form = ProjForm()
    else:
        form = ProjForm()
    if id != None:
        p = Spec.objects.get(pk=id)
        p.delete()
    p = Spec.objects.order_by('name')
    return render(request, 'proj.html', {'form': form, 'p': p})


def show_ProjEd(request, id):
    #    p=Spec.objects.get(pk=id)
    p = get_object_or_404(Spec, pk=id)
    if request.method == 'POST':
        form = ProjForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            return redirect('show_Proj', permanent=True)
    else:
        form = ProjForm(instance=p)
    return render(request, 'projed.html', {'form': form})


class ItemForm(ModelForm):
    title = 'Детали'

    class Meta:
        model = Item
        exclude=()

def show_Item(request, id=None):
    if request.method == 'POST':
        # request.POST изменять нельзя.
        pst = request.POST.copy()
        # для всех полей с нецелыми числами меняем , на .
        pst["dlina"] = pst["dlina"].replace(",", ".")
        pst["visota"] = pst["visota"].replace(",", ".")
        pst["m"] = pst["m"].replace(",", ".")
        pst["s"] = pst["s"].replace(",", ".")
        pst["s2"] = pst["s2"].replace(",", ".")
        form = ItemForm(pst)
        if form.is_valid():
            form.save()
            form = ItemForm()
    else:
        form = ItemForm()
    #если передан id то данную деталь надо удалить
    if id != None:
        #проверяем что деталь не используется в проектах
        p = Item.objects.get(pk=id)
        det_list = ItemList.objects.filter(item=id)
        if det_list:
            names = []
            for k in det_list:
                names.append(k.spec.name)
            return render(request, 'in_use2.html', {'name': p.name, 'use_list': names})
        p.delete()
    p = Item.objects.order_by('name')
    t = ItemType.objects.all()
    return render(request, 'item.html', {'form': form, 'p': p, 't': t})


def copyItem(request, id):
    p = Item.objects.get(pk=id)
    newitem = Item(type=p.type, name=p.name.encode('utf-8') + ' Копия', dlina=p.dlina, visota=p.visota, m=p.m, s=p.s,
                   d=p.d,
                   dy=p.dy, d2=p.d2, s2=p.s2, s_name=p.s_name, tu=p.tu, tu2=p.tu2, material=p.material,
                   privod=p.privod, ust=p.ust, zav_is=p.zav_is)
    newitem.save()
    return redirect('show_ItemEd', newitem.id)


def show_ItemEd(request, id, s_id=None):
    p = Item.objects.get(pk=id)
    det_list = ItemList.objects.filter(item=id)
    if request.method == 'POST':
        form = ItemForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            #проверяем откуда мы пришли, со списка деталей из спецификации или с общего списка деталей
            if s_id:
                return redirect('show_ProjItems', s_id)
            else:
                return redirect('show_Item')
    else:
        form = ItemForm(instance=p)
    return render(request, 'itemed.html', {'form': form, 'specs': det_list})


class TUForm(ModelForm):
    title = "Список ТУ и ГОСТ на детали"

    class Meta:
        model = TU
        exclude=()

def show_TU(request, id=None):
    if request.method == 'POST':
        form = TUForm(request.POST)
        if form.is_valid():
            form.save()
            form = TUForm()
    else:
        form = TUForm()
    #если передается id то данный ТУ подлежит уничтожению
    if id != None:
        #проверяем что деталей данного ТУ не существует
        p = TU.objects.get(pk=id)
        det_list = Item.objects.filter(Q(tu=id) | Q(tu2=id))
        if det_list:
            return render(request, 'in_use.html', {'name': p.name, 'use_list': det_list})
        p.delete()
    p = TU.objects.order_by('name')
    return render(request, 'tu.html', {'form': form, 'p': p})


def show_TUEd(request, id):
    p = TU.objects.get(pk=id)
    if request.method == 'POST':
        form = TUForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            return redirect('show_TU')
    else:
        form = TUForm(instance=p)
    return render(request, 'tued.html', {'form': form})


class TypeForm(ModelForm):
    title = "Список типов деталей"

    class Meta:
        model = ItemType
        exclude=()

def show_Type(request, id=None):
    if request.method == 'POST':
        form = TypeForm(request.POST)
        if form.is_valid():
            form.save()
            form = TypeForm()
    else:
        form = TypeForm()
    #если передается id то данный тип подлежит уничтожению
    if id != None:
        #проверяем что деталей данного типа не существует
        p = ItemType.objects.get(pk=id)
        det_list = Item.objects.filter(type=id)
        if det_list:
            return render(request, 'in_use.html', {'name': p.name, 'use_list': det_list})
        p.delete()
    p = ItemType.objects.order_by('name')
    return render(request, 'type.html', {'form': form, 'p': p})


def show_TypeEd(request, id):
    p = ItemType.objects.get(pk=id)
    if request.method == 'POST':
        form = TypeForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            return redirect('show_Type')
    else:
        form = TypeForm(instance=p)
    return render(request, 'typeed.html', {'form': form})


class ZavodListView(ListView):
    template_name = "zavod.html"
    queryset = Zavod.objects.order_by('name')
    paginate_by = 20
    context_object_name = 'p'


class ZavodCreate(CreateView):
    model = Zavod
    template_name = "zavoded.html"
    success_url = reverse_lazy("zavod")


class ZavodUpdate(UpdateView):
    model = Zavod
    template_name = "zavoded.html"
    success_url = reverse_lazy("zavod")
    pk_url_kwarg = 'id'


class ZavodDelete(DeleteView):
    model = Zavod
    pk_url_kwarg = 'id'
    template_name = "zavoddel.html"
    success_url = reverse_lazy("zavod")


class ZavodForm(ModelForm):
    title = "Список предприятий"

    class Meta:
        model = Zavod
        exclude=()

def show_Zavod(request, id=None):
    if request.method == 'POST':
        form = ZavodForm(request.POST)
        if form.is_valid():
            p = Zavod(name=form.cleaned_data['name'])
            p.save()
            form = ZavodForm()
    else:
        form = ZavodForm()
    #если передается id то данный завод подлежит уничтожению
    if id != None:
        #проверяем что данное предприятие не используется ни в каком ТУ
        p = Zavod.objects.get(pk=id)
        tu_list = TU.objects.filter(zavod=id)
        if tu_list:
            return render(request, 'in_use.html', {'name': p.name, 'use_list': tu_list})
        p.delete()
    p = Zavod.objects.order_by('name')
    return render(request, 'zavod.html', {'form': form, 'p': p})


def show_ZavodEd(request, id):
    p = Zavod.objects.get(pk=id)
    if request.method == 'POST':
        form = ZavodForm(request.POST, instance=p)
        if form.is_valid():
            form.save()
            return redirect('show_Zavod')
    else:
        form = ZavodForm(instance=p)
    return render(request, 'zavoded.html', {'form': form})
