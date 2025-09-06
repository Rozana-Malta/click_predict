import streamlit as st
import pandas as pd
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
    
    st.subheader("📊 Métricas de Desempenho")
    total_tickets = filtered_df['nk_ota_localizer_id'].nunique()
    receita_total = filtered_df['gmv_success'].sum()
    receita_media_por_ticket = receita_total / total_tickets if total_tickets > 0 else 0
    # Display metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total de tickets", total_tickets, delta=None, help="Número total de tickets únicos no período selecionado.")
    with col2:
        st.metric("Receita total", f"R$ {receita_total:,.2f}", delta=None, help="Receita total gerada no período selecionado.")
    with col3:
        st.metric("Receita média por ticket", f"R$ {receita_media_por_ticket:,.2f}", delta=None, help="Receita média gerada por ticket no período selecionado.")


    # Destinos mais populares
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("📍 Origens e Destinos mais relevantes")
    # Top destinations
    top_destinations = filtered_df['place_destination_departure'].value_counts().head(5)
    top_origins = filtered_df['place_origin_departure'].value_counts().head(5)

    col1, col2 = st.columns(2)
    with col1:
        fig_orig = go.Figure()
        fig_orig.add_trace(go.Bar(
            x=top_origins.values,
            y=top_origins.index,
            orientation='h',
            marker=dict(
                color='#3b2899',
                line=dict(width=1, color='#ffffff')
            ),
            name='',
        ))

        fig_orig.update_layout(
            yaxis=dict(autorange='reversed')
        )

        # Aplica borda arredondada
        fig_orig.update_layout(
            barcornerradius=12,  # bordas arredondadas
            title="Top 5 origens com maior volume de partidas",
            xaxis_title="Quantidade de tickets",
            yaxis_title="Nome do local de origem",
        )

        st.plotly_chart(fig_orig, use_container_width=True)

    with col2:
        fig_dest = go.Figure()
        fig_dest.add_trace(go.Bar(
            x=top_destinations.values,
            y=top_destinations.index,
            orientation='h',
            marker=dict(
                color='#ff4f63',
                line=dict(width=1, color='#ffffff')
            ),
            name=''
        ))

        fig_dest.update_layout(
            yaxis=dict(autorange='reversed')
        )


        fig_dest.update_layout(
            barcornerradius=12,  # bordas arredondadas
            title="Top 5 destinos mais procurados",
            xaxis_title="Quantidade de tickets",
            yaxis_title="Nome do local de destino"
        )

        st.plotly_chart(fig_dest, use_container_width=True)

    # Vendas ao longo do tempo
    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("📈 Evolução das vendas ao longo do tempo")
    filtered_df['date_purchase'] = pd.to_datetime(filtered_df['date_purchase'])
    sales_over_time = filtered_df.groupby('date_purchase').agg({'gmv_success': 'sum'}).reset_index()
    fig_sales = px.line(
        sales_over_time,
        x='date_purchase',
        y='gmv_success',
        title="Evolução das vendas ao longo do tempo",
        labels={'date_purchase': 'Data da Compra', 'gmv_success': 'Receita (R$)'},
        color_discrete_sequence=['#ff4f63']
    )
    fig_sales.update_layout(
        xaxis_title="Data da compra",
        yaxis_title="Receita (R$)",
        xaxis=dict(tickformat='%d/%m/%Y')
    )
    st.plotly_chart(fig_sales, use_container_width=True)

    st.markdown("<hr>", unsafe_allow_html=True)
    st.subheader("🚨 Análise de alta demanda")
    col1, col2 = st.columns(2)
    # Horários de maior volume de compras
    with col1:
        filtered_df['time_purchase'] = pd.to_datetime(filtered_df['time_purchase'], format='%H:%M:%S').dt.hour
        time_counts = filtered_df['time_purchase'].value_counts().sort_index()
        fig_time = go.Figure()
        fig_time.add_trace(go.Scatter(
            x=time_counts.index,
            y=time_counts.values,
            fill='tozeroy',
            fillcolor='rgba(59, 40, 153, 0.2)',
            mode='lines+markers',
            name='Volume de compras',
            line=dict(color='#3b2899', shape='spline', smoothing=1.3),
            marker=dict(size=6),
            hoverinfo='y+name'
        ))
        fig_time.update_layout(
            title="Horários de maior volume de compras",
            xaxis_title="Hora do dia",
            yaxis_title="Quantidade de tickets",
            xaxis=dict(tickmode='linear', dtick=1),
            #template="simple_white"
        )

        st.plotly_chart(fig_time, use_container_width=True)

    with col2:
        # heatmap de demanda por dia e hora
        # Cria uma coluna de dia da semana
        filtered_df['day_of_week'] = filtered_df['date_purchase'].dt.day_name()
        # Agrupa por dia da semana e hora do dia
        demand_heatmap = filtered_df.groupby(['day_of_week', 'time_purchase']).size().unstack(fill_value=0)
        # Reordena os dias da semana
        days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        demand_heatmap = demand_heatmap.reindex(days_order)
        # Cria o heatmap
        fig_heatmap = px.imshow(
            demand_heatmap,
            labels={'x': 'Hora do dia', 'y': 'Dia da semana', 'color': 'Quantidade de tickets'},
            title="Demanda por dia da semana e hora do dia",
            color_continuous_scale=['#efefef', '#ff4f63', '#3b2899']
        )       
        fig_heatmap.update_layout(
            xaxis_title="Hora do dia",
            yaxis_title="Dia da semana",
            xaxis=dict(tickmode='linear', dtick=1),
            yaxis=dict(tickmode='array', tickvals=list(range(len(days_order))), ticktext=days_order)
        )
        st.plotly_chart(fig_heatmap, use_container_width=True)