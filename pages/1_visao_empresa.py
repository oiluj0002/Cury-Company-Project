                    #VISAO: EMPRESA

#========================================================
# IMPORT LIBRARIES
#========================================================
import pandas as pd
import plotly.express as px
import folium
import streamlit as st
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

def order_metric(df1):
    ''' Função que:
            1. Retorna o número de entregas por data
            2. Plota um gráfico de barras
    '''
    #selecionar linhas
    df_aux = df1.loc[:, ['ID', 'Order_Date']].groupby(['Order_Date']).count().reset_index()

    #desenhar o gráfico de barras
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

def traffic_order_share(df1):
    ''' Função que:
            1. Retorna o número de entregas por tipo de tráfego
            2. Plota um gráfico de pizza
    '''    
    #selecionar linhas
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density']].groupby(['Road_traffic_density']).count().reset_index()

    #desenhar o gráfico de pizza
    fig = px.pie(df_aux, values='ID', names='Road_traffic_density')

    return fig

def traffic_city_distribution(df1):
    ''' Função que:
            1. Retorna o número de entregas por tipo de tráfego e cidade
            2. Plota um gráfico de distribuição
    '''
    #selecionar linhas
    df_aux = df1.loc[:, ['ID', 'Road_traffic_density', 'City']].groupby(['Road_traffic_density', 'City']).count().reset_index()

    #desenhar o gráfico de bolha
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City' )

    return fig

def order_by_week(df1):
    ''' Função que:
            1. Retorna o número de entregas por semana
            2. Plota um gráfico de linhas
    '''    
    #criar coluna semana
    df1['week_of_year'] = df1['Order_Date'].dt.strftime('%U')

    #selecionar linhas
    df_aux = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()

    #desenhar o gráfico de linha
    fig = px.line(df_aux, x='week_of_year', y= 'ID')

    return fig

def order_by_week_by_deliver(df1):
    ''' Função que:
            1. Retorna o número de entregas por cada entregador a cada semana
            2. Plota um gráfico de linhas
    '''   
    #selecionar linhas
    df_aux01 = df1.loc[:, ['ID', 'week_of_year']].groupby('week_of_year').count().reset_index()
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'week_of_year']].groupby('week_of_year').nunique().reset_index()

    #unir os 2 dataframes recém criados
    df_aux = pd.merge(df_aux01, df_aux02, how='inner')

    #criar coluna de proporção pedidos por entregador
    df_aux['order_by_deliver'] = df_aux['ID'] / df_aux['Delivery_person_ID']

    #desenhar o gráfico de linha
    fig = px.line(df_aux, x='week_of_year', y= 'order_by_deliver')

    return fig

def country_map(df1):
    ''' Função que:
            1. Retorna os pontos geográficos medianos das entregas por tipo de cidade e tipo de tráfego
            2. Plota um mapa mostrando os pontos
    '''       
    #selecionar linhas
    df_aux = df1.loc[:, ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']].groupby(['City', 'Road_traffic_density']).median().reset_index()

    #desenhar mapa
    map = folium.Map()
    for index, location_info in df_aux.iterrows():
        folium.Marker([location_info['Delivery_location_latitude'], 
                    location_info['Delivery_location_longitude']],
                    popup=location_info[['City', 'Road_traffic_density']]).add_to(map)
    
    folium_static(map, width=1024, height=600)

    return None
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
st.set_page_config(page_title='Visão Empresa', page_icon='💼', layout="wide")

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

    #Slider para data
    date_slider = st.slider(
        'Até qual valor?', 
        value=datetime(2022, 4, 13),
        min_value=datetime(2022, 2, 11),
        max_value=datetime(2022, 4, 6),
        format='DD/MM/YYYY'
    )

    #selecionar tipo de tráfico
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
st.title('Marketplace - Visão Cliente')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

with tab1:
    with st.container():
        st.title('Orders by Day')
        fig = order_metric(df1)
        st.plotly_chart(fig, use_container_width=True)
    
    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.header('Traffic Order Share')
            fig = traffic_order_share(df1)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.header('Traffic City Distribution')
            fig = traffic_city_distribution(df1)
            st.plotly_chart(fig, use_container_width=True)

with tab2:
    st.title('Orders by Week')
    fig = order_by_week(df1)
    st.plotly_chart(fig, use_container_width=True)
    
    st.title('Orders by Deliver by Week')
    fig = order_by_week_by_deliver(df1)
    st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.title('Country Map')
    fig = country_map(df1)
