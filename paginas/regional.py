import plotly.express as px
import streamlit as st
import requests
import pandas as pd


def regiao(df_filtro):
    
    st.header('Regional', divider=True)
    
    def totl_veiculo_evolutio():
        veiculo = df_filtro.groupby('ANO-MES')['CONTADOR'].count().reset_index(name='COUNT')
        veiculo = veiculo.sort_values('ANO-MES', ascending=False).reset_index(drop=True)
        veiculo['change'] = veiculo['COUNT'].pct_change(periods=-1) * 100
        return veiculo

    veiculo = totl_veiculo_evolutio()

    card1, = st.columns(1)

    with card1:
        st.metric(
            label='VEÍCULOS',
            value=f"{veiculo.loc[0, 'COUNT']:,.0f}" if not veiculo.empty else "0",
            delta=f"{veiculo.loc[0, 'change']:.2f}% vs. Mês anterior" if len(veiculo) > 1 else "Escolha dois mêses para comparar"
        )
    
    sigla_para_nome = {
        'AC': 'Acre', 'AL': 'Alagoas', 'AP': 'Amapá', 'AM': 'Amazonas', 'BA': 'Bahia', 
        'CE': 'Ceará', 'DF': 'Distrito Federal', 'ES': 'Espírito Santo', 'GO': 'Goiás', 
        'MA': 'Maranhão', 'MT': 'Mato Grosso', 'MS': 'Mato Grosso do Sul', 'MG': 'Minas Gerais', 
        'PA': 'Pará', 'PB': 'Paraíba', 'PR': 'Paraná', 'PE': 'Pernambuco', 'PI': 'Piauí', 
        'RJ': 'Rio de Janeiro', 'RN': 'Rio Grande do Norte', 'RS': 'Rio Grande do Sul', 
        'RO': 'Rondônia', 'RR': 'Roraima', 'SC': 'Santa Catarina', 'SP': 'São Paulo', 
        'SE': 'Sergipe', 'TO': 'Tocantins'
    }
    
    def mercado_regiao():
        regiao = df_filtro.groupby(['REGIÃO','ANO-MES','UF'])['CONTADOR'].count().reset_index(name='COUNT')
        regiao = regiao.sort_values('COUNT', ascending=False)
        regiao['UF_NAME'] = regiao['UF'].map(sigla_para_nome)
        return regiao
    
    regiao = mercado_regiao()
    
    
    
    def carregar_dados_completos():
        geojson_url = "https://raw.githubusercontent.com/lsouzadasilva/datasets/main/brazil-states.geojson"
        geojson = requests.get(geojson_url).json()
        return geojson
    
    geojson = carregar_dados_completos()
    
    def municipio_total():
        municipio = df_filtro.groupby('MUNICIPIO')['CONTADOR'].count().reset_index(name='COUNT')
        municipio = municipio.sort_values('COUNT', ascending=False).head(20)
        return municipio
    
    municipio = municipio_total()
    
    def combustivel():
        combustiveis = df_filtro.groupby('COMBUSTIVEL')['CONTADOR'].count().reset_index(name='COUNT')
        combustiveis = combustiveis.sort_values('COUNT', ascending=False)
        return combustiveis
    
    combustiveis = combustivel()
    
    def segmento_regiao():
        seg_re = df_filtro.groupby(['SEGMENTO', 'UF'])['CONTADOR'].count().reset_index(name='COUNT')
        seg_re = seg_re.sort_values('COUNT', ascending=False)
        return seg_re
    
    seg_re = segmento_regiao()


    col1,col4 = st.columns(2)

    with col1:
        fig = px.choropleth(
            regiao,
            geojson=geojson,
            locations='UF_NAME',  
            featureidkey='properties.name', 
            color='COUNT',
            hover_name='UF',
            color_continuous_scale='Blues',
            title='MAPA DE CALOR REGIÃO',
            scope='south america'
        )

        fig.update_geos(
            fitbounds="locations",
            visible=False,
            projection_type="mercator",  
            center={"lat": -14.2350, "lon": -51.9253}, 
            projection_scale=5,
            lakecolor="rgba(255, 255, 255, 0)",
            bgcolor="rgba(0,0,0,0)",
            )


        fig.update_layout(
            mapbox_style="carto-positron",  
            mapbox_zoom=3, 
            mapbox_center={"lat": -14.2350, "lon": -51.9253}, 
            margin={"r":0,"t":20,"l":0,"b":0},  
            paper_bgcolor="rgba(0,0,0,0)",  
            plot_bgcolor="rgba(0,0,0,0)",
            coloraxis_colorbar_title='Mercado'
            )

        col1.plotly_chart(fig, use_container_width=True)
        
        
    with col4:
            seg_re = seg_re.sort_values('COUNT', ascending=False) # ordenando de forma decrescente
            total_por_seg_re = seg_re.groupby('UF')['COUNT'].sum()# soma precisa ser feita na coluna que sera usada pivot.index
            seg_re = seg_re.loc[seg_re['UF'].isin(seg_re['UF'].head(20))] # top 20
            seg_re['TOTAL_SEG_RE'] = seg_re['UF'].map(total_por_seg_re) # Atribui total por UF.
            seg_re['PERCENTUAL'] = (seg_re['COUNT'] / seg_re['TOTAL_SEG_RE']) * 100 # Calcula percentual por registro.
            registro = seg_re.pivot(index='UF', columns='SEGMENTO', values='PERCENTUAL') # Cria a tabela 
            if registro.isnull().all().all():  # Tratamento pra valores nulos
                st.write('')
            else:
                registro = registro.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else '')
                st.write("##### PARTICIPAÇÃO POR SEGMENTO") # Titulo da tabela
                st.write(registro) # printa a tabela 
        
        
    st.divider()
    
    col2, col3 = st.columns(2)
    
        
    with col2:
        fig3 = px.pie(combustiveis, names='COMBUSTIVEL', values='COUNT', hole=0.5, title='DISTRIBUIÇÃO COMBUSTIVEL')
        col2.plotly_chart(fig3, use_container_width=True)
        
        
    with col3:
        municipio = municipio.sort_values('COUNT', ascending=True)
        fig2 = px.bar(municipio, x='COUNT', y='MUNICIPIO', text_auto=True, title='DISTIBUIÇÃO REGIONAL', orientation='h')
        fig2.update_traces(marker_color='cyan', textfont_size=9, textangle=0, textposition="outside", cliponaxis=False)
        col3.plotly_chart(fig2, use_container_width=True)
        
    
