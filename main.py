from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import database
from models import ProdutoCatalogo, ItemOrcamento, Orcamento

# Inicializa o banco de dados SQLite na primeira execução
database.init_db()

app = FastAPI(title="Emissor de Orçamentos de Velas")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ==========================================
# 1. ROTA PRINCIPAL: EMISSÃO DE ORÇAMENTO
# ==========================================
@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    clientes = database.listar_clientes()
    produtos_raw = database.listar_produtos()
    config = database.obter_config_insumos()
    data_hoje = datetime.now().strftime("%Y-%m-%d")

    produtos = [
        ProdutoCatalogo(
            id=p["id"],
            nome=p["nome"],
            valor_mao_de_obra=p["valor_mao_de_obra"],
            cera_kg_unitario=p["cera_kg_unitario"],
            pavio_m_unitario=p["pavio_m_unitario"],
        )
        for p in produtos_raw
    ]

    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={
            "clientes": clientes,
            "produtos": produtos,
            "config": config,
            "data_hoje": data_hoje,
        },
    )


@app.post("/gerar-orcamento", response_class=HTMLResponse)
async def gerar_orcamento(
    request: Request,
    cliente_id: Optional[str] = Form(None),
    cliente_nome_avulso: Optional[str] = Form(""),
    cliente_contato_avulso: Optional[str] = Form(""),
    data_emissao: str = Form(...),
    preco_kg_cera: float = Form(38.0),
    preco_metro_pavio: float = Form(0.8),
    desconto_mo: float = Form(0.0),
    observacoes: str = Form(""),
):
    form_data = await request.form()

    nome_final = cliente_nome_avulso.strip() if cliente_nome_avulso else ""
    contato_final = cliente_contato_avulso.strip() if cliente_contato_avulso else ""

    if cliente_id and cliente_id.isdigit():
        clientes = database.listar_clientes()
        cliente_db = next((c for c in clientes if c["id"] == int(cliente_id)), None)
        if cliente_db:
            nome_final = cliente_db["nome"]
            contato_final = cliente_db["contato"]

    if not nome_final:
        nome_final = "Consumidor / Não Identificado"

    produtos_raw = database.listar_produtos()
    itens_orcamento: List[ItemOrcamento] = []

    for p in produtos_raw:
        campo_qtd = f"qtd_produto_{p['id']}"
        if campo_qtd in form_data:
            try:
                qtd = int(form_data[campo_qtd])
                if qtd > 0:
                    prod_obj = ProdutoCatalogo(
                        id=p["id"],
                        nome=p["nome"],
                        valor_mao_de_obra=p["valor_mao_de_obra"],
                        cera_kg_unitario=p["cera_kg_unitario"],
                        pavio_m_unitario=p["pavio_m_unitario"],
                    )
                    itens_orcamento.append(ItemOrcamento(produto=prod_obj, quantidade=qtd))
            except ValueError:
                continue

    numero_doc = datetime.now().strftime("%Y%m%d%H%M")

    orcamento = Orcamento(
        cliente_nome=nome_final,
        cliente_contato=contato_final,
        data_emissao=data_emissao,
        numero_orcamento=numero_doc,
        itens=itens_orcamento,
        preco_kg_cera=preco_kg_cera,
        preco_metro_pavio=preco_metro_pavio,
        desconto_mo=desconto_mo,
        observacoes=observacoes,
    )

    return templates.TemplateResponse(
        request=request,
        name="orcamento.html",
        context={"orcamento": orcamento},
    )


# ==========================================
# 2. GESTÃO DE PRODUTOS
# ==========================================
@app.get("/produtos", response_class=HTMLResponse)
def tela_produtos(request: Request):
    produtos = database.listar_produtos()
    return templates.TemplateResponse(
        request=request,
        name="produtos.html",
        context={"produtos": produtos},
    )


@app.post("/produtos/adicionar")
def criar_produto(
    nome: str = Form(...),
    valor_mao_de_obra: str = Form(...),
    cera_kg_unitario: str = Form(...),
    pavio_m_unitario: str = Form(...),
):
    # Converte vírgula para ponto e limpa espaços acidentais
    v_mo = float(valor_mao_de_obra.strip().replace(",", "."))
    v_cera = float(cera_kg_unitario.strip().replace(",", "."))
    v_pavio = float(pavio_m_unitario.strip().replace(",", "."))

    database.adicionar_produto(
        nome=nome,
        valor_mao_de_obra=v_mo,
        cera_kg_unitario=v_cera,
        pavio_m_unitario=v_pavio,
    )
    return RedirectResponse(url="/produtos", status_code=303)


@app.post("/produtos/excluir/{produto_id}")
def remover_produto(produto_id: int):
    database.excluir_produto(produto_id)
    return RedirectResponse(url="/produtos", status_code=303)


# ==========================================
# 3. GESTÃO DE CLIENTES
# ==========================================
@app.get("/clientes", response_class=HTMLResponse)
def tela_clientes(request: Request):
    clientes = database.listar_clientes()
    return templates.TemplateResponse(
        request=request,
        name="clientes.html",
        context={"clientes": clientes},
    )


@app.post("/clientes/adicionar")
def criar_cliente(nome: str = Form(...), contato: str = Form("")):
    database.adicionar_cliente(nome=nome, contato=contato)
    return RedirectResponse(url="/clientes", status_code=303)


@app.post("/clientes/excluir/{cliente_id}")
def remover_cliente(cliente_id: int):
    database.excluir_cliente(cliente_id)
    return RedirectResponse(url="/clientes", status_code=303)


# ==========================================
# 4. PARÂMETROS GERAIS DE INSUMOS
# ==========================================
@app.get("/configuracoes", response_class=HTMLResponse)
def tela_config(request: Request):
    config = database.obter_config_insumos()
    return templates.TemplateResponse(
        request=request,
        name="configuracoes.html",
        context={"config": config},
    )


@app.post("/configuracoes/atualizar")
def atualizar_config(preco_kg_cera: str = Form(...), preco_metro_pavio: str = Form(...)):
    p_cera = float(preco_kg_cera.strip().replace(",", "."))
    p_pavio = float(preco_metro_pavio.strip().replace(",", "."))
    database.atualizar_config_insumos(preco_kg_cera=p_cera, preco_metro_pavio=p_pavio)
    return RedirectResponse(url="/configuracoes", status_code=303)