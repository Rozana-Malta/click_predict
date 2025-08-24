import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import warnings
from datetime import date, datetime

warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Customer Insights Dashboard",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS with your color palette
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
    .stDownloadButton > button {
        background-color: #3b2899;
        color: white;
        border-radius: 8px;
        border: 2px solid #3b2899;
        font-weight: bold;
        width: 100%;
        margin-top: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🔍 Click Predict Dashboard</h1>
    <p>Análise, Clusterização e Previsão do Comportamento do Cliente</p>
</div>
""", unsafe_allow_html=True)

# File paths from user's provided data
PATH_CLUSTERS = 'clientes_com_clusters_com_tipo_cliente.csv'
PATH_PREDICAO_ROTA = 'predicoes_next_route_alterado.csv'
PATH_PREDICAO_COMPRA = 'predicao_prox_compra_7_dias.csv'
PATH_DADOS_COMPLETOS = 'df_curado_head5000.csv'

# Function to load data from CSV and cache it
@st.cache_data
def load_data():
    try:
        df_clusters = pd.read_csv(PATH_CLUSTERS)
        df_pred_compra = pd.read_csv(PATH_PREDICAO_COMPRA)
        df_pred_rota = pd.read_csv(PATH_PREDICAO_ROTA)
        df_completo = pd.read_csv(PATH_DADOS_COMPLETOS)
        
        # Merge dataframes for filtering
        df_consolidado = pd.merge(df_clusters, df_pred_compra, on='client_id', how='left')
        df_consolidado = pd.merge(df_consolidado, df_pred_rota, on='client_id', how='left')
        df_consolidado = pd.merge(df_consolidado, df_completo[['client_id', 'purchase_datetime']], on='client_id', how='left')
        df_consolidado['purchase_datetime'] = pd.to_datetime(df_consolidado['purchase_datetime'])
        df_consolidado.drop_duplicates(subset=['client_id'], inplace=True)
        
        return df_consolidado
    except FileNotFoundError:
        st.error("Erro: Um ou mais arquivos CSV não foram encontrados. Verifique os caminhos.")
        return None

df_consolidado = load_data()

if df_consolidado is not None:
    
    # Sidebar filters
    st.sidebar.header("⚙️ Filtros Interativos")
    
    # Filter for clusters
    cluster_options = ['Todos'] + sorted(df_consolidado['tipo_cliente'].unique().tolist())
    selected_cluster = st.sidebar.selectbox("Filtro por Grupo de Cliente", cluster_options)

    # Date filters (Month/Year)
    min_date = df_consolidado['purchase_datetime'].min().to_pydatetime()
    max_date = df_consolidado['purchase_datetime'].max().to_pydatetime()

    selected_date = st.sidebar.date_input("Filtrar por Data", 
                                        value=(min_date, max_date),
                                        min_value=min_date,
                                        max_value=max_date)
    
    # Filter for top routes
    top_options = ['Todos', 'top1', 'top2', 'top3', 'top4', 'top5']
    selected_tops = st.sidebar.multiselect("Filtrar por Top de Rota", options=top_options, default='Todos')
    if 'Todos' in selected_tops and len(selected_tops) > 1:
        selected_tops.remove('Todos')

    # Percentage filter
    prob_threshold = st.sidebar.slider(
        "Filtrar por Probabilidade de Compra",
        min_value=0,
        max_value=100,
        value=0,
        step=1
    )

    # Filter data based on selection
    df_filtered = df_consolidado.copy()
    
    if selected_cluster != 'Todos':
        df_filtered = df_filtered[df_filtered['tipo_cliente'] == selected_cluster]
    
    # Filter by date range
    if len(selected_date) == 2:
        start_date, end_date = selected_date
        df_filtered = df_filtered[(df_filtered['purchase_datetime'].dt.date >= start_date) & 
                                  (df_filtered['purchase_datetime'].dt.date <= end_date)]
    
    # Filter by probability
    df_filtered = df_filtered[df_filtered['prob_prox_compra_7_dias'] >= prob_threshold / 100]

    # ---
    # Download buttons in the sidebar
    st.sidebar.markdown("---")
    st.sidebar.subheader("📥 Opções de Download")

    # The existing button for all predicted customers
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
        
    # The new button for filtered predicted customers
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

    # ---

    # Main content of the dashboard
    
    # Metrics section
    st.subheader("📊 Métricas Principais")
    col1, col2, col3 = st.columns(3)

    with col1:
        total_customers = df_filtered['client_id'].nunique()
        st.metric("Total de Clientes", f"{total_customers:,}")

    with col2:
        next_buy_true = df_filtered[df_filtered['prox_compra_7_dias'] == 1]['client_id'].nunique()
        st.metric("Clientes que Vão Comprar", f"{next_buy_true:,}")

    with col3:
        avg_prob = df_filtered['prob_prox_compra_7_dias'].mean() * 100
        st.metric("Probabilidade Média", f"{avg_prob:.2f}%")

    # ---
    
    ## Análise e Clusterização de Clientes 
    
    st.header("👥 Análise de Clientes e Clusters")
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
        
    # ---

    ## Previsão da Próxima Compra em 7 Dias
    
    st.header("💰 Previsão de Próxima Compra")
    col1, col2 = st.columns(2)
    
    if not df_filtered.empty:
        with col1:
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
            fig_hist.update_layout(
                xaxis_title='Faixa de Probabilidade',
            )
            st.plotly_chart(fig_hist, use_container_width=True)
            
        with col2:
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
            # A linha abaixo foi removida para retirar os números de cima das barras
            # fig_buy_bar.update_traces(textposition='outside', texttemplate='%{y}', textfont={'size': 14})
            fig_buy_bar.update_layout(yaxis_range=[0, buy_counts['count'].max() * 1.1])
            st.plotly_chart(fig_buy_bar, use_container_width=True)
    else:
        st.info("Não há dados de previsão de compra para os filtros selecionados.")
        
    # ---

    ## Previsão da Próxima Rota (Trecho)
    
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
                title="Rotas Mais Preditas (Top 5)",
                color='Rota',
                color_discrete_sequence=px.colors.qualitative.Dark24
            )
            fig_routes_bar.update_traces(textposition='outside', texttemplate='%{y}')
            fig_routes_bar.update_layout(
                xaxis_title="Rota (Origem -> Destino)",
                yaxis_title="Contagem"
            )
            
            st.plotly_chart(fig_routes_bar, use_container_width=True)
        else:
            st.info("Nenhuma rota encontrada para os filtros selecionados.")
    else:
        st.info("Nenhum cliente com previsão de compra positiva no filtro selecionado para exibir as rotas.")

    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #3b2899;'>🔍 Customer Insights Dashboard - Desenvolvido com Streamlit</div>",
        unsafe_allow_html=True
    )