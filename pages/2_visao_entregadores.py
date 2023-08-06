                    #VISAO: ENTREGADORES

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

def top_deliver(df1, top_asc):
    '''
        Função que retorna os 10 entregadores mais rápidos ou mais lentos por tipo de cidade
        Input -> Output
            df1 -> dataframe
            top_asc = True -> retorna os 10 entregadores mais rápidos
            top_asc = False -> retorna os 10 entregadores mais lentos
    '''
    # retornar os entregadores mais rápidos por cidade
    df_aux = (df1.loc[:, ['Delivery_person_ID','Time_taken(min)','City']]
                .groupby(['City','Delivery_person_ID'])
                .min()
                .sort_values(['City','Time_taken(min)'], ascending = top_asc)
                .reset_index())

    # retornar 3 dataframes com os 10 por tipo de cidade
    df_aux01 = df_aux.loc[df_aux['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_aux.loc[df_aux['City'] == 'Semi-Urban', :].head(10)
    df_aux03 = df_aux.loc[df_aux['City'] == 'Urban', :].head(10)

    # unir os 3 dataframes criados
    df2 = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index(drop=True)

    return df2

def avg_deliver_rating(df1):
    '''
        Função que retorna a média das avaliações por entregador
    '''
    df2 = (df1.loc[:, ['Delivery_person_Ratings', 'Delivery_person_ID']]
                            .groupby('Delivery_person_ID')
                            .mean()
                            .reset_index())

    return df2

def avg_std_traffic_ratings( df1 ):
    '''
        Função que retorna a média e o desvio padrão das avaliações dos entregadores por tipo de tráfego
    '''
    # média e desvio padrão agregados
    df2 = (df1.loc[:, ['Delivery_person_Ratings','Road_traffic_density']]
                        .groupby('Road_traffic_density')
                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))
    
    # renomear colunas agregadas
    df2.columns = ['delivery_mean','delivery_std']
    
    # resetar index
    df2.reset_index()

    return df2

def avg_std_climate_ratings( df1 ):
    '''
        Função que retorna a média e o desvio padrão das avaliações dos entregadores por condição climática
    '''
    # média e desvio padrão agregados
    df2 = (df1.loc[:, ['Delivery_person_Ratings','Weatherconditions']]
                        .groupby('Weatherconditions')
                        .agg({'Delivery_person_Ratings': ['mean', 'std']}))

    # renomear colunas agregadas
    df2.columns = ['Weatherconditions_mean','Weatherconditions_std']

    # resetar index
    df2.reset_index()

    return df2
#---------------------------------- CODE LOGIC STRUTURE -----------------------------------

#========================================================
# IMPORT DATASET
#========================================================
df = pd.read_csv('dataset/train.csv')

#========================================================
# CLEAN DATA
#========================================================
df1 = clean_data(df)

#========================================================
# SET STREAMLIT PAGE WIDTH
#========================================================
st.set_page_config(page_title='Visão Entregadores', page_icon='🛵', layout="wide")

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
st.title('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs( ['Visão Gerencial', '-', '-'] )

with tab1:
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4)
       
        with col1:
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
        
        with col2:
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
        
        with col3:
            melhor_veiculo = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição veículo', melhor_veiculo)

        with col4:
            pior_veiculo = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição veículo', pior_veiculo)
    
    st.markdown('''---''')

    with st.container():
        st.title('Avaliações Médias')

        col1, col2, col3 = st.columns(3)

        with col1:
            st.markdown('##### Avaliação média por entregador')
            df2 = avg_deliver_rating( df1 )
            st.dataframe(df2)
        
        with col2:
            st.markdown('##### Avaliação média por traffic')
            df2 = avg_std_traffic_ratings( df1 )
            st.dataframe(df2)

        with col3:
            st.markdown('##### Avaliação média por climate')
            df2 = avg_std_climate_ratings(df1)
            st.dataframe(df2)
    
    st.markdown('''---''')

    with st.container():
        st.title('Top 10 entregadores')

        col1, col2 = st.columns(2)

        with col1:
            st.markdown('##### Top 10 entregadores mais rápidos por cidade')
            df2 = top_deliver( df1, top_asc=True )
            st.dataframe(df2)

        with col2:
            st.markdown('##### Top 10 entregadores mais lentos por cidade')
            df2 = top_deliver(df1, top_asc=False)
            st.dataframe(df2)