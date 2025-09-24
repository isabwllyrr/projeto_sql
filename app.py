import streamlit as st
import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt

# --- CSS para tema rosinha ---
st.markdown("""
    <style>
    /* Fundo geral */
    .stApp {
        background-color: #ffe6f0;
    }
    /* Cabeçalho */
    .css-18e3th9 {
        background-color: #ffcce6;
        color: #660033;
    }
    /* Barras laterais */
    .css-1d391kg {
        background-color: #ffb3d9;
        color: #660033;
    }
    /* Botões */
    div.stButton > button {
        background-color: #ff99cc;
        color: white;
        border-radius: 10px;
        border: none;
    }
    div.stButton > button:hover {
        background-color: #ff66b3;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# --- Conexão com MySQL ---
def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="36353658",
        database="ecommerce_db"
    )

# --- Funções CRUD ---
def inserir_produto(nome_produto, preco, tamanho, clean_product, marca_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM marcas WHERE marca_id=%s", (marca_id,))
    if cursor.fetchone()[0] == 0:
        conn.close()
        return False
    cursor.execute("""
        INSERT INTO produtos (nome_produto, preco, tamanho, clean_product, marca_id)
        VALUES (%s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nome_produto = VALUES(nome_produto),
            preco = VALUES(preco),
            tamanho = VALUES(tamanho),
            clean_product = VALUES(clean_product),
            marca_id = VALUES(marca_id)
    """, (nome_produto, preco, tamanho, clean_product, marca_id))
    conn.commit()
    conn.close()
    return True

def consultar_produtos():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT p.produto_id, p.nome_produto, p.preco, p.tamanho, p.clean_product, m.nome_marca
        FROM produtos p
        LEFT JOIN marcas m ON p.marca_id = m.marca_id
    """)
    colunas = [desc[0] for desc in cursor.description]
    dados = cursor.fetchall()
    conn.close()
    return pd.DataFrame(dados, columns=colunas)

def atualizar_preco(produto_id, novo_preco):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE produtos SET preco=%s WHERE produto_id=%s", (novo_preco, produto_id))
    conn.commit()
    conn.close()

def deletar_produto(produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE produto_id=%s", (produto_id,))
    conn.commit()
    conn.close()


# --- Interface Streamlit ---
st.title("📦 Sistema de Produtos - Ecommerce")
menu = st.sidebar.radio("Menu", ["Inserir", "Consultar", "Atualizar", "Deletar", "Gráficos"])

if menu == "Inserir":
    st.subheader("Inserir Produto")
    nome_produto = st.text_input("Nome do Produto")
    preco = st.number_input("Preço (USD)", min_value=0.0, format="%.2f")
    tamanho = st.text_input("Tamanho")
    clean_product = st.checkbox("Produto Clean")
    marca_id = st.number_input("ID da Marca", min_value=1)

    if st.button("Salvar"):
        sucesso = inserir_produto(nome_produto, preco, tamanho, clean_product, marca_id)
        if sucesso:
            st.success("Produto inserido com sucesso!")
        else:
            st.error(f"Marca com ID {marca_id} não existe. Crie a marca primeiro.")

elif menu == "Consultar":
    st.subheader("Lista de Produtos")
    df = consultar_produtos()
    if df.empty:
        st.info("Nenhum produto cadastrado.")
    else:
        st.table(df)

elif menu == "Atualizar":
    st.subheader("Atualizar Preço")
    produto_id = st.number_input("ID do Produto", min_value=1)
    novo_preco = st.number_input("Novo Preço (USD)", min_value=0.0, format="%.2f")
    if st.button("Atualizar"):
        atualizar_preco(produto_id, novo_preco)
        st.success("Preço atualizado com sucesso!")

elif menu == "Deletar":
    st.subheader("Deletar Produto")
    produto_id = st.number_input("ID do Produto", min_value=1)
    if st.button("Deletar"):
        deletar_produto(produto_id)
        st.success("Produto deletado com sucesso!")

elif menu == "Gráficos":
    st.subheader("📊 Análise de Produtos")
    df = consultar_produtos()
    
    if df.empty:
        st.info("Nenhum produto cadastrado para gerar gráficos.")
    else:
        # 1️⃣ Quantidade de produtos por marca (Top 10)
        st.markdown("**Quantidade de produtos por marca (Top 10)**")
        qtd_marca = df.groupby("nome_marca")["produto_id"].count().sort_values(ascending=False).head(10)
        fig1, ax1 = plt.subplots()
        qtd_marca.plot(kind="bar", ax=ax1, color="#ff99cc")
        ax1.set_ylabel("Quantidade")
        ax1.set_xlabel("Marca")
        ax1.set_title("Produtos por Marca (Top 10)")
        st.pyplot(fig1)

        # 2️⃣ Preço médio por marca (Top 10)
        st.markdown("**Preço médio por marca (Top 10)**")
        preco_medio = df.groupby("nome_marca")["preco"].mean().sort_values(ascending=False).head(10)
        fig2, ax2 = plt.subplots()
        preco_medio.plot(kind="bar", ax=ax2, color="#ff66b3")
        ax2.set_ylabel("Preço médio (USD)")
        ax2.set_xlabel("Marca")
        ax2.set_title("Preço Médio por Marca (Top 10)")
        st.pyplot(fig2)

        # 3️⃣ Distribuição de produtos Clean
        st.markdown("**Produtos Clean vs Não Clean**")
        clean_counts = df["clean_product"].value_counts()
        fig3, ax3 = plt.subplots()
        clean_counts.plot(kind="pie", labels=["Não Clean", "Clean"], autopct="%1.1f%%",
                          startangle=90, colors=["#ffb3d9", "#ff66b3"])
        ax3.set_ylabel("")
        ax3.set_title("Distribuição de Produtos Clean")
        st.pyplot(fig3)

