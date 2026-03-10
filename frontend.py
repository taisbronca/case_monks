import streamlit as st
import requests

# Configurações da página
st.set_page_config(page_title="Analista de Mídia | Monks", page_icon="📈", layout="centered")

# Cabeçalho
st.title("Fale com o Cleytinho")
st.markdown("Faça perguntas em linguagem natural sobre o tráfego, ROI e performance do e-commerce para seu analista júnior de mídia")

# Inicializa o histórico do chat (se não existir)
if "messages" not in st.session_state:
    st.session_state.messages = []

# Exibe as mensagens antigas na tela ao recarregar
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Cria o campo de digitação no fundo da tela
if prompt := st.chat_input("Ex: Qual canal trouxe mais receita em janeiro de 2024?"):
    
    # 1. Mostra a mensagem do usuário na tela e salva no histórico
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    # 2. Faz a requisição para a sua API (FastAPI)
    with st.chat_message("assistant"):
        # Mostra um "loading" enquanto a IA pensa e busca no banco
        with st.spinner("Analisando dados no BigQuery..."):
            try:
                # Faz o POST para a rota que criamos no main.py
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"pergunta": prompt}
                )
                
                if response.status_code == 200:
                    resposta_ia = response.json()["resposta"]
                    st.markdown(resposta_ia)
                    
                    # Salva a resposta da IA no histórico
                    st.session_state.messages.append({"role": "assistant", "content": resposta_ia})
                else:
                    st.error(f"Erro na API: Código {response.status_code}")
                    
            except Exception as e:
                st.error(f"Erro de conexão: {str(e)}\n\nO servidor FastAPI está rodando na porta 8000?")