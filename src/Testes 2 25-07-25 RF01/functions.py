from llama_cpp import Llama

MODEL_PATH = r"C:\Users\vinic\Desktop\IA CMAKER\testes\model\Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf"

llm = Llama(
    model_path=MODEL_PATH,
    n_ctx=2048,
    n_threads=8,
    n_gpu_layers=40,
    f16_kv=True
)

def pergunta_ia(user_input):
    output = llm(                   # ← envia prompt cru,
        user_input,                     #   sem [INST]
        temperature=0.1,
        top_p=0.95,
        max_tokens=300,
        stop=["}"] 
    )
    resposta = output['choices'][0]['text'] + "}" 
    resposta_formatada = resposta.strip() 
    return resposta_formatada[:2000]