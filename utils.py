'''
the common functions will be used by the other process
Authers: Xiahou Jie 2019/3/29
'''
import time
import os
import math
from datetime import datetime
import numpy 
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import datetime
import struct

##时间转换函数time ticks##
def timetoticks(t,geshi):
    ticks=time.mktime(time.strptime(t,geshi))
    return ticks

def tickstotime(ticks,geshi):
    timetime=time.strftime(geshi,time.localtime(ticks))
    return timetime
##时间转换函数time ticks##

######时间加减函数#######
def switchtime(t,geshi0,dt,geshi1): #t为时间 geshi为时间格式 dt为时间的变化量（天）
    newtime=tickstotime((timetoticks(t,geshi0)+3600*24*dt),geshi1)
    return newtime

def listfiels(path):
    path = path.replace("\\", "/")
    mlist = os.listdir(path)
    p=[]
    for m in mlist:
        mpath = os.path.join(path, m)
        if os.path.isfile(mpath):
            pt = os.path.abspath(mpath)
            # print pt.decode("gbk").encode("utf-8") #会报错
        else:
            pt = os.path.abspath(mpath)
            listfiels(pt)
        p.append(pt)
    return p

def pathendwith(path,endwith):
    p=[]
    for ph in path:
        if endwith in ph:
            p.append(ph)
    return p


def cal_q(P,td):   #hPa,摄氏度
    A=6.10875;B=24.775;C=4.9283
    e=A*math.exp(B*(1-273.16/(td+273.16)))*(273.16/(td+273.16))**C
    q=662*e/(P-0.378*e)
    return q

def timesmoth(vardf):
    newvardf=vardf
    for t in vardf.index:
        t1=switchtime(str(t),'%Y-%m-%d %H:00:00',-0.5,'%y%m%d%H')
        t2=switchtime(str(t),'%Y-%m-%d %H:00:00',-1,'%y%m%d%H')
        t1=datetime.strptime(t1,'%y%m%d%H')
        t2=datetime.strptime(t2,'%y%m%d%H')
        try:
            newvardf.loc[t]=(vardf.loc[t]+vardf.loc[t1]+vardf.loc[t2])/3
        except:
            print('splits not exist______'+str(t))
    ii=newvardf[newvardf<0].index
    newvardf=newvardf.drop(ii,axis=0)
    
    return newvardf

def sortindex(df):
    df.reset_index(inplace=True)
    df = df.sort_values(by = 'index')
    df.index=df['index']
    del df['index']
    return df

def dclist(mn,mx,n):
    d=(mx-mn)/n
    l=[mn]
    s=mn
    while s<=mx:
        s=s+d
        l.append(s)
    return l
    
def start_time():   #初始化启始预报时间date
    nowtime=datetime.datetime.now().strftime('%y%m%d%H')
    pasttime=(datetime.datetime.now()-datetime.timedelta(days=1)).strftime('%y%m%d%H')
    if float(nowtime[-2:])<15:
        date=pasttime[:-2]+'20'
    else:
        date=nowtime[:-2]+'08'
    return date


def existdir(path):  #判断某目录是否存在,否则创建
    if os.path.exists(path):
        print('dir exist')
    else:
        os.mkdirs(path)
        
def ft():
    ft=['.000','.003','.006','.009','.012','.015','.018','.021','.024','.027','.030','.033','.036','.039','.042','.045','.048','.051','.054','.057','.060','.066','.069','.072','.078','.084','.090','.096','.102','.108','.114','.120','.126','.132','.138','.144','.150','.156','.162','.168','.174','.180','.186','.192','.198','.204','.210','.216','.222','.228','.234','.240']
    return ft
        
        
def tlist(t0,tt):  #[t0,tt)
    t=[t0];add_t=t0
    if len(t0)==8:
        while add_t!=tt:
            add_t=switchtime(add_t,'%y%m%d%H',0.5,'%y%m%d%H')
            t.append(add_t)
    elif len(t0)==10:
        while add_t!=tt:
            add_t=switchtime(add_t,'%Y%m%d%H',0.5,'%Y%m%d%H')
            t.append(add_t)
    elif len(t0)==14:
        while add_t!=tt:
            add_t=switchtime(add_t,'%Y%m%d%H%M%S',0.5,'%Y%m%d%H%M%S')
            t.append(add_t)
    else:
        print('wrong filename');input()
    return t

        
def tomicaps_grid(product_dir,name,ft,data):  #station lon lat height variable
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)
    lon=data['Lon']
    lat=data['Lat']
    dlon=data['dlon']
    dlat=data['dlat']
    nlon=data['nlon']
    nlat=data['nlat']
    stlon=data['stlon']
    stlat=data['stlat']
    edlon=data['edlon']
    edlat=data['edlat']
    t=data['date']
    lev=data['level'][0]
    g=pd.DataFrame(data['Grid'])
    datatype=data['datatype']
    
    fmicaps=open(product_dir+t+'.'+ft,'w')    #ft='012'
    dateend=switchtime(t,'%Y%m%d%H',int(ft)/24,'%Y%m%d%H')
    fmicaps.write('diamond '+str(datatype)+' '+name+'('+t+'.'+ft+':'+dateend+')(夏侯杰提供)\n')
    fmicaps.write(t[:4]+' '+t[4:6]+' '+t[6:8]+' '+t[8:]+' '+str(int(ft))+' '+str(lev)+'\n')
    fmicaps.write(str(dlon)+' '+str(dlat)+' '+str(stlon)+' '+str(edlon)+' '+str(stlat)+' '+str(edlat)+' '+str(nlon)+' '+str(nlat)+' 0 0 0 1 1'+'\n')
    fmicaps.write(g.to_string(header=False,index=False))
    fmicaps.close()
    print('tomicaps------'+t+'.'+ft)
    

def read_type(filepath):
    f = open(filepath, 'rb')
    if f.read(4).decode() != 'mdfs':
        raise ValueError('Not valid mdfs data')
    datatype = struct.unpack('h', f.read(2))[0]
    return datatype
    
    
def tomicaps_station(product_dir,name,ft,data):  #station lon lat height variable
    if not os.path.exists(product_dir):
        os.makedirs(product_dir)
    datatype=data['datatype']
    t=data['date']
    num=int(data['num'])
    lev=int(data['level'])
    col=list(data.keys())
    df=pd.DataFrame(data)
    df.pop('date');df.pop('level');df.pop('num');df.pop('datatype')
    stationlevel=1
    if datatype==2:
        df.insert(4,'stationlevel',stationlevel)
        df.insert(8,'ttd',df[803])
        df.pop(803)
    df.dropna(inplace=True)
    
    
   
    
    fmicaps=open(product_dir+t+'.'+ft,'w')    #ft='012'
    dateend=switchtime(t,'%Y%m%d%H',int(ft)/24,'%Y%m%d%H')
    fmicaps.write('diamond '+str(datatype)+' '+name+'('+t+'.'+ft+':'+dateend+')(夏侯杰提供)\n')
    fmicaps.write(t[:4]+' '+t[4:6]+' '+t[6:8]+' '+t[8:]+' '+str(lev)+' '+str(data['num'])+'\n')
    fmicaps.write(df.to_string(header=False,index=False))
    fmicaps.close()
    print('tomicaps------'+t+'.'+ft)
    

    
    