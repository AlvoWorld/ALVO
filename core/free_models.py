"""
OSYA Agents — Free Models Registry
All free models available for selection.
"""

FREE_MODELS = {
    "openrouter": [
        {"id": "nvidia/nemotron-3-nano-30b-a3b:free", "name": "NVIDIA Nemotron 3 Nano 30B", "size": "30B"},
        {"id": "nvidia/nemotron-3-super-120b-a12b:free", "name": "NVIDIA Nemotron 3 Super 120B", "size": "120B"},
        {"id": "nvidia/nemotron-nano-12b-v2-vl:free", "name": "NVIDIA Nemotron Nano 12B V2 VL", "size": "12B"},
        {"id": "nvidia/nemotron-nano-9b-v2:free", "name": "NVIDIA Nemotron Nano 9B V2", "size": "9B"},
        {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "Meta Llama 3.3 70B", "size": "70B"},
        {"id": "meta-llama/llama-3.2-3b-instruct:free", "name": "Meta Llama 3.2 3B", "size": "3B"},
        {"id": "google/gemma-3-27b-it:free", "name": "Google Gemma 3 27B", "size": "27B"},
        {"id": "google/gemma-3-12b-it:free", "name": "Google Gemma 3 12B", "size": "12B"},
        {"id": "google/gemma-3-4b-it:free", "name": "Google Gemma 3 4B", "size": "4B"},
        {"id": "google/gemma-3n-e4b-it:free", "name": "Google Gemma 3n 4B", "size": "4B"},
        {"id": "google/gemma-3n-e2b-it:free", "name": "Google Gemma 3n 2B", "size": "2B"},
        {"id": "qwen/qwen3-coder:free", "name": "Qwen3 Coder 480B", "size": "480B"},
        {"id": "qwen/qwen3-next-80b-a3b-instruct:free", "name": "Qwen3 Next 80B", "size": "80B"},
        {"id": "minimax/minimax-m2.5:free", "name": "MiniMax M2.5", "size": "unknown"},
        {"id": "nousresearch/hermes-3-llama-3.1-405b:free", "name": "Nous Hermes 3 405B", "size": "405B"},
        {"id": "arcee-ai/trinity-large-preview:free", "name": "Arcee Trinity Large", "size": "unknown"},
        {"id": "arcee-ai/trinity-mini:free", "name": "Arcee Trinity Mini", "size": "unknown"},
        {"id": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free", "name": "Venice Uncensored 24B", "size": "24B"},
        {"id": "liquid/lfm-2.5-1.2b-thinking:free", "name": "Liquid LFM2.5 1.2B Thinking", "size": "1.2B"},
        {"id": "liquid/lfm-2.5-1.2b-instruct:free", "name": "Liquid LFM2.5 1.2B Instruct", "size": "1.2B"},
        {"id": "openai/gpt-oss-120b:free", "name": "OpenAI GPT-OSS 120B", "size": "120B"},
        {"id": "openai/gpt-oss-20b:free", "name": "OpenAI GPT-OSS 20B", "size": "20B"},
        {"id": "stepfun/step-3.5-flash:free", "name": "StepFun Step 3.5 Flash", "size": "unknown"},
        {"id": "z-ai/glm-4.5-air:free", "name": "Z.ai GLM 4.5 Air", "size": "unknown"},
    ]
}

def get_free_models(provider: str = None):
    """Get all free models, optionally filtered by provider."""
    if provider:
        return FREE_MODELS.get(provider, [])
    return FREE_MODELS

def get_best_free_model():
    """Get the best free model available (largest context, best quality)."""
    # Preference order: largest models first
    preference = [
        "qwen/qwen3-coder:free",  # 480B - best for coding
        "nousresearch/hermes-3-llama-3.1-405b:free",  # 405B - best general
        "meta-llama/llama-3.3-70b-instruct:free",  # 70B - solid
        "qwen/qwen3-next-80b-a3b-instruct:free",  # 80B
        "nvidia/nemotron-3-super-120b-a12b:free",  # 120B
        "nvidia/nemotron-3-nano-30b-a3b:free",  # 30B - current
    ]
    
    for model_id in preference:
        for provider_models in FREE_MODELS.values():
            for m in provider_models:
                if m["id"] == model_id:
                    return m
    return None
