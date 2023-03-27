# imports
import requests
import psycopg2
import random
import time
import pandas as pd
from datetime import datetime
import streamlit as st
from bs4 import BeautifulSoup


class Data:
    # ===================================================
    # Métodos do banco (CRUD)
    # ===================================================
    # Conecta no banco
    def db_connection(self):
        """Método para conexão no banco"""
        con = psycopg2.connect(
            host="localhost", database="ats", user="almir", password="almir"
        )
        return con

    # Cria a tabela
    def create_table(self):
        """Cria a tabela no banco de dados"""
        create = """
            CREATE TABLE supervisory (
                id SERIAL PRIMARY KEY,
                Data VARCHAR(255) NOT NULL,
                Caldeira NUMERIC NOT NULL,
                Pneumatico DECIMAL NOT NULL,
                Rotacao DECIMAL NOT NULL,
                Aquecimento DECIMAL NOT NULL,
                Resfriamento DECIMAL NOT NULL,
                Pressao DECIMAL NOT NULL,
                Umidade DECIMAL NOT NULL,
                Velocidade DECIMAL NOT NULL,
                CLP VARCHAR(255) NOT NULL
            )
            """

        con = None
        try:
            con = self.db_connection()
            cursor = con.cursor()
            cursor.execute("DROP TABLE IF EXISTS supervisory")
            cursor.execute(create)
            cursor.close()
            con.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()

    # Insere dados
    def insert_db(self, df):
        """Insere dados na tabela"""
        con = None
        try:
            con = self.db_connection()

            # Setting auto commit false
            con.autocommit = True
            cursor = con.cursor()

            # df = formata_dados_painel()

            # Preparing SQL queries to INSERT a record into the database.
            cursor.execute(
                f"""
            INSERT INTO supervisory(            
                Data,
                Caldeira,
                Pneumatico,
                Rotacao,
                Aquecimento,
                Resfriamento,
                Pressao,
                Umidade,
                Velocidade,
                CLP)
                VALUES(
                    \'{df.index.values[0]}\',
                    {df.iloc[0,0]},
                    {df.iloc[0,1]},
                    {df.iloc[0,2]},
                    {df.iloc[0,3]},
                    {df.iloc[0,4]},
                    {df.iloc[0,5]},
                    {df.iloc[0,6]},
                    {df.iloc[0,7]},
                    \'{df.iloc[0,8]}\')
            """
            )

            # Commit your changes in the database
            con.commit()
            # print("Records inserted........")

            # Closing the connection
            con.close()
            cursor.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()

    # Pega dados
    def get_data_db(self):
        """Pega os dados da tabela"""
        con = None
        try:
            con = self.db_connection()
            # Setting auto commit false
            con.autocommit = True
            cursor = con.cursor()

            # Retrieving data
            cursor.execute("""SELECT * from supervisory""")

            # Fetching all rows from the table
            result = cursor.fetchall()
            column_names = [desc[0] for desc in cursor.description]

            # Commit your changes in the database
            con.commit()

            # Closing the connection
            con.close()
        except (Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if con is not None:
                con.close()

        return result, column_names

    # ===================================================
    # Métodos do painel (conexão e dados)
    # ===================================================
    # Retorna a feature hora e a tabela do site
    def conecta_painel(self):
        """Método para conectar no painel"""

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
    def le_dados_painel(self, hora, tbody):
        """Método para leitura do painel"""

        colunas = list()
        linhas = list()

        for tr in tbody.find_all("tr"):
            td = tr.find_all("td")[0].text
            colunas.append(td)

        for tr in tbody.find_all("tr"):
            td = tr.find_all("td")[1].text
            td = float(td) + random.randint(-5, 5)
            linhas.append(td)

        colunas.append("CLP")
        linhas.append("CLP_" + str(random.randint(1, 3)))

        linhas = [linhas]

        dataframe = pd.DataFrame(linhas, columns=colunas, index=[hora])

        return dataframe

    # Pega os dados do painel e grava no banco de dados
    def painel_para_bd(self):
        for i in range(7200):
            # Conecta no painel e pega os dados
            a, b = self.conecta_painel()
            # Converte os dados para formato dataframe
            df = self.le_dados_painel(a, b)
            # Insere os dados do dataframe no banco de dados
            self.insert_db(df)
            time.sleep(1)

    # Formata os dados do painel
    def formata_dados_painel(self):
        """Método que formata os dados do painel"""

        # Dá um select no banco e armazena em um dataframe
        result, cols = self.get_data_db()
        df = pd.DataFrame(result, columns=cols)
        df.data = pd.to_datetime(df.data)

        return df
