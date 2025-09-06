import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def page():
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
    </style>
    """, unsafe_allow_html=True)

    # -- CABEÇALHO -- #
    st.markdown("""
    <div class="main-header">
        <h1>🚌 Click Predict Dashboard</h1>
        <p>Predição de Tickets de Passagens com Base em Dados Históricos</p>
    </div>
    """, unsafe_allow_html=True)

    # -- CARREGAMENTO DOS DADOS -- #
    df = pd.read_csv("data/df_t.csv", sep=',', encoding_errors='ignore')
    df['date_purchase'] = pd.to_datetime(df['date_purchase'])

    # -- FILTROS -- #
    col1, col2, col3 = st.columns(3)
    with col1:
        # Filtro por período
        date_range = st.date_input(
            "Período de Análise",
            value=(df['date_purchase'].min(), df['date_purchase'].max()),
            min_value=df['date_purchase'].min(),
            max_value=df['date_purchase'].max()
        )

    with col2:
        # Filtro de origem
        origins = ['Todos'] + sorted(df['place_origin_departure'].unique().tolist())
        selected_origin = st.selectbox("Origem", origins)

    with col3:
        # Filtro de destino
        destinations = ['Todos'] + sorted(df['place_destination_departure'].unique().tolist())
        selected_destination = st.selectbox("Destino", destinations)

    # Filtrar dados no dataframe com base nos filtros selecionados na página
    filtered_df = df[
        (df['date_purchase'] >= pd.to_datetime(date_range[0])) &
        (df['date_purchase'] <= pd.to_datetime(date_range[1]))
    ]

    if selected_origin != 'Todos':
        filtered_df = filtered_df[filtered_df['place_origin_departure'] == selected_origin]

    if selected_destination != 'Todos':
        filtered_df = filtered_df[filtered_df['place_destination_departure'] == selected_destination]

    # Acrescenta espaço entre os filtros e as métricas
    st.markdown("<hr>", unsafe_allow_html=True)

    # -- MÉTRICAS -- #
    # Alerta crítico, Próximo pico e Tendência

    st.markdown("""
    <style>
    .card-container {
        display: flex;
        gap: 20px;
        margin-top: 20px;
        flex-wrap: wrap;
    }

    .card {
        flex: 1;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid transparent;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        min-width: 250px;
    }

    .card.alerta {
        background-color: #fff5f5;
        border-color: #ffcccc;
        color: #b00020;
    }

    .card.pico {
        background-color: #f0f5ff;
        border-color: #c3d2ff;
        color: #0033cc;
    }

    .card.tendencia {
        background-color: #f2fef6;
        border-color: #c3f1d6;
        color: #007b33;
    }

    .card .title {
        font-weight: 600;
        font-size: 16px;
        display: flex;
        align-items: center;
        margin-bottom: 8px;
    }

    .card .title i {
        margin-right: 6px;
    }

    .card .value {
        font-size: 24px;
        font-weight: bold;
        margin-bottom: 4px;
    }

    .card .desc {
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)

    with col1:
        # Alerta Crítico
        alerta_value = 5
        alerta_desc = "Períodos com alta demanda"
        alerta_card = f"""
        <div class="card-container">
            <div class="card alerta">
                <div class="title">⚠️ Alerta Crítico</div>
                <div class="value">{alerta_value}</div>
                <div class="desc">{alerta_desc}</div>
            </div>
        </div>
        """
        st.markdown(alerta_card, unsafe_allow_html=True)

    with col2:
        # Próximo Pico
        pico_value = "Out. Sem. 4"
        pico_desc = "98% de demanda prevista"
        pico_card = f"""
        <div class="card-container">
            <div class="card pico">
                <div class="title">📈 Próximo Pico</div>
                <div class="value">{pico_value}</div>
                <div class="desc">{pico_desc}</div>
            </div>
        </div>
        """
        st.markdown(pico_card, unsafe_allow_html=True)
    with col3:
        # Tendência
        tendencia_value = "+15%"
        tendencia_desc = "Crescimento médio"
        tendencia_card = f"""
        <div class="card-container">
            <div class="card tendencia">
                <div class="title">📊 Tendência</div>
                <div class="value">{tendencia_value}</div>
                <div class="desc">{tendencia_desc}</div>
            </div>
        </div>
        """ 
        st.markdown(tendencia_card, unsafe_allow_html=True)
    # -- espaço entre as métricas e o gráfico -- #
    st.markdown("<hr>", unsafe_allow_html=True)


    # -- PREVISÕES -- #
    st.subheader("📈 Previsão de vendas de passagens")

    # --- Simula dados reais (jan a mar de 2023) ---
    real_dates = pd.date_range(start='2023-01-01', end='2023-03-31', freq='D')
    real_values = np.random.normal(loc=48000, scale=4000, size=len(real_dates))

    real_df = pd.DataFrame({
        'date_purchase': real_dates,
        'gmv_success': real_values,
        'tipo': 'Real'
    })

    # --- Simula dados de previsão (abr a mai de 2023) ---
    forecast_dates = pd.date_range(start='2023-04-01', end='2023-05-31', freq='D')
    trend = np.linspace(real_df['gmv_success'].mean(), real_df['gmv_success'].mean() * 1.15, len(forecast_dates))
    noise = np.random.normal(loc=0, scale=3500, size=len(forecast_dates))

    forecast_df = pd.DataFrame({
        'date_purchase': forecast_dates,
        'gmv_success': trend + noise,
        'tipo': 'Previsto'
    })

    # Junta os dados
    full_df = pd.concat([real_df, forecast_df])
    full_df = full_df.sort_values('date_purchase')

    # Criação do gráfico
    fig = go.Figure()

    # Linha de dados reais
    fig.add_trace(go.Scatter(
        x=full_df[full_df['tipo'] == 'Real']['date_purchase'],
        y=full_df[full_df['tipo'] == 'Real']['gmv_success'],
        mode='lines',
        name='Vendas realizadas',
        line=dict(color='#3b2899', width=2)
    ))

    # Linha de previsão
    fig.add_trace(go.Scatter(
        x=full_df[full_df['tipo'] == 'Previsto']['date_purchase'],
        y=full_df[full_df['tipo'] == 'Previsto']['gmv_success'],
        mode='lines',
        name='Previsão',
        line=dict(color='#ff4f63', width=2, dash='dash')
    ))

    fig.update_layout(
        title='Previsão de vendas de passagens | Fictício',
        xaxis_title='Data',
        yaxis_title='Valor total das vendas (R$)',
        template='plotly_white',
        legend=dict(title='Legenda'),
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)


    st.subheader("📊 Análise de probabilidade")
    
    col1, col2 = st.columns(2)
    with col1:
        # Customer behavior
        customer_stats = filtered_df.groupby('fk_contact').agg({
            'total_tickets_quantity_success': 'sum',
            'gmv_success': 'sum',
            'date_purchase': 'count'
        }).rename(columns={'date_purchase': 'num_purchases'})

        # Probability categories
        def categorize_customer(row):
            if row['num_purchases'] >= 5:
                return 'Alta Probabilidade'
            elif row['num_purchases'] >= 2:
                return 'Média Probabilidade'
            else:
                return 'Baixa Probabilidade'

        customer_stats['probability_category'] = customer_stats.apply(categorize_customer, axis=1)
        prob_dist = customer_stats['probability_category'].value_counts()
    
        fig_prob = px.pie(
            values=prob_dist.values,
            names=prob_dist.index,
            title="Probabilidade de compra futura",
            color_discrete_sequence=['#efefef', '#3b2899', '#ff4f63']
        )
        # colocar a legenda do grafico do lado esquerdo
        fig_prob.update_traces(textinfo='percent+label', pull=[0, 0.1, 0.1])  # destaque para os segmentos
        fig_prob.update_layout(
            legend=dict(orientation='v', y=1.02, xanchor='left', x=0),
            margin=dict(t=50, b=20, l=20, r=20)  # margens do gráfico
        )
        st.plotly_chart(fig_prob, use_container_width=True)

    with col2:
        np.random.seed(42)  # Reprodutibilidade

        # Criação do DataFrame fictício
        clusters = [f'Cluster {i}' for i in range(1, 11)]  # 10 clusters fictícios
        data = []

        for cluster in clusters:
            num_purchases = np.random.randint(1, 10)  # entre 1 e 9 compras por cluster
            total_tickets = np.random.randint(10, 200)
            gmv = np.round(np.random.uniform(1000, 10000), 2)

            data.append({
                'cluster': cluster,
                'total_tickets_quantity_success': total_tickets,
                'gmv_success': gmv,
                'date_purchase': num_purchases  # usamos isso como número de compras
            })

        filtered_df = pd.DataFrame(data)

        # Agrupamento e cálculo da probabilidade
        cluster_stats = filtered_df.groupby('cluster').agg({
            'total_tickets_quantity_success': 'sum',
            'gmv_success': 'sum',
            'date_purchase': 'sum'
        }).rename(columns={'date_purchase': 'num_purchases'})

        # Classificação da probabilidade
        cluster_stats['probability_category'] = cluster_stats['num_purchases'].apply(
            lambda x: 'Cluster 1' if x >= 7 else ('Cluster 2' if x >= 4 else 'Cluster 3')
        )

        # Contagem por categoria
        prob_dist_cluster = cluster_stats['probability_category'].value_counts()

        # Gráfico
        fig_cluster_prob = px.bar(
            x=prob_dist_cluster.index,
            y=prob_dist_cluster.values,
            title="Probabilidade de retorno por cluster",
            labels={'x': 'Cluster', 'y': 'Probabilidade de retorno (%)'},
            color_discrete_sequence=['#3b2899', '#ff4f63', '#efefef']
        )
        fig_cluster_prob.update_layout(
            barcornerradius=12,  # bordas arredondadas
        )

        st.plotly_chart(fig_cluster_prob, use_container_width=True)

    # Informativo final
    st.info("""
            🔔 **Recomendações estratégicas:**

            • Aumentar preços durante períodos de alta demanda (Jul Sem 4, Ago Sem 2)

            • Preparar capacidade extra para Set Sem 2 (demanda crítica prevista)

            • Oferecer promoções em períodos de baixa demanda (Set Sem 1)

            • Monitorar feriados prolongados que podem gerar picos inesperados
        """)