# Bibliotecas
import re
from haversine import haversine
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

st. set_page_config(page_title = 'Visão Entregadores', page_icon='🦲', layout='wide')
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
# Funções
# -----------------------------------------------------------------------------------------------------------------------------------------------------------------------
def clean_code(df):
    """ Esta função tem a responsabilidade de limpar o dataframe
        1. Remoção dos dados NaN
        2. Mudança do tipo de coluna de dados
        3. Remoção dos espaços das variáveis de texto
        4. Formatação de coluna de datas
        5. Limpeza da coluna de tempo (remoção do texto da variável numérica)
        
        Input: Dataframe
        Output: Dataframe
    """
    # Convertendo colunas e retirando valores NaN
    linhas_selecionadas = (df['Delivery_person_Age'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Road_traffic_density'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['City'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    linhas_selecionadas = (df['Festival'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()

    df['Delivery_person_Age'] = df['Delivery_person_Age'].astype( int )

    # Convertendo a coluna ratings de texto para numero decimal (float)
    df['Delivery_person_Ratings'] = df['Delivery_person_Ratings'].astype( float )

    # Convertendo a coluna order date de texto para data
    df['Order_Date'] = pd.to_datetime(df['Order_Date'], format='%d-%m-%Y')

    # Convertendo multiple_deliveries de textopara numero inteiro (int)
    linhas_selecionadas = (df['multiple_deliveries'] != 'NaN ')
    df = df.loc[linhas_selecionadas, :].copy()
    df['multiple_deliveries'] = df['multiple_deliveries'].astype( int )

    # Removendo os espaços dentro de string/texto/objeto
    df.loc[:, 'ID'] = df.loc[:, 'ID'].str.strip()
    df.loc[:, 'Road_traffic_density'] = df.loc[:, 'Road_traffic_density'].str.strip()
    df.loc[:, 'Type_of_order'] = df.loc[:, 'Type_of_order'].str.strip()
    df.loc[:, 'Type_of_vehicle'] = df.loc[:, 'Type_of_vehicle'].str.strip()
    df.loc[:, 'City'] = df.loc[:, 'City'].str.strip()
    df.loc[:, 'Festival'] = df.loc[:, 'Festival'].str.strip()

    # Limpando a Coluna de time taken
    df['Time_taken(min)'] = df['Time_taken(min)'].apply( lambda x: x.split( '(min)' )[1])
    df['Time_taken(min)'] = df['Time_taken(min)'].astype( int )
    
    return df
# Retornar melhores entregadores por cidade
def top_delivers(df, top_asc):
    df_slowest_delivery_city = (df.loc[:, ['Delivery_person_ID', 'City', 'Time_taken(min)']]
                                .groupby(['City', 'Delivery_person_ID'])
                                .mean()
                                .sort_values(['City', 'Time_taken(min)'], ascending=top_asc).reset_index())

    df_aux01 = df_slowest_delivery_city.loc[df_slowest_delivery_city['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df_slowest_delivery_city.loc[df_slowest_delivery_city['City'] == 'Urban', :].head(10)
    df_aux03 = df_slowest_delivery_city.loc[df_slowest_delivery_city['City'] == 'Semi-Urban', :].head(10)

    df_new = pd.concat([df_aux01, df_aux02, df_aux03]).reset_index()

    return df_new
# Dataset
df_root = pd.read_csv('dataset/train.csv')

# Fazendo cópia do dataframe lido
df = df_root.copy()

# Limpandando Dataset
df = clean_code(df)

#====================================================
# Barra Lateral
#====================================================

image = Image.open('eu.png')

st.sidebar.image(image, width = 120)
st.sidebar.markdown('# Curry Company')
st.sidebar.markdown('# Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

date_slider = st.sidebar.slider('Até qual valor?', value=pd.datetime(2022, 4 , 13),
                 min_value=pd.datetime(2022, 2 , 11),
                 max_value=pd.datetime(2022, 4, 6),
                 format='DD-MM-YYYY')

st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect('Quais as condições de trânsito?',
                      ['Low', 'Medium', 'High', 'Jam'],
                      default = ['Low', 'Medium', 'High', 'Jam'])
st.sidebar.markdown("""---""")
st.sidebar.markdown('Powerd by Comunidade DS')

# Filtro de Data
linhas_selecionadas = df['Order_Date'] < date_slider
df = df.loc[linhas_selecionadas, :]

# Filtro de transito
linhas_selecionadas = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas, :]

#====================================================
# Layout no Streamlit
#====================================================
st.header('Marketplace - Visão Entregadores')

tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '_', '_'])

with tab1:
    with st.container():
        st.title('Overall Metrics')
        
        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1:
            # A maior idade dos entregadores
            maior_idade = df['Delivery_person_Age'].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2:
            # A menor idade dos entregadores
            menor_idade = df['Delivery_person_Age'].min()
            col2.metric('Menor idade', menor_idade)
            
        with col3:
            # A melhor condição de veículos
            melhor_condicao = df['Vehicle_condition'].max()
            col3.metric('Melhor condição de veículos', melhor_condicao)
            
        with col4:
            # A pior condição de veículos
            pior_condicao = df['Vehicle_condition'].min()
            col4.metric('Pior condição de veículos', pior_condicao)
        
    with st.container():
        st.markdown("""---""")
        st.title('Avaliações')
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Avaliação média por entregador')
            df_average_ratings_by_deliveries = (df.loc[:, ['Delivery_person_ID', 'Delivery_person_Ratings']]
                                                .groupby(['Delivery_person_ID'])
                                                .mean()
                                                .reset_index())
            st.dataframe(df_average_ratings_by_deliveries)
            
        with col2:
            st.markdown('##### Avaliação média por trânsito')
            df_avg_std_rating_by_traffic = (df.loc[:, ['Delivery_person_Ratings', 'Road_traffic_density']]
                                            .groupby(['Road_traffic_density'])
                                            .agg({'Delivery_person_Ratings': ['mean', 'std']}))

            # Mudando nomes das colunas
            df_avg_std_rating_by_traffic.columns = ['delivery_mean', 'delivery_std']

            # Resetando o index
            df_avg_std_rating_by_traffic = df_avg_std_rating_by_traffic.reset_index()
            st.dataframe(df_avg_std_rating_by_traffic)
            
            st.markdown('##### Avaliação média por clima')
            df_avg_std_rating_by_weather = (df.loc[:, ['Delivery_person_Ratings', 'Weatherconditions']]
                                            .groupby(['Weatherconditions'])
                                            .agg({'Delivery_person_Ratings' : ['mean', 'std']}))

            # Mudando os nomes das colunas
            df_avg_std_rating_by_weather.columns = ['weather_mean', 'weather_std']

            # Resetando index
            df_avg_std_rating_by_weather = df_avg_std_rating_by_weather.reset_index()
            st.dataframe(df_avg_std_rating_by_weather)
            
    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de Entrega')
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('##### Top entregadores mais rápidos')
            df_aux = top_delivers(df, True)
            st.dataframe(df_aux)
                                  
        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df_aux = top_delivers(df, False)
            st.dataframe(df_aux)
            