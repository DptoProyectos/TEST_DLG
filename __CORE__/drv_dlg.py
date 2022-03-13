
'''
DRIVER PARA EL TRABAJO CON EL DATALOGGER

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.3 16-04-2020 12:58
''' 

#CONEXIONES
from __CORE__.drv_redis import Redis
from __CORE__.mypython import bin2dec

# INSTANCIAS
redis = Redis()

# FUNCIONES
def douts(dlgid,out_dec):
    '''
    DESCRIPTION
        Se encarga de poner en la salida digital (d2,d1,d0) el valor que se le pasa en decimal sin afectar las otras entradas
        
    LEYENDA:
        dlgid => datalogger id
        out_dec => numero decimal que se va a querer porner en las salidas digitales (d2,d1,d0)
        EJ: douts(MER006,7)
    '''
    ## INSTANCIAS
    redis = Redis()
    #
    # LEO LA SALIDA ACTUAL SETEADA
    last_out = redis.hget(dlgid,'OUTPUTS')
    # APLICO LA MASCARA 0000011
    last_out = int(last_out) & int('0000011',2)
    # 
    #
    #
    # APLICO LA MASCARA 0000111 A no_dec
    out_dec = int(out_dec) & int('0000111',2)
    # HAGO UN BITWISE LEFT 3 UNIDADES
    out_dec = out_dec << 3
    #
    #
    # CONCATENO LOS DOS PRIMEROS BITS CON LA SALIDA DIGITAL
    out = out_dec | last_out
    #
    #
    # MANDO A SETEAR LAS SALIDAS DEL DATALOGGER
    redis.hset(dlgid,'OUTPUTS',out)
    
def pump1(dlgid,action):
    '''
    DESCRIPTION
        Se encarga de prender o apagar la bomba 1 del sistema
        
    LEYENDA:
        dlgid => datalogger id
        action => [True (PRENDER BOMBA) | False (APAGAR BOMBA)]
        EJ: pump1('MER006',True)
    '''
    ## INSTANCIAS
    redis = Redis()
    #
    #
    # LEO LA SALIDA ACTUAL SETEADA
    last_out = redis.hget(dlgid,'OUTPUTS')
    # APLICO LA MASCARA 1111100
    last_out = int(last_out) & int('1111100',2)
    #
    #
    # VEO QUE ACCION ES LA SELECCIONADA
    if action: out = last_out | int('11',2)
    else: out = last_out | int('1',2)
    #
    #
    # MANDO A SETEAR LAS SALIDAS DEL DATALOGGER
    redis.hset(dlgid,'OUTPUTS',out)
   
def emerg_system(dlgid):
    '''
    DESCRIPTION
        Se encarga de poner a funcionar el sitema de emergencia
        
    LEYENDA:
        dlgid => datalogger id
        EJ: pump1('MER006',True)
    '''
    ## INSTANCIAS
    redis = Redis()
    #
    # CHEQUEO SI EXISTE OUTPUTS, SI NO EXSITE LO CREO CON VALOR 0
    if not(redis.hexist(dlgid,'OUTPUTS')):
        redis.hset(dlgid, 'OUTPUTS', 0)
    
    # LEO LA SALIDA ACTUAL SETEADA
    last_out = redis.hget(dlgid,'OUTPUTS')
    
    # APLICO LA MASCARA 1111010
    last_out = int(last_out) & int('1111010',2)
    #
    #
    # MANDO A SETEAR LAS SALIDAS DEL DATALOGGER
    redis.hset(dlgid,'OUTPUTS',last_out)
    
def read_param(dlgid,param):
    '''
    DESCRIPTION
        Se encarga de leer del datalogger el canal con el nombre 'param'
        devuelve un string
        
    LEYENDA:
        dlgid => datalogger id
        param => nombre del canal que se quiere leer
                 si se quiere leer la fecha param = DATE
                 si se quiere leer la hora param = TIME
        EJ: read_param('MER001','PA')
    '''
    
    def head_detect(line, key_word):
        '''
        DETECTA SI LA CABECERA DEL line HAY ESTE key_word
        '''
        i = 0
        match = 0
        for char in key_word:
            if line[i] == char:
                match += 1
            i += 1
        if match == 9: return True
        else: return False
    
    
    ## INSTANCIAS
    
    redis = Redis()
    # LEO LINE
    if redis.hexist(dlgid, 'LINE'): line = redis.hget(dlgid,'LINE') 
    else: return None
         
    
    # DETECTO SI EXISTE CABECERA LINE
    if head_detect(line,'LINE=DATE'):
        parsed_line = line.split(';')
        #
        # CREO UNA LISTA A PARTIR DE SEPARAR LOS CAMPOS DEL LINE
        n = 0
        my_list = []
        for elements in parsed_line:
            fields = elements.split(':')
            my_list.append(fields[0])
            try:
                my_list.append(fields[1])
            except:
                pass
      
            n = n+1
            
        # VEO SI SE ESTA SELECCIONADO DATE O TIME 
        if param == 'DATE': out = f'20{my_list[1]}'
        else: 
            try:
                out = my_list[my_list.index(param)+1]
            except:
                out = '' 
        return out
        
    else:
        
        parsed_line = line.split(',')
        #
        # CREO UNA LISTA A PARTIR DE SEPARAR LOS CAMPOS DEL LINE
        n = 0
        my_list = []
        for elements in parsed_line:
            fields = elements.split('=')
            my_list.append(fields[0])
            try:
                my_list.append(fields[1])
            except:
                pass
      
            n = n+1  
        #
        # VEO SI SE ESTA SELECCIONADO DATE O TIME 
        if param == 'DATE': out = my_list[1]
        elif param == 'TIME': out = my_list[2]
        else: 
            try:
                out = my_list[my_list.index(param)+1]
            except:
                out = '' 
        return out

def dlg_detection(dlgid):
    '''
        Detecta el tipo de datalogger mirando el nombre del canal que mide la bateria
    '''
    if read_param(dlgid, 'BAT'):
        return '8CH'
    elif read_param(dlgid, 'bt'):
        return '5CH'
    else:
        return 'None'
    
def set_outs(dlgid,DO_0=0,DO_1=0,DO_2=0,DO_3=0,DO_4=0,DO_5=0,DO_6=0,DO_7=0):
    #
    str_outputs = f'{DO_7}{DO_6}{DO_5}{DO_4}{DO_3}{DO_2}{DO_1}{DO_0}'
    #
    dec_outputs = bin2dec(str_outputs)
    #
    redis.hset(dlgid, 'OUTPUTS', dec_outputs)

def get_outs(dlgid,dec_value_outs,no_out):
    '''
    dec_value_outs => valor decimal del OUTPUTS que se escribe en la Redis
    no_out = numero de la salida [0:7]
    return => estado de la salida referida en no_out
    '''
    #
    if no_out > 7: return None
    #
    bin_value_outs = bin(int(dec_value_outs))
    str_value_outs = bin_value_outs[2:]
    #
    if no_out >= len(str_value_outs):
        return 0
    else:
        return int(str_value_outs[abs(no_out - (len(str_value_outs) - 1))])
         
    
    
    
    
    
    
    
    

 
