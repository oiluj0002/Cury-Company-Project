import streamlit as st
from PIL import Image

st.set_page_config(
    page_title = 'Home',
    page_icon = '🏠'
)

with st.sidebar:
    image = Image.open('img1.png')
    st.image(image, width= 120)

    st.title('Cury Company')
    st.header('Fastest Delivery in Town')
    st.markdown('''---''')

    st.header('Powered by Oiluj')

st.write('# Cury Company Growth Dashboard')

st.markdown(
    """
        Growth Dashboard foi construído para acompanhar as métricas de crescimento dos Entregadores e Restaurantes.
        ### Como utilizar esse Growth Dashboard?
        - Visão Empresa:
            - Visão Gerencial: Métricas gerais de comportamento.
            - Visão Tática: Indicadores semanais de crescimento.
            - Visão Geográfica: Insights de geolocalização.
        - Visão Entregador:
            - Acompanhamento dos indicadores semanais de crescimento
        - Visão Restaurantes:
            - Indicadores semanais de crescimento dos restaurantes
        ### Ask for Help
        - Júlio Gabriel
            - Email: juliogabriel.pe@gmail.com
            - Discord: @oiluj0002
    """
)
