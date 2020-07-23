#!/drbd/www/cgi-bin/spx/aut_env/bin/python3.6
'''
DRIVER PARA EL TRABAJO CON LA BASE DE DATOS GDA DE MySQL

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.1 07-06-2020
''' 

# CANEXIONES
from sqlalchemy import create_engine
from sqlalchemy import text
from collections import defaultdict
from __CORE__.drv_config import dbuser,dbpasswd,dbhost,dbaseName


class GDA(object):
    '''
        trabajo con base de datos con la estructura GDA
        parametros necesarios
        dbuser
        dbpasswd
        dbhost
        dbaseName
    '''

    def __init__(self, dbuser = dbuser, dbpasswd = dbpasswd, dbhost = dbhost, dbaseName = dbaseName ):
        '''
        Constructor
        '''
        self.datasource = ''
        self.engine = ''
        self.conn = ''
        self.connected = False
        self.url = 'mysql://{0}:{1}@{2}/{3}'.format(dbuser,dbpasswd,dbhost,dbaseName)
        
    def connect(self):
        """
        Retorna True/False si es posible generar una conexion a la bd GDA
        """
        
        if self.connected:
            return self.connected
        
        try:
            self.engine = create_engine(self.url)
        except Exception as err_var:
            self.connected = False
            print('ERROR_{0}: engine NOT created. ABORT !!'.format(dbaseName))
            print('ERROR: EXCEPTION_{0} {1}'.format(dbaseName, err_var))
            exit(1)
        
        try:
            self.conn = self.engine.connect()
            self.connected = True
        except Exception as err_var:
            self.connected = False
            print('ERROR_{0}: NOT connected. ABORT !!'.format(dbaseName))
            print('ERROR: EXCEPTION_{0} {1}'.format(dbaseName, err_var))
            exit(1)

        return self.connected

    def read_all_dlg_conf(self, dlgid):
        '''
        Leo la configuracion desde GDA
                +----------+---------------+------------------------+----------+
                | canal    | parametro     | value                  | param_id |
                +----------+---------------+------------------------+----------+
                | BASE     | RESET         | 0                      |      899 |
                | BASE     | UID           | 304632333433180f000500 |      899 |
                | BASE     | TPOLL         | 60                     |      899 |
                | BASE     | COMMITED_CONF |                        |      899 |
                | BASE     | IMEI          | 860585004331632        |      899 |

                
        '''
        
        if not self.connect():
            return

        sql = """SELECT spx_unidades_configuracion.nombre as 'canal', spx_configuracion_parametros.parametro, 
                    spx_configuracion_parametros.value, spx_configuracion_parametros.configuracion_id as 'param_id' FROM spx_unidades,
                    spx_unidades_configuracion, spx_tipo_configuracion, spx_configuracion_parametros 
                    WHERE spx_unidades.id = spx_unidades_configuracion.dlgid_id 
                    AND spx_unidades_configuracion.tipo_configuracion_id = spx_tipo_configuracion.id 
                    AND spx_configuracion_parametros.configuracion_id = spx_unidades_configuracion.id 
                    AND spx_unidades.dlgid = '{}'""".format (dlgid)            
                    
        try:
            query = text(sql)
        except Exception as err_var:
            print(err_var)
            return False

        try:
            rp = self.conn.execute(query)
        except Exception as err_var:
            print(err_var)
            return False

        results = rp.fetchall()
        d = defaultdict(dict)
        for row in results:
            #print(row)
            canal, pname, value, pid = row
            d[(canal, pname)] = value
        return d

    def read_dlg_conf(self,dlgid,canal,param):
        self.connect()
        dlg_config = self.read_all_dlg_conf(dlgid)
        key = (canal, param)
        return dlg_config.get(key)
        

