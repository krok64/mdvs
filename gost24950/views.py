# -*- coding: utf-8 -*-

from django import forms
from django.shortcuts import render, redirect
from math import pi, tan, radians, sqrt, atan, degrees, cos
from gost24950.models import Pipe, Obj
from mdv_u.utils import FloatField2


class PipeObjForm(forms.Form):
    action = '/pipe/select/'
    title = 'Редактирование трассы %(name)s'
    piket = FloatField2(label='Пикет центра объекта', required=True)
    L = FloatField2(label='Длина объекта, м', required=True)
    n = forms.IntegerField(label='Количество стыков на объекте', required=True)
    comment = forms.CharField(label='Описание объекта', required=False)
    ans = []

def show_PipeObjEd(request, pipe_id, obj_id, action):
    if request.method=='POST':
        form=PipeObjForm(request.POST)
        if form.is_valid():
            p=Obj.objects.get(pk=obj_id)
            p.piket=form.cleaned_data['piket']
            p.l=form.cleaned_data['L']
            p.n=form.cleaned_data['n']
            p.comment=form.cleaned_data['comment']
            p.save()
            return redirect('show_PipeObj', pipe_id)
    else:
        p=Obj.objects.get(pk=obj_id)
        data={ 'piket': p.piket,
          'L': p.l,
          'n': p.n,
          'comment': p.comment, }
        form=PipeObjForm(data)
    form.title=PipeObjForm.title % {'name':Pipe.objects.get(pk=pipe_id)}
    return render(request,'pipeobjed.html',{'form':form, 'pipe_id':pipe_id} )

def show_PipeObj(request, pipe_id, obj_id=None, action=None):
    if request.method=='POST':
        form=PipeObjForm(request.POST)
        if form.is_valid():
            piket=form.cleaned_data['piket']
            L=form.cleaned_data['L']
            n=form.cleaned_data['n']
            comment=form.cleaned_data['comment']
            p=Obj(l=L,n=n,piket=piket,comment=comment,p=Pipe.objects.get(pk=pipe_id))
            p.save()
    else:
        form=PipeObjForm()
    if obj_id !=None:
       if action=='del':
           p=Obj.objects.get(pk=obj_id)
           p.delete()
    form.title=PipeObjForm.title % {'name':Pipe.objects.get(pk=pipe_id)}
    form.action=PipeObjForm.action+pipe_id+r'/'
    p=Obj.objects.filter(p=pipe_id).order_by('piket')
    if p.count()>1:
        Ltrub=Pipe.objects.get(pk=pipe_id).ltrub
        obj_num=p.count()
        dlina=p[obj_num-1].piket-p[0].piket
        st_obj=0
        st_tr=0
        for i in range(obj_num-1):
            st_obj=st_obj+p[i].n
            st_tr=st_tr+int((p[i+1].piket-p[i].piket-(p[i+1].l+p[i].l)/2)/Ltrub)
        st_obj=st_obj+p[obj_num-1].n
        form.ans=[]
        form.ans.append((st_obj+st_tr,'Всего стыков'))
        form.ans.append((st_obj,'Стыков на объектах'))
        form.ans.append((st_tr,'Стыков между объектами'))
        form.ans.append((dlina,'Длина участка, м'))
        form.ans.append((Ltrub,'Длина 1 трубы, м'))
    return render(request,'pipeobj.html',{'form':form, 'p':p, 'pipe_id':pipe_id} )

class PipeForm(forms.Form):
    action='show_Pipe'
    title='Расчет количества стыков на трассе газопровода'
    name=forms.CharField(label='Название трассы', required=True)
    dy=forms.IntegerField(label='Условный диаметр трубы, мм', required=True)

def show_Pipe(request, id=None):
    if request.method=='POST':
        form=PipeForm(request.POST)
        if form.is_valid():
            name=form.cleaned_data['name']
            dy=form.cleaned_data['dy']
            if dy<500:
                L=9
            elif dy>800:
                L=11.3
            else:
                L=10.5
            p=Pipe(name=name,dy=dy,ltrub=L)
            p.save()
    else:
        form=PipeForm()
    if id!=None:
       p=Pipe.objects.get(pk=id)
       p.delete()
    p=Pipe.objects.order_by('name')
    return render(request,'pipe.html',{'form':form, 'p':p} )

