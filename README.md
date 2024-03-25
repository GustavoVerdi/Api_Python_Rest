## PIP INSTALL
    pip install flask
    pip install sqlalchemy
    pip install requests

## CREATE TABLE
    CREATE TABLE tempresa (
        id SERIAL PRIMARY KEY,
        cnpj VARCHAR NOT NULL UNIQUE,
        situacao VARCHAR,
        nome VARCHAR,
        tipo VARCHAR,
        fantasia VARCHAR,
        uf VARCHAR(2),
        municipio VARCHAR,
        logradouro VARCHAR,
        natureza_juridica VARCHAR,
        porte VARCHAR,
        telefone VARCHAR,
        atividade_principal TEXT,
        numero_funcionarios INTEGER,
        faturamento_anual INTEGER,
        vendedor_responsavel VARCHAR
    );
