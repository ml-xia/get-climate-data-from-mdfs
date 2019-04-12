import utils
import main

root='D:/mdfs/'
dictory='UPPER_AIR/PLOT/500/'
name=dictory.split('/')[0]+'-'+dictory.split('/')[1]+'_'+dictory.split('/')[2]
t0='20190407080000'
tt='20190408080000'
#ft=utils.ft()
ft='.000'
t=utils.tlist(t0,tt)
if ft=='.000':
    flist=[tt+ft for tt in t]
else:
    flist=[tt+f for f in ft for tt in t]
print(flist);input()
dataset=main.batch_down(flist,root,dictory)
for i,data in enumerate(dataset):
    utils.tomicaps_station(root+'decode/'+dictory,name,flist[i].split('.')[1],data)
