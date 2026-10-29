# Painel E-commerce – Sistema de Gestão e Separação

Aplicação web corporativa de alta performance desenhada para centralizar e otimizar a esteira de triagem, separação e controle de pedidos provenientes do e-commerce, resolvendo gargalos logísticos e fornecendo rastreabilidade, auditoria operacional e indicadores gerenciais em tempo real.

---

## 🔗 Ambiente e Acesso

* **Ambiente de Produção:** Intranet Corporativa (Uso interno)
* **Integração e Login:** Autenticação validada diretamente via credenciais do ERP WinThor (TOTVS)

---

## Tecnologias Utilizadas

### Backend

* Python + FastAPI
* Uvicorn (Servidor ASGI assíncrono para execução contínua)
* Integração direta ao ERP via Oracle SQL (oracledb)
* SQLite (Persistência de estado local e auditoria)
* Python-dotenv (Gerenciamento seguro de credenciais)

### Frontend

* HTML5 & Jinja2 (Estruturação modular)
* CSS3 & TailwindCSS
* JavaScript (Vanilla JS para motores reativos e persistência de navegação)
* HTMX (Atualizações dinâmicas parciais sem recarregamento)
* Chart.js (Renderização de gráficos gerenciais)

---

## Arquitetura de Dados (Padrão Sidecar)

* **Consumo de Dados ERP (Oracle):** Leitura das informações vitais estritamente em modo consulta, eliminando riscos de sobrecarga no banco corporativo.
* **Gerenciamento de Fila e Auditoria (Sidecar):** Controle dos estados de fila, auditorias de separadores e anotações persistido de forma autônoma em um banco de dados local em arquivo (SQLite).
* **Benefício da Arquitetura:** Garante alta performance no rastreio logístico sem sobrecarregar o servidor do ERP principal, operando com uma estrutura ultraleve.

---

## Funcionalidades e Impacto

* Fila de operação dinâmica com marcadores visuais de status e KPIs reativos com exclusão mútua.
* Auditoria de separação física obrigatória (registro de separador, usuário sistêmico e carimbo de data/hora).
* Conferência de itens do pedido cruzando dados do ERP diretamente na interface.
* Inserção de observações logísticas com destaque visual imediato na fila de expedição.
* Dashboard de SLA monitorando o fluxo sob a régua de 1 dia (Pedidos no Prazo vs. Separação Atrasada) e controle de bloqueios.
* Sub-dashboards interativos (Drill-down) com mini-KPIs e listagem específica de gargalos.
* Filtros avançados inteligentes persistentes e trava de segurança sistêmica para pedidos já encerrados (Faturados ou Cancelados).
