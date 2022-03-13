
'''

DETECCION DE ERRORES EN DLG

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.9 22-06-2020
''' 

## LIBRERIAS
import os


## CONEXIONES
from __CORE__.mypython import config_var
from __CORE__.drv_logs import ctrl_logs
from __CORE__.drv_redis import Redis
from __CORE__.PROCESS.ctrl_library import process_error




def error_process(LIST_CONFIG):
    
    name_function = 'ERROR_PROCESS'
    
    conf = config_var(LIST_CONFIG)
    
    #VARIABLES DE EJECUCION
    print_log = conf.lst_get('print_log')
    DLGID = conf.lst_get('DLGID') 
    TYPE = conf.lst_get('TYPE')                  
    SERVICE = conf.lst_get('SERVICE')
           
    ## INSTANCIAS
    logs = ctrl_logs(SERVICE,'ctrl_error',DLGID,print_log)
    redis = Redis()
    e = process_error(LIST_CONFIG)
    
    #---------------------------------------------------------
    
    # SOLO EJECUTO SI EL TYPE ES 'TEST'
    if TYPE != 'TEST':
        logs.print_inf(name_function, f'SOLO SE CORRE TYPE = TEST  [TYPE = {TYPE}]')
        logs.print_inf(name_function, 'NO SE EJECUTA EL SCRIPT')
        return
        
    ##ERROR PROCESS
    logs.print_log(__doc__)
    
    # MUESTRO VARIABLES DE ENTRADA
    logs.print_in(name_function, LIST_CONFIG)
    
    # ESCRIBO NUMERO DE EJECUCION
    redis.no_execution(f'{DLGID}_ERROR')
    
    # CHEQUEO ERROR TX Y RTC
    logs.print_inf(name_function, 'TEST_TX_ERRORS')
    e.test_tx()
    
    
    
    
    
    
    
    
        
    
    
    
