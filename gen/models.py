# -*- coding: utf-8 -*-

from django.db import models

#Таблица соответствий Ду к Д
DYD={10:(14,), 15:(22,), 20:(25,28), 25:(32,), 32:(38,), 40:(45,), 50:(57,), 65:(76,),
     80:(89,), 100:(108,114), 125:(133,), 150:(159,168), 200:(219,), 250:(273,),
     300:(325,), 350:(377,), 400:(426,), 500:(530,), 600:(630,), 700:(720,),
     800:(820,), 900:(920,), 1000:(1020,), 1200:(1220,), 1400:(1420,), 1700:(1720,) }

#Таблица площадей поверхности кранов, м3
KranArea={10:0.2, 15:0.2, 20:0.2, 25:0.3, 32:0.3, 40:0.5, 50:0.7, 65:0.7,
     80:0.8, 100:1.0, 125:1.0, 150:1.2, 200:1.5, 250:1.6,
     300:1.7, 350:1.7, 400:2.0, 500:3.5, 600:3.5, 700:5.0,
     800:5.0, 900:5.0, 1000:7.0, 1200:8.6, 1400:10.0, 1700:10.0 }


#Таблица 7 из ГОСТ 12821-80 размеры фланцев Ру 6,3 МПа
#Ду:h4,Dm
Flanec7={10:(46,34),15:(46,38),20:(54,48),25:(56,52),32:(60,64),40:(65,74),50:(67,86),65:(72,106),80:(72,120),100:(77,140),
        125:(95,172),150:(105,206),175:(105,232),200:(110,264),225:(115,290),250:(115,316),300:(120,370),350:(140,430),
        400:(155,484),500:(165,594),600:(180,704),700:(225,820),800:(225,920),900:(265,1050),1000:(280,1160),1200:(315,1386)
        }

ALL_D=((14,'14'),
       (22,'22'),
       (25,'25'),
       (28,'28'),
       (32,'32'),
       (38,'38'),
       (45,'45'),
       (57,'57'),
       (76,'76'),
       (89,'89'),
       (108,'108'),
       (114,'114'),
       (133,'133'),
       (159,'159'),
       (168,'168'),
       (219,'219'),
       (273,'273'),
       (325,'325'),
       (377,'377'),
       (426,'426'),
       (530,'530'),
       (630,'630'),
       (720,'720'),
       (820,'820'),
       (1020,'1020'),
       (1220,'1220'),
       (1420,'1420'),
       (1720,'1720'),)

ALL_Dy=((10,'10'),
        (15,'15'),
        (20,'20'),
        (25,'25'),
        (32,'32'),
        (40,'40'),
        (50,'50'),
        (65,'65'),
        (80,'80'),
        (100,'100'),
        (125,'125'),
        (150,'150'),
        (200,'200'),
        (250,'250'),
        (300,'300'),
        (350,'350'),
        (400,'400'),
        (500,'500'),
        (600,'600'),
        (700,'700'),
        (800,'800'),
        (900,'900'),
        (1000,'1000'),
        (1200,'1200'),
        (1400,'1400'),
        (1700,'1700'),)

CLIMAT_NORM='U'
CLIMAT_HOLOD='S'
CLIMAT_ISP_CH=( (CLIMAT_NORM, 'Умеренное исп.'),
                (CLIMAT_HOLOD, 'Северное исп.'))

UST_NAD='N'
UST_POD='P'
USTANOVKA_CH=((UST_NAD,'Надземная'),
              (UST_POD,'Подземная'),)

PRIVOD_GIDRO='G'
PRIVOD_HAND='H'
PRIVOD_ELECTRO='E'
PRIVOD_CH=((PRIVOD_GIDRO, 'пневмогидропривод'),
           (PRIVOD_HAND, 'ручной привод'),
           (PRIVOD_ELECTRO, 'электропривод'),)

ED_IZM_SHT='S'
ED_IZM_COMPL='C'
ED_IZM_UZEL='U'
ED_IZM_KG='K'
ED_IZM_M='M'
ED_IZM_CH=((ED_IZM_SHT,'шт'),
           (ED_IZM_COMPL,'компл'),
           (ED_IZM_UZEL,'узел'),
           (ED_IZM_KG,'кг'),
           (ED_IZM_M,'м'),)

COUNT_NUM='N'
COUNT_NSPLIT='NS'
COUNT_MSPLIT='MS'
COUNT_CH=((COUNT_NUM,'Количество'),
          (COUNT_NSPLIT,'Количество с разделением на подземные и надземные'),
          (COUNT_MSPLIT,'Метры с разделением на подземные и надземные'))

