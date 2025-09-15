import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
from datetime import date, datetime, timedelta
import sqlite3

warnings.filterwarnings('ignore')

# CONFIGURAÇÃO DA PÁGINA
st.set_page_config(
    page_title="Customer Insights Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CUSTOMIZAÇÃO DA PALETA DE COR
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(90deg, #ff4f63 0%, #3b2899 100%);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        color: white;
        margin-bottom: 30px;
    }
    .metric-card {
        background: #ffffff;
        padding: 20px;
        border-radius: 10px;
        border-left: 4px solid #ff4f63;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sidebar .sidebar-content {
        background: #efefef;
    }
    .stMetric > label {
        color: #3b2899 !important;
    }
    [data-testid="stMetricValue"] {
        color: #333333 !important;
    }
    .stDownloadButton > button {
        background-color: #3b2899;
        color: white;
        border-radius: 8px;
        border: 2px solid #3b2899;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
    }
    
    /* Padronização de Títulos e Subtítulos */
    h1, h2 {
        color: #3b2899;
    }
    h3 {
        color: #ff4f63;
        font-size: 24px;
        margin-top: 25px;
        margin-bottom: 15px;
    }
    .big-font {
        font-size: 20px !important;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        background-color: #3b2899;
        color: white;
        font-weight: bold;
        padding: 15px;
        border-radius: 10px;
        border: none;
    }
</style>
""", unsafe_allow_html=True)

# CABEÇALHO GLOBAL
st.markdown("""
<div class="main-header">
    <h1>🔍 Click Predict Dashboard</h1>
    <p>Análise, Clusterização e Previsão do Comportamento do Cliente</p>
</div>
""", unsafe_allow_html=True)

## Nomes dos seus arquivos CSV
#PATH_CLUSTERS = 'clientes_com_clusters_com_tipo_cliente.csv'
#PATH_PREDICAO_ROTA = 'data/predict_next_route.csv'
#PATH_PREDICAO_COMPRA = 'data/predict_next_purchase.csv'
#PATH_DADOS_COMPLETOS = 'data/df_curado_head5000.csv'
#
## Nomes das tabelas que serão criadas no banco de dados
#TABLE_CLUSTERS = 'clientes_com_clusters'
#TABLE_PREDICAO_ROTA = 'predicoes_next_route'
#TABLE_PREDICAO_COMPRA = 'predicao_prox_compra'
#TABLE_DADOS_COMPLETOS = 'df_curado_head5000'
#
## Conexão com o banco de dados (será criado um arquivo .db na mesma pasta)
#conn = sqlite3.connect('dashboard_data.db')
#
#try:
#    # Carregue cada arquivo CSV em um DataFrame
#    df_clusters = pd.read_csv(PATH_CLUSTERS)
#    df_pred_compra = pd.read_csv(PATH_PREDICAO_COMPRA)
#    df_pred_rota = pd.read_csv(PATH_PREDICAO_ROTA)
#    df_completo = pd.read_csv(PATH_DADOS_COMPLETOS, delimiter=";")
#
#    # Exporte cada DataFrame para uma tabela no banco de dados
#    df_clusters.to_sql(TABLE_CLUSTERS, conn, if_exists='replace', index=False)
#    df_pred_compra.to_sql(TABLE_PREDICAO_COMPRA, conn, if_exists='replace', index=False)
#    df_pred_rota.to_sql(TABLE_PREDICAO_ROTA, conn, if_exists='replace', index=False)
#    df_completo.to_sql(TABLE_DADOS_COMPLETOS, conn, if_exists='replace', index=False)
#
#    print("Banco de dados criado e populado com sucesso!")
#
#except FileNotFoundError:
#    print("Erro: Um ou mais arquivos CSV não foram encontrados.")
#finally:
#    conn.close()

# FUNÇÃO PARA LER O BANCO DE DADOS 
@st.cache_data
def load_data_from_db():
    conn = sqlite3.connect('dashboard_data.db')
    
    df_clusters = pd.read_sql_query("SELECT * FROM clientes_com_clusters", conn)
    df_pred_compra = pd.read_sql_query("SELECT * FROM predicao_prox_compra", conn)
    df_pred_rota = pd.read_sql_query("SELECT * FROM predicoes_next_route", conn)
    df_completo = pd.read_sql_query("SELECT * FROM df_curado", conn)
    
    df_consolidado = pd.merge(df_clusters, df_pred_compra, on='client_id', how='left')
    df_consolidado = pd.merge(df_consolidado, df_pred_rota, on='client_id', how='left')
    df_consolidado = pd.merge(df_consolidado, df_completo[['client_id', 'purchase_datetime','total_value']], on='client_id', how='left')
    df_consolidado['purchase_datetime'] = pd.to_datetime(df_consolidado['purchase_datetime'])
    df_consolidado.drop_duplicates(subset=['client_id'], inplace=True)
    
    # Criando a nova coluna de 'acerto_previsao_compra'
    df_consolidado['acerto_previsao_compra'] = ((df_consolidado['prox_compra_7_dias'] == 1.0) & (df_consolidado['total_value'].notna())).astype(int)

    # Adicione esta linha para salvar a tabela no banco de dados
    df_consolidado.to_sql('df_consolidado', conn, if_exists='replace', index=False)

    conn.close()

    return df_consolidado
    

df_consolidado = load_data_from_db()

# --- FUNÇÕES PARA CADA PÁGINA ---
def render_home_page():
    st.title("Bem-vindo ao Click Predict Dashboard")
    st.markdown("---")
    st.write(
        """
        Este dashboard oferece uma visão completa e interativa sobre o comportamento dos seus clientes.
        Explore as análises de clusterização, previsões de compra e rotas para identificar oportunidades
        e tomar decisões estratégicas mais inteligentes.
        """
    )

    st.markdown("## Navegue pelo Dashboard")

    col_home_1, col_home_2 = st.columns(2)
    with col_home_1:
        if st.button("👥 Análise de Clusters"):
            st.session_state.page = "Análise de Clusters"
            st.rerun()
    with col_home_2:
        if st.button("💰 Previsão de Compra"):
            st.session_state.page = "Previsão de Compra"
            st.rerun()

    col_home_3, col_home_4 = st.columns(2)
    with col_home_3:
        if st.button("📍 Previsão de Rotas"):
            st.session_state.page = "Previsão de Rotas"
            st.rerun()
    with col_home_4:
        if st.button("📈 Comparativo de Receita"):
            st.session_state.page = "Comparativo de Receita"
            st.rerun()

    col_home_5, col_home_6 = st.columns(2)
    with col_home_5:
        if st.button("📊 Receita por Data"):
            st.session_state.page = "Receita por Data"
            st.rerun()


def render_dashboard_page(df_consolidado):
    if df_consolidado is None:
        st.error("Não foi possível carregar os dados. Verifique a conexão com o banco de dados e os arquivos CSV.")
        return

    # Sidebar: Filtro de Cluster
    unique_clusters = sorted(df_consolidado['tipo_cliente'].unique())
    all_clusters_option = ['Todos'] + unique_clusters
    selected_cluster = st.sidebar.selectbox("Filtrar por Cluster", all_clusters_option)

    # Sidebar: Filtro de Data
    st.sidebar.header("🗓️ Filtro de Dados")
    selected_date = st.sidebar.date_input(
        "Filtrar por Data da Compra",
        value=(df_consolidado['purchase_datetime'].min().date(), df_consolidado['purchase_datetime'].max().date()),
        min_value=df_consolidado['purchase_datetime'].min().date(),
        max_value=df_consolidado['purchase_datetime'].max().date()
    )
        
    # Sidebar: Filtro de Probabilidade
    prob_threshold = st.sidebar.slider(
        "Filtrar por Probabilidade de Compra",
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )

    # Sidebar: Filtro de Top de Rotas
    top_options = ['Todos', 'top1', 'top2', 'top3', 'top4', 'top5']
    selected_tops = st.sidebar.multiselect("Filtrar por Top de Rota", options=top_options, default='Todos')
    if 'Todos' in selected_tops and len(selected_tops) > 1:
        selected_tops.remove('Todos')

    # FILTRAR DADOS COM BASE NA SELEÇÃO
    df_filtered = df_consolidado.copy()
    
    if selected_cluster != 'Todos':
        df_filtered = df_filtered[df_filtered['tipo_cliente'] == selected_cluster]
    
    if len(selected_date) == 2:
        start_date, end_date = selected_date
        df_filtered = df_filtered[(df_filtered['purchase_datetime'].dt.date >= start_date) & 
                                  (df_filtered['purchase_datetime'].dt.date <= end_date)]
    
    df_filtered = df_filtered[df_filtered['prob_prox_compra_7_dias'] >= prob_threshold / 100]

    # BOTÃO DE DOWNLOAD DO CSV
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Opções de Download")

    clientes_com_previsao_positiva = df_consolidado[df_consolidado['prox_compra_7_dias'] == 1.0]
    if not clientes_com_previsao_positiva.empty:
        df_para_download_all = clientes_com_previsao_positiva[['client_id', 'top1', 'top2', 'top3', 'top4', 'top5']]
        csv_para_download_all = df_para_download_all.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download de Todos os Clientes Previstos",
            data=csv_para_download_all,
            file_name='todos_clientes_previstos_7dias.csv',
            mime='text/csv',
        )
        
    clientes_com_previsao_positiva_filtrados = df_filtered[df_filtered['prox_compra_7_dias'] == 1.0]
    if not clientes_com_previsao_positiva_filtrados.empty:
        df_para_download_filtered = clientes_com_previsao_positiva_filtrados[['client_id', 'top1', 'top2', 'top3', 'top4', 'top5']]
        csv_para_download_filtered = df_para_download_filtered.to_csv(index=False).encode('utf-8')
        st.sidebar.download_button(
            label="Download dos Clientes Previstos Filtrados",
            data=csv_para_download_filtered,
            file_name='clientes_previstos_filtrados_7dias.csv',
            mime='text/csv',
        )
    
    # Adicionando o botão de voltar para a capa na barra lateral
    st.sidebar.markdown("---")
    if st.sidebar.button("🏠 Voltar para a Capa"):
        st.session_state.page = "Capa"
        st.rerun()

    # CONTEUDO PRINCIPAL DO DASHBOARD
    st.header("📊 Métricas Principais")
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_customers = df_filtered['client_id'].nunique()
        st.metric("Total de Clientes", f"{total_customers:,}")

    with col2:
        next_buy_true = df_filtered[df_filtered['prox_compra_7_dias'] == 1]['client_id'].nunique()
        st.metric("Clientes que Vão Comprar", f"{next_buy_true:,}")

    with col3:
        avg_prob = df_filtered['prob_prox_compra_7_dias'].mean() * 100
        st.metric("Probabilidade Média", f"{avg_prob:.2f}%")

    with col4:
        # Calcular a receita prevista
        predicted_revenue = df_filtered[df_filtered['prox_compra_7_dias'] == 1]['total_value'].sum()
        st.metric("Receita Prevista (Próx. 7 dias)", f"R$ {predicted_revenue:,.2f}")

    st.markdown("---")

    
    # Renderização de seções com base na navegação
    
    if st.session_state.page == "Análise de Clusters":
        render_cluster_analysis(df_consolidado, df_filtered)
    
    if st.session_state.page == "Previsão de Compra":
        render_purchase_prediction(df_filtered)

    if st.session_state.page == "Previsão de Rotas":
        render_route_prediction(df_filtered, selected_tops)
    
    if st.session_state.page == "Comparativo de Receita":
        render_revenue_comparison(df_filtered)

    if st.session_state.page == "Receita por Data":
        render_revenue_by_date(df_filtered)

def render_cluster_analysis(df_consolidado, df_filtered):
    st.markdown("<a name='clusters'></a>", unsafe_allow_html=True)
    st.header("👥 Análise de Clientes e Clusters")
    
    col4, col5 = st.columns(2)
    if not df_consolidado.empty:
        prob_media_geral = df_consolidado['prob_prox_compra_7_dias'].mean() * 100
        cluster_prob_media = df_consolidado.groupby('tipo_cliente')['prob_prox_compra_7_dias'].mean().sort_values(ascending=False)

        cluster_maior_prob = cluster_prob_media.index[0]
        maior_prob_valor = cluster_prob_media.values[0] * 100

        cluster_menor_prob = cluster_prob_media.index[-1]
        menor_prob_valor = cluster_prob_media.values[-1] * 100

        delta_maior = maior_prob_valor - prob_media_geral
        delta_maior_color = "green" if delta_maior > 0 else "red"
        delta_maior_symbol = "↑" if delta_maior > 0 else "↓"

        # Caixa Maior Probabilidade
        with col4:
            st.markdown(f"""
                <div style="background-color: #D3D3D3; padding: 20px; border-radius: 10px; border-left: 4px solid #ff4f63; color: black; height: 200px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">Maior Probabilidade de Compra</div>
                    <div style="display: flex; align-items: baseline; justify-content: space-between;">
                        <div style="font-size: 35px; font-weight: bold;">{maior_prob_valor:.2f}%</div>
                        <div style="font-size: 35px; color: {delta_maior_color}; font-weight: bold; margin-left: 10px;">
                            {delta_maior_symbol} {abs(delta_maior):.2f} p.p.
                        </div>
                    </div>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 10px; text-transform: capitalize;">{cluster_maior_prob}</div>
                </div>
                """, unsafe_allow_html=True)

        # Caixa Menor Probabilidade
        delta_menor = menor_prob_valor - prob_media_geral
        delta_menor_color = "green" if delta_menor > 0 else "red"
        delta_menor_symbol = "↑" if delta_menor > 0 else "↓"
        with col5:
            st.markdown(f"""
                <div style="background-color: #D3D3D3; padding: 20px; border-radius: 10px; border-left: 4px solid #ff4f63; color: black; height: 200px;">
                    <div style="font-size: 16px; font-weight: bold; margin-bottom: 5px;">Menor Probabilidade de Compra</div>
                    <div style="display: flex; align-items: baseline; justify-content: space-between;">
                        <div style="font-size: 35px; font-weight: bold;">{menor_prob_valor:.2f}%</div>
                        <div style="font-size: 35px; color: {delta_menor_color}; font-weight: bold; margin-left: 10px;">
                            {delta_menor_symbol} {abs(delta_menor):.2f} p.p.
                        </div>
                    </div>
                    <div style="font-size: 20px; font-weight: bold; margin-top: 10px; text-transform: capitalize;">{cluster_menor_prob}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("Não há dados de clusters para os filtros selecionados.")

    
    st.markdown("### Distribuição dos Clusters")
    col1, col2 = st.columns(2)
    if not df_filtered.empty:
        with col1:
            cluster_counts = df_filtered['tipo_cliente'].value_counts()
            fig_clusters = px.pie(
                values=cluster_counts.values,
                names=cluster_counts.index,
                title="Distribuição dos Clusters de Clientes",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig_clusters, use_container_width=True)

        with col2:
            fig_bar_clusters = px.bar(
                x=cluster_counts.index,
                y=cluster_counts.values,
                title="Quantidade de Clientes por Cluster",
                color=cluster_counts.index,
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            fig_bar_clusters.update_traces(textposition='outside', texttemplate='%{y}')
            st.plotly_chart(fig_bar_clusters, use_container_width=True)
    else:
        st.info("Não há dados de clusters para os filtros selecionados.")
    st.markdown("---")

def render_purchase_prediction(df_filtered):
    st.markdown("<a name='compra'></a>", unsafe_allow_html=True)
    st.header("💰 Previsão de Próxima Compra")
    col1, col2 = st.columns(2)
    
    if not df_filtered.empty:
        with col1:
            st.markdown("### Distribuição da Probabilidade de Compra")
            prob_data = df_filtered.groupby(pd.cut(df_filtered['prob_prox_compra_7_dias'], bins=10)).size().reset_index(name='count')
            prob_data['percentage'] = (prob_data['count'] / prob_data['count'].sum()) * 100
            prob_data['prob_range'] = prob_data['prob_prox_compra_7_dias'].apply(lambda i: f"{int(i.left * 100)}-{int(i.right * 100)}%")
            
            fig_hist = px.bar(
                prob_data,
                x='prob_range',
                y='count',
                title="Distribuição da Probabilidade de Compra",
                color_discrete_sequence=['#3b2899']
            )
            fig_hist.update_layout(xaxis_title='Faixa de Probabilidade')
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col2:
            st.markdown("### Clientes que Vão Comprar nos Próximos 7 Dias")
            buy_counts = df_filtered['prox_compra_7_dias'].value_counts().reset_index()
            buy_counts.columns = ['Vão Comprar', 'count']
            buy_counts['Vão Comprar'] = buy_counts['Vão Comprar'].map({0.0: 'Não Vão Comprar', 1.0: 'Vão Comprar'})
            
            fig_buy_bar = px.bar(
                buy_counts,
                x='Vão Comprar',
                y='count',
                title="Clientes que Vão Comprar nos Próximos 7 Dias",
                color='Vão Comprar',
                color_discrete_map={'Vão Comprar': '#ff4f63', 'Não Vão Comprar': '#3b2899'},
                category_orders={"": ["Vão Comprar", "Não Vão Comprar"]}
            )
            fig_buy_bar.update_layout(yaxis_range=[0, buy_counts['count'].max() * 1.1])
            st.plotly_chart(fig_buy_bar, use_container_width=True)
    else:
        st.info("Não há dados de previsão de compra para os filtros selecionados.")
    st.markdown("---")

def render_route_prediction(df_filtered, selected_tops):
    st.markdown("<a name='rotas'></a>", unsafe_allow_html=True)
    st.header("📍 Previsão da Próxima Rota")
    
    clientes_que_vao_comprar = df_filtered[df_filtered['prox_compra_7_dias'] == 1.0].copy()

    if 'Todos' not in selected_tops and selected_tops:
        mask = clientes_que_vao_comprar[selected_tops].notna().any(axis=1)
        clientes_que_vao_comprar = clientes_que_vao_comprar[mask]
    
    if not clientes_que_vao_comprar.empty:
        selected_routes_data = clientes_que_vao_comprar[selected_tops] if 'Todos' not in selected_tops else clientes_que_vao_comprar[['top1', 'top2', 'top3', 'top4', 'top5']]
        all_routes = pd.concat([selected_routes_data[col] for col in selected_routes_data.columns]).dropna()
        top_routes_counts = all_routes.value_counts().head(5).sort_values(ascending=False)
        
        if not top_routes_counts.empty:
            df_top_routes = top_routes_counts.reset_index()
            df_top_routes.columns = ['Rota', 'Contagem']

            fig_routes_bar = px.bar(
                df_top_routes,
                x='Rota',
                y='Contagem',
                title="Rotas Mais Preditas",
                color='Rota',
                color_discrete_sequence=px.colors.qualitative.Dark24
            )
            fig_routes_bar.update_traces(textposition='outside', texttemplate='%{y}')
            fig_routes_bar.update_layout(
                xaxis_title="Rota",
                yaxis_title="Contagem"
            )
            st.plotly_chart(fig_routes_bar, use_container_width=True)
        else:
            st.info("Nenhuma rota encontrada para os filtros selecionados.")
    else:
        st.info("Nenhum cliente com previsão de compra positiva no filtro selecionado para exibir as rotas.")
    st.markdown("---")

def render_revenue_comparison(df_filtered):
    st.markdown("<a name='receita'></a>", unsafe_allow_html=True)
    st.header("📈 Comparativo de Receita: Previstos vs. Não Previstos")

    if not df_filtered.empty:
        revenue_comparison = df_filtered.groupby('prox_compra_7_dias')['total_value'].sum().reset_index()
        revenue_comparison.columns = ['Previsão de Compra', 'Receita']
        revenue_comparison['Previsão de Compra'] = revenue_comparison['Previsão de Compra'].map({
            0.0: 'Receita Clientes NÃO Previstos 7 dias',
            1.0: 'Receita Clientes Previstos 7 dias'
        })
        
        fig_revenue_comp = px.bar(
            revenue_comparison,
            x='Previsão de Compra',
            y='Receita',
            title='Receita por Grupo de Previsão de Compra',
            color='Previsão de Compra',
            color_discrete_map={
                'Receita Clientes Previstos 7 dias': '#ff4f63',
                'Receita Clientes NÃO Previstos 7 dias': '#3b2899'
            },
            text=revenue_comparison['Receita'].apply(lambda x: f'R$ {x:,.2f}')
        )

        fig_revenue_comp.update_traces(textposition='outside')
        max_revenue = revenue_comparison['Receita'].max()
        fig_revenue_comp.update_layout(
            xaxis_title="",
            yaxis_title="Receita Total (R$)",
            showlegend=False,
            yaxis_range=[0, max_revenue * 1.15]
        ) 
        st.plotly_chart(fig_revenue_comp, use_container_width=True)
    else:
        st.info("Não há dados para os filtros selecionados.")
    st.markdown("---")

def render_revenue_by_date(df_filtered):
    st.header("📊 Receita por Data")
    st.markdown("---")

    if not df_filtered.empty:
        df_daily_revenue = df_filtered.groupby(df_filtered['purchase_datetime'].dt.date)['total_value'].sum().reset_index()
        df_daily_revenue.columns = ['Data', 'Receita']

        fig_revenue_by_date = px.line(
            df_daily_revenue,
            x='Data',
            y='Receita',
            title='Receita Total por Dia',
            markers=True,
            line_shape='spline',
            color_discrete_sequence=['#3b2899']
        )
        fig_revenue_by_date.update_layout(
            xaxis_title="Data da Compra",
            yaxis_title="Receita (R$)",
            hovermode="x unified"
        )
        st.plotly_chart(fig_revenue_by_date, use_container_width=True)
    else:
        st.info("Não há dados de receita para os filtros selecionados.")
    st.markdown("---")


# --- LÓGICA DE NAVEGAÇÃO PRINCIPAL ---
if 'page' not in st.session_state:
    st.session_state.page = "Capa"

# Verificando qual página deve ser renderizada
if st.session_state.page == "Capa":
    render_home_page()
else:
    render_dashboard_page(df_consolidado)
