import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector

# --- Conexão com MySQL ---


def get_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="ecommerce_db"
    )

# ------------------------
# Funções CRUD Produtos
# ------------------------


def inserir_produto(nome_produto, preco, tamanho, clean_product, marca_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT COUNT(*) FROM marcas WHERE marca_id=%s", (marca_id,))
    if cursor.fetchone()[0] == 0:
        conn.close()
        return False
    cursor.execute("""
        INSERT INTO produtos (nome_produto, preco, tamanho, clean_product, marca_id)
        VALUES (%s, %s, %s, %s, %s)
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
    cursor.execute(
        "UPDATE produtos SET preco=%s WHERE produto_id=%s", (novo_preco, produto_id))
    conn.commit()
    conn.close()


def deletar_produto(produto_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM produtos WHERE produto_id=%s", (produto_id,))
    conn.commit()
    conn.close()

# ------------------------
# Funções CRUD Marcas
# ------------------------


def inserir_marca(nome_marca):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO marcas (nome_marca)
        VALUES (%s)
    """, (nome_marca,))
    conn.commit()
    conn.close()


def consultar_marcas():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM marcas")
    colunas = [desc[0] for desc in cursor.description]
    dados = cursor.fetchall()
    conn.close()
    return pd.DataFrame(dados, columns=colunas)


def atualizar_marca(marca_id, novo_nome):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE marcas SET nome_marca=%s WHERE marca_id=%s", (novo_nome, marca_id))
    conn.commit()
    conn.close()


def deletar_marca(marca_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM marcas WHERE marca_id=%s", (marca_id,))
    conn.commit()
    conn.close()


# ------------------------
# 📌 Streamlit App
# ------------------------
st.title("🛒 Sistema de E-commerce")
menu_principal = st.sidebar.radio(
    "Menu Principal", ["CRUD Produtos", "CRUD Marcas", "Gráficos"])

# ------------------------
# 📦 CRUD Produtos
# ------------------------
if menu_principal == "CRUD Produtos":
    st.header("📦 Gerenciamento de Produtos")
    opcao_produto = st.radio(
        "Ação", ["Inserir", "Consultar", "Atualizar", "Deletar"])

    if opcao_produto == "Inserir":
        nome = st.text_input("Nome do Produto")
        preco = st.number_input("Preço", min_value=0.0)
        tamanho = st.text_input("Tamanho")
        clean = st.selectbox("É Clean?", ["Sim", "Não"])
        marca_id = st.number_input("ID da Marca", min_value=1, step=1)
        if st.button("Inserir Produto"):
            ok = inserir_produto(nome, preco, tamanho, clean, marca_id)
            if ok:
                st.success("Produto inserido com sucesso!")
            else:
                st.error("Marca não encontrada.")

    elif opcao_produto == "Consultar":
        st.subheader("Lista de Produtos")
        df = consultar_produtos()
        st.dataframe(df)

    elif opcao_produto == "Atualizar":
        produto_id = st.number_input("ID do Produto", min_value=1, step=1)
        novo_preco = st.number_input("Novo Preço", min_value=0.0)
        if st.button("Atualizar"):
            atualizar_preco(produto_id, novo_preco)
            st.success("Preço atualizado com sucesso!")

    elif opcao_produto == "Deletar":
        produto_id = st.number_input("ID do Produto", min_value=1, step=1)
        if st.button("Deletar"):
            deletar_produto(produto_id)
            st.success("Produto deletado com sucesso!")

# ------------------------
# 🏷️ CRUD Marcas
# ------------------------
elif menu_principal == "CRUD Marcas":
    st.header("🏷️ Gerenciamento de Marcas")
    opcao_marca = st.radio(
        "Ação", ["Inserir", "Consultar", "Atualizar", "Deletar"])

    if opcao_marca == "Inserir":
        nome_marca = st.text_input("Nome da Marca")
        if st.button("Inserir Marca"):
            inserir_marca(nome_marca)
            st.success("Marca inserida com sucesso!")

    elif opcao_marca == "Consultar":
        st.subheader("Lista de Marcas")
        df = consultar_marcas()
        st.table(df)

    elif opcao_marca == "Atualizar":
        marca_id = st.number_input("ID da Marca", min_value=1, step=1)
        novo_nome = st.text_input("Novo Nome da Marca")
        if st.button("Atualizar"):
            atualizar_marca(marca_id, novo_nome)
            st.success("Marca atualizada com sucesso!")

    elif opcao_marca == "Deletar":
        marca_id = st.number_input("ID da Marca", min_value=1, step=1)
        if st.button("Deletar"):
            deletar_marca(marca_id)
            st.success("Marca deletada com sucesso!")

# ------------------------
# 📊 Gráficos
# ------------------------
elif menu_principal == "Gráficos":
    st.header("📊 Análise de Produtos")
    df = consultar_produtos()

    if df.empty:
        st.info("Nenhum produto cadastrado para gerar gráficos.")
    else:
        # 1️⃣ Quantidade de produtos por marca (Top 10)
        st.markdown("**Quantidade de produtos por marca (Top 10)**")
        qtd_marca = df.groupby("nome_marca")["produto_id"].count(
        ).sort_values(ascending=False).head(10)
        fig1, ax1 = plt.subplots()
        qtd_marca.plot(kind="bar", ax=ax1, color="#ff99cc")
        ax1.set_ylabel("Quantidade")
        ax1.set_xlabel("Marca")
        ax1.set_title("Produtos por Marca (Top 10)")
        st.pyplot(fig1)

        # 2️⃣ Preço médio por marca (Top 10)
        st.markdown("**Preço médio por marca (Top 10)**")
        preco_medio = df.groupby("nome_marca")["preco"].mean(
        ).sort_values(ascending=False).head(10)
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

