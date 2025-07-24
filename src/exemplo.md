# Execução Local de LLaMA 2 7B Quantizado com Streamlit

Bem-vindo ao guia prático para executar o modelo **LLaMA 2 7B quantizado (GGUF 4-bit)** localmente com interface em **Streamlit**! 
Ideal para testes, demonstrações e projetos offline com performance leve e responsiva.

## 📦 Requisitos Iniciais
- Modelo `.gguf` quantizado (ex: `llama-2-7b-chat.gguf.q4_K_M.bin`)
- Placa de vídeo com **8GB de VRAM** ou superior
- Lembre de instalar um compilador C/C++ recomenda-se a
 utilização do Build Tools do Visual Studio
- é necessário caso queira utilizar a gpu instalar o ToolKit CUDA da NVIDIA 
- é necessario instalar o CMAKE TOOLS
- Instalação das bibliotecas:

```bash
git clone --recurse-submodules https://github.com/abetlen/llama-cpp-python.git
cd llama-cpp-python

$env:CMAKE_ARGS="-DGGML_CUDA=ON -DGGML_AVX512=ON -DGGML_CUDA_FA_ALL_QUANTS=ON -DGGML_CUDA_MMV_Y=2 -DGGML_CUDA_PEER_MAX_BATCH_SIZE=4096 -DGGML_CUDA_USE_GRAPHS=ON"
pip install --verbose .[server] // O processo pode demorar
```

## 🛠️ Estrutura do Projeto
- `app.py`: Interface Streamlit com campo de entrada e resposta
- `model/`: Pasta onde deve estar o arquivo `.gguf` do modelo

- Arquivo `.gguf` que deve ser baixado diretamento do repositorio do github ou HuggingFace do modelo de preferência usado no exemplo --> "https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/tree/main"

## 🧪 Código de Exemplo (`app.py`)
```python
import streamlit as st
from llama_cpp import Llama

MODEL_PATH = "model/llama-2-7b-chat.gguf.Q4_K_M.gguf"

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
