from concurrent.futures import ThreadPoolExecutor
import asyncio, os
from llama_cpp import Llama

_MODEL_PATH = r"C:\Users\vinic\Desktop\IA CMAKER\testes\model\Meta-Llama-3.1-8B-Instruct-Q5_K_M.gguf"
_llm = Llama(model_path=_MODEL_PATH, n_ctx=2048, n_threads=8, n_gpu_layers=40)

_executor = ThreadPoolExecutor(max_workers=2)       # pool dedicado

async def generate(prompt: str) -> str:
    loop = asyncio.get_running_loop()
    def _infer():
        out = _llm(prompt, temperature=0.1, top_p=0.95,
                   max_tokens=300, stop=["}"])
        return out["choices"][0]["text"] + "}"
    return await loop.run_in_executor(_executor, _infer)
