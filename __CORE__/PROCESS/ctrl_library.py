
'''
LIBRERIA DE APLICACION CTRL_FREC

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.2.2 03-08-2020
''' 

# LIBRERIAS
#import redis
import json

#CONEXIONES
from __CORE__.drv_logs import *
from __CORE__.drv_redis import Redis
from __CORE__.mypython import config_var,lst2str,str2lst
from __CORE__.drv_config import name_log_ctrl_error
from __CORE__.drv_config import dbUrl
from __CORE__.drv_db_GDA import GDA

redis = Redis()

class process_error(object):  
    '''
    FUNCIONES USADAS POR ctrl_error_frec.py
    '''
    def __init__(self,LIST_CONFIG):
        '''
        Constructor
        '''
        #
        config = config_var(LIST_CONFIG)
        #
        #VARIABLES DE EJECUCION
        self.print_log = config.lst_get('print_log')
        self.DLGID = config.lst_get('DLGID')
        self.TYPE = config.lst_get('TYPE')
        self.SERVICE = config.lst_get('SERVICE')
        self.TEST_OUTPUTS = config.lst_get('TEST_OUTPUTS')
        self.TIMER_POLL = config.lst_get('TIMER_POLL')
        self.TIMER_DIAL = config.lst_get('TIMER_DIAL')
        #
        #
        # INSTANCIAS
        self.logs = ctrl_logs(self.SERVICE,'ctrl_error',self.DLGID,self.print_log)
        self.redis = Redis()   
    
    def test_tx(self):
        '''
            detecta errores tx y RTC
            return ''       =>     No existe el line del datalogger
            return False    =>     Hay errores TX
            return True     =>     Trasmision correcta
        '''
        
        name_function = 'TEST_TX_ERRORS'
        
        db = GDA(dbUrl)

        # VARIABLES DE ENTRADA  ----------------------------------------------------------------------
        ## TPOLL
        if self.TIMER_POLL == 'AUTO':
            # OBTENGO TPOLL EN SEGUNDOS
            try:
                self.TIMER_POLL = int(db.read_dlg_conf(self.DLGID, 'BASE', 'TPOLL'))
                #
                self.logs.print_in(name_function, 'TIMER_POLL', self.TIMER_POLL)
                #self.logs.print_in(name_function, 'TIMER_DIAL', tdial)
                #
            except:
                self.logs.print_inf(name_function, f'ERROR AL LEER TPOLL PARA {self.DLGID}')
                self.logs.print_inf(name_function, 'SE ASUME TPOLL = 1')
                self.TIMER_POLL = 1
        else:
            ### El Tpoll mantiene el valor que se le configuró al correr el script
            self.logs.print_in(name_function, 'TIMER_POLL', self.TIMER_POLL)

        ## TDIAL
        if self.TIMER_DIAL == 'AUTO':
            # OBTENGO TDIAL EN SEGUNDOS
            try:
                self.TIMER_DIAL = int(db.read_dlg_conf(self.DLGID, 'BASE', 'TDIAL'))
                #
                self.logs.print_in(name_function, 'TIMER_DIAL', self.TIMER_DIAL)
                #
            except:
                self.logs.print_inf(name_function, f'ERROR AL LEER TDIAL PARA {self.DLGID}')
                self.logs.print_inf(name_function, 'SE ASUME TDIAL = 0')
                self.TIMER_DIAL = 0
        else:
            ### El Tdial mantiene el valor que se le configuró al correr el script
            self.logs.print_in(name_function, 'TIMER_DIAL', self.TIMER_DIAL)    
        #
        ## NIVEL DE BATERIA
        # ASIGNO EL VALOR DE LA BATERIA PARA MOSTRARLO EN LOS LOGS
        if read_param(self.DLGID, 'BAT'): 
            bat = read_param(self.DLGID, 'BAT')
        else: 
            bat = read_param(self.DLGID, 'bt')


        # MAIN ---------------------------------------------------------------------------------------------------------
        ## CHEQUEO SI EXISTE EL LINE EN EL DATALOGGER
        if not(self.redis.hexist(self.DLGID, 'LINE')):
            self.logs.print_inf(name_function, f'NO EXISTE VARIABLE LINE EN {self.DLGID}')
            self.logs.print_inf(name_function, f'NO SE EJECUTA {name_function}')
            return ''
        else:
            # DEVUELVO last_line CON EL LINE ANTERIOR Y current_line CON EL LINE ACTUAL
            if not self.redis.hexist(f'{self.DLGID}_ERROR', 'last_line'):
                last_line = self.redis.hget(self.DLGID, 'LINE')
                self.redis.hset(f'{self.DLGID}_ERROR', 'last_line', last_line)
                current_line = last_line
                return True     # tx OK
            else:
                last_line = self.redis.hget(f'{self.DLGID}_ERROR', 'last_line')
                current_line = self.redis.hget(self.DLGID, 'LINE')
                self.redis.hset(f'{self.DLGID}_ERROR', 'last_line', current_line)

                # CHEQUEO CAMBIO DE DATOS
                if last_line == current_line: 
                    #
                    # Incremento el contador de minutos con error o lo creo en caso de que no exista
                    if not(self.redis.hexist(f'{self.DLGID}_ERROR','count_error_tx')):
                        self.redis.hset(f'{self.DLGID}_ERROR', 'count_error_tx', 1) 
                        count_error_tx = 1                                                   
                    else:
                        count_error_tx = int(self.redis.hget(f'{self.DLGID}_ERROR','count_error_tx'))
                        count_error_tx += 1
                        self.redis.hset(f'{self.DLGID}_ERROR', 'count_error_tx', count_error_tx)
                    #
                    # chequeo la configuracion del timer dial
                    if self.TIMER_DIAL == 0:
                        # EQUIPOS EN CONTINUO
                        if count_error_tx >= self.TIMER_POLL:
                            self.logs.print_inf(name_function, 'TX STOPPED [{0}]'.format(count_error_tx))
                            self.logs.dlg_performance('< ERROR TX [{0}]> [BAT = {1}]'.format(count_error_tx,bat))
                            return False     #Tx Fail
                        else:
                            self.logs.print_inf(name_function, f'CONTADOR DE ERROR TX [{count_error_tx}]')
                            return True     #Tx Ok
                    else:
                        self.logs.print_inf(name_function, 'Falta programar el caso TDIAL != 0')    
                else: 
                    self.logs.print_inf(name_function, 'TX OK')                 # HUBO CAMBIO DE DATOS
                    #
                    # ELIMINO EL CONTADOR DE ERRORES TX EN CASO DE QUE EXISTA
                    if self.redis.hexist(f'{self.DLGID}_ERROR','count_error_tx'): self.redis.hdel(f'{self.DLGID}_ERROR','count_error_tx')  
                    #
                    return True     #Tx Ok
    
    def test_RTC_error(self):
        '''
        return False: si no se comprueba el RTC por error_1min
                      si no hay errores RTC
        return True:  si hay errores TRC 
                          
        '''
        
        name_function = 'TEST_RTC_ERROR'
        
        # DEVUELVO LOS VALORES DE last_fecha_data y last_hora_data asi como fecha_data y hora_data
        if self.redis.hexist(f'{self.DLGID}_ERROR', 'last_fecha_data') & self.redis.hexist(f'{self.DLGID}_ERROR', 'last_hora_data'):
            last_fecha_data = self.redis.hget(f'{self.DLGID}_ERROR', 'last_fecha_data')
            last_hora_data = self.redis.hget(f'{self.DLGID}_ERROR', 'last_hora_data')
            fecha_data = read_param(self.DLGID, 'DATE')
            hora_data = read_param(self.DLGID, 'TIME')
            #
            # ACTUALIZO last_fecha_data Y last_hora_data CON LOS VALORES ACTUALES
            self.redis.hset(f'{self.DLGID}_ERROR', 'last_fecha_data', fecha_data)
            self.redis.hset(f'{self.DLGID}_ERROR', 'last_hora_data', hora_data)
        else:
            fecha_data = read_param(self.DLGID, 'DATE')
            hora_data = read_param(self.DLGID, 'TIME')
            last_fecha_data = fecha_data
            last_hora_data = hora_data
            #
            # ACTUALIZO last_fecha_data Y last_hora_data CON LOS VALORES ACTUALES
            self.redis.hset(f'{self.DLGID}_ERROR', 'last_fecha_data', fecha_data)
            self.redis.hset(f'{self.DLGID}_ERROR', 'last_hora_data', hora_data)
            #
            return False
        #
        # CHEQUEO QUE NO ESTE CAMBIANDO LA FECHA Y HORA
        if fecha_data == last_fecha_data and hora_data == last_hora_data: return True
        else: return False  
    
    def testModbusRxError(self):
        '''
        return False: si no de detecta NaN en el LINE
                      
        return True:  si hay errores TRC 
                          
        '''
        
        name_function = 'testModbusRxError'
        
        if read_param(self.DLGID, 'ST') == 'NaN':
            return True
        else:
            return False
        
                  
    def visual(self): pass
             
