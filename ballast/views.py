# -*- coding: utf-8 -*-

from django import forms
from django.shortcuts import render

import numpy as np
import matplotlib.pyplot as plt
import re
from math import pi, cos, ceil
import tempfile

class BallastForm(forms.Form):
    action='show_Ballast'    
    title='Переукладка тубопровода с балластировкой'
    data_file=forms.FileField(label='Файл описания объекта:', required=True)


def show_Ballast(request):
    if request.method=='POST':
        form=BallastForm(request.POST, request.FILES)
        if form.is_valid():
            fn=handle_uploaded_file(request.FILES['data_file'])
            file_list=[]
            for i in range(1,7):
                file_list.append(fn+"fig"+str(i)+".png")
            return render(request,'formballast.html', {'form':form, 'fn':file_list})
    else:
        form=BallastForm()
    return render(request,'formballast.html', {'form':form})


def get_k_n(d,p):
#Значение коэффициента надежности по ответственности трубопровода kн для газопроводов (СП 36.13330.2012 табл. 12)
    p_MPA=p/10**6
    if p_MPA<=5.5:
        if d<=1.020:
            return 1.1
        else:
            return 1.155
    if p_MPA<=7.5:
        if d<=1.020:
            return 1.1
        if d<=1.220:
            return 1.155
        else:
            return 1.210
    if p_MPA<=10.0:
        if d<=0.530:
            return 1.1
        if d<=1.020:
            return 1.155
        if d<=1.220:
            return 1.210
        else:
            return 1.265
    return 0    #что-то пошло не так
    

def str_to_arr_rus_float(s):
#преобразовать строку чисел разделенных пробелами в массив float
    s=re.sub(",", ".", s)
    return [float(x) for x in s.split()]
    
def poly_num(x,y,num):
#вернуть сглаженный полиномом num степени массив y(x)
    y_s=np.poly1d(np.polyfit(x,y,num))
    return [y_s(x1) for x1 in x]
    
def Izg_Napr(x,y,D,E):
#изгибающее напряжение в трубопроводе по 5 точкам, по графику y(x), 
#E-модуль упругости, D-внешний диаметр. 2 первые и 2 последние точки не считаем
#возвращем в МПа
    Ksi=[]
    for i in range(2,len(x)-2):
        y_c=np.polyfit(x[i-2:i+3],y[i-2:i+3],2)
        r=1/(2*y_c[0])
        Ksi.append(E*D/(2*r)/10**6)
    return Ksi

def MaxDY(x0,L,x,y):
#расчет расстояния (по y) от прямой через точки y(x0) и y(x0+L) до минимальной точке на кривой y(x)
    x_lin=[x0,x0+L]
    y_s=np.poly1d(np.polyfit(x,y,6))
    y_lin=[y_s(x0),y_s(x0+L)]
    y_s_lin=np.poly1d(np.polyfit(x_lin,y_lin,1))
    min_y=min(y)
    for i in range(0,len(x)):
        if (y[i]-min_y)<0.0001:
            min_x=x[i]
    return y_s_lin(min_x)-min_y

    