class VKotlovanForm(forms.Form):
    action='show_VKotlovan'
    title='Объем котлована'
    f1=FloatField2(label='Площадь нижнего основания котлована, м2', required=True)
    f2=FloatField2(label='Площадь верхнего основания котлована, м2', required=True)
    h=FloatField2(label='Глубина котлована, м', required=True)
    ans=[]

def show_VKotlovan(request):
    if request.method=='POST':
        form=VKotlovanForm(request.POST)
        if form.is_valid():
            f1=form.cleaned_data['f1']
            f2=form.cleaned_data['f2']
            h=form.cleaned_data['h']
            V=h/3*(f2+f1+sqrt(f2*f1))
            form.ans=[]
            form.ans.append(('%.1f' % (V,),'Объем котлована, м3'))
    else:
        form=VKotlovanForm()
    return render(request,'form24950.html',{ 'form':form} )

class GazTUForm(forms.Form):
    action='show_GazTU'
    title='Гибка труб по ГазТУ 102-488/2-05'
    ug=forms.IntegerField(label='Угол гибки, град', required=True)
    d=forms.ChoiceField(label='Диаметр трубы, мм', required=True,
                    choices=((200,219),(250,273),(300,325),(350,377),(400,426),(500,530),(600,630),(700,720),(800,820),(1000,1020),(1200,1220),(1400,1420)))
    ans=[]

def show_GazTU(request):
    dlist={'200':{'col':1,'R':1000,'L':9800},
           '250':{'col':2,'R':1250,'L':9800},
           '300':{'col':3,'R':1500,'L':9800},
           '350':{'col':4,'R':1750,'L':9800},
           '400':{'col':5,'R':2000,'L':9800},
           '500':{'col':6,'R':2500,'L':11600},
           '600':{'col':7,'R':3000,'L':11600},
           '700':{'col':8,'R':3500,'L':11600},
           '800':{'col':9,'R':4000,'L':11600},
           '1000':{'col':10,'R':5000,'L':11600},
           '1200':{'col':11,'R':6000,'L':11600},
           '1400':{'col':12,'R':7000,'L':11600},
           }
    A=0
    if request.method=='POST':
        form=GazTUForm(request.POST)
        if form.is_valid():
            ug=form.cleaned_data['ug']
            d=form.cleaned_data['d']
            k=dlist[d]['col']
            f=open('/var/www/mdvs/gost24950/gaztu','r')
            for line in f:
                if ug==int(line.split()[0]):
                    A=int(line.split()[k])
                    break
            f.close()
            R=dlist[d]['R']
            L=dlist[d]['L']
            a1=R*tan(radians(ug)/2)
            L1=A-a1
            L2=pi*R*ug/180
            L3=L-L1-L2
            B=a1+L3
            T=a1/1000
            Bis=a1**2/(2*L2)/1000
            form.ans=[]
            form.ans.append((A,'A, мм'))
            form.ans.append(("%d" % (B+0.5),'B, мм'))
            form.ans.append(("%.4f" % T,'T, м'))
            form.ans.append(("%.4f" % Bis,'Биссектрисса='))
    else:
        form=GazTUForm()
    return render(request,'form24950.html',{ 'form':form} )

class ProgalForm(forms.Form):
    action='show_Progal'
    title='Устройство прогала'
    pic='progal.PNG'
    a=FloatField2(label='Ширина дороги (а), м', required=True)
    b=FloatField2(label='Ширина подошвы дороги (b), м', required=True)
    H=FloatField2(label='Высота полотна дороги (H), м', required=True)
    c=FloatField2(label='Ширина траншеи по дну (с), м', required=True)
    Ht=FloatField2(label='Глубина траншеи (h), м', required=True)
    X1=FloatField2(label='Откос траншеи 1:Х', required=True)
    X2=FloatField2(label='Откос прогала 1:Х', required=True)
    ans=[]