class TEST_DLG(object):
    
    def __init__(self,print_log,DLGID,TYPE): 
        self.logs = ctrl_logs(False,'ctrl_error',DLGID,print_log)
        self.print_log = print_log
        self.DLGID = DLGID
        self.TYPE = TYPE
        self.name_function = 'APP_ERROR_SELECTION'
        
    def upgrade_config(self,DLGID,LIST_CONFIG):
        
        if redis.hexist(f'{DLGID}_ERROR','TAG_CONFIG'):
            last_TAG_CONFIG = redis.hget(f'{DLGID}_ERROR','TAG_CONFIG')
            #   
            for param in last_TAG_CONFIG.split(','):
                redis.hdel(f'{DLGID}_ERROR', param)
            #    
            redis.hdel(f'{DLGID}_ERROR','TAG_CONFIG')
    
        TAG_CONFIG = []
        n = 4
        for param in LIST_CONFIG:
            if n < (len(LIST_CONFIG)): 
                redis.hset(f'{DLGID}_ERROR',LIST_CONFIG[n],LIST_CONFIG[n+1])
                TAG_CONFIG.append(LIST_CONFIG[n])
                n += 2
        
        # ESCRIBO EN REDIS EL NOMBRE DE LAS VARIABLES DE CONFIGURACION PARA QUE PUEDAN SER LEIDAS
        redis.hset(f'{DLGID}_ERROR','TAG_CONFIG',lst2str(TAG_CONFIG))
        
        # LEO VARIABLES ESCRITAS
        n = 4
        check_config = []
        for param in LIST_CONFIG:
            if n < (len(LIST_CONFIG)): 
                check_config.append(LIST_CONFIG[n])
                check_config.append(redis.hget(f'{DLGID}_ERROR',LIST_CONFIG[n]))
                n += 2
     
    def read_config_var(self,DLGID):
        ''''''
        
        FUNCTION_NAME = 'READ_CONFIG_VAR'
        
        ## INSTANCIAS
        #logs = ctrl_logs('CTRL_FREC',DLGID,print_log)
        logs = ctrl_logs(False,'ctrl_error',DLGID,self.print_log)
        redis = Redis()
        # 
        # LEO LOS TAGS DE CONFIGURACION
        if redis.hexist(f'{DLGID}_ERROR','TAG_CONFIG'): 
            TAG_CONFIG = redis.hget(f'{DLGID}_ERROR', 'TAG_CONFIG')
            TAG_CONFIG = TAG_CONFIG.split(',')
        else: 
            logs.print_inf(FUNCTION_NAME,f'NO EXISTE {DLGID}_TAG_CONFIG IN serv_error_APP_selection')
            logs.print_inf(FUNCTION_NAME,'NO SE EJECUTA EL SCRIPT')
            return None
        #
        
        # LEO CONFIGURACION DE LA REDIS
        #logs.print_inf(FUNCTION_NAME,'LEO CONFIG EN REDIS')
        vars_config = []
        for param in TAG_CONFIG:
            vars_config.append(param)
            vars_config.append(redis.hget(f'{DLGID}_ERROR',param))
        #
        
        # MUESTRO VARIABLES LEIDAS
        n = 0
        for param in vars_config:
            if n < (len(vars_config)): 
                #logs.print_out(FUNCTION_NAME,vars_config[n],vars_config[n+1])
                n += 2
        #
        # CONCATENO LAS VARIABLES DE EJECUCION Y DE CONFIGURACION
        list_out = []
        LIST_CONFIG = ['print_log', self.print_log, 'DLGID', DLGID, 'TYPE', self.TYPE]
        n = 0
        for param in LIST_CONFIG:
            if n < 4:
                list_out.append(LIST_CONFIG[n])
                n +=1
        
        for param in vars_config:
            list_out.append(param)
        
        return list_out               
    
    #def show_var_list(self,lst,name_function = 'APP_ERROR_SELECTION'):
        #if bool(lst):
            #n = 0
            #for param in lst:
                #if n < (len(lst)): 
                    #self.logs.print_out(name_function,lst[n],lst[n+1])
                    #n += 2
        
    def add_2_RUN(self,dlgid):
        '''
            funcion que anade a serv_error_APP_selection / RUN 
            el DLGID_CTRL y el DLGID_REF
        '''
        
        name_function = 'ADD_VAR_TO_RUN'
        
        if redis.hexist('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}'):
            TAG_CONFIG = redis.hget('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}')
            lst_TAG_CONFIG = str2lst(TAG_CONFIG)
            try:
                lst_TAG_CONFIG.index(dlgid)
            except:
                lst_TAG_CONFIG.append(dlgid)
                str_TAG_CONFIG = lst2str(lst_TAG_CONFIG)
                redis.hset('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}', str_TAG_CONFIG)
                
        else:
            redis.hset('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}', dlgid)      
            
    def del_2_Run(self,service,dlgid):
        '''
            funcion que elimina de  serv_error_APP_selection / RUN dlgid
        '''
        
        name_function = 'DEL_VAR_TO_RUN'
        
        if redis.hexist('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}'):
            TAG_CONFIG = redis.hget('ERROR_PROCESS',f'RUN_{name_log_ctrl_error}')
            lst_TAG_CONFIG = str2lst(TAG_CONFIG)
            #
            # ELIMINO EL DATALOGGER DE LA LISTA
            try: lst_TAG_CONFIG.remove(dlgid)
            except: self.logs.print_inf(name_function, f'{dlgid} YA FUE ELIMINADO')  
                  
                
            #SI LA LISTA QUEDA VACIA ELIMINO LA VARIABLE RUN 
            if not(bool(lst_TAG_CONFIG)):
                #    # ENTRO EN ESTA CONDICION YA CUANDO NO HAY DATALOGGER EN LA LISTA. ENTONCES ELIMI
                #    #redis.del_key('ERROR_PROCESS')
                self.logs.print_inf(name_function, f'ELIMINO {dlgid} PARA QUE NO SE EJECUTE')
                redis.hdel('ERROR_PROCESS', f'RUN_{name_log_ctrl_error}')
                
                
                self.logs.print_inf(name_function, f'ELIMINO RUN_{name_log_ctrl_error} DE ERROR_PROCESS')
                #    
                #    return False
            else:
                # CONVIERO A STR LA LISTA
                str_TAG_CONFIG = lst2str(lst_TAG_CONFIG)
                
                # ACTUALIZO EL RUN EL LA REDIS
                redis.hset('ERROR_PROCESS', f'RUN_{name_log_ctrl_error}', str_TAG_CONFIG)
                
                # IMPRIMO LOG EN CONSOLA
                self.logs.print_inf(name_function, f'ELIMINO {dlgid} PARA QUE NO SE EJECUTE')
            
            # LIMPIO RESTOS DE CONFIGURACION DE LA REDIS
            redis.del_key(f'{dlgid}_ERROR')
            
            # CAMBIO EL NOMBRE A LA CARPETA DE TEST DEL DLG ELIMINADO
            #try:
                #os.rename(f'{service}/{dlgid}', f'{service}/{dlgid}_stopped')   
            #except:
                # SI EXISTE UNA CARPETA VIEJA QUE HAYA ESTADO DETENIDA LA ELIMINO PARA RENOMBRAR LA MAS RECIENTE
                #import shutil
                #shutil.rmtree(f'{service}/{dlgid}_stopped')
                #os.rename(f'{service}/{dlgid}', f'{service}/{dlgid}_stopped')
            