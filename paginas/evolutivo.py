import streamlit as st
import plotly.express as px
import pandas as pd

def evolutivo(df_filtro):

    st.header('Evolutivo', divider=True)

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


    def total_regiao():
        regiao = df_filtro.groupby('REGIÃO')['CONTADOR'].count().reset_index(name='COUNT')
        return regiao
    
    regiao = total_regiao()

    def participacao_uf():
        uf = df_filtro.groupby(['FABRICANTE','UF'])['CONTADOR'].count().reset_index(name='COUNT')
        return uf
    
    uf = participacao_uf()

    def segmento_mes():
        seg_mes = df_filtro.groupby(['SEGMENTO', 'ANO-MES'])['CONTADOR'].count().reset_index(name='COUNT')
        return seg_mes
    
    seg_mes = segmento_mes()


    def fabricante_mes():
        fabri_mes = df_filtro.groupby(['FABRICANTE', 'ANO-MES'])['CONTADOR'].count().reset_index(name='COUNT')
        return fabri_mes
    
    fabri_mes = fabricante_mes()
    
    dat_url = 'https://raw.githubusercontent.com/lsouzadasilva/datasets/main/data.xlsx'

    @st.cache_data
    def segmento_completo():
        df_completo_seg = pd.read_excel(dat_url)
        df_completo_seg['CONTADOR'] = 1    
        df_completo_seg['DATA_EMPLACAMENTO'] = pd.to_datetime(df_completo_seg['DATA_EMPLACAMENTO'])
        df_completo_seg['ANO-MES'] = df_completo_seg['DATA_EMPLACAMENTO'].apply(lambda x: f"{x.year}-{x.month}")
        df_completo_seg = df_completo_seg.sort_values('ANO-MES', ascending=True)
        filt_seg = df_completo_seg['SEGMENTO'].isin(['AUTOMÓVEL', 'CAMINHONETE', 'CAMIONETA', 'UTILITÁRIO'])
        df_completo_seg = df_completo_seg[filt_seg]
        return df_completo_seg
    
    df_completo_seg = segmento_completo()

    perido_regiao = st.toggle('Região e Segmento')

    visulizar_perido_região = perido_regiao


    col1, col2  = st.columns(2)

    color_regiao_evolutivo = {
        'SUDESTE': '#04BFAD',
        'SUL': '#313E40',
        'CENTRO-OESTE': '#F25C5C',
        'NORDESTE': '#F2BB13',
        'NORTE': 'royalblue'
    }
    

    if not visulizar_perido_região:
        with col1:
            fig1 = px.pie(regiao, names='REGIÃO', values='COUNT', hole = 0.5, color='REGIÃO', color_discrete_map=color_regiao_evolutivo, title='FATIA POR REGIÃO')
            col1.plotly_chart(fig1, use_container_width=True)

        with col2:
            uf = uf.sort_values('COUNT', ascending=False)
            total_por_uf = uf.groupby('FABRICANTE')['COUNT'].sum()
            uf = uf.loc[uf['FABRICANTE'].isin(uf['FABRICANTE'].head(20))]
            uf['TOTAL_UF'] = uf['FABRICANTE'].map(total_por_uf)
            uf['PERCENTUAL'] = (uf['COUNT'] / uf['TOTAL_UF']) * 100
            registro = uf.pivot(index='FABRICANTE', columns='UF', values='PERCENTUAL')
            if registro.isnull().all().all():
                st.write('')
            else:
                registro = registro.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else '')
                st.write("##### PARTICIPAÇÃO POR REGIÃO")
                st.write(registro)



    else:
        with col1:
            fig4 = px.pie(seg_mes, names='SEGMENTO', values='COUNT', hole=0.5, color='SEGMENTO', title='FATIA POR SEGMENTO')
            col1.plotly_chart(fig4, use_container_width=True)

        with col2:
            fabri_mes = fabri_mes.sort_values('COUNT', ascending=False)
            total_por_mes = fabri_mes.groupby('FABRICANTE')['COUNT'].sum()
            fabri_mes = fabri_mes.loc[fabri_mes['FABRICANTE'].isin(fabri_mes['FABRICANTE'].head(20))]
            fabri_mes['TOTAL_MENSAL'] = fabri_mes['FABRICANTE'].map(total_por_mes)
            fabri_mes['PERCENTUAL'] = (fabri_mes['COUNT'] / fabri_mes['TOTAL_MENSAL']) * 100
            registro = fabri_mes.pivot(index='FABRICANTE', columns='ANO-MES', values='PERCENTUAL')
            if registro.isnull().all().all():
                st.write('')
            else:
                registro = registro.applymap(lambda x: f'{x:.2f}%' if pd.notnull(x) else '')
                st.write("#### PARTICIPAÇÃO POR PERÍODO")
                st.write(registro)




    st.divider()

    segmeto_top_marcas = st.toggle('Esolha evolutivo por marca ou Segmento')

    visualizar_marcas_segmento = segmeto_top_marcas
    

    col3, = st.columns(1)
    if not visualizar_marcas_segmento:
        with col3:
            df_completo_seg['ANO-MES'] = pd.to_datetime(df_completo_seg['ANO-MES'], format='%Y-%m')
            total_5 = df_completo_seg.groupby(['SEGMENTO', 'ANO-MES'])['CONTADOR'].count().reset_index(name='COUNT')
            total_5 = total_5.sort_values('ANO-MES')
            fig2 = px.line(total_5, x='ANO-MES', y='COUNT', markers=True, color='SEGMENTO', title='EVOLUÇÃO MENSAL POR SEGMENTO')

            fig2.update_traces(line=dict(width=2), marker=dict(size=8, opacity=0.8))
            fig2.update_layout(
                xaxis_title='Ano-Mês',
                yaxis_title='Quantidade',
                legend_title='Segmento',
                font=dict(color='white'),
                hovermode='x unified'
            )

            fig2.for_each_trace(lambda t: t.update(text=t.y, textposition='top right'))

            col3.plotly_chart(fig2, use_container_width=True)
    else:
        with col3:
            df_completo_seg['ANO-MES'] = pd.to_datetime(df_completo_seg['ANO-MES'], format='%Y-%m')
            total_6 = df_completo_seg.groupby(['FABRICANTE', 'ANO-MES'])['CONTADOR'].count().reset_index(name='COUNT')
            total_6 = total_6.sort_values('ANO-MES')
            total_6 = total_6.loc[total_6['FABRICANTE'].isin(total_6['FABRICANTE'].head(5))]
            fig3 = px.line(total_6, x='ANO-MES', y='COUNT', markers=True, color='FABRICANTE', title='EVOLUTIVO PARTICIPAÇÃO TOP 5')

            fig3.update_traces(line=dict(width=2), marker=dict(size=8, opacity=0.8))
            fig3.update_layout(
            xaxis_title='Ano-Mês',
            yaxis_title='Quantidade',
            legend_title='Top Marcas',
            font=dict(color='white'),
            hovermode='x unified'
            )

            fig3.for_each_trace(lambda t: t.update(text=t.y, textposition='top right'))

            col3.plotly_chart(fig3, use_container_width=True)




