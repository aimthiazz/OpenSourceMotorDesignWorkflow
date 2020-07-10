
# -*- coding: utf-8 -*-
"""
DQ Inductance computation
Author: Imthiaz Ahmed
"""

import femm as fem
from femm import *
import math as math
from math import *
from matplotlib import * 
from matplotlib.pyplot import *
import time as myTime
import pandas as pd
import matplotlib.pyplot as plt
import xlwt
from statistics import mean
import os


cwd=os.getcwd()
savedir=cwd+'\Results'

def rotate(origin, point, angle):
    """
    Rotate a point counterclockwise by a given angle around a given origin.
    The angle should be given in radians.
    """
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

openfemm()
newdocument(0)


Length = 83.6;# #mm motor length
mi_probdef(0,'millimeters','planar',1e-8,Length,30,1)

## Stator Geometry
Nslots = 48;
StatorOD = 269;
StatorID = 161.93;
ShoeHeight = 1.02;# Hs0
ShoeRadius = 0.50;# Hs1
SlotHeight = 29.16;# Hs2
SlotDia = 5.64; # 2Rs
PostHeight = SlotDia/2+SlotHeight+ShoeRadius+ShoeHeight;
SlotOpen = 1.93; #Bs0
SlotWidthTop = 3.15;
SlotWidthBot = SlotDia;
StatorPitchAirgap = pi*StatorID/Nslots;
StatorPitchSlotTop = pi*(StatorID+2*ShoeHeight)/Nslots;
StatorPitchSlotBot = pi*(StatorID+2*ShoeHeight+2*ShoeRadius+2*SlotHeight)/Nslots;
PostThickTop = StatorPitchSlotTop-SlotWidthTop;
PostThickBot = StatorPitchSlotBot-SlotWidthBot;

Npoles = 8;
RotorOD = 160.47;
RotorID = 111;
BridgeID = 9.4;
DuctMinDia = RotorID+2*BridgeID;
DuctThick = 4.7;
RibHeight = 3;
RibWidth = 14;
DistMinMag = 3;
MagThick = 6.5;
MagWidth = 18.9;
Bridge = 1.42;
DuctMaxDia = RotorOD-2*Bridge;
alpha = 72.5;
theta = 360/Npoles/2;


mi_readdxf('prius_mm_pizza.dxf')
mi_zoomnatural()

#AddingMaterial
mi_getmaterial('Air')
mi_getmaterial('20 AWG')
mi_addmaterial('19 AWG',1.0,1.0,0,0,58,0,0,0,3,0,0,1,0.912)
mi_addmaterial('N36Z_20',1.03,1.03,920000,0,0.667)
mi_addmaterial('M19_29G',0,0,0,0,1.9,0.34,0,0.94,0)
b=[0,0.05,0.1,0.15,0.36,0.54,0.65,0.99,1.2,1.28,1.33,1.36,1.44,1.52,
 1.58,1.63,1.67,1.8,1.9,2,2.1,2.3,2.5,2.563994494,3.7798898740]
h=[0,22.28,25.46,31.83,47.74,63.66,79.57,159.15,318.3,477.46,636.61,
795.77,1591.5,3183,4774.6,6366.1,7957.7,15915,31830,111407,190984,
350135,509252,560177.2,1527756]
for n in range(0,len(b)):
    mi_addbhpoint('M19_29G',b[n],h[n])



r0=0.5*StatorOD
ri=0.5*RotorID
r0In=0.5*StatorID
riOut=0.5*RotorOD


#AddingBlockLabels
#At this point I am directly refering the geometry for coordinates
mi_addblocklabel(0.95*r0,5) #Adding StatorLabel
mi_selectlabel(0.95*r0,5)
mi_setblockprop('M19_29G',1,0,'None',0,1,0)
mi_clearselected()

