import streamlit as st
import mysql.connector

# --- Conexão com MySQL ---
conn = mysql.connector.connect(
    host="localhost",
    user="root", 
    password="", # senha do banco de dados de vocês
    database="projetosql" # nome do banco de dados de vocês
)
cursor = conn.cursor()

# --- Funções CRUD ---
def inserir_produto(product_id, product_name, brand_id, brand_name, loves_count, revenues, rating, reviews, price_usd, primary_category, secondary_category, tertiary_category):
    cursor.execute("""
        INSERT INTO product_info_ 
        (product_id, product_name, brand_id, brand_name, loves_count, revenues, rating, reviews, price_usd, primary_category, secondary_category, tertiary_category) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (product_id, product_name, brand_id, brand_name, loves_count, revenues, rating, reviews, price_usd, primary_category, secondary_category, tertiary_category))
    conn.commit()

def consultar_produtos():
    cursor.execute("SELECT * FROM product_info_")
    return cursor.fetchall()

def atualizar_preco(product_id, novo_preco):
    cursor.execute("UPDATE product_info_ SET price_usd=%s WHERE product_id=%s", (novo_preco, product_id))
    conn.commit()

def deletar_produto(product_id):
    cursor.execute("DELETE FROM product_info_ WHERE product_id=%s", (product_id,))
    conn.commit()

# --- Interface ---
st.title("📦 Sistema de Produtos")

menu = st.sidebar.radio("Menu", ["Inserir", "Consultar", "Atualizar", "Deletar"])

if menu == "Inserir":
    st.subheader("Inserir Produto")
    product_id = st.number_input("ID do Produto", min_value=1)
    product_name = st.text_input("Nome do Produto")
    brand_id = st.number_input("ID da Marca", min_value=1)
    brand_name = st.text_input("Nome da Marca")
    loves_count = st.number_input("Loves Count", min_value=0)
    revenues = st.number_input("Receita", min_value=0.0, format="%.2f")
    rating = st.number_input("Rating", min_value=0.0, max_value=5.0, format="%.2f")
    reviews = st.number_input("Número de Reviews", min_value=0)
    price_usd = st.number_input("Preço (USD)", min_value=0.0, format="%.2f")
    primary_category = st.text_input("Categoria Principal")
    secondary_category = st.text_input("Categoria Secundária")
    tertiary_category = st.text_input("Categoria Terciária")

    if st.button("Salvar"):
        inserir_produto(product_id, product_name, brand_id, brand_name, loves_count, revenues, rating, reviews, price_usd, primary_category, secondary_category, tertiary_category)
        st.success("Produto inserido!")

elif menu == "Consultar":
    st.subheader("Lista de Produtos")
    dados = consultar_produtos()
    st.table(dados)

elif menu == "Atualizar":
    st.subheader("Atualizar Preço")
    product_id = st.number_input("ID do Produto", min_value=1)
    novo_preco = st.number_input("Novo Preço (USD)", min_value=0.0, format="%.2f")
    if st.button("Atualizar"):
        atualizar_preco(product_id, novo_preco)
        st.success("Preço atualizado!")

elif menu == "Deletar":
    st.subheader("Deletar Produto")
    product_id = st.number_input("ID do Produto", min_value=1)
    if st.button("Deletar"):
        deletar_produto(product_id)
        st.success("Produto deletado!")
