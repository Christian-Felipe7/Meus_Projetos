# Painel E-commerce – Sistema de Gestão e Separação

Aplicação web corporativa desenhada para centralizar e otimizar o processo de separação e controle de pedidos provenientes do e-commerce, resolvendo problemas de rastreabilidade e lentidão na expedição.

---

## 🔗 Ambiente e Acesso

* **Ambiente de Produção:** Intranet Corporativa (Uso interno)

---

## Tecnologias Utilizadas

### Backend

* Python + FastAPI
* Uvicorn (Servidor ASGI assíncrono)
* Integração direta ao ERP via Oracle SQL
* SQLite (Persistência de estado local)

### Frontend

* HTML
* CSS
* JavaScript (Interface web dinâmica)

---

## Arquitetura de Dados (Padrão Sidecar)

* **Consumo de Dados ERP:** Leitura das informações vitais diretamente do banco de dados corporativo Oracle.
* **Gerenciamento de Fila (Sidecar):** Controle dos estados de fila e transições de pedidos implementado de forma autônoma em um banco de dados local em arquivo (SQLite).
* **Benefício da Arquitetura:** Garante alta performance no rastreio logístico sem sobrecarregar o servidor do ERP principal com atualizações de estado.

---

## Funcionalidades e Impacto

* Centralização do fluxo de pedidos e-commerce.
* Rastreabilidade ponta a ponta na esteira de expedição.
* Aceleração considerável do tempo de operação e triagem de mercadorias.
