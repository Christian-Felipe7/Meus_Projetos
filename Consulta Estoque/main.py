import os
import oracledb
from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging

# Carrega as credenciais do arquivo .env
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Consulta de Estoque - Conexão Direta Oracle")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Servidor de Arquivos e Templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

async def get_oracle_connection():
    """Gera conexão enxuta e nativa (Thin) com o Oracle ERP."""
    host = os.getenv("ORACLE_HOST")
    port = os.getenv("ORACLE_PORT")
    service = os.getenv("ORACLE_SERVICE_NAME")
    dsn_string = f"{host}:{port}/{service}"
    
    return await oracledb.connect_async(
        user=os.getenv("ORACLE_USER"),
        password=os.getenv("ORACLE_PASSWORD"),
        dsn=dsn_string
    )

@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Página principal."""
    return templates.TemplateResponse(
        request=request, 
        name="base.html", 
        context={"request": request}
    )

@app.get("/api/v1/produtos/busca", response_class=HTMLResponse)
async def buscar_produtos_htmx(request: Request, query: str = "", filial: str = "Todas", campo: str = "DESCRICAO"):
    """
    Rota acionada pelo HTMX. Respeita o campo de busca, permite buscas múltiplas por código 
    separadas por vírgula e protege o banco contra consultas pesadas.
    """
    query = query.strip()
    
    if not query:
        return HTMLResponse("<tr><td colspan='11' class='text-center text-muted p-4'>Aguardando pesquisa... Digite um termo acima.</td></tr>")
        
    if campo == "DESCRICAO" and len(query) < 3:
        return HTMLResponse("<tr><td colspan='11' class='text-center text-muted p-4'>Digite pelo menos 3 caracteres para buscar por descrição...</td></tr>")

    connection = None
    try:
        connection = await get_oracle_connection()
        with connection.cursor() as cursor:
            
            # Filtro de filiais alterado para valores genéricos de demonstração
            filial_clause = "E.CODFILIAL IN (1, 2, 3)" 
            binds = {}
            
            if filial != "Todas":
                filial_clause = "E.CODFILIAL = :filial"
                binds['filial'] = filial
            
            sql = f"""
                SELECT 
                    E.CODFILIAL,
                    TO_CHAR(P.CODFAB) AS CODFAB,
                    TO_CHAR(P.CODAUXILIAR) AS CODAUXILIAR,
                    TO_CHAR(E.CODPROD) AS CODPROD,
                    P.UNIDADE,
                    P.DESCRICAO,
                    (E.QTESTGER - E.QTRESERV - E.QTBLOQUEADA) AS QT_DISPONIVEL,
                    E.QTRESERV,
                    E.QTBLOQUEADA,
                    TO_CHAR(E.DTULTENT, 'DD/MM/YYYY') AS ULTIMA_ENTRADA,
                    TO_CHAR(E.DTULTSAIDA, 'DD/MM/YYYY') AS ULTIMA_SAIDA,
                    F.FORNECEDOR
                FROM PCEST E
                JOIN PCPRODUT P ON E.CODPROD = P.CODPROD
                LEFT JOIN PCFORNEC F ON P.CODFORNEC = F.CODFORNEC
                WHERE {filial_clause}
            """
            
            if campo == "DESCRICAO":
                sql += " AND UPPER(P.DESCRICAO) LIKE UPPER(:query)"
                binds['query'] = f"%{query}%"
            else:
                if ',' in query:
                    valores = [v.strip() for v in query.split(',') if v.strip()]
                    
                    bind_names = []
                    for i, val in enumerate(valores):
                        bind_name = f"val_{i}"
                        bind_names.append(f":{bind_name}")
                        binds[bind_name] = val
                        
                    bind_str = ", ".join(bind_names)
                    
                    if campo == "CODFAB":
                        sql += f" AND TO_CHAR(P.CODFAB) IN ({bind_str})"
                    elif campo == "CODAUXILIAR":
                        sql += f" AND TO_CHAR(P.CODAUXILIAR) IN ({bind_str})"
                    else:
                        sql += f" AND TO_CHAR(E.CODPROD) IN ({bind_str})"
                else:
                    if campo == "CODFAB":
                        sql += " AND TO_CHAR(P.CODFAB) = :query"
                    elif campo == "CODAUXILIAR":
                        sql += " AND TO_CHAR(P.CODAUXILIAR) = :query"
                    else:
                        sql += " AND TO_CHAR(E.CODPROD) = :query"
                    binds['query'] = query
            
            sql += " FETCH NEXT 50 ROWS ONLY"

            await cursor.execute(sql, binds)
            rows = await cursor.fetchall()
            
            produtos = []
            for row in rows:
                produtos.append({
                    "filial": row[0],
                    "cod_fabrica": row[1] or "",
                    "cod_barras": row[2] or "",
                    "cod_produto": row[3] or "",
                    "unidade": row[4] or "",
                    "descricao": row[5] or "",
                    "qt_disponivel": float(row[6] or 0.0),
                    "qt_reservada": float(row[7] or 0.0),
                    "qt_bloqueada": float(row[8] or 0.0),
                    "ultima_entrada": row[9],
                    "ultima_saida": row[10]
                })

            return templates.TemplateResponse(
                request=request, 
                name="estoque.html", 
                context={"request": request, "produtos": produtos}
            )

    except Exception:
        # Tratamento de exceção alterado para não expor a variável de erro no log
        logger.error("Erro de execução ou conexão no banco de dados.")
        return HTMLResponse("<tr><td colspan='11' class='text-center text-danger fw-bold p-4'>Erro de conexão com o ERP. Verifique suas credenciais.</td></tr>")
    finally:
        if connection:
            await connection.close()

if __name__ == "__main__":
    app_port = int(os.getenv("PORT", 8000))
    logger.info(f"Iniciando o servidor unificado... Acesse http://127.0.0.1:{app_port}")
    uvicorn.run("main:app", host="0.0.0.0", port=app_port, reload=True)
