import streamlit as st
import streamlit_antd_components as sac

from views import home
from views import analises
from views import previsoes

# Configure page
st.set_page_config(
    page_title="Click Predict",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

with st.sidebar:
    pagina_selecionada = sac.menu(
        [
            sac.MenuItem("Página Inicial", icon="house"),
            sac.MenuItem("Análises", icon="bar-chart"),
            sac.MenuItem("Previsões", icon="graph-up-arrow"),
#            sac.MenuItem(
#                "Projetos",
#                icon="bar-chart",
#                children=[
#                    sac.MenuItem("Análises de Dados", icon="chevron-right"),
#                    #sac.MenuItem("Previsões", icon="chevron-right"),
#                    #sac.MenuItem("Machine Learning", icon="chevron-right"),
#                    #sac.MenuItem("Deep Learning", icon="chevron-right"),
#                    #sac.MenuItem("IA", icon="chevron-right"),
#                ],
#            ),
        ],
    )

page_mapping = {
        "Página Inicial": home.page,
        "Análises": analises.page,
        "Previsões": previsoes.page,
    }

page_mapping[pagina_selecionada]()