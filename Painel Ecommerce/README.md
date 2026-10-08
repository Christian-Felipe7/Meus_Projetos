🛒 **Painel E-commerce (Sistema de Gestão e Separação)**

* **Objetivo e Impacto:** Aplicação web desenhada para centralizar e otimizar o processo de separação e controle de pedidos provenientes do e-commerce. Resolve o problema de rastreabilidade e lentidão na etapa de expedição de mercadorias, centralizando e acelerando consideravelmente o tempo de operação.


* **Tecnologias Utilizadas:** Backend assíncrono desenvolvido em **Python** utilizando o framework **FastAPI** e o servidor ASGI **Uvicorn**. Interface web dinâmica construída com **HTML, CSS e JavaScript**. Integração direta ao ERP via **Oracle SQL** e persistência de estado local gerenciada com **SQLite**.


* **Arquitetura de Dados (Padrão Sidecar):** O sistema foi arquitetado para consumir as informações vitais diretamente do banco de dados Oracle do ERP. No entanto, para gerenciar os estados de fila e transições de pedidos sem sobrecarregar o ERP, implementei uma abordagem "sidecar" utilizando um banco de dados local em arquivo em **SQlite**.
