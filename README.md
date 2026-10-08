# Meus_Projetos 💻

Portfólio de aplicações web corporativas desenvolvidas para modernizar operações, integrar sistemas legados e resolver gargalos logísticos reais. Atualmente em ambiente de produção.

🛒 **Painel E-commerce (Sistema de Gestão e Separação)**

* **Objetivo e Impacto:** Aplicação web desenhada para centralizar e otimizar o processo de separação e controle de pedidos provenientes do e-commerce. Resolve o problema de rastreabilidade e lentidão na etapa de expedição de mercadorias, centralizando e acelerando consideravelmente o tempo de operação.


* **Tecnologias Utilizadas:** Backend assíncrono desenvolvido em **Python** utilizando o framework **FastAPI** e o servidor ASGI **Uvicorn**. Interface web dinâmica construída com **HTML, CSS e JavaScript**. Integração direta ao ERP via **Oracle SQL** e persistência de estado local gerenciada com **SQLite**.


* **Arquitetura de Dados (Padrão Sidecar):** O sistema foi arquitetado para consumir as informações vitais diretamente do banco de dados Oracle do ERP. No entanto, para gerenciar os estados de fila e transições de pedidos sem sobrecarregar o ERP, implementei uma abordagem "sidecar" utilizando um banco de dados local em arquivo em **SQlite**.



🔍 **Consulta Estoque (Motor de Busca de SKUs)**

* **Objetivo e Impacto:** Sistema web para rastreio e validação de disponibilidade de SKUs no inventário. Criado para substituir um sistema legado, eliminando a lentidão operacional e entregando dados com agilidade para a equipe.


* **Tecnologias Utilizadas:** API RESTful estruturada em **Python**, **FastAPI** e **Uvicorn**, focada em processamento rápido e baixíssima latência. Renderização de views no frontend utilizando **HTML e CSS**. Comunicação de alta performance com o banco corporativo construída através de scripts e queries avançadas em **Oracle SQL**.


* **Busca Altamente Otimizada:** O diferencial de engenharia desta aplicação é a performance de sua camada de busca. O sistema de consultas foi otimizado no nível do banco (Oracle), reduzindo drasticamente a latência de I/O. Isso permite que buscas de SKUs (por código do produto, código de barras, código de fábrica, descrição e inclusive permitindo o usuário pesquisar por múltiplos produtos basicamente separando-os por vírgula)  retornem resultados quase instantâneos, mesmo lidando com a densa estrutura de dados do ERP.



🎯 **Impacto**: Aplicações atualmente em produção, desenvolvidas para resolver gargalos operacionais reais do negócio.
