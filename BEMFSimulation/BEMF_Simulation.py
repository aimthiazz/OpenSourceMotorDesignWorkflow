# -*- coding: utf-8 -*-
"""
Simulate Back EMF Voltage for Toyota Prius Motor at different Speed
Pizza Model = only part of the model is simulated and results are extrapolated
Multiprocessing disabled = One instance of simulation is enabled as flux linkage
is constant wrt to speed

Author: Imthiaz Ahmed
"""
"""
Number of workers defined based on number of problems. Since this particular 
multiprocess is not computationally intensive making it equal to 12 workers
"""
#TODO:
# [] Deviation in simulation vs Experimental Results by 1.2

Workers=12
DeviationFactor=1.2
import femm as fem
from femm import *
import math as math
from math import *
from matplotlib import * 
from matplotlib.pyplot import *
import time as myTime
import pandas as pd
import matplotlib.pyplot as plt
from statistics import mean
from numpy import diff
import concurrent.futures
import os 

cwd=os.getcwd()
xldir=cwd+'\ExcelResults'
pltdir=cwd+'\Plots'


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


def BEMFSimulation(BEMFSpeed):
    try:    
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
        
        
        #Reading Geometry
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
        mi_setblockprop('Air',0.1,0,'None',0,1,0)
        mi_clearselected()
        
        mi_addblocklabel(82,5) #Adding RotorAir
        mi_selectlabel(82,5)
        mi_setblockprop('Air',0.1,0,'None',0,1,0)
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
        
    
        
    #Initialization if circuit parameters
        Current = [10] # Amps
        Strands = 9;
        ParallelWires = 13;
        Turns = 117 # 9 strands x 13 wires in parallel 
        Phase_init = 0; #120 # deg electrical angle
        # Phase_step = 8;
        Phase = Phase_init;
        SpeedRPM = BEMFSpeed #RPM
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
        InitialAngle=360/Nslots
        StepAngle=1
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
        Angle=InitialAngle
        mi_modifyboundprop('SlidingBoundary',10,InitialAngle)
        startTime=float(myTime.time())
        startTimeInterval=float(myTime.time())
        avgTorqArray=[]
        
        
        SpeedRPM = BEMFSpeed #RPM
        Freq = Npoles*SpeedRPM/120
        Phase=40
        time=0
        step_vec=[]; 
        torq_vec=[]; 
        time_vec=[]; 
        Phase_vec=[]; 
        PhA_vec=[]; 
        PhB_vec=[]; 
        PhC_vec=[];
        CircPropA=[]
        CircPropB=[]
        CircPropC=[]
        
        #Simulation Start
            
        for i in range((niterat)):
            Curr_PhA = 0 
            Curr_PhB = 0
            Curr_PhC = 0
    
            mi_modifycircprop('A',1,Curr_PhA) 
            mi_modifycircprop('B',1,Curr_PhB) 
            mi_modifycircprop('C',1,Curr_PhC) 
            mi_modifyboundprop('SlidingBoundary',10,Angle)
    
            mi_saveas('BEMF'+str(BEMFSpeed)+'.FEM')
            mi_clearselected() 
            smartmesh(1)
            mi_analyze(0);  
            mi_loadsolution();
            
            #Uncomment if you want to save the density plot
            
            # mo_showdensityplot(1,0,2,0.0,'mag');
            # mo_savebitmap('SinglePoimt'+'Current'+str(Current[j])+'_'+str(i)+'.png')
            
            Angle=Angle+StepAngle
    
            CircPropA.append(mo_getcircuitproperties('A'))
            CircPropB.append(mo_getcircuitproperties('B'))
            CircPropC.append(mo_getcircuitproperties('C'))
            
        
    
            time_vec.append(time) 
            Phase_vec.append(Phase) 
            torq_vec.append(Torque)
            time = time + 1/Freq/niterat  

            InitialAngle =0; 

    
        totTorq.append(torq_vec)
        avgTorqArray.append(mean(torq_vec))
        nowTime=myTime.time()
        fluxLinkageA=[]
        fluxLinkageB=[]
        fluxLinkageC=[]
    
        for i in range(len(CircPropA)):
            fluxLinkageA.append(CircPropA[i][2])
            fluxLinkageB.append(CircPropB[i][2])
            fluxLinkageC.append(CircPropC[i][2])
        
        closefemm()
        
        return fluxLinkageA,fluxLinkageB,fluxLinkageC,niterat
        
    
        
    except Exception as e:
        return e
        