def show_Progal(request):
    if request.method=='POST':
        form=ProgalForm(request.POST)
        if form.is_valid():
            a=form.cleaned_data['a']
            b=form.cleaned_data['b']
            H=form.cleaned_data['H']
            c=form.cleaned_data['c']
            Ht=form.cleaned_data['Ht']
            X1=form.cleaned_data['X1']
            X2=form.cleaned_data['X2']
            d=c+Ht*X1*2
            S=(a+b)/2*H
            e=d+H*X2*2
            sr=(e+d)/2
            V=S*sr
            Dor=e*a
            form.ans=[]
            form.ans.append((V,'Объем прогала, м3'))
            form.ans.append((Dor,'Восстановление дорожного полотна, м2'))
    else:
        form=ProgalForm()
    return render(request,'form24950.html',{ 'form':form} )

class SovUgForm(forms.Form):
    action='show_SovUg'
    title='Совмещенный угол'
    Ggrad=FloatField2(label='Угол в плане, градусы', required=True)
    Gmin=FloatField2(label='Угол в плане, минуты', required=True)
    Vgrad=FloatField2(label='Угол в профиле, градусы', required=True)
    Vmin=FloatField2(label='Угол в профиле, минуты', required=True)
    B=FloatField2(label='Биссектриса совмещенного угла, м', required=True)
    ans=[]

def show_SovUg(request):
    if request.method=='POST':
        form=SovUgForm(request.POST)
        if form.is_valid():
            Ggrad=form.cleaned_data['Ggrad']
            Gmin=form.cleaned_data['Gmin']
            Vgrad=form.cleaned_data['Vgrad']
            Vmin=form.cleaned_data['Vmin']
            B=form.cleaned_data['B']
            G=Ggrad+Gmin/60
            V=Vgrad+Vmin/60
            SovUg=degrees(atan(sqrt(tan(radians(G))**2+tan(radians(V))**2)))
            SovUggrad=int(SovUg)
            SovUgmin=(SovUg-SovUggrad)*60
            va=[cos(radians(V)),0,cos(radians(90-V))]
            vb=[va[0],va[0]*tan(radians(G)),0]
            vc=[va[0],0,0]
            vd=[va[0]-vc[0],va[1]-vc[1],va[2]-vc[2]]
            ve=[vb[0]+vd[0],vb[1]+vd[1],vb[2]+vd[2]]
            vf=[-ve[0],0,0]
            vg=[(ve[0]+vf[0])/2,(ve[1]+vf[1])/2,(ve[2]+vf[2])/2]
            vh=[vg[0]**2,vg[1]**2,vg[2]**2]
            L=sqrt(vh[0]+vh[1]+vh[2])
            vi=[vg[0]/L*B,vg[1]/L*B,vg[2]/L*B]
            BG=sqrt(vi[0]**2+vi[2]**2)
            BV=sqrt(vi[0]**2+vi[1]**2)
            form.ans=[]
            form.ans.append((SovUggrad,'Совмещенный угол, град'))
            form.ans.append((SovUgmin,'Совмещенный угол, мин'))
            form.ans.append((BG,'Биссектрисса в профиле, м'))
            form.ans.append((BV,'Биссектрисса в плане, м'))
    else:
        form=SovUgForm()
    return render(request,'form24950.html',{ 'form':form} )

class ValikForm(forms.Form):
    action='show_Valik'
    title='Устройство валика'
    L=FloatField2(label='Длина валика, м', required=True)
    verh=FloatField2(label='Ширина валика по верху, м', required=True)
    x=FloatField2(label='Откос (1:х)', required=True)
    H=FloatField2(label='Средняя высота валика, м', required=True)
    ans=[]

def show_Valik(request):
    if request.method=='POST':
        form=ValikForm(request.POST)
        if form.is_valid():
            L=form.cleaned_data['L']
            verh=form.cleaned_data['verh']
            x=form.cleaned_data['x']
            H=form.cleaned_data['H']
            niz=verh+(2*x*H)
            hyp=sqrt(H**2+((niz-verh)/2)**2)
            Sotk=(hyp*L)*2+(niz*hyp)*2
            Spol=L*verh
            V=(verh+niz)/2*H*L
            form.ans=[]
            form.ans.append((Sotk,'Площадь откосов, м2'))
            form.ans.append((Spol,'Площадь земляного полотна, м2'))
            form.ans.append((V,'Отсыпка насыпи, м3'))
            form.ans.append((V,'Уплотнение насыпи, м3'))
    else:
        form=ValikForm()
    return render(request,'form24950.html',{ 'form':form} )

