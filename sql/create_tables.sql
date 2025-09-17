-- para testar , usa o dbivier /mysql workbench ou via terminal com o comando : mysql -u root -p < create_tables.sql


-- Criar banco de dados
CREATE DATABASE IF NOT EXISTS ecommerce_db;
USE ecommerce_db;

-- Tabela de marcas
CREATE TABLE IF NOT EXISTS marcas (
    marca_id INT PRIMARY KEY AUTO_INCREMENT,
    nome_marca VARCHAR(255) UNIQUE NOT NULL
);

-- Tabela de produtos
CREATE TABLE IF NOT EXISTS produtos (
    produto_id INT PRIMARY KEY AUTO_INCREMENT,
    nome_produto VARCHAR(255) NOT NULL,
    preco DECIMAL(10,2),
    tamanho VARCHAR(50),
    clean_product BOOLEAN,
    marca_id INT,
    FOREIGN KEY (marca_id) REFERENCES marcas(marca_id)
);

-- Tabela de categorias
CREATE TABLE IF NOT EXISTS categorias (
    categoria_id INT PRIMARY KEY AUTO_INCREMENT,
    nome_categoria VARCHAR(255) UNIQUE NOT NULL
);

-- Relacionamento produto ↔ categoria (N:N)
CREATE TABLE IF NOT EXISTS produto_categorias (
    produto_id INT,
    categoria_id INT,
    PRIMARY KEY (produto_id, categoria_id),
    FOREIGN KEY (produto_id) REFERENCES produtos(produto_id) ON DELETE CASCADE,
    FOREIGN KEY (categoria_id) REFERENCES categorias(categoria_id) ON DELETE CASCADE
);

-- Tabela de avaliações
CREATE TABLE IF NOT EXISTS avaliacoes (
    avaliacao_id INT PRIMARY KEY AUTO_INCREMENT,
    produto_id INT NOT NULL,
    n_reviews INT,
    n_loves INT,
    review_score DECIMAL(3,2),
    FOREIGN KEY (produto_id) REFERENCES produtos(produto_id) ON DELETE CASCADE
);

