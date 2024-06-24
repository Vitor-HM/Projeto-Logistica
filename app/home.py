import re

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

# Configuração da pagina
st.set_page_config(
    page_title='Dashboard Logistica',
    page_icon='🧊',
    layout='wide',
    initial_sidebar_state='collapsed',
)

st.title('Analise De Logistica')

# Carregando dataframe
df = pd.read_excel('data/dataset.xlsx')

total_entregas = df.value_counts().sum()

#########################Calculos#########################
# Aplica o filtro de entregas no prazo
entregas_no_prazo = df[df['Status_Entrega'] == 'No Prazo']

# Agrupa o total de entregas no prazo por Canal_Entrega
entregas_agrupadas = entregas_no_prazo.groupby('Canal_Entrega')

# Contando o total de entregas em cada grupo
entregas_por_canal = entregas_agrupadas['Status_Entrega'].value_counts()

# Transforma a série em um DataFrame e reseta o índice
df_entregas_por_canal = entregas_por_canal.reset_index(
    name='Total_Entregas_No_Prazo'
)

# ---------------------------------------------------------------------------------------#

entregas_no_antecipadas = df[df['Status_Entrega'] == 'Antecipado']

percentual_entrega_antecipadas = round(
    entregas_no_antecipadas.shape[0] / total_entregas * 100, 2
)

entrega_por_distribuidora = entregas_no_antecipadas.groupby(
    'Equipe_Entrega'
).size()

entrega_por_distribuidora = entrega_por_distribuidora.reset_index(
    name='Entregas_Antecipadas'
)

entrega_por_distribuidora.sort_values(
    by='Entregas_Antecipadas', ascending=False
).reset_index().drop(columns='index')
# percentual de cada distribuidora
entrega_por_distribuidora['Percentual_Entrega'] = round(
    entrega_por_distribuidora['Entregas_Antecipadas'] / total_entregas * 100, 2
)

# ---------------------------------------------------------------------------------------##---------------------------------------------------------------------------------------#
df['Mes_Entrega'] = df['Data_Entrega_Realizada'].apply(
    lambda x: re.search(r'de (\w+) de', x).group(1)
)

mes_para_numero = {
    'janeiro': 1,
    'fevereiro': 2,
    'março': 3,
    'abril': 4,
    'maio': 5,
    'junho': 6,
    'julho': 7,
    'agosto': 8,
    'setembro': 9,
    'outubro': 10,
    'novembro': 11,
    'dezembro': 12,
}

# aplicando a funcao e criando a coluna mes numerico
df['mes_numerico'] = df['Mes_Entrega'].apply(lambda x: mes_para_numero[x])

df_meses = df[['Mes_Entrega']]
df_total_mes = df_meses.groupby('Mes_Entrega').size().reset_index()
df_total_mes.columns = ['Mes_Entrega', 'Total_Entrega']
df_total_mes['Mes_Numero'] = df_total_mes['Mes_Entrega'].apply(
    lambda x: mes_para_numero[x]
)
df_total_mes = df_total_mes.sort_values('Mes_Numero')
# ---------------------------------------------------------------------------------------##---------------------------------------------------------------------------------------#

df_vendedor = df.groupby('ID_Vendedor').size().reset_index()
df_vendedor.columns = ['ID_Vendedor', 'Total_Venda']
df_vendedor = df_vendedor.sort_values(by='Total_Venda', ascending=False)
df_vendedor = df_vendedor.head(5)
df_vendedor['ID_Vendedor'] = df_vendedor['ID_Vendedor'].apply(
    lambda x: f'Vendedor_{x}'
)
# ---------------------------------------------------------------------------------------##---------------------------------------------------------------------------------------#

df_atraso = df[df['Status_Entrega'] == 'Atrasado']
df_atraso = df_atraso.groupby('ID_Cidade').size()
df_atraso = df_atraso.reset_index()
df_atraso.columns = ['ID_Cidade', 'Total_Entrega_Atrasado']
df_atraso['ID_Cidade'] = df_atraso['ID_Cidade'].astype(str)
df_atraso = df_atraso.sort_values(by='Total_Entrega_Atrasado', ascending=False)
# ---------------------------------------------------------------------------------------##---------------------------------------------------------------------------------------#

