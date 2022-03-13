#!/usr/aut_env/bin/python3.8

'''
Created on 11 jul. 2020

@author: Yosniel Cabrera

'''

import os
import sys
from datetime import datetime

version = 'Version 3.0.5'

mode = 'upload'                     # [ upload | download ]    
url_remote = 'http://git.spymovil.com/ycabrera/test_dlg.git'

# PONER EN ESTA LISTA LOS ARCHVIS QUE SE QUIEREN MANTENER ACTUALIZADOS EN EL SERVIDOR       

staged_files = [
                    '__CORE__/config.ini',
                    '__CORE__/drv_db_GDA.py',
                    '__CORE__/drv_logs.py',
                    '__CORE__/mypython.py',
                    '__CORE__/serv_TEST_DLG.py',
                    '__CORE__/drv_config.py',
                    '__CORE__/drv_dlg.py',
                    '__CORE__/drv_redis.py',
                    '__CORE__/PROCESS/ctrl_error.py',
                    '__CORE__/PROCESS/ctrl_library.py',
                    'git.py',
                    'spx_analize.py',
                    'error_process_DLGID',
                ]


class GIT:
    def __init__(self,):
        pass
    
    def status(self):
        print('GIT    =>    INFORMACION DE LA RAMA LOCAL')  
        os.system('git status --ignored')
    
    def add(self,staged_files):   
        print('GIT    =>    INFORMACION DE LA RAMA LOCAL')
        for files in staged_files:
            print (f'ADDING TO COMMIT => {files}' )
            os.system(f'git add {files}')
        
    def commit(self,message=''):
        now = datetime.now()
        header = '"{0} {1} {2}"'.format(version,f'{now.date()} {now.time()}',message)
        os.system(f'git commit -m {header}')
        
    def save_credential(self):
        os.system(f'git config credential.helper store')
    
    def push(self):
        os.system(f'git push -u origin master')
    
    def checkout_file(self,staged_files):
        '''
        Sacamos del stagin area los archivos de la lista staged_files
        '''
        for files in staged_files:
            print (f'CHECKOUT TO COMMIT => {files}' )
            os.system(f'git checkout {files}')
        
    def pull(self):
        os.system("git pull '{0}'".format(url_remote))
        
    def log(self):  
        os.system('git log --oneline --decorate --graph --all')
    
    def remote_show_origin(self):
        print('GIT    =>    INFORMACION DE LA RAMA REMOTA')  
        os.system('git remote show origin')
    
    def remote_v(self):
        print('GIT    =>    INFORMACION DE LA RAMA REMOTA') 
        os.system('git remote -v')
         
    def checkout(self,branch):
        os.system(f'git checkout {branch}')
        
    def checkout_b(self,branch):
        os.system(f'git checkout -b {branch}')
        
    def branch_d(self,branch):
        os.system(f'git branch -d {branch}')
    
    def merge(self,branch):
        os.system(f'git merge {branch}')
    
    def help(self):
        help = """
GIT.
  +--------------------------------------------------------------------------+
  |  COMANDO DISPONIBLES                                                     |
  +--------------------------------------------------------------------------+
  status     muestra el estado actual de la rama local y la remota
  
  log        muestra la rama a la cual apunta el HEAD (RAMA ACTUAL), el resto
             de las ramas del arbol, sus realaciones asi como sus commits.
  
  commit     se commitan los archivos definidos en [staged_files]   
  
  addbr      anade una nueva rama de trabajo y se camba el HEAD  esta nueva.
  
  chbr       se cambia a la rama descrita
  
  rmbr       se elimina la rama descrita
  
  merge      combina la rama descrita con la rama actual (HEAD)
  
  upload     se realiza un commit de los archivos de [staged_files] con un
             mensaje en caso que se quiera y se actualiza la rama remota
           
  download   se srescriben los archivos de [staged_files] con los que estan en 
             la rama remota. Se crea una salva de la carpeta en la que se 
             realiza el cambio.
             
  save       Se crea una salva de la carpeta actual en un archivo tar.gz 
             
  restore    restaura el estado del directorio a partir de un archivo tar.gz dado
           """
        print(help)

class LINUX:
    
    def __init__(self):
        pass
    
    def backup_tar_gz(self):
        '''
        Realiza una salva de todos los archivos del directorio.
        '''
        now = datetime.now()
        dd = str(datetime.now()).split(' ')[0].split('-')
        dt = str(datetime.now()).split(' ')[1].split(':')
        system_datetime_raw = '{0}{1}{2}_{3}{4}{5}'.format(dd[0],dd[1],dd[2],dt[0],dt[1],dt[2].split('.')[0])
        
        os.system('tar -czvf {0}-backup.tar.gz *'.format(system_datetime_raw))
        
    def rm(self):
        '''
        Elimina todos los archivos del directorio exceptp los .tar.gz
        '''
        os.system("find . \! -name '*.tar.gz' -delete")
    
    def restore_tar_gq(self,file_name):
        '''
            Restaura el estado del directorio a partir del tar.gz file_name
        '''
        os.system(f'tar -xzvf {file_name}')
    
def main(function,arg2=''):
    
    git = GIT()
    cmd = LINUX()
    
    if function == 'upload':
        #git.status()
        git.add(staged_files)
        git.status()
        git.commit(arg2)
        git.save_credential()
        git.push()
        
    elif function == 'download':
        cmd.backup_tar_gz()
        git.checkout_file(staged_files) 
        git.commit(arg2)
        git.save_credential()
        git.pull()

    elif function == 'status':
        git.status()
        git.remote_v()
        #git.remote_show_origin()
    
    elif function == 'log':
        git.log()
    
    elif function == 'commit':
        git.add(staged_files)
        git.commit(arg2)
    
    elif function == 'addbr':
        git.checkout_b(arg2)
        
    elif function == 'chbr':
        git.checkout(arg2)
        
    elif function == 'rmbr':
        git.branch_d(arg2)
    
    elif function == 'merge':
        git.merge(arg2)
    
    elif function == 'save':
        cmd.backup_tar_gz()
        
    elif function == 'restore':
        cmd.rm()
        cmd.restore_tar_gq(arg2)
        
    else: 
        error = f"""
command no found => [{function}]

LOS COMANDO DISPONIBLES SE MUESTRAN ABAJO"""
        print (error)
        git.help()

if __name__ == '__main__':
    git = GIT()
    try: 
        function = sys.argv[1]
        if function in ['addbr','chbr','rmbr']:
            try:    
                arg2 = sys.argv[2]
                main(function,arg2)
            except: 
                print('se espera el nombre de la branch')
                print('spy.py [command] [branch]')
        elif function in ['commit','upload']:
            try:    
                main(function,sys.argv[2])
            except: 
                main(function)
        elif function in ['restore']:
            try:    
                main(function,sys.argv[2])
            except: 
                print('se espera el nombre del archivo tar.gz')
                print('spy.py [restore] [file.tar.gz]')
        else: 
            main(function)
            
    except:
        git.help()
