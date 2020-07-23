#!/drbd/www/cgi-bin/spx/aut_env/bin/python3.6

"""

from importlib import reload
version 1.0.0

"""
from sqlalchemy import create_engine, MetaData
from sqlalchemy import text, Table, select, join
from sys import argv
import pandas as pd
import datetime
#import pymysql6
import os

#LISTA_DLGID = ['FTEST02','FTEST03','FTEST04','FTEST05','NSEN04','NSEN05','NSEN06','NSEN07','NSEN08','NSEN09','NSEN10','NSEN12','NSEN16','NSEN15','NSEN01','NSEN02','NSEN03', 'NSEN14','NSEN17','NSEN18','NSEN19','NSEN20','NSEN21','NSEN22','NSEN23','NSEN24','NSEN25','NSEN26']
LISTA_DLGID = ['UYTAC032','UYTAC042','UYTAC044','UYTAC045']
#LISTA_DLGID = ['UYTAC032']
#LISTA_DLGID = ['NSEN01','NSEN02','NSEN03','NSEN04','NSEN05']
#LISTA_DLGID = ['NSEN06','NSEN07','NSEN08','NSEN09','NSEN10']
#LISTA_DLGID = ['NSEN12']
#LISTA_DLGID = ['NSEN14','NSEN15','NSEN16','NSEN17','NSEN18','NSEN19','NSEN20']
#LISTA_DLGID = ['NSEN21','NSEN22','NSEN23','NSEN24','NSEN25']
#LISTA_DLGID = ['FTEST02','FTEST03','FTEST04','FTEST05']