class Spec(models.Model):
    name=models.CharField(max_length=100,verbose_name='Название проекта')     #название спецификации
    date=models.DateField(auto_now_add=True,verbose_name='Дата создания')  #дата создания
    comment=models.CharField(max_length=1000,verbose_name='Описание') #описание спецификации
    ClimIsp=models.CharField(max_length=1,
                             choices=CLIMAT_ISP_CH,
                             default=CLIMAT_NORM,verbose_name='Климатическое исполнение')             #код климатического исполнения
    Prab=models.FloatField(verbose_name='Рабочее давление, МПа')                  #Рабочее давление
    NumTry=models.CharField(max_length=100,verbose_name='Список к-ов давлений испытания')   #список давлений на испытания
    def __str__(self):
        return self.name

class ItemType(models.Model):
    name=models.CharField(max_length=100, verbose_name='Название типа')
    ed_izm=models.CharField(max_length=2,
                            choices=ED_IZM_CH,
                            default=ED_IZM_SHT,
                            verbose_name='Единица измерения')
    is_split=models.BooleanField(verbose_name='Разделять подземную и надземную часть')
    is_dlina=models.BooleanField(verbose_name='Длина')
    is_visota=models.BooleanField(verbose_name='Высота')
    is_m=models.BooleanField(verbose_name='Масса')
    is_s=models.BooleanField(verbose_name='Толщина стенки')
    is_d=models.BooleanField(verbose_name='Диаметр')
    is_dy=models.BooleanField(verbose_name='Условный диаметр')
    is_d2=models.BooleanField(verbose_name='Диаметр отвода')
    is_s2=models.BooleanField(verbose_name='Толщина стенки отвода')
    is_privod=models.BooleanField(verbose_name='Привод')
    is_ust=models.BooleanField(verbose_name='Установка')
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Zavod(models.Model):
    name=models.CharField(max_length=100,verbose_name='Название предприятия')
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class TU(models.Model):
    name=models.CharField(max_length=100, verbose_name='Название ТУ/ГОСТ')
    type=models.ForeignKey(ItemType, verbose_name='Тип детали')
    zavod=models.ForeignKey(Zavod, verbose_name='Завод изготовитель')
    def __str__(self):
        return self.name
    class Meta:
        ordering = ['name']

class Item(models.Model):
    type=models.ForeignKey(ItemType, verbose_name='Тип')
    name=models.TextField(verbose_name='Название детали')     #имя детали, без указания типа
    dlina=models.FloatField(verbose_name='Длина, мм', null=True, blank=True)   #длина детали, мм
    visota=models.FloatField(verbose_name='Высота, мм', null=True, blank=True)  #высота детали, мм (для тройников)
    m=models.FloatField(verbose_name='Масса, кг', null=True, blank=True)       #масса детали, кг (для трубы масса 1м)
    s=models.FloatField(verbose_name='Толщина стенки детали, мм', null=True, blank=True)       #толщина стенки детали, мм
    d=models.IntegerField(choices=ALL_D, verbose_name='Диаметр детали, мм', null=True, blank=True) #диаметр детали, мм
    dy=models.IntegerField(choices=ALL_Dy, verbose_name='Условный диаметр детали, мм', null=True, blank=True) #условный диаметр
    d2=models.IntegerField(choices=ALL_D, verbose_name='Диаметр 2, мм', null=True, blank=True)  #диаметр (для тройников, переходов), мм
    s2=models.FloatField(verbose_name='Толщина стенки 2, мм', null=True, blank=True)                 #толщина стенки (для тройников, переходов), мм
    s_name=models.CharField(max_length=100, verbose_name='Имя для спецификации', blank=True)   #имя детали для записи в спецификацию
    tu=models.ForeignKey(TU,related_name='+', verbose_name='ТУ на деталь', null=True, blank=True)       #ту на деталь
    tu2=models.ForeignKey(TU,related_name='+', verbose_name='ТУ на изоляцию', null=True, blank=True)     #ту на изоляцию детали
    material=models.CharField(max_length=100, verbose_name='Материал детали или изоляции', blank=True)   #материал детали или изоляции
    privod=models.CharField(choices=PRIVOD_CH, max_length=2, verbose_name='Привод', blank=True)
    ust=models.CharField(choices=USTANOVKA_CH, max_length=2, verbose_name='Установка', blank=True)
    zav_is=models.BooleanField(verbose_name='Заводская изоляция')
    def __str__(self):
        return self.name

class ItemList(models.Model):
    item=models.ForeignKey(Item, verbose_name='Деталь')
    spec=models.ForeignKey(Spec, verbose_name='Проект')
    numAll=models.FloatField(verbose_name='Количество всего')
    numPod=models.FloatField(verbose_name='Количество подземной установки')
    numNad=models.FloatField(verbose_name='Количество надземной установки')
    isHydroIsp=models.BooleanField(verbose_name='Учитывать в гидроиспытаниях')


