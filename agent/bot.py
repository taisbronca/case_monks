from datetime import datetime
from langchain_openai import ChatOpenAI
from langgraph.prebuilt import create_react_agent
from agent.tools import todas_as_tools

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

def perguntar_ao_agente(pergunta_do_usuario: str) -> str:
    """Função principal que será chamada pela nossa API"""
    data_atual = datetime.now().strftime("%Y-%m-%d")

    instrucao_sistema = f"""Você é um Analista Júnior de Mídia atuando em um e-commerce. 
Seu objetivo é analisar dados de tráfego e vendas para fornecer insights acionáveis sobre o ROI e a performance dos canais de mídia.

Hoje é dia {data_atual}. Use essa data como referência exata para responder perguntas sobre 'último mês', 'este ano', etc.

Sempre que o usuário fizer uma pergunta sobre dados, use as ferramentas disponíveis para buscar a informação no banco de dados antes de responder.

Regras importantes:
1. Nunca invente dados. Baseie-se APENAS no retorno das ferramentas.
2. Seja claro, direto e traga uma visão de negócio (ex: qual canal traz mais receita vs qual traz mais volume).
3. Se a pergunta estiver fora do escopo de mídia, tráfego ou vendas, responda educadamente que você só pode ajudar com análises do e-commerce."""

    agente = create_react_agent(
        model=llm,
        tools=todas_as_tools,
        prompt=instrucao_sistema
    )

    try:
        estado_inicial = {"messages": [("user", pergunta_do_usuario)]}
        resposta = agente.invoke(estado_inicial)
        mensagem_final = resposta["messages"][-1].content if resposta["messages"] else "Sem resposta"
        return mensagem_final

    except Exception as e:
        return f"Ocorreu um erro ao processar sua solicitação: {str(e)}"