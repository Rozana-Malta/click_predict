import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import datetime as dt
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import LabelEncoder
import warnings
warnings.filterwarnings('ignore')

# Configure page
st.set_page_config(
    page_title="Click Predict Dashboard",
    page_icon="🚌",
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
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1>🚌 Click Predict Dashboard</h1>
    <p>Predição de Tickets de Passagens com Base em Dados Históricos</p>
</div>
""", unsafe_allow_html=True)

# Function to generate sample data
@st.cache_data
def generate_sample_data():
    np.random.seed(25)
    
    # Sample cities
    origins = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador', 
               'Recife', 'Porto Alegre', 'Curitiba', 'Fortaleza', 'Goiânia']
    destinations = ['São Paulo', 'Rio de Janeiro', 'Belo Horizonte', 'Brasília', 'Salvador', 
                   'Recife', 'Porto Alegre', 'Curitiba', 'Fortaleza', 'Goiânia']
    
    # Generate 10000 sample records
    n_records = 1000
    
    # Date range: last 2 years
    start_date = dt.datetime(2024, 1, 1)
    end_date = dt.datetime(2024, 12, 31)
    
    data = []
    for i in range(n_records):
        # Random date
        random_date = start_date + dt.timedelta(days=np.random.randint(0, (end_date - start_date).days))
        
        # Random time (peak hours more likely)
        hour_weights = [0.5, 0.5, 0.5, 0.5, 0.5, 1, 2, 3, 2, 1, 1, 1, 1, 1, 2, 3, 3, 3, 2, 1, 1, 0.5, 0.5, 0.5]
        hour = np.random.choice(range(24), p=np.array(hour_weights)/sum(hour_weights))
        time_purchase = f"{hour:02d}:{np.random.randint(0, 60):02d}:{np.random.randint(0, 60):02d}"
        
        origin = np.random.choice(origins)
        destination = np.random.choice([d for d in destinations if d != origin])
        
        # Return trip probability
        has_return = np.random.choice([True, False], p=[0.3, 0.7])
        
        # Price based on distance and demand
        base_price = np.random.uniform(30, 200)
        quantity = np.random.choice([1, 2, 3, 4], p=[0.5, 0.3, 0.15, 0.05])
        
        data.append({
            'nk_ota_localizer_id': f'ORDER_{i:06d}',
            'fk_contact': f'CLIENT_{np.random.randint(1, 5000):06d}',
            'date_purchase': random_date.strftime('%Y-%m-%d'),
            'time_purchase': time_purchase,
            'place_origin_departure': origin,
            'place_destination_departure': destination,
            'place_origin_return': destination if has_return else '0',
            'place_destination_return': origin if has_return else '0',
            'fk_departure_ota_bus_company': f'COMPANY_{np.random.randint(1, 10)}',
            'fk_return_ota_bus_company': f'COMPANY_{np.random.randint(1, 10)}' if has_return else '1',
            'gmv_success': base_price * quantity,
            'total_tickets_quantity_success': quantity
        })
    
    return pd.DataFrame(data)

# Load data
df = generate_sample_data()

# Convert date column
df['date_purchase'] = pd.to_datetime(df['date_purchase'])
df['hour'] = pd.to_datetime(df['time_purchase'], format='%H:%M:%S').dt.hour
df['day_of_week'] = df['date_purchase'].dt.day_name()
df['month'] = df['date_purchase'].dt.month
df['year'] = df['date_purchase'].dt.year

# Sidebar filters
st.sidebar.header("🧭 Filtros Interativos")

# Date filter
date_range = st.sidebar.date_input(
    "Período de Análise",
    value=(df['date_purchase'].min(), df['date_purchase'].max()),
    min_value=df['date_purchase'].min(),
    max_value=df['date_purchase'].max()
)

# Origin filter
origins = ['Todos'] + sorted(df['place_origin_departure'].unique().tolist())
selected_origin = st.sidebar.selectbox("Origem", origins)

# Destination filter
destinations = ['Todos'] + sorted(df['place_destination_departure'].unique().tolist())
selected_destination = st.sidebar.selectbox("Destino", destinations)

# Filter data
filtered_df = df[
    (df['date_purchase'] >= pd.to_datetime(date_range[0])) &
    (df['date_purchase'] <= pd.to_datetime(date_range[1]))
]

if selected_origin != 'Todos':
    filtered_df = filtered_df[filtered_df['place_origin_departure'] == selected_origin]

if selected_destination != 'Todos':
    filtered_df = filtered_df[filtered_df['place_destination_departure'] == selected_destination]

# Main metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        "Total de Tickets",
        f"{filtered_df['total_tickets_quantity_success'].sum():,}",
        delta=f"{filtered_df['total_tickets_quantity_success'].sum() - 1000:,}"
    )

with col2:
    st.metric(
        "Receita Total",
        f"R$ {filtered_df['gmv_success'].sum():,.2f}",
        delta=f"R$ {filtered_df['gmv_success'].sum() - 50000:,.2f}"
    )

with col3:
    st.metric(
        "Ticket Médio",
        f"R$ {filtered_df['gmv_success'].mean():,.2f}",
        delta=f"R$ {filtered_df['gmv_success'].mean() - 50:,.2f}"
    )

with col4:
    return_rate = (filtered_df['place_origin_return'] != '0').mean() * 100
    st.metric(
        "Taxa de Retorno",
        f"{return_rate:.1f}%",
        delta=f"{return_rate - 30:.1f}%"
    )

# Prediction section
st.header("📈 Previsão de Vendas de Passagens")

# Time series data
daily_sales = filtered_df.groupby('date_purchase').agg({
    'total_tickets_quantity_success': 'sum',
    'gmv_success': 'sum'
}).reset_index()

# Simple linear regression for prediction
if len(daily_sales) > 10:
    X = np.arange(len(daily_sales)).reshape(-1, 1)
    y = daily_sales['total_tickets_quantity_success'].values
    
    model = LinearRegression()
    model.fit(X, y)
    
    # Predict next 30 days
    future_X = np.arange(len(daily_sales), len(daily_sales) + 30).reshape(-1, 1)
    future_predictions = model.predict(future_X)
    
    # Create prediction dates
    last_date = daily_sales['date_purchase'].max()
    future_dates = pd.date_range(start=last_date + dt.timedelta(days=1), periods=30, freq='D')
    
    # Plot
    fig = go.Figure()
    
    # Historical data
    fig.add_trace(go.Scatter(
        x=daily_sales['date_purchase'],
        y=daily_sales['total_tickets_quantity_success'],
        mode='lines+markers',
        name='Vendas Históricas',
        line=dict(color='#3b2899')
    ))
    
    # Predictions
    fig.add_trace(go.Scatter(
        x=future_dates,
        y=future_predictions,
        mode='lines+markers',
        name='Previsão',
        line=dict(color='#ff4f63', dash='dash')
    ))
    
    fig.update_layout(
        title="Previsão de Vendas - Próximos 30 Dias",
        xaxis_title="Data",
        yaxis_title="Quantidade de Tickets",
        plot_bgcolor='#efefef'
    )
    
    st.plotly_chart(fig, use_container_width=True)

# Analysis section
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 Análise de Probabilidade de Compra")
    
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
        title="Distribuição de Probabilidade de Compra",
        color_discrete_sequence=['#ff4f63', '#3b2899', '#efefef']
    )
    st.plotly_chart(fig_prob, use_container_width=True)

with col2:
    st.subheader("📍 Destinos Mais Relevantes")
    
    # Top destinations
    top_destinations = filtered_df['place_destination_departure'].value_counts().head(5)
    
    fig_dest = px.bar(
        x=top_destinations.values,
        y=top_destinations.index,
        orientation='h',
        title="Top 5 Destinos Mais Procurados",
        color_discrete_sequence=['#ff4f63']
    )
    fig_dest.update_layout(
        xaxis_title="Quantidade de Tickets",
        yaxis_title="Destino"
    )
    st.plotly_chart(fig_dest, use_container_width=True)

# Peak hours analysis
st.subheader("🚨 Análise de Alta Demanda")

col1, col2 = st.columns(2)

with col1:
    # Hourly demand
    hourly_demand = filtered_df.groupby('hour')['total_tickets_quantity_success'].sum()
    
    fig_hourly = px.bar(
        x=hourly_demand.index,
        y=hourly_demand.values,
        title="Volume de Vendas por Hora",
        color_discrete_sequence=['#3b2899']
    )
    fig_hourly.update_layout(
        xaxis_title="Hora do Dia",
        yaxis_title="Quantidade de Tickets"
    )
    st.plotly_chart(fig_hourly, use_container_width=True)

with col2:
    # Weekly demand heatmap
    df_pivot = filtered_df.pivot_table(
        values='total_tickets_quantity_success',
        index='day_of_week',
        columns='hour',
        aggfunc='sum',
        fill_value=0
    )
    
    # Reorder days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    df_pivot = df_pivot.reindex(day_order)
    
    fig_heatmap = px.imshow(
        df_pivot.values,
        x=df_pivot.columns,
        y=df_pivot.index,
        title="Heatmap de Demanda por Dia e Hora",
        color_continuous_scale=['#efefef', '#ff4f63', '#3b2899']
    )
    st.plotly_chart(fig_heatmap, use_container_width=True)

# Additional insights
st.subheader("📊 Insights Adicionais")

col1, col2, col3 = st.columns(3)

with col1:
    # Monthly trends
    monthly_sales = filtered_df.groupby('month')['total_tickets_quantity_success'].sum()
    
    fig_monthly = px.line(
        x=monthly_sales.index,
        y=monthly_sales.values,
        title="Tendência Mensal",
        markers=True
    )
    fig_monthly.update_traces(line_color='#ff4f63')
    st.plotly_chart(fig_monthly, use_container_width=True)

with col2:
    # Top origins
    top_origins = filtered_df['place_origin_departure'].value_counts().head(5)
    
    fig_orig = px.pie(
        values=top_origins.values,
        names=top_origins.index,
        title="Top 5 Origens",
        color_discrete_sequence=['#ff4f63', '#3b2899', '#efefef', '#ffffff', '#ff4f63']
    )
    st.plotly_chart(fig_orig, use_container_width=True)

with col3:
    # Return vs One-way
    return_stats = filtered_df['place_origin_return'].apply(lambda x: 'Ida e Volta' if x != '0' else 'Só Ida').value_counts()
    
    fig_return = px.bar(
        x=return_stats.index,
        y=return_stats.values,
        title="Tipo de Viagem",
        color_discrete_sequence=['#3b2899', '#ff4f63']
    )
    st.plotly_chart(fig_return, use_container_width=True)

# Footer
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #3b2899;'>🚌 Click Predict Dashboard - Desenvolvido com Streamlit</div>",
    unsafe_allow_html=True
)