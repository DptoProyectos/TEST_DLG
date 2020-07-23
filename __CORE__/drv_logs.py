#!/drbd/www/cgi-bin/spx/aut_env/bin/python3.6
'''
DRIVER PARA EL TRABAJO CON LOGS

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.1 07-06-2020 
''' 

## LIBRERIAS
import os
import json

#CONEXIONES
from io import open
from __CORE__.drv_dlg import read_param
from __CORE__.drv_config import path_log,easy_log,path_easy_log, name_log_ctrl_error, name_log_dlg_performance
from __CORE__.mypython import system_date,system_date_raw,system_hour,is_list,is_par


class saved_logs(object):
    '''
        Clase que genera los logs que se guardan en la PC
        
        header => 07/06/2020 20:01:22 [MER001] TEXTO
    '''
    def __init__(self,name_log, dlgid = 'null', path_log = path_log):
        '''
            name_log = nombre del archivo que va a servir de log
            dlgid    = datalogger que genera el log.
            path_log = ruta en donde se va a crear el log
        '''
        self.name_log = name_log
        self.path_log = path_log
        self.dlgid = dlgid
        
        # CREO LA CARPETA DONDE VA A ESTAR EL LOG
        if not(os.path.exists(path_log)): 
            os.makedirs(f"{path_log}",0o777)
            
        # CREO EL ARCHIVO EN DONDE SE VAN A REGISTRAR LOS LOGS
        log = open(f"{path_log}{name_log}.log",'a')
        #
        # CERRAMOS EL LOG
        log.close()
        #
        # DOY PERMISOS 777 AL ARCHIVO CREADO
        try:
            os.chmod(f"{path_log}{name_log}.log", 0o777)
        except Exception as err_var:
            log.write(f"{system_date} {system_hour} [{self.dlgid}] {err_var}\n") 
            
    def write(self, message): 
        # ABRO EL ARCHIVO LOG
        log = open(f"{self.path_log}{self.name_log}.log",'a')
               
        # EXCRIBIMOS EL LOG
        log.write(f"{system_date} {system_hour} [{self.dlgid}] {message}\n") 
        
        # CERRAMOS EL LOG
        log.close()
        
class ctrl_logs(object):
    '''
        Clase que maneja el tema de los logs tanto de pantalla como de archivo
        que se mandan desde los scripts
    '''
    def __init__(self,SERVICE,process_name,DLGID_CTRL,show_log):
        '''
        Constructor
        '''
        self.SERVICE = SERVICE
        self.process_name = process_name
        self.DLGID_CTRL = DLGID_CTRL
        self.show_log = show_log
        self.script_performance = saved_logs(name_log_ctrl_error, self.DLGID_CTRL)
        self.dlg_perf = saved_logs(name_log_dlg_performance, self.DLGID_CTRL)
        
        if easy_log and self.SERVICE:
            self.easy_dlg_perf_check = saved_logs(f'{self.DLGID_CTRL}_{system_date_raw}', self.DLGID_CTRL, f'{path_easy_log}{self.SERVICE}/{self.DLGID_CTRL}/')
            
    def print_log(self,message):
        if self.show_log: print(message)
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(message)
            
    def print_in(self,name_function,name_var,value_var = None):
        
        if is_list(name_var):
            for x in name_var:
                i = name_var.index(x)
                if is_par(i):
                    if self.show_log: print('{0} <= [{1} = {2}]'.format(name_function,name_var[i],name_var[i+1]))
                    self.script_performance.write('{0} <= [{1} = {2}]'.format(name_function,name_var[i],name_var[i+1]))
        else:
            if self.show_log: print(f"{name_function} <= [{name_var} = {value_var}]")
            #
            # DEJO REGISTRO EN EL LOGS
            self.script_performance.write(f"{name_function} <= [{name_var} = {value_var}]")
    
    def print_out(self,name_function,name_var,value_var = None):
        
        if is_list(name_var):
            for x in name_var:
                i = name_var.index(x)
                if is_par(i):
                    if self.show_log: print('{0} => [{1} = {2}]'.format(name_function,name_var[i],name_var[i+1]))
                    self.script_performance.write('{0} => [{1} = {2}]'.format(name_function,name_var[i],name_var[i+1]))
        else:
            if self.show_log: print(f"{name_function} => [{name_var} = {value_var}]")
            #
            self.script_performance.write(f"{name_function} => [{name_var} = {value_var}]")
        
    def print_inf(self,name_function,message):
        if self.show_log: print(f"{name_function} ==> {message}")
        #
        # DEJO REGISTRO EN EL LOGS
        self.script_performance.write(f"{name_function} ==> {message}")
        
    def dlg_performance(self,message):
        
        # OBTENGO LA FECHA DEL DLGID
        dlgid_date = read_param(self.DLGID_CTRL, 'DATE')
        
        # OBTENGO LA HORA DEL DLGID 
        dlgid_time = read_param(self.DLGID_CTRL, 'TIME')
       
        # ESCRIBO EL LOGS
        self.dlg_perf.write(f'[{dlgid_date}-{dlgid_time}] {message}')
        
        # ESCRIBO EL LOG FACIL EN CASO DE QUE ESTE HABILITADO
        if easy_log:
            # ESCRIBO EL LOGS
            self.easy_dlg_perf_check.write(f'[{dlgid_date}-{dlgid_time}] {message}')





     
        