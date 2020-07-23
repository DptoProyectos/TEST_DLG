#!/drbd/www/cgi-bin/spx/aut_env/bin/python3.6
'''
Created on 14 may. 2020

@author: Yosniel Cabrera

Version 1.1.4 22-06-2020
'''

import configparser
import os
from __CORE__.mypython import str2bool,str2lst
from parser import st2list


'''
    Manejo de variables de configuracion usadas en el sistema
    
    variables de salida
        !GENERAL
        
        working_mode                 modo en que se ejecuta el automatimso [ LOCAL | SPY | OSE ]
        easy_log                     habilita (True) o deshabilita (False) los logs de adentro de la carpeta AUTOMATISMOS/..
        project_path                 ruta en donde se encuentra la carpeta automatismos
        name_log_ctrl_error          nombre del log del script ctrl_error.py que se va a guardar en 'path_log'
        name_log_dlg_performance     nombre del log del script dlg_performance.py que se va a guardar en 'path_log'
        path_log                     ruta en donde van a estar los logs
        path_easy_log                ruta en donde van a encontrarse los easy_logs
        TYPE_2_RUN                   valores de la variable TYPE para los cuales el serv_TEST_DLG va a llamar a error process
        
        !DATABASE
        dbuser                       usuario con acceso a la base
        dbpasswd                     password para acceder a la base
        dbhost                       host en donde se encuentra la base
        dbaseName                    nombre de la base de datos
        
        
        
'''
# path del proyecto
file_path = os.path.dirname(os.path.abspath(__file__))

# serv_APP_config.ini
serv_APP_config = configparser.ConfigParser()
serv_APP_config.read(f"{file_path}/config.ini")
project_path = serv_APP_config['CONFIG']['project_path']
name_log_ctrl_error = serv_APP_config['CONFIG']['name_log_ctrl_error']
name_log_dlg_performance = serv_APP_config['CONFIG']['name_log_dlg_performance']
path_log = serv_APP_config['CONFIG']['path_log']
easy_log = str2bool(serv_APP_config['CONFIG']['easy_log']) 
path_easy_log = serv_APP_config['CONFIG']['path_easy_log']
TYPE_2_RUN = str2lst(serv_APP_config['CONFIG']['TYPE_2_RUN'])
dbase2use = serv_APP_config['CONFIG']['dbase2use']
dbuser = serv_APP_config[dbase2use]['dbuser']
dbpasswd = serv_APP_config[dbase2use]['dbpasswd']
dbhost = serv_APP_config[dbase2use]['dbhost']
dbaseName = serv_APP_config[dbase2use]['dbaseName']