class KotlovanForm(forms.Form):
    action='show_Kotlovan'
    title='Рабочий и приемный котолован при горизонтальном бурении'
    pic='kotlovan.PNG'
    RL=FloatField2(label='Рабочий котлован длина (L), м', required=True, initial=20)
    Ra=FloatField2(label='Рабочий котлован ширина (а), м', required=True, initial=3.5)
    Rh=FloatField2(label='Рабочий котлован глубина траншеи, м', required=True)
    Rx=FloatField2(label='Рабочий котлован откос 1:x', required=True)
    PL=FloatField2(label='Приемный котлован длина (L), м', required=True, initial=5)
    Pa=FloatField2(label='Приемный котлован ширина (а), м', required=True, initial=3)
    Ph=FloatField2(label='Приемный котлован глубина траншеи, м', required=True)
    Px=FloatField2(label='Приемный котлован откос 1:x', required=True)
    ans=[]

def show_Kotlovan(request):
    if request.method=='POST':
        form=KotlovanForm(request.POST)
        if form.is_valid():
            RL=form.cleaned_data['RL']
            Ra=form.cleaned_data['Ra']
            Rh=form.cleaned_data['Rh']
            Rx=form.cleaned_data['Rx']
            PL=form.cleaned_data['PL']
            Pa=form.cleaned_data['Pa']
            Ph=form.cleaned_data['Ph']
            Px=form.cleaned_data['Px']
            H=Rh+0.7
            I=H*Rx
            L1=I+RL
            a1=Ra+2*I
            Sosn=RL*Ra
            Sverh=L1*a1
            V=H/3*(Sosn+Sverh+sqrt(Sosn*Sverh))
            S=(Ra+a1)/2*H
            form.ans=[]
            form.ans.append((V,'Объем рабочего котлована, м3'))
            form.ans.append((S,'Крепление стенок рабочего котлована, м2'))
            H=Ph+0.4
            I=H*Px
            L1=PL+I*2
            a1=Pa+2*I
            Sosn=PL*Pa
            Sverh=L1*a1
            V=H/3*(Sosn+Sverh+sqrt(Sosn*Sverh))
            form.ans.append((V,'Объем приемного котлована, м3'))
    else:
        form=KotlovanForm()
    return render(request,'form24950.html',{ 'form':form} )

class SrezkaForm(forms.Form):
    action='show_Srezka'
    title='Ширина срезки'
    pic='LSrezki.PNG'
    dno=FloatField2(label='Ширина траншеи по дну (b), м', required=True)
    H=FloatField2(label='Средняя глубина траншеи (h), м', required=True)
    U=FloatField2(label='Уклон откоса траншеи, 1:х', required=True)
    ans=[]

def show_Srezka(request):
    if request.method=='POST':
        form=SrezkaForm(request.POST)
        if form.is_valid():
            dno=form.cleaned_data['dno']
            H=form.cleaned_data['H']
            U=form.cleaned_data['U']
            L=4+0.5+2*H*U+dno+2+8
            L1=4+0.5+H*U+dno/2
            L2=L-L1
            form.ans=[]
            form.ans.append((L,'Ширина срезки, м'))
            form.ans.append((L1,'Ширина срезки слева от оси трубопровода, м'))
            form.ans.append((L2,'Ширина срезки справа от оси трубопровода, м'))
    else:
        form=SrezkaForm()
    return render(request,'form24950.html',{ 'form':form} )

class TranshForm(forms.Form):
    action='show_Transh'
    title='Объем траншеи'
    L=FloatField2(label='Длина траншеи, м', required=True)
    dno=FloatField2(label='Ширина траншеи по дну, м', required=True)
    H=FloatField2(label='Средняя глубина траншеи, м', required=True)
    D=FloatField2(label='Диаметр трубы, м', required=True)
    U=FloatField2(label='Уклон откоса траншеи, 1:х', required=True)
    ans=[]

