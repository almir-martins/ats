# ===================================================
# import das bibliotecas
# ===================================================
import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
import time
import threading
from bs4 import BeautifulSoup
from datetime import datetime
from get_data import Data

data = Data()

threading.Thread(target=data.painel_para_bd).start()


def recarrega():
    df = data.formata_dados_painel()

    # TODO Configurando o df novamente
    df.set_index(keys="data", inplace=True, drop=True)
    df.drop(columns="id", inplace=True)
    for col in df.columns[:-1]:
        df[col] = df[col].astype("float")

    return df


# ===================================================
# Layout da página
# ===================================================
st.set_page_config(
    page_title="Real-Time Supervisory Control",
    page_icon="✅",
    layout="wide",
)


# Barra lateral
with st.sidebar:
    st.title("Controle supervisório")
    st.text(
        """
        Este projeto é um controle
        supervisório para centrais
        e painéis CLPs.
        """
    )

st.header("ATS Supervisory Control")

# =========================
st.write("Buscar dados do painel")

# creating a single-element container
placeholder = st.empty()
df = pd.DataFrame()
with st.spinner("Carregando o sistema..."):
    time.sleep(1.5)
    st.success("Sistema iniciado!")

# Símbolo e mensagem de "Carregando..."
# with st.spinner("Carregando dados..."):
# data = Data()
# df = data.formata_dados_painel()

# # TODO Configurando o df novamente
# df.set_index(keys="data", inplace=True, drop=True)
# df.drop(columns="id", inplace=True)
# for col in df.columns[:-1]:
#     df[col] = df[col].astype("float")


# near real-time / live feed simulation
for seconds in range(50):  # 7200
    # TODO  pegar as linhas novas do banco e inserir no df
    df = recarrega()
    # df = df.tail()

    # Apaga os elementos
    with placeholder.container():
        st.dataframe(data=df.tail())
        if "df" not in st.session_state:
            st.session_state["df"] = df

        st.write("-----------------------------------")
        st.markdown("### Variáveis")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric(df.columns[0], df.iloc[-1, 0], df.iloc[-1, 0] - df.iloc[-2, 0])
        col2.metric(df.columns[1], df.iloc[-1, 1], df.iloc[-1, 1] - df.iloc[-2, 1])
        col3.metric(df.columns[2], df.iloc[-1, 2], df.iloc[-1, 2] - df.iloc[-2, 2])
        col4.metric(df.columns[3], df.iloc[-1, 3], df.iloc[-1, 3] - df.iloc[-2, 3])
        col1.metric(df.columns[4], df.iloc[-1, 4], df.iloc[-1, 4] - df.iloc[-2, 4])
        col2.metric(df.columns[5], df.iloc[-1, 5], df.iloc[-1, 5] - df.iloc[-2, 5])
        col3.metric(df.columns[6], df.iloc[-1, 6], df.iloc[-1, 6] - df.iloc[-2, 6])
        col4.metric(df.columns[7], df.iloc[-1, 7], df.iloc[-1, 7] - df.iloc[-2, 7])

        st.write("-----------------------------------")
        st.markdown("### Gráficos")
        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            fig = px.line(
                data_frame=df,
                x=df.index,
                y=df.columns[0],
                labels={
                    "index": "",
                    df.columns[0]: "Valor",
                    "clp": "CLPs",
                },
                title="Dados da Caldeira",
            )
            st.write(fig)

        with fig_col2:
            fig2 = px.line(
                data_frame=df,
                x=df.index,
                y=df.columns[1],
                labels={
                    "index": "",
                    df.columns[1]: "Valor",
                    "clp": "CLPs",
                },
                title="Dados de Balsas/MA   ",
            )
            st.write(fig2)

        fig_col3, fig_col4 = st.columns(2)
        with fig_col3:
            fig = px.line(
                data_frame=df,
                y=df.columns[2],
                color="clp",
                labels={
                    "index": "",
                    df.columns[2]: "Valor",
                    "clp": "CLPs",
                },
                title="Região integrada 1",
            )
            st.write(fig)

        with fig_col4:
            fig = px.line(
                data_frame=df,
                x=df.index,
                y=df.columns[1],
                color="clp",
                markers=True,
                # text=df.index.time,
                labels={
                    "index": "",
                    df.columns[1]: "Valor",
                    "clp": "CLPs",
                },
                title="Região integrada 2",
            )
            st.write(fig)

        time.sleep(1.5)
