import urllib.request
import json
import pandas as pd
import numpy as np
import read_mdfs
import os
import utils

'''
download data from mdfs and decode.
auther: Xiahou Jie 2019/3/29
'''
class download_mdfs:
    
    def __init__(self,request,root,directory,filename,fr,ul):
        self.root=root
        self.request=request
        self.directory=directory
        self.filename=filename
        self.fr=fr
        self.ul=ul
        
    def baseurl(self):
        url="http://10.116.32.66:8080/DataService?requestType="+self.request+"&directory="+self.directory+"&fileName="+self.filename+"&filter="+self.fr+"&url="+self.ul
        return url
    
    def getdata(self):
        url=self.baseurl()
        f=urllib.request.urlopen(url)
        #x=f.read().decode('gbk','ignore')
        x=f.read()
        #print(x[:500].decode('gbk','ignore'));input()
        ii=x.find(b'mdfs')      #略去文件头
        try:
            os.makedirs(self.root+'origion/'+self.directory)
        except FileExistsError:
            ff=open(self.root+'origion/'+self.directory+self.filename,'wb')
            ff.write(x[ii:])
            #ff.write(x)
            ff.close()
        else:
            ff=open(self.root+'origion/'+self.directory+self.filename,'wb')
            ff.write(x[ii:])
            #ff.write(x)
            ff.close()
        
        
    def deGrid(self):
        f = read_mdfs.MDFS_Grid(self.root+'origion/'+self.directory+self.filename)
        data=f.data
        return f.data
    
    def deStation(self):
        f = read_mdfs.MDFS_Station(self.root+'origion/'+self.directory+self.filename)
        data=f.data
        return f.data
        
        
    def decode(self):
        tp=utils.read_type(self.root+'origion/'+self.directory+self.filename)
        if tp==4 or tp==11:
            data=self.deGrid()
        else:
            data=self.deStation()
        return data
        
     
   