def show_Transh(request):
    if request.method=='POST':
        form=TranshForm(request.POST)
        if form.is_valid():
            L=form.cleaned_data['L']
            dno=form.cleaned_data['dno']
            H=form.cleaned_data['H']
            D=form.cleaned_data['D']
            U=form.cleaned_data['U']
            verh=dno+2*H*U
            Strap=(verh+dno)/2*H
            Vtrap=Strap*L
            Vtr=pi*D**2/4*L
            V=Vtrap-Vtr
            if Vtr==0:
                Vvr=0
            else:
                Vvr=V*0.1
            form.ans=[]
            form.ans.append((V-Vvr,'Объем для разработки экскаватором, м3'))
            form.ans.append((Vvr,'Объем для разработки вручную, м3'))
            form.ans.append((V,'Объем обратной засыпки, м3'))
    else:
        form=TranshForm()
    return render(request,'form24950.html',{ 'form':form} )

class VSGazaForm(forms.Form):
    action='show_VSGaza'
    title='Объем стравливания газа (по Дерцакяну стр.33)'
    T=FloatField2(label='Средняя температура стравливаемого газа, град Ц', required=True)
    diam_tr=FloatField2(label='Диаметр трубы, м', required=True)
    dx_tr=FloatField2(label='Толщина стенки трубы, мм', required=True)
    Pn=FloatField2(label='Давление газа на выходе из КС1, кгс/см2', required=True)
    Pk=FloatField2(label='Давление газа на входе в КС2, кгс/см2', required=True)
    L=FloatField2(label='Расстояние между КС1 и КС2, м', required=True)
    x=FloatField2(label='Расстояние от КС1 до точки стравливания, м', required=True)
    L1=FloatField2(label='Длина участка стравливания, м', required=True)
    z=FloatField2(label='К-т сжимаемости газа', required=True)
    ans=[]

def show_VSGaza(request):
    if request.method=='POST':
        form=VSGazaForm(request.POST)
        if form.is_valid():
            T=form.cleaned_data['T']
            diam_tr=form.cleaned_data['diam_tr']
            dx_tr=form.cleaned_data['dx_tr']
            Pn=form.cleaned_data['Pn']
            Pk=form.cleaned_data['Pk']
            L=form.cleaned_data['L']
            x=form.cleaned_data['x']
            L1=form.cleaned_data['L1']
            z=form.cleaned_data['z']
            Px=sqrt(Pn**2-(Pn**2-Pk**2)*x/L)
            V=(pi*(diam_tr-dx_tr/500)**2*L1)/4*Px*293/((273+T)*z*1.033)
            form.ans=[]
            form.ans.append((Px,'Давление в точке стравливания, кгс/см2'))
            form.ans.append((V,'Объем газа для стравливания, м3'))
    else:
        form=VSGazaForm()
    return render(request,'form24950.html',{ 'form':form} )

class VImpulsForm(forms.Form):
    action='show_VImpuls'
    title='Объем импульсного газа для полного однократного открытия+закрытия кранов, в метрах 159 трубы'
    d50=forms.IntegerField(label='Кранов Ду 50, шт',required=True,initial=0)
    d80=forms.IntegerField(label='Кранов Ду 80, шт',required=True,initial=0)
    d100=forms.IntegerField(label='Кранов Ду 100, шт',required=True,initial=0)
    d150=forms.IntegerField(label='Кранов Ду 150, шт',required=True,initial=0)
    d200=forms.IntegerField(label='Кранов Ду 200, шт',required=True,initial=0)
    d300=forms.IntegerField(label='Кранов Ду 300, шт',required=True,initial=0)
    d400=forms.IntegerField(label='Кранов Ду 400, шт',required=True,initial=0)
    d500=forms.IntegerField(label='Кранов Ду 500, шт',required=True,initial=0)
    d700=forms.IntegerField(label='Кранов Ду 700, шт',required=True,initial=0)
    d1000=forms.IntegerField(label='Кранов Ду 1000, шт',required=True,initial=0)
    d1200=forms.IntegerField(label='Кранов Ду 1200, шт',required=True,initial=0)
    d1400=forms.IntegerField(label='Кранов Ду 1400, шт',required=True,initial=0)
    ans=[]

