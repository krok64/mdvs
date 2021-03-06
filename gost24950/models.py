# -*- coding: utf-8 -*-

from django.db import models

class Pipe(models.Model):
    name=models.CharField(max_length=100) #имя трассы
    dy=models.IntegerField()              #Ду трубы
    ltrub=models.FloatField()               #Длина 1 трубы
    def __str__(self):
        return self.name

class Obj(models.Model): 
    l=models.FloatField()               #Длина объекта
    n=models.IntegerField()             #Количество стыков на объекте
    p=models.ForeignKey(Pipe)           #код трассы на которой находится объект
    piket=models.FloatField()              #пикет центра объкта
    comment=models.CharField(max_length=255) #коментарий к объекту
    def __str__(self):
        return self.pk            
