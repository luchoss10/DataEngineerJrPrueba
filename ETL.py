import re
import json
import numpy as np
import pandas as pd

def getSheetData (df):
    datos_erroneos = 0
    fecha =  df.iloc[2,1]
    semana = df.iloc[3, 1]
    #print(semana)
    #Dataframe para concatenar los datos de cada granja en el sheet
    sheet_df = pd.DataFrame()
    sheet_df2 = pd.DataFrame()

    #Creacion de primeras columnas 
    frist_cols = df.iloc[6:,1:3]
    first_cols_names = ['lesionTipo', 'lesionRango']
    frist_cols.columns = first_cols_names

    for i, val in enumerate(range(3, len(df.columns),6)):
        list_ids = ['1','2','3','4','5']
        #Informacion para transformar 
        content = df.iloc[6:, val:val+5]
        content.columns = list_ids
        content = content.dropna(axis='columns', how = 'all')
        list_ids = content.columns

        #Valores individuales
        granja = df.iloc[0,val]

        if pd.isnull(granja):
            pass
        else:
            #fecha = datetime.fromtimestamp(fecha).strftime('%y-%m-%d')
            edad_str = str(df.iloc[1,val]).replace(' ', '')
            #print(edad_str)
            edad_dias = int(re.findall(r'\d+', edad_str)[0]) # cambio 
            ciclo = float(df.iloc[2,val])
            no_galpon = float(df.iloc[4,val])
            planVacuna = df.iloc[0,val+3]
            influenzaVacuna = df.iloc[1,val+3]
            newcastleVacuna = df.iloc[2,val+3]
            gumboroVacuna = df.iloc[3,val+3]

            #Union rangos, lesiones con valores
            wdf = pd.concat([frist_cols, content], axis=1)
            #Cambio de valores Nulos por 0
            wdf.fillna(0, inplace=True)

            # --- Verificacion de valores de lesion en los rangos correspondientes ---
            #Verificacion de rango en string para la verificacion
            wdf.astype({first_cols_names[1]: 'str'})
            wdf2 = wdf
            for row, index in enumerate(wdf.index):
                lesion = wdf.iloc[row][first_cols_names[0]]
                if (lesion != 'Sexo' and 
                    lesion != 'Peso' and 
                    lesion != 'Condición de Hígado' and 
                    lesion !='INTEGRIDAD INTESTINAL'):
                    rango = str(wdf.iloc[row][first_cols_names[1]]).split('-')
                    for col in list_ids:
                        valor =  wdf.iloc[row][col]
                        if valor >= int(rango[0]) and valor <= int(rango[1]):
                            pass
                        else:
                            datos_erroneos += 1
                            wdf.loc[index, col] = int(rango[0])
                
                if lesion == 'Sexo':
                    rango = wdf.iloc[row][first_cols_names[1]].split('/')
                    for col in list_ids:
                        valor = wdf.iloc[row][col]
                        if (valor is rango[0]) or (valor is rango[1]) or (valor == 0):
                            pass
                        else:
                            datos_erroneos += 1
                            wdf.loc[index, col] = 0

                if lesion == 'Condición de Hígado':
                    rango = wdf.iloc[row][first_cols_names[1]].split('-')
                    for col in list_ids:
                        valor = wdf.iloc[row][col]
                        if isinstance(valor, str):
                            if ((rango[0] in valor) or 
                                (rango[1] in valor) or 
                                (rango[2] in valor)):
                                pass
                            else:
                                datos_erroneos += 1
                                wdf.loc[index, col] = 0
                        elif valor == 0:
                            pass
                        else:
                            datos_erroneos += 1
                            wdf.loc[index, col] = 0
            
            wdf = pd.melt(wdf, id_vars=[first_cols_names[0], first_cols_names[1]], value_vars=list_ids, 
                            var_name='nAnimal', value_name='lesionPromedio')

            wdf2 =  pd.melt(wdf2, id_vars=[first_cols_names[0], first_cols_names[1]], value_vars=list_ids, 
                            var_name='nAnimal', value_name='lesionPromedio')

            #Mapeo a nombre de columnas finales
            map_etiqueta = {'Sexo' : 'sexoAnimales', 
                            'Bursometro' : 'bursometro', 
                            'Condición de Hígado' : 'condicionHigado', 
                            'INTEGRIDAD INTESTINAL' : 'integridadintestinal'}
            
            for key in map_etiqueta:
                wdf[map_etiqueta[key]] = ''
                values = wdf[wdf[first_cols_names[0]] == key]
                wdf2[map_etiqueta[key]] = ''
                values2 = wdf2[wdf2[first_cols_names[0]] == key]
                for j in range(1, len(values.index)+1):
                    idx = values.index[j-1]
                    idx2 = values2.index[j-1]
                    wdf.drop(idx, inplace=True)
                    wdf.loc[wdf.nAnimal == str(j), map_etiqueta[key]] = values.iloc[j-1,3]
                    wdf2.drop(idx2, inplace=True)
                    wdf2.loc[wdf2.nAnimal == str(j), map_etiqueta[key]] = values2.iloc[j-1,3]

            wdf['fecha'] = fecha
            wdf['semana'] = semana
            wdf['granja'] = granja
            wdf['edadEnDias'] = edad_dias
            wdf['ciclo'] = ciclo
            wdf['noGalpon'] = no_galpon
            wdf['planVacuna'] = planVacuna
            wdf['influenzaVacuna'] = influenzaVacuna
            wdf['newcastleVacuna'] = newcastleVacuna
            wdf['gumboroVacuna'] = gumboroVacuna

            wdf2['fecha'] = fecha
            wdf2['semana'] = semana
            wdf2['granja'] = granja
            wdf2['edadEnDias'] = edad_dias
            wdf2['ciclo'] = ciclo
            wdf2['noGalpon'] = no_galpon
            wdf2['planVacuna'] = planVacuna
            wdf2['influenzaVacuna'] = influenzaVacuna
            wdf2['newcastleVacuna'] = newcastleVacuna
            wdf2['gumboroVacuna'] = gumboroVacuna

            sheet_df = sheet_df.append(wdf)
            sheet_df2 = sheet_df2.append(wdf2)
            
    return sheet_df, sheet_df2, datos_erroneos