def show_VImpuls(request):
    if request.method=='POST':
        form=VImpulsForm(request.POST)
        if form.is_valid():
            d50=form.cleaned_data['d50']
            d80=form.cleaned_data['d80']
            d100=form.cleaned_data['d100']
            d150=form.cleaned_data['d150']
            d200=form.cleaned_data['d200']
            d300=form.cleaned_data['d300']
            d400=form.cleaned_data['d400']
            d500=form.cleaned_data['d500']
            d700=form.cleaned_data['d700']
            d1000=form.cleaned_data['d1000']
            d1200=form.cleaned_data['d1200']
            d1400=form.cleaned_data['d1400']
            V=float(d50*77+d80*77+d100*257+d150*520+d200*904+d300*2412+d400*6000+d500*6000+d700*15000+d1000*28000+d1200*75000+d1400*75000)
            V=V/100**3
            L=V/0.0195174192*2
            form.ans=[]
            form.ans.append((L,'Длина трубы Ду 150, м'))
            form.ans.append((V,'Объем газа, м3'))
    else:
        form=VImpulsForm()
    return render(request,'form24950.html',{ 'form':form} )

class MassaTrForm(forms.Form):
    action='show_MassaTr'
    title='Труба - масса, площадь и объем'
    diam_tr=FloatField2(label='Диаметр трубы, мм', required=True)
    dx_tr=FloatField2(label='Толщина стенки трубы, мм', required=True)
    dlina=FloatField2(label='Длина трубы, м', required=True)
    ans=[]

def show_MassaTr(request):
    if request.method=='POST':
        form=MassaTrForm(request.POST)
        if form.is_valid():
            diam=form.cleaned_data['diam_tr']
            dx_tr=form.cleaned_data['dx_tr']
            dlina=form.cleaned_data['dlina']
            V1=pi*(diam/1000)**2/4*dlina
            V=pi*((diam-2*dx_tr)/1000)**2/4*dlina
            M1=pi*((diam/1000)**2-((diam-2*dx_tr)/1000)**2)/4*7850
            S=dlina*pi*diam/1000
            L1=pi*diam
            L2=pi*(diam-2*dx_tr)
            form.ans=[]
            form.ans.append(("%.2f" % M1,'Масса 1м трубы, кг'))
            form.ans.append(("%.2f" % (M1*1.01),'Масса 1м трубы с учетом 1% на усиление сварного шва, кг'))
            form.ans.append(("%.2f" % (M1*dlina),'Масса трубы, кг'))
            form.ans.append(("%.2f" % (M1*dlina*1.01),'Масса трубы с учетом 1% на усиление сварного шва, кг'))
            form.ans.append(("%.2f" % S,'Площадь поверхности трубы, м2'))
            form.ans.append(("%.2f" % L1,'Длина внешней окружности трубы, мм'))
            form.ans.append(("%.2f" % L2,'Длина внутренней окружности трубы, мм'))
            form.ans.append(("%.3f" % V1,'Объем трубы, м3'))
            form.ans.append(("%.3f" % V,'Объем полости трубы, м3'))
    else:
        form=MassaTrForm()
    return render(request,'form24950.html',{ 'form':form} )

class VGidroForm(forms.Form):
    action='show_VGidro'
    title='Объем воды для гидроиспытаний (с учетом 15% запаса на смачивание и размыв загрязнений)'
    diam_tr=FloatField2(label='Диаметр трубы, мм', required=True)
    dx_tr=FloatField2(label='Толщина стенки трубы, мм', required=True)
    dlina=FloatField2(label='Длина участка, м', required=True)
    ans=[]

def show_VGidro(request):
    if request.method=='POST':
        form=VGidroForm(request.POST)
        if form.is_valid():
            diam=form.cleaned_data['diam_tr']
            dx_tr=form.cleaned_data['dx_tr']
            dlina=form.cleaned_data['dlina']
            V=pi*(diam/1000-2*dx_tr/1000)**2/4*dlina
            form.ans=[]
            form.ans.append(("%.2f" % (V*1.15),'Объем воды, м3'))
            form.ans.append(("%.2f" % V,'Объем воды (без 15%), м3'))
    else:
        form=VGidroForm()
    return render(request,'form24950.html',{ 'form':form} )

class GOST24950_81Form(forms.Form):
    action='show_gost24950'
    title='Гибка труб по ГОСТ 24950-81'
    diam_tr=forms.ChoiceField(label='Диаметр трубы, мм', required=True,
                    choices=((159,159),(219,219),(273,273),(325,325),(377,377),(426,426),(530,530),(720,720),(820,820),(1020,1020),(1220,1220),(1420,1420)))
    ugol_gibki=FloatField2(label='Угол гибки, грудус', required=True)
    kol_seq=forms.IntegerField(label='Количество секций', required=True)
    posl_ugol=FloatField2(label='Угол последней секции, градус')
    ans=[]

