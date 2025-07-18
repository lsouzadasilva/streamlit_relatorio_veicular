import streamlit as st
from streamlit_option_menu import option_menu
from paginas.mercado_total import mercado
from paginas.evolutivo import evolutivo
from paginas.regional import regiao
import pandas as pd


st.set_page_config(
    page_icon='🚗', 
    page_title='Relatório de emplacamento', 
    layout='wide'
)

dat_url = 'https://raw.githubusercontent.com/lsouzadasilva/datasets/main/data.xlsx'

@st.cache_data
def carregar_dados():
    df = pd.read_excel(dat_url)
    df['DATA_EMPLACAMENTO'] = pd.to_datetime(df['DATA_EMPLACAMENTO'])
    df = df.dropna()
    df['CONTADOR'] = 1
    df['ANO-MES'] = df['DATA_EMPLACAMENTO'].apply(lambda x: f"{x.year}-{x.month}")
    df['ANO'] = df['DATA_EMPLACAMENTO'].apply(lambda x: str(x.year))
    filt_seg = df['SEGMENTO'].isin(['AUTOMÓVEL', 'CAMINHONETE', 'CAMIONETA', 'UTILITÁRIO'])
    df = df[filt_seg]
    return df


df = carregar_dados()


hide_st_style = """
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            </style>
            """
st.markdown(hide_st_style, unsafe_allow_html=True)


st.sidebar.title("Navegação")
filtro, paginas = st.sidebar.tabs(['Filtros', 'Páginas'])


with paginas:
    paginas = option_menu(
        menu_title='Menu',
        options=['Veículos', 'Evolutivo', 'Regional'],
        icons=['speedometer2', 'bar-chart-fill', 'geo-alt-fill'],
        menu_icon='cast',
        default_index=0
    )


def filtro_tela(df):
    month = st.multiselect('*Selecione um período', df['ANO-MES'].unique())
    region = st.multiselect('*Região', df['REGIÃO'].unique())
    df_filtro = df[(df['ANO-MES'].isin(month) & df['REGIÃO'].isin(region))]  
    return df_filtro


with filtro:
    df_filtro = filtro_tela(df)

st.sidebar.divider()
st.sidebar.markdown("""
    **Desenvolvido por Leandro Souza**  
    [![LinkedIn](https://img.shields.io/badge/LinkedIn-0077B5?style=for-the-badge&logo=linkedin&logoColor=white)](https://www.linkedin.com/in//leandro-souza-dados/)
    [![GitHub](https://img.shields.io/badge/GitHub-100000?style=for-the-badge&logo=github&logoColor=white)](https://github.com/lsouzadasilva/streamlit_relatorio_veicular)
""")


if paginas == 'Veículos':
    mercado(df_filtro)
elif paginas == 'Evolutivo':
    evolutivo(df_filtro)
elif paginas == 'Regional':
    regiao(df_filtro)
    

