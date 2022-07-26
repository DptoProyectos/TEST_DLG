#!/usr/testDlg_env/bin/python3.8
'''
LLAMADO CON PARAMETROS A APLICACION DE CONTROL DE ERRORES EN TEST_DLG

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.9 22-06-2020
''' 
#
## LIBRERIAS
import os                                                   

## CONEXIONES
from __CORE__.mypython import lst2str
from __CORE__.drv_config import project_path
from time import time 
#
  
gen_start_time = time()  
                                             

LIST_CONFIG = [
                'print_log',        True,                           # VER LOS LOGS EN CONSOLA [ True | False ]
                #
                # ID DE LOS DATALOGGERS QUE SE VAN A UTUILIZAR EN EL SIGUIENTE FORMATO 'DLGID_1:DLGID_2:....DLGID_n'
                'DLGID',            'MER001:MER002:MER003:MER004:MER005:MER006',            
                #
                # TIPO DE PROCESO QUE SE ESTA CORRIENDO (TEST PARA ESTE CASO). DEL => PARA DETENER EL TEST.                                               
                'TYPE',             'TEST',                         # [ TEST | DEL ] 
                #                                                    
                'SERVICE',          'REC_MERCEDES',         		# SERVICIO PARA AGRUPAR LOS EASY LOGS [OJO: EL NOMBRE NO PUEDE CONTENER ESPACIOS]
                # TIEMPO DE POLLEO (en min) AL CUAL ESTA TRABAJANDO EL EQUIPO A TESTEAR
                'TIMER_POLL',       '1',                            # AUTO -> SE LEE EL VALOR DE LA CONFIG EN DB | VALUE -> TIEMPO EN MINUTOS
                # TIEMPO DE ENVIO DE DATOS (en min) AL CUAL ESTA TRABAJANDO EL EQUIPO A TESTEAR
                'TIMER_DIAL',       '0',                            # AUTO -> SE LEE EL VALOR DE LA CONFIG EN DB | VALUE -> TIEMPO EN MINUTOS
            ]


#
# LLAMADO DEL PROGRAMA 
program_path = f'{project_path}__CORE__/'
os.system('{0}/serv_TEST_DLG.py {1}'.format(program_path,lst2str(LIST_CONFIG))) 
#
# CALCULO TIEMPO DE DEMORA
#print(f'control_process_frec_{LIST_CONFIG[3]} TERMINADO A {time()-gen_start_time} s')



#
####
