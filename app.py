import streamlit as st
import mysql.connector

# --- Conexão com MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="", # senha do banco de dados de vocês
    database="ecommerce_db" # nome do banco de dados de vocês
)
cursor = conn.cursor()

# --- Funções CRUD ---
def inserir_produto(produto_id, nome_produto, preco, tamanho, clean_product, marca_id):
    cursor.execute("""
        INSERT INTO produtos (produto_id, nome_produto, preco, tamanho, clean_product, marca_id)
        VALUES (%s, %s, %s, %s, %s, %s)
        ON DUPLICATE KEY UPDATE
            nome_produto = VALUES(nome_produto),
            preco = VALUES(preco),
            tamanho = VALUES(tamanho),
            clean_product = VALUES(clean_product),
            marca_id = VALUES(marca_id)
    """, (produto_id, nome_produto, preco, tamanho, clean_product, marca_id))
    conn.commit()

def consultar_produtos():
    cursor.execute("""
        SELECT p.produto_id, p.nome_produto, p.preco, p.tamanho, p.clean_product, m.nome_marca
        FROM produtos p
        LEFT JOIN marcas m ON p.marca_id = m.marca_id
    """)
    return cursor.fetchall()

def atualizar_preco(produto_id, novo_preco):
    cursor.execute("UPDATE produtos SET preco=%s WHERE produto_id=%s", (novo_preco, produto_id))
    conn.commit()

def deletar_produto(produto_id):
    cursor.execute("DELETE FROM produtos WHERE produto_id=%s", (produto_id,))
    conn.commit()


# --- Interface ---
st.title("📦 Sistema de Produtos - Ecommerce")

menu = st.sidebar.radio("Menu", ["Inserir", "Consultar", "Atualizar", "Deletar"])

if menu == "Inserir":
    st.subheader("Inserir Produto")
    produto_id = st.number_input("ID do Produto", min_value=1)
    nome_produto = st.text_input("Nome do Produto")
    preco = st.number_input("Preço (USD)", min_value=0.0, format="%.2f")
    tamanho = st.text_input("Tamanho")
    clean_product = st.checkbox("Produto Clean")
    marca_id = st.number_input("ID da Marca", min_value=1)

    if st.button("Salvar"):
        inserir_produto(produto_id, nome_produto, preco, tamanho, clean_product, marca_id)
        st.success("Produto inserido!")

elif menu == "Consultar":
    st.subheader("Lista de Produtos")
    dados = consultar_produtos()
    st.table(dados)

elif menu == "Atualizar":
    st.subheader("Atualizar Preço")
    produto_id = st.number_input("ID do Produto", min_value=1)
    novo_preco = st.number_input("Novo Preço (USD)", min_value=0.0, format="%.2f")
    if st.button("Atualizar"):
        atualizar_preco(produto_id, novo_preco)
        st.success("Preço atualizado!")

elif menu == "Deletar":
    st.subheader("Deletar Produto")
    produto_id = st.number_input("ID do Produto", min_value=1)
    if st.button("Deletar"):
        deletar_produto(produto_id)
        st.success("Produto deletado!")