def handle_uploaded_file(f):
    #настройка русского шрифта в matplotlib
    from matplotlib import rc
    rc('font',**{'family':'DejaVu Sans'})
    rc('text.latex',unicode=True)
    rc('text.latex',preamble=r'\usepackage[utf8]{inputenc}')
    rc('text.latex',preamble=r'\usepackage[russian]{babel}')

    # D_n=1.42       #наружный диаметр трубопровода, м
    # s_st=0.012     #толщина стенки трубопровода
    # sigma_t=360*10**6 #предел текучести трубопровода Па
    # p=5.4*10**6    #рабочее давление Па
    # p_x=4.7*10**6  #давление в точке переукладки Па
    # L=351          #длина участка переукладки
    # x0=11          #координата начала переукладки
    # m=0.99         #коэффициент условий работы трубопровода (В=0.66  I,II=0.825 III,IV=0.99)
    # k_n_v=1.1      #коэффициент надежности устойчивости положения трубопровода против всплытия (болота=1.05, реки=1.1, реки(200м)=1.15)
    # delta_t_max=31
    # delta_t_min=-13
    # L_ballast=54   #длина участка балластировки, м
    # f1=3.15       #макс расстояние от прямой через точки переукладки до y2d и y_glad 
    # f0=1.03
    
    E=2.06*10**11  #модуль упругости стали Па
    g=9.81         #ускорение свободного падения м/с2
    Ro_st=7850     #плотность стали кг/м3
    Ro_vod=1000    #плотность воды кг/м3
    Ro_bet=2300    #плотность бетона кг/м3
    V_gruza=1.85   #объем 1 груза м3
    n_b=0.9        #к-т надежности по нагрузке 0,9 бетонные грузы, 1-чугунные грузы
    alpha=0.12*10**(-4) #коэффициент линейного расширения стали 1/град
    
    temp_name = next(tempfile._get_candidate_names())
    filename=r'mdvs/mdvs/media/'+temp_name
      
    #заголовки
    f.readline() 
    #основные параметры
    D_n,s_st,sigma_t,p,p_x,L,x0,m,k_n_v,delta_t_max,delta_t_min,L_ballast=str_to_arr_rus_float(f.readline())
    #координата x
    xd=str_to_arr_rus_float(f.readline())
    #отметка трубы
    yd=str_to_arr_rus_float(f.readline())
    #отметка обваловки
    od=str_to_arr_rus_float(f.readline())
    #отметка уровня земли
    ld=str_to_arr_rus_float(f.readline())
    #отметка воды
    vd=str_to_arr_rus_float(f.readline())
    #координата земли в горизонтальной плоскости
    zd=str_to_arr_rus_float(f.readline())
    #отметка переуложенной трубы
    y2d=str_to_arr_rus_float(f.readline())
    #отметка x для воды 
    x_voda=str_to_arr_rus_float(f.readline())

    r_sr=0.5*(D_n-s_st) #средний радиус сечения ТП
    J=pi*r_sr**3*s_st #осевой момент инерции сечения трубы
    W=pi*r_sr**2*s_st #осевой момент сопротивления сечения трубы
    F=2*pi*r_sr*s_st  #площадь сечения стенки трубы, м2

    #рисунок 1
    y_glad=poly_num(xd,yd,6)
    plt.figure(figsize=(13,6.5))
    plt.plot(xd,od,label="1")
    plt.plot(xd,ld,label="2", linestyle = '--')
    plt.plot(x_voda,vd,label="3", linestyle = '-.')
    plt.plot(xd,yd,label="4",  linestyle = ':', linewidth = 2)
    plt.plot(xd,y_glad,label="5", linestyle = '-', linewidth = 2)
    plt.plot(xd,y2d,label="6", linestyle = '-.', linewidth = 2)
    plt.xlabel(u'$x, м$')
    plt.ylabel(u'$y, м$')
    plt.legend()
    plt.grid()
    plt.savefig(filename+"fig1.png")
    plt.clf()

    #расчет f0 и f1
    f0=MaxDY(x0,L,xd,yd)
    f1=MaxDY(x0,L,xd,y2d)
            
    #рисунок 2
    z_glad=poly_num(xd,zd,6)
    plt.figure(figsize=(9,4.5))
    plt.plot(xd,zd,label="1", linewidth = 2)
    plt.plot(xd,z_glad,label="2", linestyle = '--', linewidth = 2)
    plt.xlabel(u'$x, м$')
    plt.ylabel(u'$z, м$')
    plt.legend()
    plt.grid()
    plt.savefig(filename+"fig2.png")
    plt.clf()

    #рисунок 3
    Ksi_y=Izg_Napr(xd,yd,D_n,E)
    Ksi_y_glad=Izg_Napr(xd,y_glad,D_n,E)
    plt.plot(xd[2:-2],Ksi_y,label="1", linewidth = 2)
    plt.plot(xd[2:-2],Ksi_y_glad,label="2", linestyle = '--', linewidth = 2)
    plt.xlabel('$x, м$')
    plt.ylabel(r'$\sigma, МПа$')
    plt.legend()
    plt.grid()
#    plt.figure(figsize=(9,4.5))
    plt.savefig(filename+"fig3.png")
    plt.clf()

    #рисунок 4
    Ksi_z=Izg_Napr(xd,zd,D_n,E) 
    Ksi_z_glad=Izg_Napr(xd,z_glad,D_n,E)
    plt.plot(xd[2:-2],Ksi_z,label="1", linewidth = 2)
    plt.plot(xd[2:-2],Ksi_z_glad,label="2", linestyle = '--', linewidth = 2)
    plt.xlabel('$x, м$')
    plt.ylabel(r'$\sigma, МПа$')
    plt.legend()
    plt.grid()
