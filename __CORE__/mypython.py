
'''
DETECCION DE FUNCIONES ADICIONALES DE PYTHON

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.7 06-07-2020
''' 

# LIBRERIAS
import json
import os
from datetime import date, datetime


def lst2str(list):
    '''
    Convierto de lista a string
    
    EX:
    list = ['print_log', True, 'DLGID_CTRL', 'MER001']
    string = lst2str(list)
    string = print_log,True,DLGID_CTRL,MER001
    '''
    if bool(list):
        my_str = str(list[0])
        n = 0
        for param in list:
            if n < (len(list)-1): 
                n += 1
                my_str = f"{my_str},{str(list[n])}"
        return my_str
    else: return None

def str2lst (str):
    
    if type(str) == list: return str 
        
    lst = str.split(',')
    out = []
    for var in lst:
        tmp = var.split(':')
        if len(tmp) != 1:
            out.append(tmp) 
        else:
            out.append(var)    
    if lst == ['']:
        return ''
    else:
        return out

def str2bool(str):
    '''
        Funcion que garantiza que en su salida haya una variable tipo bool
    '''
    try: out = json.loads(str.lower()) 
    except: out = str
    return out
   
def not_dec(in_dec,bits):
    '''
    Invierte la representacion binaria del numero decimal entrado. Devuelve en decimal
    
    EX:
    in_dec = 1
    > 1
    out = not_dec(in_dec,3)
    out = 6
    > 110
    '''
    # ESXTRAIGO LOS DOS PRIMEROS CARACTERES BINARIOS
    out_char = ''
    n = 0
    for x in bin(in_dec):
        if n >= 2: out_char = f"{out_char}{x}"
        n += 1
    #
    # CALCULO LA LONGITUD STRING OBTENIDO
    n = 0
    for y in out_char:
        n +=1
    #
    # COMPLETO CON CEROS EL NUMERO DE BITS
    while n < bits:
        out_char = f"0{out_char}"
        n += 1
        
    # INVIERTO CADA CARACTER DEL STRING OBTENIDO
    out_bin = ''
    for x in out_char:
        out_bin = f"{out_bin}{int(not(int(x)))}"
        n += 1
    return int(out_bin,2)

def bin2dec(str_in):
    '''
    Le entra un string binario y devuelve su valor en decimal
    '''
    return int(str_in, 2)

def is_list(var):
    if type(var) == list: return True
    else: return False
 
def is_par(var):
    try:
        var = int(var)  
    except:
        return None  
    
    if var%2 == 0:
        return True
    else:
        return False

class config_var():
    
    def __init__(self,vars):
        self.var = vars
    
    def str_get(self,param):
        my_list = self.var.split(',')
        try: return my_list[my_list.index(param)+1]
        except: return None
     
    def lst_get(self,param):
        my_list = self.var
        try:
            value = my_list[my_list.index(param)+1]
            
            if type(value) == bool:
                return value
            elif type(value) == list:
                return value
            elif type(value) == str:
                # DETECTO QUE SEA UN BOOL IN A STRING
                if value == 'True':
                    return True
                elif value == 'False':
                    return False
                # DETECTO QUE SEA UN INT IN A STRING
                try: 
                    return int(value)
                except:
                    pass
                # POR DECANTACION ES STRING PURO   
                return value
            
        except: return None
     
    def lst_set(self,param,value = None):
        self.var[self.var.index(param) + 1] = value
        return self.var 
     
     
# OTHERS             
system_hour = str(datetime.now()).split(' ')[1].split('.')[0]               # HORA DEL SERVER FORMATEADA A 'HH:MM:SS'
                                                                              
dt = str(datetime.now()).split(' ')[0].split('-')
system_date = f'{dt[2]}/{dt[1]}/{dt[0]}'                                    # FECHA DEL SERVER FORMATEADA A 'DD/MM/AAAA' 
system_date_raw = f'{dt[0]}{dt[1]}{dt[2]}'                                  # FECHA DEL SERVER FORMATEADA A 'AAAAMMDD' 
   

  
    