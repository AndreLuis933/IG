[![Python application](https://github.com/AndreLuis933/IG/actions/workflows/daily-request.yml/badge.svg)](https://github.com/AndreLuis933/IG/actions/workflows/daily-request.yml)
![Docker support](https://img.shields.io/badge/docker-supported-blue)
[![License](https://img.shields.io/github/license/AndreLuis933/IG)](LICENSE)

# 🛒 Irmãos Gonçalves Scraper

Automatize o monitoramento de preços do maior supermercado de Rondônia! Este projeto realiza scraping diário do site [Irmãos Gonçalves](https://www.irmaosgoncalves.com.br/), armazena os dados em banco de dados relacional e oferece visualização interativa via Streamlit.

> 💻 **Veja a visualização online:**  
> [https://view-ig.streamlit.app/](https://view-ig.streamlit.app/)

---

## Índice

1. [Funcionalidades](#funcionalidades)
2. [Visualização dos Dados](#visualizacao-dos-dados)
3. [Estrutura do Projeto](#estrutura-do-projeto)
4. [Sobre a infraestrutura em nuvem](#sobre-a-infraestrutura-em-nuvem)
5. [Otimização e volume de dados](#otimizacao-e-volume-de-dados)
6. [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados)
7. [Pré-requisitos para rodar localmente](#pre-requisitos-para-rodar-localmente)
8. [Instalação](#instalacao)
9. [Configuração](#configuracao)
10. [Como Usar](#como-usar)
11. [Licença](#licenca)
12. [Contato](#contato)

---

## ✨ Funcionalidades

- 🕸️ Scraping automatizado do site do Irmãos Gonçalves
- 📦 Extração de nome, preço, categoria, imagem e link dos produtos
- ☁️ Armazenamento dos dados em banco PostgreSQL
- 📊 Visualização da evolução de preços por categoria via Streamlit
- 🐳 Deploy simplificado com Docker e Fly.io
- 🔄 Automação diária via GitHub Actions

---

## 📊 Visualização dos Dados

Veja abaixo exemplos de como os dados podem ser visualizados na aplicação Streamlit:

![Dashboard Geral](docs/images/dashboard_geral.png)  
_Dashboard principal mostrando a evolução dos preços médios ao longo do tempo._

![Filtro por Cidade](docs/images/Filtros.png)  
_Menu lateral com filtros dinâmicos para cidade, nome, preço, categoria e data._

![Gráfico por Categoria](docs/images/grafico_categoria.png)  
_Gráfico comparativo da evolução de preços por categoria de produto._

![Tabela de Dados](docs/images/tabela_dados.png)  
_Tabela interativa com todos os dados brutos, incluindo opção de download em CSV._

---

## 📁 Estrutura do Projeto

```plaintext
IRMAOS-GONCALVES-SCRAPER/
├── .github/
├── scraper/
│   ├── ...
├── view/
│   ├── ...
├── .dockerignore
├── .env
├── .gitignore
├── LICENSE
├── README.md
```

- **scraper/**: Scripts de coleta e processamento de dados
- **view/**: Aplicação Streamlit para visualização
- **.github/**: Workflows de automação

---

## ☁️ Sobre a infraestrutura em nuvem

Este projeto foi projetado para rodar diariamente de forma **totalmente automatizada e otimizada para custos** em ambiente de nuvem. Utilizamos [GitHub Actions](https://github.com/features/actions) para orquestração, [Fly.io](https://fly.io/) para hospedar os containers Docker do scraper (com desligamento automático da máquina após a execução, o que permite que o projeto rode **sem custo financeiro dentro do plano gratuito**), [Supabase](https://supabase.com/) para armazenamento dos dados e [Streamlit Cloud](https://streamlit.io/cloud) para a visualização online.

Essas configurações permitem que o scraping, armazenamento e visualização dos dados ocorram de forma autônoma, eficiente e sem intervenção manual, garantindo a atualização contínua dos dados com custo zero.

No entanto, toda a documentação deste README é focada no uso local, para facilitar a replicação e testes por qualquer pessoa. Se você tiver interesse em saber mais sobre a automação e deploy em nuvem, entre em contato.

---

## 📈 Otimização e volume de dados

Para garantir eficiência e evitar custos desnecessários no Supabase, o projeto adota estratégias avançadas de compressão e agrupamento dos dados históricos. Em vez de registrar uma linha para cada dia, cada produto e cada cidade, os dados são armazenados em intervalos contínuos de tempo e, quando possível, agrupados por cidade. Isso reduz drasticamente o volume de registros, mantendo o histórico completo e detalhado para análise.

O monitoramento está em operação desde **26/04/2025**, cobrindo atualmente **11 mercados** (lojas) e cerca de **18.000 produtos por mercado**. Graças a essas otimizações, mesmo com o crescimento contínuo dos dados, o projeto se mantém sustentável e eficiente. Atualmente, a maior tabela (`disponibilidade_cidades`, que monitora a disponibilidade diária de cada produto em cada loja) já conta com mais de **823 mil registros**.

> Para detalhes técnicos sobre a estrutura das tabelas e regras de agrupamento, consulte a seção [Estrutura do Banco de Dados](#estrutura-do-banco-de-dados).
<details>
<summary>🗺️ Ver cidades e identificação das lojas monitoradas</summary>

**Cidades e lojas monitoradas:**

- Ariquemes
- Cacoal
- Jaru
- Ouro Preto do Oeste
- Rolim de Moura
- Vilhena

**Ji-Paraná**
- Ji-Parana 1: DOIS DE ABRIL — Av. Mal. Rondon c/ Rua dos Mineiros, nº 1793, CEP: 76.900-137
- Ji-Parana 2: CAFEZINHO — Av. das Seringueiras, nº 1201, CEP: 76.913-112

**Porto Velho**
- Porto Velho 1: AV. SETE DE SETEMBRO (N.S. DAS GRAÇAS) — CEP: 76.804-142
- Porto Velho 2: AV. AMAZONAS (TIRADENTES) — CEP: 76.824-652
- Porto Velho 3: AVENIDA JATUARANA (CALADINHO) — CEP: 76.808-110

</details>
---

## 🗄️ Estrutura do Banco de Dados

O projeto utiliza um banco relacional com as seguintes tabelas principais:

<details>
<summary>Clique para ver o diagrama Mermaid</summary>

```mermaid
erDiagram
    PRODUTOS ||--o| IMAGENS : tem
    PRODUTOS ||--o{ HISTORICO_PRECOS : possui
    PRODUTOS ||--o{ DISPONIBILIDADE_CIDADES : possui

    CIDADES ||--o{ HISTORICO_PRECOS : possui
    CIDADES ||--o{ DISPONIBILIDADE_CIDADES : possui

    PRODUTOS {
        int id PK
        string nome
        string link
        string categoria
        date data_atualizacao
    }

    IMAGENS {
        int produto_id PK,FK
        string link_imagem
        date data_atualizacao
    }

    CIDADES {
        int id PK
        string nome
    }

    HISTORICO_PRECOS {
        int id PK
        int produto_id FK
        int cidade_id FK
        float preco
        date data_inicio
        date data_fim
        unique(produto_id, cidade_id, data_inicio)
    }

    DISPONIBILIDADE_CIDADES {
        int id PK
        int produto_id FK
        int cidade_id FK
        bool disponivel
        date data_inicio
        date data_fim
        unique(produto_id, cidade_id, data_inicio)
    }

    LOG_EXECUCAO {
        date data_execucao PK
    }
```

</details>

**Observações de Implementação:**

- As datas de início e fim (`data_inicio`, `data_fim`) são inclusivas.
- As tabelas são criadas automaticamente na primeira execução do scraper, não é necessário rodar scripts SQL manualmente.
- Na tabela `historico_precos`, só é salvo um registro para todas as cidades se o preço for igual em todas; caso contrário, é salvo um preço específico para cada cidade.
- Se o preço for o mesmo para todas as cidades disponíveis naquele dia, o `id` da cidade será `1`.

---

## 🛠️ Pré-requisitos para rodar localmente

- Python 3.12+
- PostgreSQL 15+
- Navegador web compatível com Selenium (ex: Chrome, Firefox)

---

## 🚀 Instalação

```bash
git clone https://github.com/AndreLuis933/IG.git
cd IG
```

---

## ⚙️ Configuração

<details>
<summary>Variáveis de ambiente</summary>

1. Crie um banco de dados PostgreSQL local e anote as credenciais.
2. Crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo (ajuste para suas credenciais):

```env
DATABASE_URL=postgresql+psycopg2://meuusuario:minhasenha@localhost:5432/minhabasededados
LOCAL=true
```

- Não é necessário configurar cookies manualmente, a coleta é automática.
- As tabelas do banco são criadas automaticamente na primeira execução do scraper.
</details>

---

## ▶️ Como Usar

Abra **dois terminais**:

- **Terminal 1: Rodando o scraper**

  ```bash
  cd scraper
  python -m venv .venv
  pip install -r requirements.txt
  python main.py
  ```

  O scraper irá coletar os dados e salvar no banco de dados local.

- **Terminal 2: Visualização dos dados**

  ```bash
  cd view
  python -m venv .venv
  pip install -r requirements.txt
  streamlit run Dashboard.py
  ```

  O Streamlit irá buscar os dados automaticamente do banco e exibir a interface interativa.

- **Download dos dados:**  
  O download dos dados brutos em CSV está disponível diretamente na interface do Streamlit.

---

## 📄 Licença

Este projeto está licenciado sob a Licença MIT - veja o arquivo [LICENSE](LICENSE) para detalhes.

---

## 🙋‍♂️ Contato

Fique à vontade para abrir uma issue, sugerir melhorias ou só bater um papo sobre dados, scraping e automação!

- **LinkedIn:** [linkedin.com/in/andreluissouzacardoso](https://www.linkedin.com/in/andreluissouzacardoso/)  
- **GitHub:** [github.com/AndreLuis933](https://github.com/AndreLuis933)

Se quiser saber mais sobre o projeto, contribuir ou trocar ideias, é só chamar!
