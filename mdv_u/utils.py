# -*- coding: utf-8 -*-

from django import forms

class FloatField2(forms.FloatField):
    """ Переопределение поля для ввода чисел с плавающей точностью так чтобы
    небыло разницы между . и ,
    """
    def to_python(self, value):
        value=str(value).replace(",",".")
        return super(FloatField2, self).to_python(value)
