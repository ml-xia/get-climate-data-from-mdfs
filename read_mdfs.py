'''
decode the bye data from mdfs download
cover:Xiahou Jie
2019/3/29
'''
# -*- coding: utf-8 -*-
# Author: Puyuan Du

import struct
import datetime
import pickle
import warnings

import numpy as np
#from netCDF4 import Dataset

def create_dict(_dict, index):
    if index not in _dict.keys():
        _dict[index] = list()

corr_dtype = {1:'x', 2:'h', 3:'i', 4:'l', 5:'f', 6:'d', 7:'s'}
corr_size = {1:1, 2:2, 3:4, 4:4, 5:4, 6:8, 7:1}
buf = open('data_table.pickle', 'rb')
var_table = pickle.load(buf)
buf.close()

class MDFS_Station:
    def __init__(self, filepath):
        f = open(filepath, 'rb')
        if f.read(4).decode() != 'mdfs':
            raise ValueError('Not valid mdfs data')
        # Header
        dtype = struct.unpack('h', f.read(2))[0]
        self.data_dsc = f.read(100).decode('gbk').replace('\x00', '')
        self.level = struct.unpack('f', f.read(4))[0]
        self.level_dsc = f.read(50).decode('gbk').replace('\x00', '')
        year, month, day, hour, min_, sec, tz = struct.unpack('7i', f.read(28))
        self.utc_time = datetime.datetime(year, month, day, hour, min_, sec) - datetime.timedelta(hours=tz)
        f.seek(100, 1)#288
        # Data block 1
        station_num = struct.unpack('i', f.read(4))[0] #292
        # Data block 2
        quantity_num = struct.unpack('h', f.read(2))[0] #294
        x = dict([(struct.unpack('h', f.read(2))[0], struct.unpack('h', f.read(2))[0]) for i in range(quantity_num)])
        # Data block 3
        data = {}
        for i in ['ID', 'Lon', 'Lat']:
            create_dict(data, i)
        for i in x.keys():
            create_dict(data, i)
        for _ in range(station_num):
            stid, stlon, stlat = struct.unpack('iff', f.read(12))
            data['ID'].append(stid)
            data['Lon'].append(stlon)
            data['Lat'].append(stlat)
            q_num = struct.unpack('h', f.read(2))[0]
            id_list = list()
            # iterate over q_num
            for __ in range(q_num):
                var_id = struct.unpack('h', f.read(2))[0]
                if var_id % 2 == 0 and var_id not in range(22):
                    var_info = 1
                else:
                    var_info = var_table[var_id]
                    id_list.append(var_id)
                var_value = struct.unpack(corr_dtype[var_info], f.read(corr_size[var_info]))
                if var_value and var_id % 2 != 0:
                    var_value = var_value[0]
                    data[var_id].append(var_value)
            for i in x.keys():
                if i not in id_list:
                    data[i].append(np.nan)
        
        if month<10:
            str_m='0'+str(month)
        else:
            str_m=str(month)
        if day<10:
            str_d='0'+str(day)
        else:
            str_d=str(day)
        if hour<10:
            str_h='0'+str(hour)
        else:
            str_h=str(hour)
        
        data['date']=str(year)+str_m+str_d+str_h
        data['level']=self.level
        data['num']=station_num
        data['datatype']=dtype
        
        self.data = data