def show_gost24950(request):
    t_par={159:{'urad':15, 'l1':1, 'len':9.8, 'm_ug':27},
           219:{'urad':15, 'l1':1, 'len':9.8, 'm_ug':27},
           273:{'urad':15, 'l1':1, 'len':9.8, 'm_ug':27},
           325:{'urad':15, 'l1':1, 'len':9.8, 'm_ug':27},
           377:{'urad':15, 'l1':1, 'len':9.8, 'm_ug':27},
           426:{'urad':20, 'l1':1, 'len':9.8, 'm_ug':21},
           530:{'urad':25, 'l1':1.9, 'len':11.6, 'm_ug':18},
           720:{'urad':35, 'l1':1.9, 'len':11.6, 'm_ug':9},
           820:{'urad':35, 'l1':1.9, 'len':11.6, 'm_ug':9},
          1020:{'urad':40, 'l1':2.4, 'len':11.6, 'm_ug':9},
          1220:{'urad':60, 'l1':3.5, 'len':11.6, 'm_ug':6},
          1420:{'urad':60, 'l1':3.5, 'len':11.6, 'm_ug':6},
         }
    if request.method=='POST':
        form=GOST24950_81Form(request.POST)
        if form.is_valid():
              diam=int(form.cleaned_data['diam_tr'])
              ugol=form.cleaned_data['ugol_gibki']
              kol_seq=form.cleaned_data['kol_seq']
              posl_ugol=form.cleaned_data['posl_ugol']
              len=t_par[diam]['len']
              max_ugol=t_par[diam]['m_ug']
              l1=t_par[diam]['l1']
              unirad=t_par[diam]['urad']
              l2=pi*unirad*posl_ugol/180
              l3=len-l1-l2
              L=kol_seq*len-l1-l3
              R=(L*180)/(pi*ugol)
              t1=R*tan(radians(ugol/2))
              B=t1**2/(2*R)
              form.ans=[]
              form.ans.append((unirad,'Радиус гибки, м'))
              form.ans.append(('%.2f' % (l1+t1),'T1, м'))
              form.ans.append(('%.2f' % (l3+t1),'T2, м'))
              form.ans.append(('%.4f' % (B,),'Биссектрисса, м'))
              form.ans.append((max_ugol,'Максимальный угол гибки, градус'))
    else:
        form=GOST24950_81Form()
    return render(request, 'form24950.html', {'form': form })
    
class KojuxForm(forms.Form):
    action='show_Kojux'
    title='Опорные кольца кожуха'
    pic='kojux.png'
    dlina=FloatField2(label='Длина кожуха, м (L)', required=True)
    shag=FloatField2(label='Шаг расстановки колец, м (a)', required=True)
    first_colco=FloatField2(label='Отступ от начала кожуха до первого кольца, м (b)', required=True)
    double_colco=forms.BooleanField(label='Удвоенное первое и последнее кольцо', required=False)
    ans=[]

def show_Kojux(request):
    if request.method=='POST':
        form=KojuxForm(request.POST)
        if form.is_valid():
            dlina=form.cleaned_data['dlina']
            shag=form.cleaned_data['shag']
            first_colco=form.cleaned_data['first_colco']
            double_colco=form.cleaned_data['double_colco']
            num_colco=(dlina-2*first_colco)/shag+2-1
            if double_colco:
                num_colco+=2
            form.ans=[]
            form.ans.append(("%d" % (num_colco),'Количество колец, шт'))
    else:
        form=KojuxForm()
    return render(request,'form24950.html',{ 'form':form} )

 
def main(request):
    aps=(PipeForm, GazTUForm, ProgalForm, SovUgForm, ValikForm, KotlovanForm, SrezkaForm,
                    TranshForm, VSGazaForm, VImpulsForm, MassaTrForm, VGidroForm,
                    GOST24950_81Form, VKotlovanForm, KojuxForm)
    l=[]
    for s in aps:
        f=s()
        l.append((f.title,f.action))
    l.append(('Генератор ВР и СО', 'show_Proj'))
    l.append(('Переукладка и балластировка','show_Ballast'))
    l.sort()
    return render(request, 'main.html', {'l':l})