mi_addblocklabel(0.95*r0In,5) #Adding RotorLabel
mi_selectlabel(0.95*r0In,5)
mi_setblockprop('M19_29G',1,0,'None',0,1,0)
mi_clearselected()

mi_addblocklabel(82.83,5) #Adding StatorAir
mi_selectlabel(82.83,5)
mi_setblockprop('Air',0,0.1,'None',0,1,0)
mi_clearselected()

mi_addblocklabel(82,5) #Adding RotorAir
mi_selectlabel(82,5)
mi_setblockprop('Air',0,0.1,'None',0,1,0)
mi_clearselected()

mi_addblocklabel(r0In+10,5) #Adding Winding
mi_selectlabel(r0In+10,5)
mi_setblockprop('20 AWG',1,0,'None',0,1,0) 
mi_copyrotate(0,0,360/Nslots,5)
mi_clearselected()

mi_addblocklabel(68,16.5) #Adding RotorMagnet1
mi_selectlabel(68,16.5)
mi_setblockprop('N36Z_20',1,0,'None',40,3,0)
mi_clearselected()


mi_addblocklabel(60,36.5) #Adding RotorMagnet2
mi_selectlabel(60,36.5)
mi_setblockprop('N36Z_20',1,0,'None',5,3,0)
mi_clearselected()

mi_addblocklabel(75,9) #Adding Airpocket
mi_selectlabel(75,9)
mi_setblockprop('Air',1,0,'None',0,1,0)
mi_clearselected()

mi_addblocklabel(62,25) #Adding Airpocket
mi_selectlabel(62,25)
mi_setblockprop('Air',1,0,'None',0,1,0)
mi_clearselected()


mi_addblocklabel(60,47) #Adding Airpocket  
mi_selectlabel(60,47)
mi_setblockprop('Air',1,0,'None',0,1,0)
mi_clearselected()



#adding boundary
#Anti periodic Boundary = Since 1 pole is present adding Antiperiodic boundary


mi_addboundprop('AirBound',0,0,0,0,0,0,0,0,0) #Vector Potential Boundary
mi_selectarcsegment(125,50)
mi_selectarcsegment(51,21)
mi_setarcsegmentprop(5,'AirBound',0,1);
mi_clearselected()


mi_addboundprop('pb1',0,0,0,0,0,0,0,0,5,0,0) #Stator Side Boundary
mi_selectsegment(80,80)
mi_selectsegment(100,0)
mi_setsegmentprop('pb1',1,0,0,0)
mi_clearselected()



mi_addboundprop('pb2',0,0,0,0,0,0,0,0,5,0,0) #Stator Air Boundary
mi_selectsegment(58.5,58.5)
mi_selectsegment(82.7,0)
mi_setsegmentprop('pb2',1,0,0,0)
mi_clearselected()

mi_addboundprop('pb3',0,0,0,0,0,0,0,0,5,0,0) #Rotor Air Boundary
mi_selectsegment(58.1,58.1)
mi_selectsegment(82.21,0)
mi_setsegmentprop('pb3',1,0,0,0)
mi_clearselected()

mi_addboundprop('pb4',0,0,0,0,0,0,0,0,5,0,0) #Rotor Air Boundary
mi_selectsegment(53,53)
mi_selectsegment(75,0)
mi_setsegmentprop('pb4',1,0,0,0)
mi_clearselected()



mi_addboundprop('SlidingBoundary',0,0,0,0,0,0,0,0,7,0,-67.5) #SlidingBoundary
mi_selectarcsegment(82.5,5)
mi_selectarcsegment(82.2,5)
mi_setarcsegmentprop(0.1,'SlidingBoundary',0,0)
mi_clearselected()



mi_saveas('LdLqComputation.FEM')
mi_zoomnatural()
mi_createmesh()


