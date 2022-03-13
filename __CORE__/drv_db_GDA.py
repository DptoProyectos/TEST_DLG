
'''
DRIVER PARA EL TRABAJO CON LA BASE DE DATOS GDA DE MySQL

Created on 16 mar. 2020 

@author: Yosniel Cabrera

Version 2.1.1 07-06-2020
''' 

# DEPENDENCIAS
from sqlalchemy import Table, select, create_engine, MetaData, update, delete
from sqlalchemy.orm import sessionmaker
from collections import defaultdict
from __CORE__.drv_config import dbUrl


class GDA(object):
    '''
        clase para el trabajo con la base de datos GDA
    '''

    def __init__(self,dbUrl):
            '''
                Constructor
            '''
            self.engine = None
            self.conn = None
            self.connected = False
            self.metadata = None
            self.session = None
            #self.url = 'mysql+pymysql://pablo:spymovil@192.168.0.8/GDA'
            #self.url = 'postgresql+psycopg2://admin:pexco599@192.168.0.6/GDA'
            self.url = dbUrl        
    def connect(self):
        """
            Retorna True/False si es posible generar una conexion a la bd GDA
        """
        try:
            self.engine = create_engine(self.url)
            Session = sessionmaker(bind=self.engine) 
            self.session = Session()
        except Exception as err_var:
            print('ERROR: engine NOT created. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            return False

        try:
            self.conn = self.engine.connect()
        except Exception as err_var:
            print('ERROR: NOT connected. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            return False

        self.metadata = MetaData()
        return True

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
        

