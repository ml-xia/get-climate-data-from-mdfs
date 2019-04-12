from multiprocessing import Pool
from multiprocessing.dummy import Pool as ThreadPool
import urllib.request
import json
import pandas as pd
import numpy as np
import mdfs
from functools import partial
import utils
'''
the main process of download and butch download data from mdfs
auther:Xiahou Jie 2019/3/29
'''

def download(fn,root,dictory):
    service = mdfs.download_mdfs("getData",root,dictory,fn,"","")
    service.getdata()
    data=service.decode()
    print('sucessful------'+fn)
    return data
    
def batch_down(filelist,r,d):
    pool=ThreadPool(8)
    partial_download = partial(download,root=r,dictory=d)
    data=pool.map(partial_download,filelist)
    pool.close()
    pool.join()
    return data
    
#batch_down(["20190306100000.000","20190307100000.000","20190308100000.000"])
#data=download("20190406080000.000",'D:/mdfs/','UPPER_AIR/PLOT/500/')
#utils.tomicaps_station('D:/mdfs/','UPPER_AIR/PLOT/500/','000',data)
#print(list(data.keys()))