# Execução Local de LLaMA 2 7B Quantizado com Streamlit

Bem-vindo ao guia prático para executar o modelo **LLaMA 2 7B quantizado (GGUF 4-bit)** localmente com interface em **Streamlit**! 
Ideal para testes, demonstrações e projetos offline com performance leve e responsiva.

## 📦 Requisitos Iniciais
- Modelo `.gguf` quantizado (ex: `llama-2-7b-chat.gguf.q4_K_M.bin`)
- Placa de vídeo com **8GB de VRAM** ou superior
- Instalação das bibliotecas:

```bash
pip install streamlit llama-cpp-python
```

## 🛠️ Estrutura do Projeto
- `app.py`: Interface Streamlit com campo de entrada e resposta
- `model/`: Pasta onde deve estar o arquivo `.gguf` do modelo

## 🧪 Código de Exemplo (`app.py`)
```python
import streamlit as st
from llama_cpp import Llama

MODEL_PATH = "model/llama-2-7b-chat.gguf.q4_K_M.bin"

@st.cache_resource
def load_model():
    return Llama(
        model_path=MODEL_PATH,
        n_ctx=2048,
        n_threads=8,
        n_gpu_layers=20,
        f16_kv=True
    )

llm = load_model()

st.title("💬 Chat Local - LLaMA 2 7B Quantizado")

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
```

## 📋 O que está acontecendo
- O modelo é carregado com cache para desempenho.
- As mensagens do usuário são formatadas no estilo `[INST]...[/INST]`.
- A resposta é exibida com `st.success()` após o processamento.

## ⚡ Dicas de Otimização
- Use `n_gpu_layers=20` para aproveitar a GPU (em placas com 8GB).
- Experimente `low_vram=True` para cargas mais leves.
- Para histórico de conversa, utilize `st.session_state` para armazenar os prompts.

## 🚀 Resultados Esperados
- Tempo de resposta entre **1 e 2 segundos** por prompt.
- Totalmente offline e personalizável.
- Ideal para experiências educacionais, protótipos ou laboratórios locais.

---

Caso deseje uma versão com **histórico de conversa**, **ajustes de temperatura**, ou **botão de limpar conversa**, consulte o README completo ou fale comigo! 🚀
