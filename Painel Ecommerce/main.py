from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Form, Response
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from datetime import datetime
import database
import json
import os

@asynccontextmanager
async def lifespan(app: FastAPI):
    database.init_db()
    print("🚀 Sistema unificado Python operante.")
    yield

app = FastAPI(lifespan=lifespan)
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

def get_current_user(request: Request):
    # Dica de portfólio: Nome genérico para o cookie, ocultando a empresa original
    user_cookie = request.cookies.get("app_auth")
    if user_cookie:
        try:
            return json.loads(user_cookie)
        except:
            pass
    return None

# ==========================================
# ROTAS DE AUTENTICAÇÃO
# ==========================================
@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse(request=request, name="login.html", context={"error": None})

@app.post("/login", response_class=HTMLResponse)
async def process_login(request: Request, username: str = Form(default=""), password: str = Form(default="")):
    user = await database.authenticate_user(username, password)
    if user:
        response = RedirectResponse(url="/", status_code=303)
        response.set_cookie(key="app_auth", value=json.dumps(user), httponly=True, max_age=43200)
        return response
    return templates.TemplateResponse(request=request, name="login.html", context={"error": "Usuário ou senha inválidos."})

@app.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=303)
    response.delete_cookie("app_auth")
    return response

# ==========================================
# FUNÇÕES DE APOIO PARA HTMX
# ==========================================
def reconstruct_order(pedido_id: str, form_data) -> dict:
    state_str = str(form_data.get("current_state", "")).strip().lower()
    notes_json = form_data.get("notes_json", "[]")
    
    try:
        notes = json.loads(notes_json) if notes_json else []
    except:
        notes = []

    return {
        "pedido": pedido_id,
        "data": form_data.get("data", ""),
        "cliente": form_data.get("cliente", ""),
        "vias": form_data.get("vias", ""),
        "status_erp": form_data.get("status_erp", ""),
        "notes": notes,
        "is_separated": state_str in ("true", "1", "on"),
        "separator_name": form_data.get("separator_name", ""),
        "separated_by_user": form_data.get("separated_by_user", ""),
        "separated_at": form_data.get("separated_at", "")
    }

# ==========================================
# ROTAS DA APLICAÇÃO
# ==========================================
@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login", status_code=303)

    orders = await database.get_orders_hybrid()
    
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"orders": orders, "hora_atualizacao": datetime.now().strftime("%H:%M:%S"), "user": user}
    )

@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard_page(request: Request):
    user = get_current_user(request)
    if not user: return RedirectResponse(url="/login", status_code=303)

    orders = await database.get_orders_hybrid()
    orders_json = json.dumps(orders)
    
    return templates.TemplateResponse(
        request=request, name="dashboard.html",
        context={"orders_json": orders_json, "hora_atualizacao": datetime.now().strftime("%H:%M:%S"), "user": user}
    )

@app.post("/toggle/{order_id}")
async def toggle_order(request: Request, order_id: str):
    user = get_current_user(request)
    if not user: return HTMLResponse("Sessão expirada", status_code=401)
    
    form_data = await request.form()
    order = reconstruct_order(order_id, form_data)
    
    separator_name = str(form_data.get("separator_name", "")).strip()
    separated_by_user = user["nome"]
    separated_at = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    new_state = database.toggle_separation(order_id, order["is_separated"], separator_name, separated_by_user, separated_at)
    order["is_separated"] = bool(new_state) 
    
    if new_state:
        order["separator_name"] = separator_name
        order["separated_by_user"] = separated_by_user
        order["separated_at"] = separated_at
    else:
        order["separator_name"] = ""
        order["separated_by_user"] = ""
        order["separated_at"] = ""
    
    return templates.TemplateResponse(request=request, name="order_row.html", context={"order": order})

@app.post("/modal/{order_id}")
async def get_modal(request: Request, order_id: str):
    if not get_current_user(request): return HTMLResponse("Sessão expirada", status_code=401)
    form_data = await request.form()
    order = reconstruct_order(order_id, form_data)
    
    # Busca itens do pedido no banco legando/ERP
    items = await database.get_order_items(order_id)
    
    return templates.TemplateResponse(request=request, name="modal.html", context={"order": order, "items": items})

@app.post("/notes/{order_id}")
async def save_notes(request: Request, order_id: str):
    user = get_current_user(request)
    if not user: return HTMLResponse("Sessão expirada", status_code=401)
    
    form_data = await request.form()
    order = reconstruct_order(order_id, form_data)
    new_note = form_data.get("new_note", "").strip()
    
    if new_note:
        now_str = datetime.now().strftime("%d/%m/%Y %H:%M")
        order["notes"].append({"author": user["nome"], "time": now_str, "text": new_note})
        database.save_order_notes(order_id, json.dumps(order["notes"]))
        
    return templates.TemplateResponse(request=request, name="modal_and_row.html", context={"order": order, "oob": True})

if __name__ == "__main__":
    import uvicorn
    # A porta pode ser configurada via variáveis de ambiente no deploy de produção
    APP_
