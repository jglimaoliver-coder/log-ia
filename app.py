import streamlit as st
from groq import Groq
import os
import urllib.parse
import requests

# Configuração da página com o seu novo título
st.set_page_config(page_title="LOG IA", page_icon="🤖", layout="centered")

# ==============================================================================
# ESTILO CSS INTEGRAL (MANTÉM O SEU DESIGN PERFEITO)
# ==============================================================================
st.markdown("""
    <style>
    .stApp { background-color: #000000 !important; }
    [data-testid="stBottom"], [data-testid="stBottomBlockContainer"], 
    [data-testid="stChatMessageContainer"], .st-emotion-cache-bm2z3a, 
    .st-emotion-cache-12fm631, footer, header {
        background-color: #000000 !important; background: #000000 !important;
    }
    .stImage > img { display: block; margin-left: auto; margin-right: auto; margin-top: 5% !important; margin-bottom: 5% !important; }
    [data-testid="stChatInput"] { background-color: #FFFFFF !important; border-radius: 30px !important; border: none !important; padding: 5px 10px !important; max-width: 700px !important; margin: 0 auto !important; }
    .stChatInput textarea { color: #000000 !important; background-color: transparent !important; font-size: 1.1rem !important; }
    [data-testid="stChatInputSubmitButton"] { color: #000000 !important; }
    [data-testid="stHeader"] { background: transparent !important; }
    .stChatMessage { background-color: #111111 !important; color: #FFFFFF !important; border-radius: 15px !important; margin-bottom: 10px; }
    
    /* Estilização para deixar o botão de download centralizado e bonito */
    .stDownloadButton { text-align: center; }
    .stDownloadButton button { background-color: #222222 !important; color: #FFFFFF !important; border: 1px solid #444444 !important; border-radius: 10px !important; }
    .stDownloadButton button:hover { background-color: #FFFFFF !important; color: #000000 !important; }
    </style>
""", unsafe_allow_html=True)

# --- EXIBIÇÃO DA LOGO EM GRAFITE ---
nome_logo = "logo.jpg.png"
if os.path.exists(nome_logo):
    col1, col2, col3 = st.columns(3)
    with col2: st.image(nome_logo, width="stretch")
else:
    st.markdown("<h1 style='text-align: center; color: #FFFFFF; font-size: 4rem; font-family: sans-serif; font-weight: bold; margin-top: 10%; margin-bottom: 5%;'>LOG IA</h1>", unsafe_allow_html=True)

# Botão discreto no topo para limpar a memória se travar
if st.button("🔄 Limpar Memória do Chat"):
    st.session_state.messages = []
    st.rerun()

# Sua chave do Groq salva perfeitamente
API_KEY = "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"

if "client" not in st.session_state:
    st.session_state.client = Groq(api_key=API_KEY, timeout=60.0, max_retries=3)

if "messages" not in st.session_state:
    st.session_state.messages = []

# Mostra as mensagens antigas na tela
for index, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        if message.get("type") == "image":
            st.image(message["content"], caption="Imagem gerada pela LOG IA", width="stretch")
            st.download_button(
                label="📥 Baixar Imagem",
                data=message["content"],
                file_name=f"log_ia_{index}.png",
                mime="image/png",
                key=f"download_{index}"
            )
        else:
            st.markdown(message["content"])

# Caixa de texto para envio
if user_input := st.chat_input(" "):
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        with st.spinner("Processando..."):
            if user_input.lower().startswith("/imagem"):
                try:
                    prompt_desenho = user_input[7:].strip()
                    if not prompt_desenho:
                        prompt_desenho = "um robo futurista estilo cyberpunk"
                    
                    prompt_criptografado = urllib.parse.quote(prompt_desenho)
                    
                    # LINK TOTALMENTE CORRIGIDO COM A BARRA CORRETA
                    semente_aleatoria = len(prompt_desenho) * 15
                    url_da_imagem = f"https://pollinations.ai{prompt_criptografado}?width=1024&height=1024&nologo=true&seed={semente_aleatoria}"
                    
                    # Faz o download seguro em segundo plano
                    resposta_web = requests.get(url_da_imagem, timeout=30)
                    if resposta_web.status_code == 200:
                        img_bytes = resposta_web.content
                        st.session_state.messages.append({"role": "assistant", "content": img_bytes, "type": "image"})
                    else:
                        st.error("O servidor do Pollinations não conseguiu processar esta imagem. Tente outro prompt.")
                    
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro de conexão ao gerar imagem: {e}")
            
            else:
                try:
                    box_response = st.session_state.client.chat.completions.create(
                        model="llama-3.3-70b-versatile",
                        messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages if m.get("type") != "image"]
                    )
                    resposta = box_response.choices[0].message.content
                    st.markdown(resposta)
                    st.session_state.messages.append({"role": "assistant", "content": resposta, "type": "text"})
                    st.rerun()
                except Exception as e:
                    st.error(f"Erro ao conectar ao Groq: {e}")
