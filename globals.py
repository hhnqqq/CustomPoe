import os
import json
import pandas as pd

current_dir = os.getcwd()
paper_dir = r'your-file-path'
history_dir = os.path.join(current_dir, 'history')
keep_running = True
global_chat_history = []
global_token_usage = {}
client_dict = {}
history_name = None
config_path = os.path.join(current_dir,'defualt_config.json')
upload_img = os.path.join(current_dir, 'upload.png')
get_save_name_prompt = "请将以上对话总结成一个不超过六个字的标题。只输出标题，不输出额外的文本或解释:"
chat_cursor = 0


default_config = json.load(open(config_path,'r',encoding='utf-8'))
defualt_prompts = pd.DataFrame({"act":["empty", "default"], "prompt":["", default_config["default_system_prompt"]]})

diy_prompts = pd.concat([defualt_prompts, pd.read_excel(os.path.join(current_dir,'prompts.xlsx'))], axis=0)
personal_info = default_config.get("personal_info", None)