Current = [50] # Amps
Strands = 9;
ParallelWires = 13;
Turns = 117 # 9 strands x 13 wires in parallel 
Phase_init = 120; #120 # deg electrical angle
# Phase_step = 8;
Phase = Phase_init;
SpeedRPM = 1000 #RPM
Freq = Npoles*SpeedRPM/120 # Hz
time = 0;
mi_addcircprop('A',Current[0]*sin(2*pi*Freq*time+Phase*pi/180),1)
mi_addcircprop('B',Current[0]*sin(2*pi*Freq*time+Phase*pi/180+2*pi/3),1)
mi_addcircprop('C',Current[0]*sin(2*pi*Freq*time+Phase*pi/180+4*pi/3),1)    
Circuit = ['A','A','B','B','C','C']
CoilDir = [+1,+1,-1,-1,+1,+1]

origin=(0,0)
point=(r0In+10,5)
for i in range(len(Circuit)):
    x,y=rotate(origin,point,radians(i*7.5))
    mi_selectlabel(x,y)
    mi_setblockprop('19 AWG',1,0,Circuit[i],0,1,CoilDir[i]*Strands)
    mi_clearselected()


 
mi_zoomnatural()
PhaseArray=[40]
niterat=90;
StepAngle=1;
Angle=0
k=0;
Torque=0;
step_vec=[];
torq_vec=[];
time_vec=[];
Phase_vec=[];
Phase_max=[];
Torque_max=[];
PhA_vec=[];
PhB_vec=[];
PhC_vec=[];
totTorq=[]
CircProp=[]
InitialAngle=0
mi_modifyboundprop('SlidingBoundary',10,InitialAngle)
startTime=float(myTime.time())
startTimeInterval=float(myTime.time())
avgTorqArray=[]
InitialAngle=0
InductArray=[]
AngleArray=[]
LdAngle=30
LqAngle=55.5
Ld=[]
Lq=[]
Current=[50,75,100,125,150,175,200,225,250]
for j in range(len(PhaseArray)):
    Phase=PhaseArray[j]
    time=0
    step_vec=[]; 
    torq_vec=[]; 
    time_vec=[]; 
    Phase_vec=[]; 
    PhA_vec=[]; 
    PhB_vec=[]; 
    PhC_vec=[];
    LdCircProp=[]
    LqCircProp=[]
    for i in range(len(Current)):
        Curr_PhA = Current[i]*sin(2*pi*Freq*time+Phase*pi/180); 
        Curr_PhB = Current[i]*sin(2*pi*Freq*time+Phase*pi/180+2*pi/3);   
        Curr_PhC = Current[i]*sin(2*pi*Freq*time+Phase*pi/180+4*pi/3);

        mi_modifycircprop('A',1,Curr_PhA) 
        mi_modifycircprop('B',1,Curr_PhB) 
        mi_modifycircprop('C',1,Curr_PhC) 
        
        
        mi_modifyboundprop('SlidingBoundary',10,LdAngle)
        mi_saveas('LdLqComputation.FEM')
        mi_clearselected() 
        smartmesh(1)
        mi_analyze(0); 
        mi_loadsolution();
        LdCircProp.append(mo_getcircuitproperties('A'))
        Ld.append(1000*((Npoles*LdCircProp[i][2]/Current[i])/1.2))
        
        
        mi_modifyboundprop('SlidingBoundary',10,LqAngle)
        mi_saveas('LdLqComputation.FEM')
        mi_clearselected() 
        smartmesh(1)
        mi_analyze(0);  
        mi_loadsolution();
        LqCircProp.append(mo_getcircuitproperties('A'))
        Lq.append(1000*((Npoles*LqCircProp[i][2]/Current[i])/1.2))
        
        

    






nowTime=myTime.time()
title('DQ Inductance Plot')
xlabel('Current(A)')
ylabel('Inductance(mH)')
plot(Current,Ld,label='Ld',color='b')
plot(Current,Lq,label='Lq',color='r')
legend(loc='best')
print("Total Time",abs(startTime-nowTime))
savefig(savedir+'\LdLqPlots.png')