class DATABASE:

    def __init__(self,):
        self.engine = None
        self.conn = None
        self.connected = False
        self.metadata = None
        self.url = 'mysql+pymysql://pablo:spymovil@192.168.0.8/GDA'

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
            print('ERROR: engine NOT created. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            exit(1)

        try:
            self.conn = self.engine.connect()
        except Exception as err_var:
            self.connected = False
            print('ERROR: NOT connected. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            exit(1)

        self.connected = True
        self.metadata = MetaData()
        return self.connected

    def leer_df_inits(self, fecha_inicio='2020-06-17 12:00'):
        tb_inits = Table('spx_inits', self.metadata, autoload=True, autoload_with=self.engine)
        sel = select([tb_inits.c.dlgid_id, tb_inits.c.csq, tb_inits.c.fecha])
        sel = sel.where(tb_inits.c.fecha > '{0}'.format(fecha_inicio))
        rp = self.conn.execute(sel)
        df = pd.DataFrame(rp.fetchall())
        df.columns = rp.keys()
        return df

    def leer_df_unidades(self, lista_dlgid=None):
        if lista_dlgid is None:
            lista_dlgid = LISTA_DLGID
        tb_unidades = Table('spx_unidades', self.metadata, autoload=True, autoload_with=self.engine)
        sel = select([tb_unidades.c.id, tb_unidades.c.dlgid]).where(tb_unidades.c.dlgid.in_(lista_dlgid))
        rp = self.conn.execute(sel)
        df = pd.DataFrame(rp.fetchall())
        df.columns = rp.keys()
        return df

    def leer_df_datalines(self, fecha_inicio='2020-06-17 12:00'):
        tb_datos = Table('spx_datos', self.metadata, autoload = True, autoload_with=self.engine)
        sel = select([tb_datos.c.fechadata, tb_datos.c.valor, tb_datos.c.ubicacion_id])
        sel = sel.where(tb_datos.c.medida_id == 8)
        sel = sel.where(tb_datos.c.fechadata > '{0}'.format(fecha_inicio))
        sel = sel.where(tb_datos.c.fechadata < datetime.datetime.now())
        rp = self.conn.execute(sel)
        df = pd.DataFrame(rp.fetchall())
        df.columns = rp.keys()
        return df

    def leer_df_ubicaciones_id(self, lista_dlgid=None):
        if lista_dlgid is None:
            lista_dlgid = LISTA_DLGID
        tb_instalacion = Table('spx_instalacion', self.metadata, autoload = True, autoload_with = self.engine )
        tb_unidades = Table('spx_unidades', self.metadata, autoload=True, autoload_with=self.engine)
        j = tb_instalacion.join(tb_unidades, tb_instalacion.c.unidad_id == tb_unidades.c.id)
        sel = select([tb_instalacion.c.ubicacion_id, tb_unidades.c.dlgid])
        sel = sel.select_from(j)
        sel = sel.where(tb_unidades.c.dlgid.in_(lista_dlgid))
        rp = self.conn.execute(sel)
        df = pd.DataFrame(rp.fetchall())
        df.columns = rp.keys()
        return df

    def process_df_inits(self, fecha_inicio='2020-06-17 12:00', lista_dlgid=None):
        if lista_dlgid is None:
            lista_dlgid = LISTA_DLGID
        df_unidades = self.leer_df_unidades(lista_dlgid)
        df_inits = self.leer_df_inits(fecha_inicio)
        """
        Combino los 2 df. para tener uno solo con los dlgid y los datos
        """
        df = pd.merge(df_unidades, df_inits, left_on='id', right_on='dlgid_id')
        index = pd.to_datetime(df.fecha)
        df.index = index
        df.drop(['dlgid_id', 'id', 'fecha'], axis=1, inplace=True)
        df['day'] = df.index.strftime('%d')
        df['hour'] = df.index.strftime('%H')
        df_tmp = df.groupby(['dlgid', 'day', 'hour']).size()
        """
        Tengo un df con un multiindice: dlgid | dia | hh
        """
        df_res = df_tmp.unstack(level=[0, 1])
        print(df_res.to_string())
        df_res.to_excel(r'inits.xlsx', sheet_name='inits')
        return df_res

    def process_df_datos(self, fecha_inicio='2020-06-17 12:00', lista_dlgid=None):
        if lista_dlgid is None:
            lista_dlgid = LISTA_DLGID
        df_ubicaciones_id = self.leer_df_ubicaciones_id(lista_dlgid)
        df_datalines = self.leer_df_datalines(fecha_inicio)
        """
        Combino los 2 df. para tener uno solo con los dlgid y los datos
        """
        df = pd.merge(df_datalines, df_ubicaciones_id, left_on='ubicacion_id', right_on='ubicacion_id')
        index = pd.to_datetime(df.fechadata)
        df.index = index
        df.drop(['ubicacion_id', 'valor', 'fechadata'], axis=1, inplace=True)
        df['day'] = df.index.strftime('%d')
        df['hour'] = df.index.strftime('%H')
        df_tmp = df.groupby(['dlgid', 'day', 'hour']).size()
        """
        Tengo un df con un multiindice: dlgid | dia | hh
        """
        df_res = df_tmp.unstack(level=[0, 1])
        print(df_res.to_string())
        df_res.to_excel(r'datos.xlsx', sheet_name='datos')
        return df_res

    def leer_parametros_unidades(self, lista_dlgid=None):
        """
        SELECT T1.parametro, T1.value,T3.dlgid FROM spx_configuracion_parametros AS T1
        INNER JOIN spx_unidades_configuracion AS T2
        ON T1.configuracion_id = T2.id
        INNER JOIN spx_unidades as T3
        ON T2.dlgid_id = T3.id
        WHERE T1.parametro IN ('TDIAL','TPOLL')
        AND T2.nombre = 'BASE'
        AND T3.dlgid IN ('TEST01','FTEST02');
        """
        if lista_dlgid is None:
            lista_dlgid = LISTA_DLGID
        tb_configuracion_parametros = Table('spx_configuracion_parametros', self.metadata, autoload=True, autoload_with=self.engine)
        tb_unidades_configuracion = Table('spx_unidades_configuracion', self.metadata, autoload=True, autoload_with=self.engine)
        tb_unidades = Table('spx_unidades', self.metadata, autoload=True,autoload_with=self.engine)
        T1 = tb_configuracion_parametros.alias('T1')
        T2 = tb_unidades_configuracion.alias('T2')
        T3 = tb_unidades.alias('T3')
        j1 = T1.join(T2,T1.c.configuracion_id == T2.c.id)
        j2 = T2.join(T3,T2.c.dlgid_id == T3.c.id)
        sel = select([T1.c.parametro, T1.c.value, T3.c.dlgid])
        sel = sel.select_from(j1)
        sel = sel.select_from(j2)
        sel = sel.where(T1.c.parametro.in_(['TDIAL','TPOLL']))
        sel = sel.where(T2.c.nombre == 'BASE')
        sel = sel.where(T3.c.dlgid.in_(lista_dlgid))
        rp = self.conn.execute(sel)
        df = pd.DataFrame(rp.fetchall())
        df.columns = rp.keys()
        return df

    def evaluar_resultados(self, fecha_inicio='2020-06-17 12:00', lista_dlgid=None):
        if lista_dlgid is None:
            lista_dlgid = LISTA_DLGID
        df_inits = bd.process_df_inits(fecha_inicio, lista_dlgid)
        df_datos = bd.process_df_datos(fecha_inicio, lista_dlgid)
        df_parametros = bd.leer_parametros_unidades(lista_dlgid)

    def run_files(self):
        print('RUN => inits.xlsx')
        os.system('lowriter inits.xlsx')
        print('RUN => datos.xlsx')
        os.system('lowriter datos.xlsx')
        

if __name__ == '__main__':

    opts = {'fecha_inicio':'2020-07-21 00:00', 'lista_dlg':LISTA_DLGID }

    if len(argv) > 1 and argv[1].startswith('--help'):
        print("""
        programa spx_analize.py: Analiza comportamiento de dataloggers SPX en base de datos GDA
        invocación: ./spx_analize.py fecha_inicio='yyyy-mm-dd hh:mm' lista_dlg=['dlg01','dlg02',...]
        Genera 2 archivos:
            inits.xlsx: planilla excel con el numero de conexiones
            datos.xlsx: planilla excel con el numero de dataframes transmitidos
        """)
        exit(0)

    while argv:
        if argv[0].startswith('fecha_inicio'):
            r, fecha_inicio = argv[0].split('=')
            opts['fecha_inicio'] = fecha_inicio
        elif argv[0].startswith('lista_dlg'):
            r, lista_dlg = argv[0].split('=')
            lista_dlg = lista_dlg[1:-1]
            l_dlg = lista_dlg.split(',')
            opts['lista_dlg'] = l_dlg
        argv = argv[1:]

    print('fecha_inicio={0}'.format(opts['fecha_inicio']))
    print('lista_dlg={0}'.format(opts['lista_dlg']))
    print('')

    bd = DATABASE()
    bd.connect()
    df_inits = bd.process_df_inits(opts['fecha_inicio'],opts['lista_dlg'])
    df_datos = bd.process_df_datos(opts['fecha_inicio'],opts['lista_dlg'])
    #bd.evaluar_resultados(opts['fecha_inicio'],opts['lista_dlg'])
    bd.run_files()
    
    exit(0)
