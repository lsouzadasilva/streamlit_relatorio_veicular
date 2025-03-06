import streamlit as st
import pandas as pd
import plotly.express as px


def mercado(df_filtro): 

    st.header('Estudo de mercado de veiculos elétricos 2023 ⚡', divider=True)

    color_regiao = {
        'SUDESTE': '#04BFAD',
        'SUL': '#313E40',
        'CENTRO-OESTE': '#F25C5C',
        'NORDESTE': '#F2BB13',
        'NORTE': 'royalblue'
    }

    dat_url = 'https://raw.githubusercontent.com/lsouzadasilva/datasets/main/data.xlsx'
    
    @st.cache_data
    def carregar_dados_completos():
        df = pd.read_excel(dat_url)
        df['DATA_EMPLACAMENTO'] = pd.to_datetime(df['DATA_EMPLACAMENTO'])
        df = df.dropna()
        df['CONTADOR'] = 1
        df['ANO-MES'] = df['DATA_EMPLACAMENTO'].apply(lambda x: f"{x.year}-{x.month}")
        df['ANO'] = df['DATA_EMPLACAMENTO'].apply(lambda x: str(x.year))
        filt_seg = df['SEGMENTO'].isin(['AUTOMÓVEL', 'CAMINHONETE', 'CAMIONETA', 'UTILITÁRIO'])
        df = df[filt_seg]
        return df   

    df_completo = carregar_dados_completos()


    def total_veiculo():
        veiculo = df_filtro.groupby('ANO-MES')['CONTADOR'].count().reset_index(name='COUNT')
        veiculo = veiculo.sort_values('ANO-MES', ascending=False).reset_index(drop=True)
        veiculo['change'] = veiculo['COUNT'].pct_change(periods=-1) * 100
        return veiculo

    veiculo = total_veiculo()


    def total_regiao():
        total = df_filtro.groupby('REGIÃO')['CONTADOR'].count().reset_index(name='COUNT')
        total['PERCENT'] = (total['COUNT'] / total['COUNT'].sum() * 100).map('{:.2f}%'.format)
        total['COUNT_FORMAT'] = total['COUNT'].apply(lambda x: f'{x:,.0f}'.replace(',', '.'))
        total['LABEL'] = total['COUNT_FORMAT'].astype(str) + '<br>' + total['PERCENT']
        return total

    total = total_regiao()

    def total_municipio():
        total_1 = df_filtro.groupby('MUNICIPIO')['CONTADOR'].count().reset_index(name='COUNT')
        total_1 = total_1.sort_values('COUNT', ascending=False).head(15)
        return total_1

    total_1 = total_municipio()

    def total_segmento():
        total_2 = df_filtro.groupby('SEGMENTO')['CONTADOR'].count().reset_index(name='COUNT')
        total_2 = total_2.sort_values('COUNT', ascending=False)
        return total_2

    total_2 = total_segmento()

    def fab_seg():
        total_3 = df_filtro.groupby(['FABRICANTE', 'SEGMENTO'])['CONTADOR'].count().reset_index(name='MERCADO')
        total_3 = total_3.sort_values('MERCADO', ascending=False)
        return total_3

    total_3 = fab_seg()


    card1, = st.columns(1)

    with card1:
        st.metric(
            label='VEÍCULOS',
            value=f"{veiculo.loc[0, 'COUNT']:,.0f}" if not veiculo.empty else "0",
            delta=f"{veiculo.loc[0, 'change']:.2f}% vs. Mês anterior" if len(veiculo) > 1 else "Escolha dois mêses para comparar"
        )

    col1, col2, col3 = st.columns(3)

    with col1:
        fig = px.treemap(total, path=['REGIÃO'], values='COUNT', title='VEÍCULOS POR REGIÃO',
                        color='REGIÃO', color_discrete_map=color_regiao)
        fig.update_traces(textinfo='label+text', text=total['LABEL'])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        total_1 = total_1.sort_values('COUNT', ascending=True)
        fig2 = px.bar(total_1, x='COUNT', y='MUNICIPIO', text_auto=True, orientation='h', title='DISTRIBUIÇÃO MUNICIPAL TOP 15')
        fig2.update_traces(marker_color='cyan', textfont_size=9, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig2, use_container_width=True)

    with col3:
        total_2 = total_2.sort_values('COUNT', ascending=True)
        fig3 = px.bar(total_2, x='COUNT', y='SEGMENTO', text_auto=True, orientation='h', title='DISTRIBUIÇÃO SEGMENTO')
        fig3.update_traces(marker_color='cyan', textfont_size=9, textangle=0, textposition="outside", cliponaxis=False)
        st.plotly_chart(fig3, use_container_width=True)

    st.divider()

    col4, col5 = st.columns(2)

    max_emplacamento = total_3['MERCADO'].max() if not total_3.empty else 0

    with col4:
        st.dataframe(
            total_3,
            column_config={
                'MERCADO': st.column_config.ProgressColumn(
                    'MERCADO', format="%.0f", min_value=0, max_value=int(max_emplacamento)
                )
            },
            use_container_width=True,
            hide_index=True
        )

    with col5:
        st.container()
        total_4 = df_completo.groupby('ANO-MES')['CONTADOR'].count().reset_index(name='COUNT')
        total_4 = total_4.sort_values('ANO-MES', ascending=False)
        total_4['delta'] = total_4['COUNT'].pct_change(periods=-1) * 100

        fig4 = px.bar(total_4, x='ANO-MES', y='COUNT', title='EVOLUTIVO DE MERCADO (Completo)')

        def format_delta_text(row):
            count_text = f"{row['COUNT']:,.0f}"
            if pd.notna(row['delta']):
                if row['delta'] > 0:
                    delta_text = f"+{row['delta']:.2f}% ↑"
                elif row['delta'] < 0:
                    delta_text = f"{row['delta']:.2f}% ↓"
                else:
                    delta_text = "0.00%"
            else:
                delta_text = ""
            return count_text, delta_text

        total_4['count_text'], total_4['delta_text'] = zip(*total_4.apply(format_delta_text, axis=1))


        fig4.update_traces(
            text=total_4['count_text'],
            textposition='inside',
            insidetextanchor='middle',
            marker_color='cyan',
            textfont_size=12
        )


        for i, row in total_4.iterrows():
            fig4.add_annotation(
                x=row['ANO-MES'],
                y=row['COUNT'],
                text=row['delta_text'],
                showarrow=False,
                yshift=10,
                font=dict(color='green' if row['delta'] > 0 else 'red', size=10)
            )

        st.plotly_chart(fig4, use_container_width=True)




