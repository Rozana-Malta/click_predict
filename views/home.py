import streamlit as st

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

    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🚌 Click Predict Dashboard</h1>
        <p>Predição de Tickets de Passagens com Base em Dados Históricos</p>
    </div>
    """, unsafe_allow_html=True)

    # Apresentação do Projeto desenvolvido pelo grupo da faculdade
    st.markdown("""
    <div class="metric-card">
        <h2>Protótipo da solução proposta</h2>
        <p>Este projeto foi desenvolvido por alunos do curso Tecnólogo em Ciências de Dados da Faculdade de Informática e Administração Paulista (FIAP) como parte das atividades acadêmicas. 
        O objetivo é demonstrar o protótipo de um dashboard para a predição de tickets de passagens utilizando dados históricos.</p>
        <p>O dashboard foi construído com o Streamlit e utiliza técnicas de análise de dados e predição para fornecer insights sobre vendas de passagens rodoviárias pela ClickBus.</p>
        <p>O projeto inclui a análise de dados históricos de vendas de passagens, permitindo insights sobre o comportamento dos clientes e previsões de demanda futura.</p>
        <p>Empresa parceira: <strong>ClickBus</strong></p>
        <p>Desenvolvedores: <strong>Ana Paula Bacelar, Igor Cardoso, Murilo Jucá, Rozana Malta e Ruan Garcia.</strong></p>
        <p>Tutor da turma: <strong>Prof. Dr. Leandro Romualdo da Silva</strong></p>
    </div>
    """, unsafe_allow_html=True)

    # espaço
    st.markdown("<br>", unsafe_allow_html=True)

    # Orienta o usuário a navegar pelo menu lateral

    st.info("""
    Use o menu lateral para navegar pelas seções:
    
    **Análises** – Explore dados históricos sobre volume de compras, horários de pico, destinos mais procurados e padrões de demanda ao longo da semana.

    **Previsões** – Acesse projeções futuras de vendas de tickets, identificação de períodos críticos e estimativas de receita, com apoio de modelos de _machine learning_.

    Utilize os filtros interativos para personalizar as visualizações de acordo com datas, regiões ou trechos específicos.
    Aproveite os _insights_ para apoiar decisões mais inteligentes e antecipar a demanda com eficiência!""", icon="ℹ️")


