                            #VISAO: RESTAURANTE

#========================================================
# IMPORT LIBRARIES
#========================================================
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import folium
import streamlit as st
import numpy as np
from haversine import haversine
from PIL import Image
from datetime import datetime
from streamlit_folium import folium_static

#=======================================================
# FUNCTIONS
#=======================================================
def clean_data( df1 ):
    ''' Função que limpa o dataframe
        
        Limpezas efetuadas:
            1. Remoção de dados NaN
            2. Conversão de dados para os tipos corretos
            3. Remoção dos espaços nas strings
            4. Formatação da coluna de datas
            5. Remoção de string na coluna de tempo
        
            Input: Dataframe
            Output: Dataframe
    '''
    #retirar str 'NaN '
    linhas_select = (df1['Delivery_person_Age'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['multiple_deliveries'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['ID'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['Road_traffic_density'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['Type_of_order'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['Type_of_vehicle'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['City'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]
    linhas_select = (df1['Festival'] != 'NaN ')
    df1 = df1.loc[linhas_select, :]

    #converter para int
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype(int)
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype(int)

    #converter para float
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype(float)

    #converter para data
    df1['Order_Date'] = pd.to_datetime(df1['Order_Date'], format = '%d-%m-%Y')

    #resetar index
    df1 = df1.reset_index(drop = True)

    #retirar espaços
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #limpando coluna time taken
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply(lambda x: x.split('(min) ')[1])
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)

    return df1

def std_mean_festival(df1, festival, op):
    ''' 
        Função que retorna a média e desvio padrão com e sem festival de acordo com os Inputs:
            Input -> Output
                df1 -> dataframe
                festival = 'Yes' -> com festival
                festival = 'No' -> sem festival
                op = 'avg_time' -> retorna a média
                op = 'std_time' -> retorna o desvio padrão
    '''
    df_aux = (df1.loc[:, ['Festival', 'Time_taken(min)']]
                .groupby('Festival')
                .agg({'Time_taken(min)':['mean', 'std']}))
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    #linhas_select
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op], 2)

    return df_aux

def avg_delivery_city(df1):
    '''
        Função que:
            1. Retorna a média do tempo das entregas por cidade
            2. Plota um gráfico de barras
    '''
    df_aux = df1.loc[:, ['City','Time_taken(min)']].groupby('City').agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['Time_taken_mean', 'Time_taken_std']
    mean_std_city = df_aux.reset_index()
    fig = go.Figure()
    fig.add_trace( go.Bar( name='Control',
                            x=mean_std_city['City'],
                            y=mean_std_city['Time_taken_mean'],
                            error_y=dict(type='data', array=df_aux['Time_taken_std'])))
    fig.update_layout(barmode='group')
    
    return fig

def time_by_city_by_order(df1):
    '''
        Função que retorna a média e o desvio padrão do tempo das entregas por cidade e por tipo de pedido
    '''
    df_aux = df1.loc[:, ['City','Time_taken(min)','Type_of_order']].groupby(['City','Type_of_order']).agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['Time_taken_mean', 'Time_taken_std']
    df_aux = df_aux.reset_index()

    return df_aux

def avg_distance(df1, fig):
    '''
        Função que retorna a distância média por cidade
        Input -> Output
            df1 -> dataframe
            fig = False -> retorna a média das distâncias por cidade
            fig = True -> plota um gráfico de pizza com a média da distância por cidade
    '''
    df1['distance'] = ( df1.loc[ :, [ 'Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude'] ]
                        .apply( lambda x: haversine( ( x['Restaurant_latitude'], x['Restaurant_longitude'] ),
                                                    ( x['Delivery_location_latitude'], x['Delivery_location_longitude'] ) ),
                                                        axis=1 ) )
    df_aux = df1.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
    if fig == False:
        df_aux = np.round(df1['distance'].mean(), 2)
        return df_aux

    else:
        #plotar gráfico
        fig = go.Figure(data=[go.Pie(labels=df_aux['City'], values=df_aux['distance'], pull=[0, 0.1, 0])])
        return fig
    
def avg_std_time_city_traffic(df1):
    '''
        Função que:
            1. Retorna a média e desvio padrão do tempo de entrega por cidade e por tipo de tráfego
            2. Plota um gráfico de explosão solar
    '''
    df_aux = df1.loc[:, ['City','Time_taken(min)','Road_traffic_density']].groupby(['City','Road_traffic_density']).agg({'Time_taken(min)': ['mean','std']})
    df_aux.columns = ['Time_taken_mean', 'Time_taken_std']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='Time_taken_mean', 
                    color='Time_taken_std', color_continuous_scale= 'RdBu', 
                    color_continuous_midpoint=np.average(df_aux['Time_taken_std']))
    return fig

#---------------------------------- CODE LOGIC STRUTURE -----------------------------------

#========================================================
# IMPORT DATASET
#========================================================
df = pd.read_csv('dataset/train.csv')

#========================================================
# CLEAN DATA
#========================================================
df1 = clean_data( df )

#========================================================
# SET STREAMLIT PAGE WIDTH
#========================================================
st.set_page_config(page_title='Visão Restaurantes', page_icon='🍴', layout='wide')

#========================================================
# SIDEBAR LAYOUT
#========================================================
with st.sidebar:
    image = Image.open('img1.png')
    st.image(image)

    st.title('Cury Company')
    st.header('Fastest Delivery in Town')
    st.markdown('''---''')

    st.header('Selecione uma data limite')

    date_slider = st.slider(
        'Até qual valor?', 
        value=datetime(2022, 4, 13),
        min_value=datetime(2022, 2, 11),
        max_value=datetime(2022, 4, 6),
        format='DD/MM/YYYY'
    )

    traffic_options = st.multiselect(
        'Selecione o tipo de tráfico',
        ['Jam', 'High', 'Medium', 'Low'],
        default=['Jam', 'High', 'Medium', 'Low']
    )

    st.header('Powered by Oiluj')

    #filtro date
    linhas_select = df1['Order_Date'] <= date_slider
    df1 = df1.loc[linhas_select, :]

    #filtro traffic
    linhas_select = df1['Road_traffic_density'].isin(traffic_options)
    df1 = df1.loc[linhas_select, :]

#========================================================
# PAGE LAYOUT
#========================================================
st.title('Marketplace - Visão Restaurante')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '-', '-'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        with col1:
            df_aux = df1.loc[:, 'Delivery_person_ID'].nunique()
            st.metric(label = 'Entregadores únicos', value=df_aux)
        
        with col2:
            df_aux = avg_distance(df1, False)
            st.metric(label = 'Média da distância', value=df_aux)
        
        with col3:
            df_aux = std_mean_festival(df1, 'Yes', 'avg_time')
            st.metric(label = 'Tempo médio com festival', value=df_aux)
        
        with col4:
            df_aux = std_mean_festival(df1, 'Yes', 'std_time')
            st.metric(label = 'Desvio padrão com festival', value=df_aux)
        
        with col5:
            df_aux = std_mean_festival(df1, 'No', 'avg_time')
            st.metric(label = 'Tempo médio sem festival', value=df_aux)
        
        with col6:
            df_aux = std_mean_festival(df1, 'No', 'std_time')
            st.metric(label = 'Desvio padrão sem festival', value=df_aux)
    
    with st.container():
        st.markdown('''---''')
        st.title('Média e desvio padrão do tempo')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Entrega por cidade')
            fig = avg_delivery_city(df1)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('### Entrega por cidade e tipo de ordem')
            df_aux = time_by_city_by_order(df1)
            st.dataframe(df_aux, use_container_width=True)

    with st.container():
        st.markdown('''---''')
        st.title('Distribuição do tempo')
        col1, col2 = st.columns(2)
        with col1:
            st.markdown('### Por cidade')
            fig = avg_distance(df1, True)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown('### Por cidade e tipo de tráfego')
            fig = avg_std_time_city_traffic(df1)
            st.plotly_chart(fig, use_container_width=True)
        
        