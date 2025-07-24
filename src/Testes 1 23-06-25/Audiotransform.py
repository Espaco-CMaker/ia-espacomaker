import streamlit as st
from llama_cpp import Llama

MODEL_PATH = r"C:\Users\vinic\Desktop\IA CMAKER\testes\model\Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf"

@st.cache_resource
def load_model():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=8,
        n_gpu_layers=40,
        f16_kv=True
    )

llm = load_model()

st.title("💬 Chat Local - LLaMA 3 8B Quantizado")

user_input = st.text_input("Digite sua pergunta:")

if user_input:
    with st.spinner("Pensando..."):
        output = llm(
            f"[INST] {user_input} [/INST]",
            temperature=0.7,
            top_p=0.9,
            max_tokens=512,
            stop=["</s>"]
        )
        resposta = output['choices'][0]['text']
        st.success(resposta.strip())