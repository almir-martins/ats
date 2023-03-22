# import das bibliotecas
import psycopg2
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import random
import time
from bs4 import BeautifulSoup
from datetime import datetime


# Retorna a feature hora e a tabela do site
def conecta_painel():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/110.0"
    }

    url = "https://www.horariodebrasilia.org/"
    url2 = "https://www.canalrural.com.br/cotacao/soja/"

    hora_site = requests.get(url, headers=headers)
    soup_hora = BeautifulSoup(hora_site.content, "html.parser")
    tempo = soup_hora.find("p", id="relogio")

    preco_site = requests.get(url2, headers=headers)
    soup_preco = BeautifulSoup(preco_site.content, "html.parser")

    tabela = soup_preco.find("tbody")

    # tempo = time.strftime("%H:%M:%S", datetime.now())
    tempo = datetime.now()
    # date_str = str(datetime.now())
    # tempo = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S.%f")

    return tempo, tabela


# Retorna a tabela do site como dataframe
def le_dados_painel(hora, tbody):
    colunas = list()
    linhas = list()

    for tr in tbody.find_all("tr"):
        td = tr.find_all("td")[0].text
        colunas.append(td)

    for tr in tbody.find_all("tr"):
        td = tr.find_all("td")[1].text
        td = float(td) + random.randint(-50, 50)
        linhas.append(td)

    colunas.append("CLP")
    linhas.append("CLP_" + str(random.randint(1, 3)))

    linhas = [linhas]

    dataframe = pd.DataFrame(linhas, columns=colunas, index=[hora])

    return dataframe


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

# Símbolo e mensagem de "Carregando..."
with st.spinner("Carregando dados..."):
    a, b = conecta_painel()
    df = le_dados_painel(a, b)
    for i in range(1):
        time.sleep(1)
        a, b = conecta_painel()
        df2 = le_dados_painel(a, b)
        df = pd.concat([df, df2])


# near real-time / live feed simulation
for seconds in range(30):
    a, b = conecta_painel()
    df2 = le_dados_painel(a, b)
    df = pd.concat([df, df2])

    # Apaga os elementos
    with placeholder.container():
        st.dataframe(data=df)
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
        st.markdown("<p style='text-align: center;'>Text_content</p>")
        st.markdown("### Gráficos")
        # create two columns for charts
        fig_col1, fig_col2 = st.columns(2)

        with fig_col1:
            fig = px.line(
                data_frame=df,
                x=df.index,
                y="Dourados (MS)",
                labels={
                    "index": "",
                    "Dourados (MS)": "Valor",
                    "CLP": "CLPs",
                },
                title="Dados de Dourados/MS",
            )
            st.write(fig)

        with fig_col2:
            fig2 = px.line(
                data_frame=df,
                x=df.index,
                y="Balsas (MA)",
                labels={
                    "index": "",
                    "Balsas (MA)": "Valor",
                    "CLP": "CLPs",
                },
                title="Dados de Balsas/MA   ",
            )
            st.write(fig2)

        fig_col3, fig_col4 = st.columns(2)
        with fig_col3:
            fig = px.line(
                data_frame=df,
                y="Dourados (MS)",
                color="CLP",
                labels={
                    "index": "",
                    "Dourados (MS)": "Valor",
                    "CLP": "CLPs",
                },
                title="Região integrada 1",
            )
            st.write(fig)

        with fig_col4:
            fig = px.line(
                data_frame=df,
                x=df.index,
                y="Dourados (MS)",
                color="CLP",
                markers=True,
                # text=df.index.time,
                labels={
                    "index": "",
                    "Dourados (MS)": "Valor",
                    "CLP": "CLPs",
                },
                title="Região integrada 2",
            )
            st.write(fig)

        time.sleep(1)
