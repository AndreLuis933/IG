### 📊 Monitor de Preços Irmão Gonçalves

## ✨ Sobre o Projeto

Este projeto é um sistema de **monitoramento diário de preços e disponibilidade** do site Irmão Gonçalves, pensado como **projeto de portfólio** com foco em:

- Coletar **centenas de milhares de registros por dia**,
- Operar **100% em free tier** (AWS, Supabase, Vercel),
- Oferecer um **dashboard web** com métricas agregadas por cidade, leve e rápido.

A arquitetura foi desenhada para ser **barata, escalável e resiliente**, otimizando o uso de banco de dados com técnicas de **intervalos de vigência** e **retenção de 6 meses** com arquivamento em CSV.

**[🚀 Veja a demo online aqui!](https://analize-ig.vercel.app/)**

---

## 🚀 Tecnologias Utilizadas

| Categoria             | Tecnologia(s)                                               |
| :-------------------- | :--------------------------------------------------------- |
| **Coleta / Backend**  | Python, `aiohttp`, SQLAlchemy                              |
| **Infra de Coleta**   | AWS Lambda, EventBridge/CloudWatch (cron diário)          |
| **Banco / Storage**   | Supabase Postgres, Supabase Storage (CSV), `pg_cron`      |
| **Funções Backend**   | Supabase Edge Functions, GitHub Actions (cron mensal)     |
| **Front-end**         | React, MUI (Material UI), MUI X Charts                    |
| **Integração Dados**  | `@supabase/supabase-js`                                   |
| **Hospedagem Front**  | Vercel                                                    |

---

## ⚙️ Como Funciona (Visão Geral)

O sistema é dividido em três blocos principais que trabalham em conjunto:

### 1. Scraper Diário em Python (AWS Lambda)

- Função **AWS Lambda (512 MB)** executando **1 vez por dia**, por volta do meio-dia.
- Coleta dados a partir da **API interna** usada pelo próprio site.
- Usa **requisições assíncronas com `aiohttp`**:
  - Até **10 conexões simultâneas**, balanceando velocidade e respeito à infra do site.
- **Manipulação de cookies por cidade**:
  - Cada chamada é feita com o contexto de cidade correto (11 cidades monitoradas).
- Domínio monitorado:
  - **17 categorias base** com subcategorias em até **3 níveis**,
  - Centenas de requisições por dia (cidade × categoria/subcategoria).
- Dados coletados (JSON):
  - Nome, link, categoria, imagem do produto,
  - Preço por cidade,
  - Disponibilidade por cidade,
  - Metadados para reconstruir o histórico ao longo do tempo.
- Performance típica:
  - ~**20 s** para coleta assíncrona,
  - ~**60 s** para gravação no Postgres via SQLAlchemy.

---

### 2. Banco de Dados e Otimizações de Espaço (Supabase)

O backend é um **PostgreSQL no Supabase**, com **storage de arquivos (CSV)** para histórico frio. O foco é **sobreviver ao volume** dentro do free tier.

#### a) Armazenamento por Intervalos (Ranges)

Para **preço** e **disponibilidade**, o sistema não grava um registro por dia, e sim **intervalos de vigência**:

- Cada linha registra:
  - `data_inicio` do intervalo,
  - `data_fim` (nula enquanto o valor estiver vigente).
- Enquanto não há mudança de preço/estado, **nenhum novo registro é criado**.
- Quando muda:
  - O intervalo anterior é fechado,
  - Um novo intervalo é inserido com o valor atualizado.

Resultado prático:

- Modelo ingênuo: ~**200.000 linhas/dia**,
- Com ranges: ~**10.000 linhas/dia** (apenas mudanças),
- Redução de mais de uma ordem de grandeza no crescimento diário nas tabelas críticas.

#### b) Janela de 6 Meses + Arquivamento Mensal em CSV

Além de reduzir o crescimento diário, o sistema controla **quanto tempo os dados ficam “quentes”**:

- Apenas os **últimos 6 meses** permanecem nas tabelas principais.
- Quando um mês sai dessa janela:
  - Os registros daquele mês são **exportados para um CSV**,
  - O arquivo é salvo no **Supabase Storage**,
  - As linhas são apagadas das tabelas ativas.

Orquestração:

- Processo mensal via **Edge Function** no Supabase,
- Disparo por **GitHub Action** agendada (`cron`),
- Mantém o banco dentro do espaço do plano gratuito, com volume máximo controlado.

#### c) Tabela de Resumo Diário (Fonte do Front)

Para evitar que o front consulte diretamente tabelas gigantes:

- Uma **tabela de resumo diário por cidade** é gerada a partir dos dados brutos.
- Métricas principais:
  - Variação acumulada de preço,
  - Número de produtos disponíveis por dia,
  - Preço médio geral diário por cidade.
- Implementação:
  - **Função SQL** no Postgres,
  - Execução via **`pg_cron`** alguns minutos após o scraper diário.
- Resultado:
  - Dataset pequeno, estável e pronto para consumo direto pelo dashboard.

---

### 3. Front-end: Dashboard de Análise (React + Vercel)

- App em **React** hospedado na **Vercel**.
- UI construída com **MUI (Material UI)** e **MUI X Charts**.
- Integração direta com Supabase via **`@supabase/supabase-js`**, consumindo apenas a **tabela de resumo diário**.

Funcionalidades principais:

- Seleção de:
  - **Cidade específica**, ou
  - **Todas as cidades agregadas**.
- Filtros por **intervalo de datas** (até 6 meses de janela).
- Visualização de:
  - Variação acumulada de preço no período,
  - Número de produtos disponíveis por dia,
  - Preço médio diário por cidade.
- Foco em:
  - **Carregamento rápido** (sem consultas pesadas),
  - **Experiência fluida** mesmo com histórico volumoso no backend.

---

## 💰 Custos e Escalabilidade

Todo o desenho foi feito para operar **inteiramente dentro dos tiers gratuitos** de:

- **AWS** (Lambda + agendador),
- **Supabase** (Postgres, Edge Functions, `pg_cron`, Storage),
- **Vercel** (Front-end),

