import os
import json
import time
import threading
import gradio as gr

from copy import copy
from collections import deque
from typing import Optional

from globals import *
from openai import OpenAI
from utils.api import call_gpt
from utils.constant import MODEL_URL
from utils import ensure_directory_exists, sort_files_by_mtime, manage_sys_prompt, open_file_dialog

def save_current_chat_history():
    save_chat_history = None
    while keep_running:
        save_path = os.path.join(history_dir, 'current.json')
        if global_chat_history and global_token_usage and global_chat_history != save_chat_history:
            with open(save_path, 'w', encoding='utf-8') as file:
                save_chat_history = copy(global_chat_history)
                json.dump({"history": global_chat_history, "usage": global_token_usage, "history_name": chat_history_name}, file, ensure_ascii=False)
        time.sleep(10)

save_thread = threading.Thread(target=save_current_chat_history, daemon=True)
save_thread.start()

def stop_save_thread():
    global keep_running
    keep_running = False
    save_thread.join()

import atexit
atexit.register(stop_save_thread)

with gr.Blocks(theme=gr.themes.Soft()) as demo:
    gr.Markdown(value='# Personal AI Model API Platform')
    ensure_directory_exists(history_dir)

    model_options = list(MODEL_URL.keys())
    token_usage_dict = {}

    with gr.Tab("Chat"):
        with gr.Row():
            with gr.Column():
                chat_history_selector = gr.Dropdown(label="Chat History", choices=[file_name.strip('.json') for file_name in sort_files_by_mtime(history_dir)])
                diy_prompt_selector = gr.Dropdown(choices=diy_prompts['act'].to_list(), label='Diy prompts')
                with gr.Row():
                    model_selector = gr.Dropdown(choices=model_options,
                                                allow_custom_value=True,
                                                value=default_config.get("default_model", model_options[0]),
                                                label="Model",
                                                info="Select model for chat")
                    temperature_slider = gr.Slider(minimum=0.0,
                                                maximum=1.0,
                                                value=0.7,
                                                step=0.1,
                                                label="Temperature")
                    max_source_length_input = gr.Number(label="Max Source Length",
                                                        info="Maximum length of input text",
                                                        value=None)
                with gr.Row():
                    logprobs_checkbox = gr.Checkbox(label="Logprobs", 
                                                    info="Whether to use logprobs", 
                                                    show_label=True,
                                                    value=False)
                    top_logprobs_input = gr.Number(label="Top Logprobs", 
                                                info="Please input your top logprobs", 
                                                value=1)
                    single_turn_checkbox = gr.Checkbox(label="Single Turn", 
                                            info="Whether to use chat history", 
                                            show_label=True,
                                            value=False)
                token_usage_display = gr.JSON({}, label='Token Usage', visible=False)
                
            with gr.Column():
                chat_bot = gr.Chatbot(height=850, 
                                      show_copy_button=True, 
                                      placeholder='## ![](ai.jpg) Hello, what can i help you today?',
                                      latex_delimiters=[{"left": "$$", "right": "$$", "display": True},
                                                        {"left": r"$$\n", "right": r"$$\n", "display": True},
                                                        {"left": r"\[", "right": r"\]", "display": True},
                                                        {"left": r"\begin{equation}", "right": r"\end{equation}", "display": True},
                                                        {"left": r"\begin{align}", "right": r"\end{align}", "display": True},
                                                        {"left": r"\begin{gather}", "right": r"\end{gather}", "display": True},
                                                        {"left": r"\begin{CD}", "right": r"\end{CD}", "display": True},
                                                        {"left": "$", "right": "$", "display": False},
                                                        {"left": r"\(", "right": r"\)", "display": False}],
                                      avatar_images=[os.path.join(current_dir, 'programmer.jpg'), 
                                                     os.path.join(current_dir, 'ai.jpg')])
                system_prompt_input = gr.Textbox(label='Set Systematic Prompt', 
                                        value=default_config.get("default_system_prompt", None))
                user_message_input = gr.Textbox(label="Enter Your Prompt")
                with gr.Row():
                    new_chat_button = gr.Button("New Chat")
                    clear_button = gr.Button("Clear")
                    save_button = gr.Button('Save')
                    redo_button = gr.Button('Redo')
                    file_upload_button = gr.Button("Upload file", icon=upload_img)
                    file_upload_path = gr.Textbox(visible=False)

    with gr.Tab('Settings'):
        with gr.Column():
            gr.Markdown(value='## Base Settings')
            default_model_selector = gr.Dropdown(choices=model_options,
                                        label="Model",
                                        info="Choose default model",
                                        value=default_config.get("default_model", model_options[0]))
            default_system_prompt_input = gr.Textbox(label='Set Default Systematic Prompt',
                                            value=default_config.get("default_system_prompt", None))
            with gr.Row():
                user_name_input = gr.Textbox(label='Set Your Name',
                                  value=personal_info.get("name", None))
                user_age_input = gr.Number(label='Set Your Age',
                                value=personal_info.get("age", None))
                user_description_input = gr.Textbox(label='Set Your Description',
                                         value=personal_info.get("description", None))

            submit_button = gr.Button("Submit")
        with gr.Column():
            gr.Markdown(value='## Custom Prompts')
            with gr.Row():
                diy_prompt_name_input = gr.Textbox(label='Set Name for Custom Prompt',)
                diy_prompt_content_input = gr.Textbox(label='Set Content for Custom Prompt')
            add_button = gr.Button("Add")
            current_diy_prompts_display = gr.Dataframe(value=diy_prompts,
                                              datatype=['str','str'], 
                                              interactive=True, 
                                              label='Current Custom Prompts List', 
                                              col_count=2, 
                                              row_count=10)

    def save_settings(default_model, default_system_prompt, user_name, user_age, user_description):
        global default_config
        global personal_info
        settings_data = {
            'default_model': default_model,
            'default_system_prompt': default_system_prompt,
            'personal_info':{
            'name': user_name,
            'age': user_age,
            'description': user_description
            }
        }
        default_config = settings_data
        personal_info  = settings_data['personal_info']
        with open(config_path, 'w', encoding='utf-8') as file:
            json.dump(settings_data, file, ensure_ascii=False)
        gr.Info("Config saved successfully")
        return (gr.Dropdown(choices=model_options,
                    value=default_model,
                    label="Model",
                    info="Select model for chat"),
                gr.Textbox(label='Set Systematic Prompt', 
                    value=default_system_prompt),
                gr.Dropdown(choices=model_options,
                    value=default_model,
                    label="Model",
                    info="Select model for chat"),
                gr.Textbox(label='Set Default Systematic Prompt',
                    value=default_system_prompt),
                gr.Textbox(label='Set Your Name',
                    value=user_name),
                gr.Number(label='Set Your Age',
                    value=user_age),
                gr.Textbox(label='Set Your Description',
                    value=user_description))

    def user_input(user_message, chat_history: list, max_source_length: Optional[int] = None):
        chat_history.append([user_message, None])
        
        if max_source_length:
            message_length_every_turn = [sum(len(message) for message in turn) for turn in chat_history]
            total_chat_length = sum(message_length_every_turn)
            
            if total_chat_length > max_source_length:
                length_count = 0
                cut_turns_count = len(chat_history)
                
                for idx, length in enumerate(reversed(message_length_every_turn)):
                    length_count += length
                    if length_count > max_source_length:
                        cut_turns_count = len(chat_history) - idx - 1
                        break
                
                chat_history = chat_history[cut_turns_count:]
                gr.Info("The chat history exceeded the maximum length and has been truncated.")
        
        return "", chat_history
    
    def redo_input(chat_history):
        chat_history[-1][1] = None
        return "", chat_history

    def save_chat_data(chat_history, system_prompt, model_name):
        global global_chat_history
        global chat_history_name
        if chat_history_name:
            save_name = chat_history_name
            chat_history_name = None
        else:
            base_url, api_key = tuple(MODEL_URL[model_name].values())
            client_existed = base_url in client_dict.keys()
            if not client_existed:
                client_dict[base_url] = OpenAI(base_url=base_url, api_key=api_key)
            response = call_gpt(prompt=get_save_name_prompt,
                                system_prompt=system_prompt,
                                history=chat_history,
                                model=model_name,
                                temperature=0,
                                logprobs=None,
                                top_logprobs=1,
                                client=client_dict[base_url])
            save_name = response.choices[0].message.content.replace(' ', '_')
        save_path = os.path.join(history_dir, save_name + '.json').strip("\"")
        with open(save_path, 'w', encoding='utf-8') as file:
            gr.Info(message=f'Saving chat history at {save_path}')
            json.dump({"history": chat_history, "usage": token_usage_dict}, file, ensure_ascii=False)
        global_chat_history = []
        return [], gr.Dropdown(label="Chat History", choices=[file_name.strip('.json') for file_name in sort_files_by_mtime(history_dir)])
    
    def reset_chat():
        global global_chat_history
        global global_token_usage
        global chat_history_name
        chat_history_name = None
        global_chat_history = []
        global_token_usage = {}
        return [], gr.JSON({}, visible=False), gr.Textbox(visible=False)
    
    def read_current_chat_history():
        global global_chat_history
        global global_token_usage
        global chat_history_name
        path = os.path.join(history_dir, 'current.json')
        try:
            history_dict = json.load(open(path, 'r', encoding='utf-8'))
            chat_history = history_dict["history"]
            token_usage_dict = history_dict["usage"]
            chat_history_name = history_dict.get("history_name", None)
        except:
            chat_history = []
            token_usage_dict = {}
            chat_history_name = None
        global_chat_history = chat_history
        global_token_usage = token_usage_dict
        return chat_history, gr.JSON(token_usage_dict, label='Token Usage', visible=True)

    def read_chat_history(file_name):
        global chat_history_name
        chat_history_name = file_name
        path = os.path.join(history_dir, file_name+'.json')
        history_dict = json.load(open(path, 'r', encoding='utf-8'))
        chat_history = history_dict["history"]
        token_usage = history_dict["usage"]
        return chat_history, gr.JSON(token_usage, label='Token Usage', visible=True)
    
    def add_diy_prompt(diy_prompt_name, diy_prompt, current_prompts):
        if diy_prompt_name is None:
            gr.Error('please input the name of the diy prompt')
        if diy_prompt is None:
            gr.Error('please input the content of the diy prompt')
        current_prompts = pd.concat([pd.DataFrame({'act':diy_prompt_name, 'prompt':diy_prompt}, current_prompts)])
        current_prompts.to_excel(os.path.join(current_dir,'prompts.xlsx'))
        return gr.DataFrame(current_prompts), gr.Dropdown(choices=current_prompts['act'].to_list(), label='please choose a prompt as system prompt')
    
    def choose_diy_prompt(diy_prompt_name, current_prompts):
        prompts_dict = current_prompts.set_index('act')['prompt'].to_dict()
        prompt = prompts_dict[diy_prompt_name]
        return gr.Textbox(label='Set Systematic Prompt', 
                          value=prompt)
    
    def get_chat_cursor(chat_history):
        global chat_cursor
        gr.Info('Context clear')
        chat_cursor = len(chat_history)

    def bot_response(chat_history, 
                     system_prompt, 
                     file_path, 
                     model_name, 
                     temperature, 
                     logprobs, 
                     top_logprobs, 
                     single_turn):
        global chat_cursor
        global global_chat_history
        global global_token_usage
        try:
            top_logprobs_value = int(top_logprobs)
        except ValueError:
            top_logprobs_value = 1

        if logprobs and top_logprobs_value > 1:
            gr.Warning(message="Logprobs must be true when top_logprobs is greater than 1")
            top_logprobs_value = 1

        base_url, api_key = tuple(MODEL_URL[model_name].values())
        client = client_dict.get(base_url, OpenAI(base_url=base_url, api_key=api_key))
        client_dict[base_url] = client

        if single_turn:
            input_history = None
            prompt = chat_history[-1][0]
        else:
            input_history = chat_history[chat_cursor:]
            prompt = None

        system_prompt = manage_sys_prompt(personal_info, system_prompt, file_path)
        response = call_gpt(prompt=prompt,
                            system_prompt=system_prompt,
                            history=input_history,
                            model=model_name,
                            temperature=temperature,
                            logprobs=logprobs,
                            top_logprobs=top_logprobs_value,
                            client=client_dict[base_url],
                            stream=True)

        if model_name not in token_usage_dict.keys():
            token_usage_dict[model_name] = dict(completion_tokens=0, prompt_tokens=0, total_tokens=0)

        global_chat_history = chat_history
        global_chat_history[-1][1] = f'<span style="color: red;">{model_name}</span>:  '
        for chunk in response:
            chunk_message = chunk.choices
            chunk_usage = chunk.usage
            if chunk_usage is not None:
                token_usage_dict[model_name]["completion_tokens"]+=chunk_usage.completion_tokens
                token_usage_dict[model_name]["prompt_tokens"]+=chunk_usage.prompt_tokens
                token_usage_dict[model_name]["total_tokens"]+=chunk_usage.total_tokens
                global_token_usage = token_usage_dict
                yield global_chat_history, gr.JSON(token_usage_dict, label='Token Usage', visible=True)

            if chunk_message and global_chat_history:
                chunk_message_content = chunk_message[0].delta.content
                chunk_message_content = '' if chunk_message_content is None else chunk_message_content
                for i in chunk_message_content:
                    global_chat_history[-1][1] += i
                    yield global_chat_history, gr.JSON(token_usage_dict, label='Token Usage', visible=True)
            


    save_button.click(save_chat_data, [chat_bot, system_prompt_input, model_selector], [chat_bot, chat_history_selector], queue=False)
    clear_button.click(reset_chat, None, [chat_bot, token_usage_display, file_upload_path])
    new_chat_button.click(get_chat_cursor, [chat_bot], None)
    file_upload_button.click(open_file_dialog, None, [file_upload_path])
    chat_history_selector.change(read_chat_history, [chat_history_selector], [chat_bot, token_usage_display])
    demo.load(read_current_chat_history, None, [chat_bot, token_usage_display])
    add_button.click(add_diy_prompt, [diy_prompt_name_input, diy_prompt_content_input, current_diy_prompts_display], [current_diy_prompts_display, diy_prompt_selector])
    diy_prompt_selector.change(choose_diy_prompt, [diy_prompt_selector, current_diy_prompts_display], [system_prompt_input])

    user_message_input.submit(user_input, [user_message_input, chat_bot], [user_message_input, chat_bot], queue=False).then(
        bot_response, 
        [chat_bot, 
         system_prompt_input, 
         file_upload_path,
         model_selector, 
         temperature_slider, 
         logprobs_checkbox, 
         top_logprobs_input, 
         single_turn_checkbox], 
         [chat_bot, 
          token_usage_display])

    redo_button.click(redo_input, [chat_bot], [user_message_input, chat_bot], queue=False).then(
        bot_response, 
        [chat_bot, 
         system_prompt_input, 
         file_upload_path,
         model_selector, 
         temperature_slider, 
         logprobs_checkbox, 
         top_logprobs_input, 
         single_turn_checkbox], 
         [chat_bot, 
          token_usage_display])
    
    submit_button.click(
        save_settings, 
        [default_model_selector, 
        default_system_prompt_input, 
        user_name_input, 
        user_age_input, 
        user_description_input], 
        [model_selector, 
        system_prompt_input, 
        default_model_selector, 
        default_system_prompt_input, 
        user_name_input, 
        user_age_input, 
        user_description_input])



demo.queue(api_open=False)
demo.launch()
