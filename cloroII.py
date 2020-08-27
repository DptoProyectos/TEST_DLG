#!/drbd/www/cgi-bin/spx/aut_env/bin/python3.6

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import seaborn as sns
from sqlalchemy import create_engine, MetaData, text, Table
from datetime import datetime
import gzip

PATH = '/home/pablo/Spymovil/scripts/python/AnalisisCloroTemperatura/'
FNAME = 'datos_cloroII.csv'
url = 'mysql+pymysql://pablo:spymovil@192.168.0.8/GDA'
DLG_LIST = ['NSEN01', 'NSEN02', 'NSEN03', 'NSEN04']
DIAS_ATRAS = 10


class CLORO:

    def __init__(self):
        self.df_base = None
        self.df_parametros = None
        self.wdf = None
        self.dlg_list = []
        sns.set()

    # ---------------------------------------------------------------------------------------------------
    # DATOS BASE
    def leer_datos_from_bd(self, dias_atras=DIAS_ATRAS, dlg_list=DLG_LIST, debug=False):
        '''
        Lee los datos de los dataloggers en testing desde la base de datos
        Guarda los datos en un archivo CSV
        Los deja en un dataframe que lo retorna
        '''
        engine = None
        try:
            engine = create_engine(url)
        except Exception as err_var:
            print('ERROR: engine NOT created. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            exit(1)

        conn = None
        try:
            conn = engine.connect()
        except Exception as err_var:
            print('ERROR: NOT connected. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            exit(1)

        metadata = MetaData()
        T1 = Table('spx_datos', metadata, autoload=True, autoload_with=engine)
        T1.columns.keys()
        sql = """SELECT T2.dlgid, T1.fechadata, T1.valor, T1.medida_id 
           FROM spx_datos as T1 
           JOIN spx_instalacion AS T3 ON T1.ubicacion_id = T3.ubicacion_id 
           JOIN spx_unidades AS T2 ON T2.id = T3.unidad_id 
           WHERE T1.medida_id IN (170, 171) 
           AND T1.fechadata > SUBDATE(NOW(),'{0}')
           AND T1.fechadata < NOW()
           AND T2.dlgid IN {1} ORDER BY dlgid,fecha""".format(dias_atras, tuple(dlg_list))
        query = text(sql)
        if debug is True:
            print(query)
        rp = conn.execute(query)
        self.df_base = pd.DataFrame(rp.fetchall())
        self.df_base.columns = rp.keys()
        self.df_base.index.name = 'idx'
        # Convierto a archivo y zipeo
        now = datetime.now()
        csv_file_name = 'datos_cloro_{}.csv'.format(now.strftime('%Y%m%d'))
        self.df_base.to_csv(csv_file_name)
        # Convierto el archivo a gzip para transportarlo mejor
        f_in = open(csv_file_name, 'rb')
        data = f_in.read()
        bindata = bytearray(data)
        with gzip.open(csv_file_name + '.gz', 'wb') as f_out:
            f_out.write(bindata)
            f_out.close()
        # Luego podemos traernos el archivo csv para comenzar a analizarlo
        return self.df_base

    def leer_datos_from_csv(self, file, path=PATH):
        """
        Leo los datos de un archivo .csv con la informacion bajada de la BD
        de varios dataloggers.
        """
        full_file_name = os.path.join(path, file)
        if os.path.isfile(full_file_name) is False:
            print('No existe archivo {}'.format(full_file_name))
            print('Debe leer desde la bd !!')
            return None
        self.df_base = pd.read_csv(full_file_name, index_col='idx')
        return self.df_base

    def get_df_base(self):
        return self.df_base

    def get_dlg_list(self):
        return self.dlg_list

    def leer_parametros_from_bd(self, dlg_list=DLG_LIST):
        engine = None
        try:
            engine = create_engine(url)
        except Exception as err_var:
            print('ERROR: engine NOT created. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            exit(1)

        conn = None
        try:
            conn = engine.connect()
        except Exception as err_var:
            print('ERROR: NOT connected. ABORT !!')
            print('ERROR: EXCEPTION {0}'.format(err_var))
            exit(1)

        metadata = MetaData()
        sql = """SELECT T1.parametro, T1.value,T3.dlgid FROM spx_configuracion_parametros AS T1
            INNER JOIN spx_unidades_configuracion AS T2
            ON T1.configuracion_id = T2.id
            INNER JOIN spx_unidades as T3
            ON T2.dlgid_id = T3.id
            WHERE T1.parametro IN ('TDIAL','TPOLL')
            AND T2.nombre = 'BASE'
            AND T3.dlgid IN {0}""".format(tuple(dlg_list))
        query = text(sql)
        # print(query)
        # Armo un dataframe con los datos leidos
        rp = conn.execute(query)
        self.df_parametros = pd.DataFrame(rp.fetchall())
        self.df_parametros.columns = rp.keys()
        # Reacomodo el df para que quede mas facil de trabajar
        self.df_parametros.set_index(['dlgid', 'parametro'], drop=True, inplace=True)
        self.df_parametros = self.df_parametros.unstack('parametro')
        self.df_parametros.index.name = 'dlgid'
        self.df_parametros.columns = ['TDIAL','TPOLL']
        # El resultado lo deja en un archivo csv para no tener que leer siempre la BD.
        now = datetime.now()
        csv_file_name = 'parametros_cloro_{}.csv'.format(now.strftime('%Y%m%d'))
        self.df_parametros.to_csv(csv_file_name)
        # Convierto el archivo a gzip para transportarlo mejor
        f_in = open(csv_file_name, 'rb')
        data = f_in.read()
        bindata = bytearray(data)
        with gzip.open(csv_file_name + '.gz', 'wb') as f_out:
            f_out.write(bindata)
            f_out.close()
        # Luego podemos traernos el archivo csv para comenzar a analizarlo
        return self.df_parametros

    def leer_parametros_from_csv(self, file, path=PATH):
        """
        Leo los datos de un archivo .csv con la informacion bajada de la BD
        de varios dataloggers.
        """
        full_file_name = os.path.join(path, file)
        if os.path.isfile(full_file_name) is False:
            print('No existe archivo {}'.format(full_file_name))
            print('Debe leer desde la bd !!')
            return None
        self.df_parametros = pd.read_csv(full_file_name, index_col='dlgid')
        return self.df_parametros

    def get_df_parametros(self):
        if self.df_parametros is None:
            print('No se han leido los parametros de la bd ni csv. !!')
            return None
        return self.df_parametros

    # ---------------------------------------------------------------------------------------------------
    # PREPARACION DE DATOS
    def preparar_datos_df_base(self):
        # Reordena el df para facilitar operar en el.
        # Renombra las magnitudes para acceder por nombre
        # El resultado es el wdf que es el df_base indexado en columnas por dlgid
        self.wdf=self.df_base.copy()
        medida_id_2_medida_name = {170: 'CLORO', 171: 'TEMP'}
        self.wdf.medida_id = self.wdf.medida_id.map(medida_id_2_medida_name)
        # Generar un indice compuesto
        self.wdf.fechadata = pd.to_datetime(self.wdf.fechadata)
        self.wdf.set_index(['fechadata','dlgid','medida_id'], drop=True, inplace=True)
        # Creo 2 niveles de columnas
        self.wdf = self.wdf.unstack(['dlgid', 'medida_id'])
        # Me quedo con una lista de los dlgid que tienen datos reales.
        self.dlg_list = list(self.wdf.columns.levels[1])
        return self.wdf

    def get_wdf(self):
        return self.wdf

    def pv_datos2quality( self,row,dpd=1440):
        perf = np.abs(row['count'] / dpd - 1)
        if perf < 0.05:
            return 'OK'
        elif perf < 0.1:
            return 'WARN'
        else:
            return 'FAIL'

    def check_calidad_datos(self):
        '''
        Revisa para c/datalogger que la cantidad de datos por hora sea la correcta,
        es decir que no hallan holes o datos perdidos.
        Toleramos un 5% de perdidas
        '''
        if self.df_base is None:
            print('ERROR: debe leer los datos primero.!!')
            return None
        if self.dlg_list is None:
            print('ERROR: debe leer la lista de dlg disponibles primero.!!')
            return None
        if self.df_parametros is None:
            print('ERROR: debe leer los parametros primero.!!')
            return None
        if self.wdf is None:
            print('ERROR: debe preparar los datos primero.!!')
            return None
        #
        qdf = pd.DataFrame()
        for dlgid in self.dlg_list:
            DATOS_X_HORA = 3600 / int(self.df_parametros.loc[dlgid, 'TPOLL'])
            DATOS_X_DIA = 24 * DATOS_X_HORA
            # Me quedo con los datos del dlg en cuestion
            df_tmp = self.wdf['valor',dlgid].dropna().copy()
            # Lo indexo en fecha y hora
            df_tmp['fecha'] = df_tmp.index.strftime('%Y-%m-%d')
            df_tmp.fecha = pd.to_datetime(df_tmp.fecha)
            df_tmp['hora'] = df_tmp.index.strftime('%H')
            df_tmp.set_index(['fecha', 'hora'], drop=True, inplace=True)
            datos_x_hora = df_tmp.groupby(['fecha','hora'])['CLORO'].count()
            datos_x_dia = df_tmp.groupby('fecha')['CLORO'].count().to_frame(name='count')
            # Por ahora el analisis lo voy a hacer diario ya que estoy en modo batch
            datos_x_dia[dlgid] = datos_x_dia.apply( self.pv_datos2quality, args=(DATOS_X_DIA,), axis=1)
            #print( datos_x_dia)
            qdf = pd.concat([ qdf,datos_x_dia[dlgid]], axis=1)
        return qdf

    # ---------------------------------------------------------------------------------------------------
    # VISUALIZACION
    def visualizar_all_dlg(self):
        '''
        Grafica el cloro y la temperatura para todos los dataloggers en el mismo
        frame de modo de poder compararlos
        '''
        nrows = len(self.dlg_list)
        fig,ax=plt.subplots(nrows,1,figsize=(10,10) )
        #
        for (i,dlgid) in enumerate(self.dlg_list):
            data = self.wdf['valor', dlgid].dropna().copy().resample('1Min', axis=0).mean()
            #
            cloro_media = data.CLORO.mean()
            ax[i].plot(data.index,data.CLORO,color='red',label='Cloro')
            ax[i].hlines(y=cloro_media, xmin=data.index[0], xmax=data.index[-1], color='red')
            ax[i].text(x=data.index[0], y=cloro_media + 0.2, s=('hcl=%.02f' % cloro_media), color='black')
            #
            temp_media = data.TEMP.mean()
            ax[i].plot(data.index,data.TEMP,color='blue',label='Temp')
            ax[i].hlines(y=temp_media, xmin=data.index[0], xmax=data.index[-1], color='blue')
            ax[i].text(x=data.index[0], y=temp_media + 0.2, s=('tmp=%.02f' % temp_media), color='black')
            #
            ax[i].set_title(dlgid)
            ax[i].set_ylabel('Cloro/Temp')

            ax[i].legend()
        plt.tight_layout()

    def visualizar_x_mag(self,magnitud='TEMP'):
        '''
        Visualiza en una ventana la misma magnitud para todas las unidades
        '''
        df_boundle=pd.DataFrame()
        for (i, dlgid) in enumerate(self.dlg_list):
            data = self.wdf['valor', dlgid].dropna().copy().resample('1Min', axis=0).mean()[magnitud].to_frame(name=dlgid)
            df_boundle = pd.concat([df_boundle, data[dlgid]], axis=1)
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        df_boundle.plot(ax=ax)
        plt.tight_layout()
        return

    # ---------------------------------------------------------------------------------------------------
    # CORRELACIONES
    def correlacion_x_mag(self, magnitud='TEMP'):
        df_bundle=pd.DataFrame()
        for (i, dlgid) in enumerate(self.dlg_list):
            data = self.wdf['valor', dlgid].dropna().copy().resample('1Min', axis=0).mean()[magnitud].to_frame(name=dlgid)
            df_bundle = pd.concat([df_bundle, data[dlgid]], axis=1)
        df_corr = df_bundle.corr()
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))
        sns.heatmap(df_corr, annot=True, ax=ax)
        ax.set_title('Correlacion entre {}'.format(magnitud))
        plt.xticks(rotation=45)
        return df_corr

    def correlacion_temp_cloro(self):
        s_corr=pd.Series()
        for (i, dlgid) in enumerate(self.dlg_list):
            data = self.wdf['valor', dlgid].dropna().copy().resample('1Min', axis=0).mean()
            corr = data.TEMP.corr(data.CLORO)
            s_corr[dlgid] = corr
        return s_corr.to_frame('CORR')

    # ---------------------------------------------------------------------------------------------------
    # ANALISIS
    def analizar_dlg(self,dlgid=None):
        '''
        Analizo los datos y genero los plots para un equipo en particular.
        '''
        if dlgid is None:
            print('ERROR: Debe ingresar un dlgid !!.')
            return None

        data = self.wdf['valor', dlgid].dropna().copy().resample('1Min', axis=0).mean()
        # Valores medios (DC)
        cloro_media = data.CLORO.mean()
        temp_media = data.TEMP.mean()
        # Valores sin DC
        data['CLORO_AC'] = data.CLORO.sub(cloro_media)
        data['TEMP_AC'] = data.TEMP.sub(temp_media)
        # Valores diferenciales(incrementos)
        data['DIFF_CL'] = data.CLORO.diff()
        data['DIFF_TEMP'] = data.TEMP.diff()
        # Visualizo
        fig, ax = plt.subplots(3, 1, figsize=(10, 9))
        #
        ax[0].plot(data.index, data.CLORO, color='red', label='Cloro')
        ax[0].hlines(y=cloro_media, xmin=data.index[0], xmax=data.index[-1], color='black')
        ax[0].text(x=data.index[0], y=cloro_media + 0.2, s=('hcl=%.02f' % cloro_media), color='black')
        ax[0].plot(data.index, data.TEMP, color='blue', label='Temp')
        ax[0].hlines(y=temp_media, xmin=data.index[0], xmax=data.index[-1], color='black')
        ax[0].text(x=data.index[0], y=temp_media + 0.2, s=('tmp=%.02f' % temp_media), color='black')
        ax[0].set_title('{}: Valores medidos'.format(dlgid))
        ax[0].set_ylabel('Cloro/Temp')
        ax[0].legend()
        #
        ax[1].plot(data.index, data.CLORO_AC, color='red', label='Cloro_ac')
        ax[1].plot(data.index, data.TEMP_AC, color='blue', label='Temp_ac')
        ax[1].hlines(y=0, xmin=data.index[0], xmax=data.index[-1], color='black')
        ax[1].set_title('{}: Variacion'.format(dlgid))
        ax[1].set_ylabel('Cloro/Temp')
        ax[1].legend()
        #
        ax[2].plot(data.index, data.DIFF_CL, color='red', label='Diff.Cloro')
        ax[2].plot(data.index, data.DIFF_TEMP, color='blue', label='Diff.Temp')
        ax[2].set_title('{}: Diff Cloro/Temp'.format(dlgid))
        ax[2].set_ylabel('Diff Cloro/Temp')
        ax[2].legend()
        #
        plt.tight_layout()
        return data

    def modelado_lineal(self,dlgid=None):
        '''
        Calcula los parametros de correlacion y modela la relacion por medio de
        una regresion. Es valido si la correlacion es alta
        '''
        if dlgid is None:
            print('ERROR: Debe ingresar un dlgid !!.')
            return None

        data = self.wdf['valor', dlgid].dropna().copy().resample('1Min', axis=0).mean()
        # Valores medios (DC)
        cloro_media = data.CLORO.mean()
        temp_media = data.TEMP.mean()
        # Valores sin DC
        data['CLORO_AC'] = data.CLORO.sub(cloro_media)
        data['TEMP_AC'] = data.TEMP.sub(temp_media)
        # Valores diferenciales(incrementos)
        data['DIFF_CL'] = data.CLORO.diff()
        data['DIFF_TEMP'] = data.TEMP.diff()
        data.dropna(inplace=True)
        # Correlaciones
        print('Resumen de correlaciones: DLGID={0}'.format(dlgid))
        corr = data['TEMP_AC'].corr(data['CLORO_AC'])
        print('Correlacion TEMP_AC/CLORO_AC={0}'.format(corr))
        # Modelado lineal
        X = data['TEMP_AC'].values.reshape(-1, 1)
        Y = data['CLORO_AC'].values.reshape(-1, 1)
        regresion = LinearRegression()
        regresion.fit(X,Y)
        Y_predict = regresion.predict(X)
        data['CLORO_ACP'] = Y_predict
        # Cloro_pred = cloro_dc + f(Temp) = cloro_media + cloro_acp
        data['CLORO_PRED'] = data['CLORO_ACP'].add(cloro_media)
        print('Root Mean Squared Error:', np.sqrt(mean_squared_error(Y_predict, Y)))
        print('R2 score:', r2_score(Y_predict, Y))
        #
        # Correccion del cloro real.
        # Le resto la parte de alterna calculada a partir de la regresion de la temperatura
        data['CLORO_LIN'] = data['CLORO'].sub(data['CLORO_ACP'])
        #
        # Visualizacion
        fig, ax = plt.subplots(1, 2, figsize=(15, 5))
        ax[0].plot(data.index, data.CLORO_AC, color='red', label='Cloro_ac')
        ax[0].plot(data.index, data.TEMP_AC, color='blue', label='Temp_ac')
        ax[0].plot(data.index, data.CLORO_ACP, color='magenta', label='Cloro_pred')
        ax[0].hlines(y=0, xmin=data.index[0], xmax=data.index[-1], color='black')
        ax[0].set_title('{}: Modelado Lineal'.format(dlgid))
        ax[0].set_ylabel('Cloro/Temp')
        plt.setp(ax[0].get_xticklabels(), rotation=45)
        ax[0].legend()
        #
        ax[1].plot(data.index, data.CLORO, color='green', label='Cloro')
        ax[1].plot(data.index, data.CLORO_PRED, color='magenta', label='Cloro_pred')
        ax[1].plot(data.index, data.TEMP, color='blue', label='Temp')
        ax[1].plot(data.index, data.CLORO_LIN, color='black', label='Cloro_lin')
        ax[1].hlines(y=0, xmin=data.index[0], xmax=data.index[-1], color='black')
        ax[1].set_title('{}: Cloro Predicted.'.format(dlgid))
        ax[1].set_ylabel('Cloro/Cloro_pred.')
        plt.setp(ax[1].get_xticklabels(), rotation=45)
        ax[1].legend()
        plt.tight_layout()
        return data


def testing():
    cloro = CLORO()
    _ = cloro.leer_datos_from_csv(file='datos_cloro_20200826.csv')
    _ = cloro.leer_parametros_from_csv(file='parametros_cloro_20200826.csv')
    _ = cloro.preparar_datos_df_base()
    df_qty = cloro.check_calidad_datos()
    print(df_qty)


if __name__ == '__main__':
    testing()
    exit(0)

