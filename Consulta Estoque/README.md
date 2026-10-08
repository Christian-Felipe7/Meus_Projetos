# Consulta Estoque – Motor de Busca de SKUs

Aplicação web desenhada para o rastreio e validação instantânea de disponibilidade de SKUs no inventário, substituindo o sistema legado e eliminando a lentidão operacional de consultas da equipe.

---

## 🔗 Ambiente e Acesso

- **Ambiente de Produção:** Intranet Corporativa (Uso interno)

---

## Tecnologias Utilizadas

### Backend

- Python + FastAPI.
- Uvicorn (Servidor ASGI assíncrono).
- Integração direta e nativa ao ERP corporativo via Oracle SQL (oracledb).

### Frontend

- HTML e CSS[cite: 14]
- JavaScript (com HTMX para atualizações dinâmicas de interface).

---

## Arquitetura de Busca e Performance

- **API RESTful Stateless:** A arquitetura desacopla a interface da lógica de dados. O sistema atua de forma independente e leve, processando requisições sem reter sessões pesadas na memória.
- **Otimização de Consultas (I/O):** As pesquisas no banco Oracle são super otimizadas, utilizando *bind variables* dinâmicas, limitação inteligente de retorno de linhas (FETCH NEXT) e travas de segurança contra buscas pesadas.
- **Benefício da Arquitetura:** Garante altíssima performance e respostas quase instantâneas para os usuários, mesmo ao realizar pesquisas simultâneas por múltiplos códigos, sem gerar gargalos no banco de dados principal da empresa.

---

## Funcionalidades e Impacto

- Rastreio em tempo real de SKUs, quantidades disponíveis, reservas, bloqueios e movimentações de entrada/saída.
- Filtros dinâmicos por filial e suporte flexível a pesquisas exatas ou por descrição.
- Aceleração considerável no acesso à informação logística, eliminando a dependência e a lentidão das antigas telas do ERP.