def BEMFcomputation(fluxLinkageA,fluxLinkageB,fluxLinkageC,BEMFSpeed,niterat):
    try:
        Npoles=8
        SpeedRPM = BEMFSpeed #RPM
        Freq = Npoles*SpeedRPM/120
        Phase=40
        time=0
        step_vec=[]; 
        torq_vec=[]; 
        time_vec=[];
        diffactor=Npoles/DeviationFactor
        
            
    
    
        dt=(1/(6*SpeedRPM))
        time=0
        for i in range(len(fluxLinkageA)):
            time=time+dt*1
            time_vec.append(time)
        
        bemfA=diffactor*(diff(fluxLinkageA)/dt) #Line Neutral
        bemfB=diffactor*(diff(fluxLinkageB)/dt)
        bemfC=diffactor*(diff(fluxLinkageC)/dt)
        
        bemfTimeArray=[]
        bemfTimeArray.append(time_vec)
        bemfTimeArray[0].pop(len(bemfTimeArray[0])-1)
        figure()
        plot(bemfTimeArray[0],bemfA)
        plot(bemfTimeArray[0],bemfB)
        plot(bemfTimeArray[0],bemfC)
        title('Phase Voltage '+str(SpeedRPM)+' RPM')
        xlabel('Time(sec)')
        ylabel('Voltage(V)')
        plt.savefig(pltdir+'\BEMF-PHASE_'+str(SpeedRPM)+'.png')
    
        figure()
        title('Line Voltage '+str(SpeedRPM)+' RPM')
        plot(bemfTimeArray[0],bemfA-bemfB)
        plot(bemfTimeArray[0],bemfB-bemfC)
        plot(bemfTimeArray[0],bemfC-bemfA)
        xlabel('Time(sec)')
        ylabel('Voltage(V)')
        plt.savefig(pltdir+'\BEMF-LINE_'+str(SpeedRPM)+'.png')
        
        data = [time_vec,fluxLinkageA,fluxLinkageB,fluxLinkageC]
        alldata=pd.DataFrame(data)
        alldata=alldata.T
        alldata.columns=['Time','FA','FB','FC']
        alldata.to_excel(xldir+'\Fluxlinkage'+str(SpeedRPM)+'.xlsx',index=False)
        
        data=[bemfTimeArray[0],bemfA,bemfB,bemfC]
        alldata=pd.DataFrame(data)
        alldata=alldata.T
        alldata.columns=['Time','VA-Phase','VB-Phase','VC-Phase']
        alldata.to_excel(xldir+'\PhaseVoltage'+str(SpeedRPM)+'.xlsx',index=False)
        
        data=[bemfTimeArray[0],bemfA-bemfB,bemfB-bemfC,bemfC-bemfA]
        alldata=pd.DataFrame(data)
        alldata=alldata.T
        alldata.columns=['Time','VA-Phase','VB-Phase','VC-Phase']
        alldata.to_excel(xldir+'\LineVoltage'+str(SpeedRPM)+'.xlsx',index=False)
        
        
        
    
        print("Max of LL Voltage is for " +str(SpeedRPM) + " is "+str(max(bemfA-bemfB)))
        
    
        return SpeedRPM,max(bemfA-bemfB)     
    
    except Exception as e:
        return e


task=[]


def main(fA,fB,fC,niterat):
    executor = concurrent.futures.ProcessPoolExecutor(max_workers=Workers)
    SpeedArray=[500,1000,1500,2000,2500,3000,3500,4000,4500,5000,5500,6000]
    for spd in SpeedArray:
        task.append(executor.submit(BEMFcomputation,fA,fB,fC,spd,niterat))
    print("Process Initalized and Running")

    status = False
    while not status:
        for t in task:
            if not t.done():
                status = False
                break
            else:
                status = True

    for t in task:
        print(t.result())





    
if __name__ == '__main__':
    startTime=float(myTime.time())
    [fA,fB,fC,niterat]=BEMFSimulation(1000)
    main(fA,fB,fC,niterat)
    print("End of Simulation")
    nowTime=myTime.time()
    print("Total Time",abs(startTime-nowTime))










    
        