def cargaArchivos(ndata, nmap):
    sheets = list(range(1,   35))
    dict_data = pd.read_excel(ndata, sheet_name=sheets, header=None)
    with open(nmap) as f:
        aux_data = json.load(f)
    return dict_data, aux_data

def tranformacionData(dict_data):

    datos_errados = 0
    clean_complete_data = pd.DataFrame()
    all_complete_data = pd.DataFrame()

    for key in dict_data:
        df = dict_data[key].iloc[:44,:]
        sheet_df, sheet_df2, datos_erroneos = getSheetData(df)
        clean_complete_data = clean_complete_data.append(sheet_df)
        all_complete_data = all_complete_data.append(sheet_df2)

        datos_errados = datos_erroneos + datos_errados 

    clean_complete_data = clean_complete_data.loc[clean_complete_data['lesionTipo'] != 'Peso']
    all_complete_data = all_complete_data.loc[all_complete_data['lesionTipo'] != 'Peso']

    clean_complete_data = clean_complete_data.reset_index(drop=True)
    all_complete_data = all_complete_data.reset_index(drop=True)


    clean_complete_data.loc[clean_complete_data.granja == 'Fortuna ', 'granja'] = 'Fortuna'
    clean_complete_data.loc[clean_complete_data.granja == 'Vergel ', 'granja'] = 'Vergel'
    clean_complete_data.loc[clean_complete_data.granja == 'Sta. Delfina', 'granja'] = 'Santa Defina'

    all_complete_data.loc[all_complete_data.granja == 'Fortuna ', 'granja'] = 'Fortuna'
    all_complete_data.loc[all_complete_data.granja == 'Vergel ', 'granja'] = 'Vergel'
    all_complete_data.loc[all_complete_data.granja == 'Sta. Delfina', 'granja'] = 'Santa Defina'

    clean_complete_data['fecha'] = pd.to_datetime(clean_complete_data['fecha'])
    all_complete_data['fecha'] = pd.to_datetime(all_complete_data['fecha'])

    return clean_complete_data, all_complete_data, datos_errados


if __name__ == '__main__':
    dict_exc, dict_map = cargaArchivos('prueba.xlsx', 'aux_data.json')
    data_corregida, data_sin_correccion, datos_errados = tranformacionData(dict_exc)

    data_corregida.to_csv('lesiones_pollos.csv')
    data_sin_correccion.to_csv('lesiones_polos_con_errores.csv')
    print('Tarea completada con {} datos errados'.format(datos_errados))