class MDFS_Grid:
    def __init__(self, filepath):
        f = open(filepath, 'rb')
        if f.read(4).decode() != 'mdfs':
            raise ValueError('Not valid mdfs data')
        self.datatype = struct.unpack('h', f.read(2))[0]
        self.model_name = f.read(20).decode('gbk').replace('\x00', '')
        self.element = f.read(50).decode('gbk').replace('\x00', '')
        self.data_dsc = f.read(30).decode('gbk').replace('\x00', '')
        self.level = struct.unpack('f', f.read(4))
        year, month, day, hour, tz = struct.unpack('5i', f.read(20))
        self.utc_time = datetime.datetime(year, month, day, hour) - datetime.timedelta(hours=tz)
        self.period = struct.unpack('i', f.read(4))
        start_lon, end_lon, lon_spacing, lon_number = struct.unpack('3fi', f.read(16))
        start_lat, end_lat, lat_spacing, lat_number = struct.unpack('3fi', f.read(16))
        lon_array = np.arange(start_lon, end_lon + lon_spacing, lon_spacing)
        lat_array = np.arange(start_lat, end_lat + lat_spacing, lat_spacing)
        isoline_start_value, isoline_end_value, isoline_space = struct.unpack('3f', f.read(12))
        f.seek(100, 1)
        block_num = lat_number * lon_number
        data = {}
        
        if month<10:
            str_m='0'+str(month)
        else:
            str_m=str(month)
        if day<10:
            str_d='0'+str(day)
        else:
            str_d=str(day)
        if hour<10:
            str_h='0'+str(hour)
        else:
            str_h=str(hour)
        
        data['date']=str(year)+str_m+str_d+str_h
        data['datatype']=self.datatype
        data['level']=self.level
        data['Lon'] = lon_array
        data['stlon']=start_lon
        data['edlon']=end_lon
        data['dlon'] = lon_spacing
        data['nlon']=lon_number 
        data['Lat'] = lat_array
        data['stlat']=start_lat
        data['edlat']=end_lat
        data['dlat'] = lat_spacing
        data['nlat']=lat_number 
        
        if self.datatype == 4:
            # Grid form
            grid = struct.unpack('{}f'.format(block_num), f.read(block_num * 4))
            grid_array = np.array(grid).reshape(lat_number, lon_number)
            data['Grid'] = grid_array
        elif self.datatype == 11:
            # Vector form
            norm = struct.unpack('{}f'.format(block_num), f.read(block_num * 4))
            angle = struct.unpack('{}f'.format(block_num), f.read(block_num * 4))
            norm_array = np.array(norm).reshape(lat_number, lon_number)
            angle_array = np.array(angle).reshape(lat_number, lon_number)
            # Convert stupid self-defined angle into correct direction angle
            corr_angle_array = 270 - angle_array
            corr_angle_array[corr_angle_array < 0] += 360
            data['Norm'] = norm_array
            data['Direction'] = corr_angle_array
        self.data = data

class NetCDFWriter:
    def __init__(self, filepath):
        self.da = Dataset(filepath, 'w', format='NETCDF4')
        self.dimension = []
        self.variable = []

    def _create_dimension(self, dimension, shape):
        self.da.createDimension(dimension, shape)
        self.dimension.append(dimension)

    def _create_variable(self, varname, variable, dimension, datatype='f8'):
        if isinstance(dimension, (tuple, list)):
            for i in dimension:
                if d not in self.dimension:
                    raise ValueError('Dimension {} not created'.format(dimension))
        elif isinstance(dimension, str):
            if dimension not in self.dimension:
                raise ValueError('Dimension {} not created'.format(dimension))
        self.da.createVariable(varname, datatype, dimension)
        self.da.variables[varname][:] = variable
        self.variable.append(varname)

    def _create_attribute(self, attrname, value):
        self.da.setncattr(attrname, value)

    def close(self):
        self.da.close()

    def load_data(self, fileclass):
        if isinstance(fileclass, MDFS_Station):
            self._create_dimension('Station Data', len(fileclass.data['ID']))
            self._create_variable('Longitude', fileclass.data['Lon'], 'Station Data')
            self._create_variable('Latitude', fileclass.data['Lat'], 'Station Data')
            self._create_variable('Station ID', fileclass.data['ID'], 'Station Data')
            for i in fileclass.data.keys():
                if isinstance(i, int):
                    if len(fileclass.data[i]) != len(fileclass.data['ID']):
                        warnings.warn('Variable Size not compatible, skipped', RuntimeWarning)
                    else:
                        self._create_variable('Element ID {}'.format(i), fileclass.data[i], 'Station Data')
        elif isinstance(fileclass, MDFS_Grid):
            self._create_dimension('Longitude', fileclass.data['Lon'][0])
            self._create_dimension('Latitude', fileclass.data['Lat'][:, 0])
            if fileclass.datatype == 4:
                self._create_variable(fileclass.data_dsc, fileclass.data['Grid'], ('Longitude', 'Latitude'))
            elif fileclass.datatype == 11:
                self._create_variable(fileclass.data_dsc + ' Norm', fileclass.data['Norm'], ('Longitude', 'Latitude'))
                self._create_variable(fileclass.data_dsc + ' Direction', fileclass.data['Direction'], ('Longitude', 'Latitude'))
        self._create_attribute('Time', fileclass.utc_time.strftime('%Y-%m-%d %H:%M:%S'))