#    plt.figure(figsize=(9,4.5))
    plt.savefig(filename+"fig4.png")
    plt.clf()

    #рисунок 5
    Ksi_y2=Izg_Napr(xd,y2d,D_n,E)
    Ksi_px=[]
    for i in xd[2:-2]:
        Ksi_px.append((-2*pi**2/L**2*(f1-f0)*E*J*cos(2*pi*(i-x0)/L)/W)/10**6)
    Ksi_sum=[]
    Ksi_px_vert=[]
    for i in range(0, len(Ksi_y2)):
        Ksi_sum.append(((Ksi_y2[i]+Ksi_px[i])**2+Ksi_z_glad[i]**2)**0.5)
        Ksi_px_vert.append(Ksi_y2[i]+Ksi_px[i])
    plt.plot(xd[2:-2],Ksi_px_vert,label="1", linewidth = 2)
    plt.plot(xd[2:-2],Ksi_z_glad,label="2", linestyle = '--', linewidth = 2)
    plt.plot(xd[2:-2],Ksi_sum,label="3", linestyle = '-.', linewidth = 2)
    plt.xlabel('$x, м$')
    plt.ylabel(r'$\sigma, МПа$')
    plt.legend()
    plt.grid()
#    plt.figure(figsize=(9,4.5))
    plt.savefig(filename+"fig5.png")
    plt.cla()

    delta_f=f1-f0
    q_tr=pi*(D_n**2-(D_n-2*s_st)**2)/4*Ro_st*g
    q_iz=2*pi**4*((delta_f)*E*J+0.0938*(f1**3-f0**3)*E*F)/L**4
    k_n=get_k_n(D_n,p)
    Ksi_N=pi**2*(f1**2-f0**2)*E/(4*L**2)
    D_vn=D_n-2*s_st
    Ksi_kc_a=p_x*D_vn/(2*s_st)
    Ksi_kc_b=p*D_vn/(2*s_st)
    Ksi_s_max=max(abs(x) for x in Ksi_sum)
    Ksi_pr_n_a=Ksi_N+0.3*Ksi_kc_a-alpha*delta_t_max-Ksi_s_max*10**6
    Ksi_pr_n_b=Ksi_N+0.3*Ksi_kc_b-alpha*delta_t_min+Ksi_s_max*10**6
    psi3=(1-0.75*(Ksi_kc_a/(m*sigma_t/(0.9*k_n)))**2)**0.5-0.5*Ksi_kc_a/(m*sigma_t/(0.9*k_n))
    Usl_prochnosti=m*sigma_t/(0.9*k_n)

    n_gruz=ceil(pi/4*k_n_v*D_n**2*g*Ro_vod-q_tr+k_n_v*q_iz)*L_ballast/(n_b*(Ro_bet-k_n_v*Ro_vod)*V_gruza*g)
    l_shag=L_ballast/n_gruz

    plt.ylim( -150, 150 )
    plt.title('Результаты расчетов')
    plt.text(50,140,r'$f_0=%0.2f м, f_1=%0.2f м, \Delta f=%0.2f м$' % (f0,f1, delta_f))
    plt.text(50,120,r'$|\sigma_и|=%0.2f МПа, |\sigma_{s.max}|=%0.2fМПа$' % (max(abs(x) for x in Ksi_y_glad), Ksi_s_max ))
    plt.text(50,100,r'$EF=%e Н, EJ=%e Нм^2$' % (E*F, E*J))
    plt.text(50,80,r'$q_{тр}=%.2f МПа, q_{из}=%.2f МПа$' % (q_tr, q_iz))
    plt.text(50,60,r'$k_н=%0.3f, \sigma_N=%0.2f МПа$' % (k_n, Ksi_N/10**6))
    plt.text(50,40,r'$\sigma_{кц(а)}^н=%0.2f МПа, \sigma_{кц(б)}^н=%0.2f МПа$' % (Ksi_kc_a/10**6, Ksi_kc_b/10**6))
    plt.text(50,20,r'$\sigma_{пр(а)}^н=%0.2f МПа, \sigma_{пр(б)}^н=%0.2f МПа$' % (Ksi_pr_n_a/10**6, Ksi_pr_n_b/10**6))
    plt.text(50,00,r'$\psi_3=%.2f$' % (psi3))
    plt.text(50,-20,r'$\psi_3\frac{m}{0.9k_н}R_2^н =%.2f МПа, \frac{m}{0.9k_н}R_2^н =%.2f МПа$' % (psi3*Usl_prochnosti/10**6, Usl_prochnosti/10**6))
    plt.text(50,-40,r'число грузов $n_{УтО}=%d$, шаг установки грузов=%.2fм' % (n_gruz, l_shag))
#    plt.figure(figsize=(9,4.5))
    plt.axis('off')
    plt.savefig(filename+"fig6.png")
    
    return temp_name
