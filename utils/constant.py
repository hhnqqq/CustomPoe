#############################***API_KEYS***###########################################################
GPT_API_KEYS = ''''''

OLDV_API_KEYS = '''sk-K4SNFURDK1eIpNhCImHymNCwKEO48V3OTZcGT8HwUlZUOBiA'''

_API_BASE_URL = {
    "openai": {"base_url":"https://api.chatanywhere.tech/v1",
               "api_key":""},
    "moonshot": {"base_url":"https://api.moonshot.cn/v1",
                 "api_key":""},
    "deepseek": {"base_url":"https://api.deepseek.com/v1",
                 "api_key":"sk-dd2770815524449ab58f2e5e921839b5"},
    "zhipu": {"base_url":"https://open.bigmodel.cn/api/paas/v4/",
                 "api_key":""},
    "ali": {"base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "api_key":""},
    "yi": {"base_url": "https://api.lingyiwanwu.com/v1",
            "api_key":"6c95177f09464ddbba183690c1782d64"},
    "baichuan": {"base_url": "https://api.baichuan-ai.com/v1/",
                 "api_key": ""},
    "minimax": {"base_url": "https://api.minimax.chat/v1/text/chatcompletion_v2",
                "api_key": ""},   
}

_OPENAI_MODELS = [
    "gpt-3.5-turbo-1106",
    "gpt-3.5-turbo-0125",
    "gpt-3.5-turbo-0613",
    "gpt-3.5-turbo-0301",
    "gpt-3.5-turbo-16k",
    "gpt-3.5-turbo-16k-0613",
    "gpt-3.5-turbo-ca",
    "gpt-4",
    "gpt-4-1106-preview",
    "gpt-4-0125-preview",
    "gpt-4-vision-preview",
    "gpt-4-turbo",
    "gpt-4o"
]

_MOONSHOT_MODELS = [
    "moonshot-v1-8k",
    "moonshot-v1-32k",
    "moonshot-v1-128k"
]

_DEEPSEEK_MODELS = [
    "deepseek-chat",
    "deepseek-coder"
]

_ZHIPU_MODELS = [
    "glm-4-0520",
    "glm-4",
    "glm-4-air",
    "glm-4-airx", 
    "glm-4-flash"
    "glm-3-turbo",
    "glm-4v"
]

_ALI_MODELS = [
    "qwen-turbo",
    "qwen-plus",
    "qwen-max",
    "qwen-max-0428",
    "qwen-max-0403",
    "qwen-max-0107",
    "qwen-max-longcontext"
]

_YI_MODELS = [ 
    "yi-large", 
    "yi-medium", 
    "yi-vision", 
    "yi-medium-200k", 
    "yi-spark", 
    "yi-large-rag", 
    "yi-large-turbo", 
    "yi-large-preview", 
    "yi-large-rag-preview" 
]

_BAICHUAN_MODELS = [
    "Baichuan4",
    "Baichuan3-Turbo",
    "Baichuan3-Turbo-128k",
    "Baichuan2-Turbo",
    "Baichuan2-Turbo-192k"
]

_MINIMAX_MODELS = [
    "abab6.5",
    "abab6.5s",
    "abab6.5t",
    "abab6.5g",
    "abab5.5",
    "abab5.5s",
]

MODEL_URL = {
    model: _API_BASE_URL["openai"] for model in _OPENAI_MODELS
}
MODEL_URL.update({
    model: _API_BASE_URL["moonshot"] for model in _MOONSHOT_MODELS
})
MODEL_URL.update({
    model: _API_BASE_URL["deepseek"] for model in _DEEPSEEK_MODELS
})
MODEL_URL.update({
    model: _API_BASE_URL["zhipu"] for model in _ZHIPU_MODELS
})
MODEL_URL.update({
    model: _API_BASE_URL["ali"] for model in _ALI_MODELS
})
MODEL_URL.update({
    model: _API_BASE_URL["yi"] for model in _YI_MODELS
})
MODEL_URL.update({
    model: _API_BASE_URL["baichuan"] for model in _BAICHUAN_MODELS
})
MODEL_URL.update({
    model: _API_BASE_URL["minimax"] for model in _MINIMAX_MODELS
})


