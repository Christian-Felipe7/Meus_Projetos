# Android 16 Beta – User Trial Release Readiness Dashboard

Painel executivo fictício de Business Intelligence desenvolvido para monitorar a estabilidade de pré-lançamento de software mobile. A ferramenta transforma logs brutos de telemetria de campo em decisões claras de engenharia (Go / No-Go), identificando gargalos térmicos e falhas de sistema antes do lançamento público.

---

## 🔗 Ambiente e Acesso

- **Ambiente de Produção:** Google Data Studio
- **Acesso ao Dashboard:** https://datastudio.google.com/s/qHotujx0arQ

---

## Tecnologias Utilizadas

### Engenharia de Dados
- **Python (Pandas):** Geração e estruturação de datasets relacionais baseados em cenários reais de telemetria mobile.
- **Google Sheets:** Armazenamento dos dados.

### Visualização e BI
- **Data Studio:** Construção do painel interativo, formatação condicional e aplicação do tema visual corporativo (Dark Mode).

---

## Arquitetura de Dados (Modelagem Dimensional)

- **Star Schema (Fato e Dimensão):** Os dados foram estruturados separando os eventos transacionais de erro (Tabela Fato de Telemetria com 1.500 registros) das características de hardware dos celulares (Tabela Dimensão de Perfil de Testadores).
- **Data Blending (Left Outer Join):** O cruzamento das tabelas foi realizado nativamente no Data Studio utilizando a chave estrangeira `Tester_ID`. 
- **Benefício da Arquitetura:** Essa modelagem garantiu 100% de precisão nos KPIs, permitindo enriquecer os relatórios de bugs com o contexto de hardware (ex: processador e RAM) sem duplicar dados operacionais ou inflar os números.

---

## Funcionalidades e Impacto

- **Análise Temporal de Estabilidade:** Gráfico de colunas empilhadas rastreando o volume e a severidade dos bugs (de S1-Blocker a S4-Minor) ao longo das builds (Beta 1 até RC1).
- **Diagnóstico de Hardware (Scatter Plot):** Gráfico de dispersão correlacionando modelos de smartphones com métricas críticas de sobreaquecimento (Peak Temp) e drenagem de bateria (Battery Drain).
- **KPIs Executivos e Filtros Globais:** Visão instantânea da saúde geral da frota de testes, incluindo a nota de satisfação do usuário (CSAT Score).
- **Impacto de Negócio:** O dashboard permite isolar anomalias rapidamente — como a regressão térmica identificada em processadores Exynos durante a Beta 2 — comprovando visualmente a correção do problema na versão final (RC1) e embasando a aprovação do software para lançamento com segurança estatística.

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/054357d6-ffab-47a9-aa78-8e0392f10624" />