df_entregas = df['Status_Entrega'].value_counts().reset_index()
df_entregas.columns = ['Status_Entrega', 'Total_Entrega']
df_entregas['Percentual_Entregas'] = round(
    df_entregas['Total_Entrega'] / total_entregas * 100, 2
)

#########################Graficos#########################
grafico1 = px.bar(
    df_entregas_por_canal,
    orientation='h',
    x='Total_Entregas_No_Prazo',
    y='Canal_Entrega',
    text='Total_Entregas_No_Prazo',
    category_orders={
        'Canal_Entrega': df_entregas_por_canal.sort_values(
            by='Total_Entregas_No_Prazo', ascending=False
        )['Canal_Entrega'].values.tolist()
    },  # Ordenar pelo DataFrame original
    title='Entregas no prazo Por Canal de Entrega',
)

table = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=list(entrega_por_distribuidora.columns),
                fill_color='paleturquoise',  # Cor do cabeçalho
                align='left',
            ),
            cells=dict(
                values=[
                    entrega_por_distribuidora.Equipe_Entrega,
                    entrega_por_distribuidora.Entregas_Antecipadas,
                    entrega_por_distribuidora.Percentual_Entrega,
                ],
                fill_color='lightgray',  # Cor do preenchimento das células
                align='left',
            ),
        )
    ]
)

fig = go.Figure(
    data=go.Scatter(
        x=df_total_mes['Mes_Entrega'],
        y=df_total_mes['Total_Entrega'],
        mode='lines+markers',
    )
)

grafico4 = px.bar(
    df_vendedor,
    orientation='h',
    x='Total_Venda',
    y='ID_Vendedor',
    text='Total_Venda',
    category_orders={
        'ID_Vendedor': df_vendedor.sort_values(
            by='Total_Venda', ascending=False
        )['ID_Vendedor'].values.tolist()
    },  # Ordenar pelo DataFrame original
    title='Top 5 Vendedores',
)

table2 = go.Figure(
    data=[
        go.Table(
            header=dict(
                values=list(df_atraso.columns),
                fill_color='paleturquoise',
                align='left',
            ),
            cells=dict(
                values=[df_atraso.ID_Cidade, df_atraso.Total_Entrega_Atrasado],
                fill_color='lightgray',
                align='left',
            ),
        )
    ]
)

grafico6 = px.pie(
    data_frame=df_entregas,
    values='Total_Entrega',
    names='Status_Entrega',
    title='Percentual de Entregas Por Status de Entrega',
)


#########################Configuracao graficos#########################
grafico1.update_layout(
    width=500,
    height=600,
    title={
        'text': 'Entregas no prazo Por Canal de Entrega',
        'x': 0.5,
        'xanchor': 'center',
    },
)

table.update_layout(
    width=500,
    height=len(entrega_por_distribuidora['Equipe_Entrega']) * 50,
    title={
        'text': 'Entregas Antecipadas Por Equipe de Entrega',
        'x': 0.5,
        'xanchor': 'center',
    },
)

grafico4.update_layout(
    width=500,
    height=600,
    title={'text': 'Top 5 Vendedores', 'x': 0.5, 'xanchor': 'center'},
)

fig.update_layout(
    title={'text': 'Total de Entregas por Mês', 'x': 0.5, 'xanchor': 'center'},
    xaxis_title='Mês',
    yaxis_title='Total de Entregas',
    width=960,
    height=400,
)

table2.update_layout(
    width=500,
    height=400,
    title={'text': 'Total Entrega Por Cidade', 'x': 0.5, 'xanchor': 'center'},
)

grafico6.update_traces(textposition='inside', textinfo='percent+label')
grafico6.update_layout(
    width=600,
    height=500,
    title={
        'text': 'Percentual de Entregas Por Status de Entrega',
        'x': 0.5,
        'xanchor': 'center',
    },
)

col1, col2 = st.columns([1, 1])
with col1:
    st.plotly_chart(fig)
with col2:
    st.plotly_chart(grafico6)

# Colunas
col1, col2 = st.columns([1, 1], gap='large')

with col1:
    st.plotly_chart(table2)
    st.plotly_chart(grafico4)
with col2:
    st.plotly_chart(table)
    st.plotly_chart(grafico1)
