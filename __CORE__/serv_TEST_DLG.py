#!/usr/testDlg_env/bin/python3.8
'''
SERVICIO DE DETECCION DE ERRORES EN AUTOMATISMOS

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.7 09-07-2020
####
#
''' 

# LIBRERIAS
import sys

# CONEXIONES
from __CORE__.drv_redis import Redis
from __CORE__.mypython import str2lst, config_var
from __CORE__.drv_logs import ctrl_logs
from __CORE__.PROCESS.ctrl_library import TEST_DLG
from __CORE__.PROCESS.ctrl_error import error_process
from __CORE__.drv_config import TYPE_2_RUN,name_log_ctrl_error


redis = Redis()

print_log = True                    # HACE QUE SE IMPRIMAN LOS LOGS EN CONSOLA
         

def serv_TEST_DLG(LIST_CONFIG):     
    
    name_function = 'APP_ERROR_SELECTION'
    
    conf = config_var(LIST_CONFIG)
    
    print_log = conf.lst_get('print_log')
    DLGID = conf.lst_get('DLGID')
    TYPE = conf.lst_get('TYPE')

    lib = TEST_DLG(print_log,DLGID,TYPE)
             
    ## INSTANCIAS
    logs = ctrl_logs(False,'ctrl_error',DLGID,print_log)
    redis = Redis()
    
    def run_error_process(LIST_CONFIG):
        try:
            TYPE = config_var(LIST_CONFIG).lst_get('TYPE')
            
            if TYPE in TYPE_2_RUN:
                error_process(LIST_CONFIG)
            else:
                logs.print_inf(name_function, f'TYPE != {TYPE_2_RUN}')
                logs.print_inf(name_function, 'NO SE EJECUTA SCRIPT') 
        except:
            logs.print_inf(name_function, f'HUBO PROBLEMAS AL CORRER {DLGID}') 
    
    n = -1      # ESTADO INICIAL
    
    while True:
        # CHEQUEO SI ESTOY EN ESTADO UNICIAL (PRIMERA CORRIDA)
        if n == -1:
            #print(TYPE)
            
            if TYPE not in ['SCAN','CHARGE']:
                # LLAMADA CON VARIABLES DE CONFIGURACION 
                
                # OBTENGO LISTA DE DATALOGGERS A CORRER
                lst_DLGID = str2lst(config_var(LIST_CONFIG).lst_get('DLGID'))
            
                # EJECUTO EL PROGRAMA CON LA LISTA DE DATALOGGER PASADA
                for DLGID in lst_DLGID:
                    
                    LIST_CONFIG = conf.lst_set('DLGID',DLGID)
                    
                    # IMPRIMO LOGS
                    logs.print_in(name_function,LIST_CONFIG)
                   
                    # DETENGO LA EJECUCION DEL SCRIPT SI TYPE = DELETED
                    if TYPE == 'DEL':
                        logs.print_inf(name_function,'DEL_2_RUN')
                        SERVICE = conf.lst_get('SERVICE')
                        lib.del_2_Run(SERVICE,DLGID)
                    else:
                        # ANADO DLGID_CTRL A 'DLGID_CTRL_TAG_CONFIG' PARA QUE SE EJECUTE EL ctrl_error_frec
                        logs.print_inf(name_function,'ADD_2_RUN')
                        lib.add_2_RUN(conf.lst_get('DLGID'))
                        
                        # ACTUALIZO LA CONFIGURACION
                        logs.print_inf(name_function,'UPGRADE CONFIG')
                        lib.upgrade_config(DLGID,LIST_CONFIG)
                        
                        # MUESTRO LAS VARIABLES QUE SE LE VAN A PASAR AL PROCESS Y LO LLAMO
                        logs.print_out(name_function, LIST_CONFIG)
                        
                        # LLAMO AL PROCESS DEL AUTOMATISMO Y LE PASO LIST_CONFIG
                        if bool(LIST_CONFIG): 
                            logs.print_inf(name_function,'ERROR_PROCESS')
                            #error_process(LIST_CONFIG)
                            run_error_process(LIST_CONFIG)
                    
                break
            #
            else:
                # LLAMADA CON DLGID O SIN PARAMETROS
                if TYPE == 'CHARGE':
                    # LLAMADA CON DLGID
                    
                    ## VARIABLES GLOBALES QUE LE ENTRAN A CORE
                    logs.print_log(f"EXECUTE: {name_function}")
                    logs.print_in(name_function,'print_log',print_log)
                    logs.print_in(name_function,'DLGID',DLGID)
                    
                    # LEO LAS VARIABLES DE CONFIGURACION
                    logs.print_inf(name_function,'READ_CONFIG_VAR')
                    LIST_CONFIG = lib.read_config_var(DLGID)
                    
                    # LLAMO AL PROCESS DEL AUTOMATISMO Y LE PASO LIST_CONFIG
                    if bool(LIST_CONFIG): 
                        logs.print_out(name_function, LIST_CONFIG)
                        logs.print_inf(name_function,'ERROR_PROCESS')
                        #error_process(LIST_CONFIG)
                        run_error_process(LIST_CONFIG)
                    
                    break
                
                elif TYPE == 'SCAN':
                    # LLAMADA SIN PARAMETROS
                    
                    # LEO IDs PARA EJECUTAR CORRER ctrl_error_frec.py
                    if redis.hexist('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}'): 
                        str_RUN = redis.hget('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}')
                        lst_RUN = str2lst(str_RUN)
                    else:
                        logs.print_inf(name_function, f'NO EXISTE VARIABLE RUN_{name_log_ctrl_error} in ERROR_PROCESS')
                        logs.print_inf(name_function, 'NO SE EJECUTA SCRIPT') 
                        lst_RUN = ''
                    n += 1
                    
                    # ACTUALIZO EL DLGID A EJECUTAR     
                    if lst_RUN: DLGID = lst_RUN[n] 
                    
        #
        
        # YA NO SE TRATA DE LA PRIMERA CORRIDA
        else:
            
            # ENTRAMOS EN ESTA CONDICION POR UN LLAMADO SIN ARGUMENTOS
            
            if bool(lst_RUN):
                
                # INTANCIA DE ctrl_logs SOLO PARA LLAMADA SIN ARGUMENTOS
                logs = ctrl_logs(False,'ctrl_error',DLGID,print_log)
                    
                ## VARIABLES GLOBALES QUE LE ENTRAN A CORE
                logs.print_log(' ')
                logs.print_log(f"EXECUTE: {name_function}")
                logs.print_in(name_function,'print_log',print_log)
                logs.print_in(name_function,'DLGID',DLGID)
                
                # LEO LAS VARIABLES DE CONFIGURACION
                logs.print_inf(name_function,'READ_CONFIG_VAR')
                
                if lib.read_config_var(DLGID):
                    LIST_CONFIG = lib.read_config_var(DLGID)
                else:
                    # SOLO EJECUTO CON VARIABLES DE EJECUCION
                    LIST_CONFIG = ['print_log', print_log, 'DLGID', DLGID, 'TYPE', TYPE]
                
                # MUESTRO LAS VARIABLES QUE SE LE VAN A PASAR AL PROCESS Y LO LLAMO
                logs.print_out(name_function, LIST_CONFIG)
                        
                # LLAMO AL PROCESS DEL AUTOMATISMO Y LE PASO LIST_CONFIG
                if bool(LIST_CONFIG): 
                    logs.print_inf(name_function,'ERROR_PROCESS')
                    #error_process(LIST_CONFIG)
                    run_error_process(LIST_CONFIG)
                
                # EVALUO CONDICION DE RUPTURA      
                if n < (len(lst_RUN) - 1):
                    n += 1
                    
                    # ACTUALIZO EL DLGID A EJECUTAR     
                    DLGID = lst_RUN[n]
                    
                else:
                    break           
            
            else:
                break
            
#---------------------------------------------------------------------------------------------------------------------------------            
if __name__ == '__main__':
    
    LIST_CONFIG = []
    
    # DETECTO LLAMADA CON Y SIN PARAMETROS
    try: LIST_CONFIG = str2lst(sys.argv[1])                                             # LLAMADA CON PARAMETROS
    except: pass                                                                        # LLAMADA SIN PARAMETROS
        
    called_conf = config_var(LIST_CONFIG) 
    
    if bool(LIST_CONFIG):
        if called_conf.lst_get('DLGID'): pass                                           # LLAMADA CON VARIABLES DE EJECUCION
        else: LIST_CONFIG = ['print_log', True,'DLGID',sys.argv[1],'TYPE','CHARGE']     # LLAMADA SOLO CON EL ID DEL DATALOGGER
            
    else: LIST_CONFIG = ['print_log', True,'DLGID',None,'TYPE','SCAN']                   # LLAMADA SIN DATOS [LLAMADA SE VA A EJECUTAR EN EL SERVIDOR]
            
    serv_TEST_DLG(LIST_CONFIG)  
