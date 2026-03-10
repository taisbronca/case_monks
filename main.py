from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from database.bigquery_client import testar_conexao
from agent.bot import perguntar_ao_agente

app = FastAPI(title="Agente de Mídia Monks")

class RequisicaoPergunta(BaseModel):
    pergunta: str

@app.get("/")
def read_root():
    return {"mensagem": "API rodando perfeitamente!"}

@app.get("/test-db")
def check_db():
    return testar_conexao()

@app.post("/chat")
def chat_com_agente(req: RequisicaoPergunta):
    resposta_ia = perguntar_ao_agente(req.pergunta)

    if resposta_ia.startswith("Ocorreu um erro"):
        raise HTTPException(status_code=500, detail=resposta_ia)

    return {
        "pergunta": req.pergunta,
        "resposta": resposta_ia
    }