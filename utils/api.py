import json
import websocket
import random
import hashlib
import base64
import hmac
import string
import ssl
import openai
import re

from datetime import datetime
from wsgiref.handlers import format_date_time
from time import mktime
from urllib.parse import urlencode
from urllib.parse import urlparse
from openai import OpenAI
from typing import Optional, Union, List

from .utils import retry

@retry(max_attempts=3, delay=5, print_trace_back=True, return_error_info=True)
def call_gpt(prompt:str, 
             system_prompt:Optional[str],
             history:List[str]=[],
             client=None,
             base_url:Optional[str]=None,
             model:str="gpt-3.5-turbo", 
             api_key:Union[None,str]=None, 
             max_tokens:int=None, 
             temperature:float=0.7,
             logprobs:bool=False,
             top_logprobs:int=1,
             stream:bool=False,
             **kwargs) -> str:
    '''
    作用：openai库最新版的调用gpt的函数
    输入：prompt -> 提问的问题，model —> 调用的模型，max_tokens -> 最大的token数量， api_key（不能为空）
    输出：回答
    '''
    if 'qwen' in model and logprobs:
        return "logprobs is not supported by qwen currently", {"completion_tokens":0, "prompt_tokens":0, "total_tokens":0}
    if not client:
        assert api_key is not None,'请输入你的api key'
        client = OpenAI(
            api_key=api_key,
            base_url=base_url
            )
    if not logprobs:
        top_logprobs = None

    messages = [{"role": "system", "content": system_prompt}] if system_prompt is not None else []
    if history:
        for completion in history:
            if completion[1] is not None:
                assisant_content = re.sub(r'<span style="color: red;">.*?</span>:  ', '', completion[1])
                messages += [{"role": "user", "content": completion[0]}, {"role": "assistant", "content": assisant_content}] 
            else:
                messages += [{"role": "user", "content": completion[0]}]
    if prompt:
        messages.append({"role": "user", "content": prompt}) 
    print(messages)

    if stream:
        kwargs['stream_options']={"include_usage": True}

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        logprobs=logprobs,
        top_logprobs=top_logprobs,
        stream=stream,
        **kwargs
    )
    return response

@retry(max_attempts=3, delay=1)
def call_openai_emb(query:str,
                    api_key:str,
                    model:str="text-embedding-ada-002"):
    client = OpenAI(
    api_key=api_key
    )
    res = client.embeddings.create(input=query,
    model=model
    )
    return res


@retry(max_attempts=3, delay=5)
def oldv_call_gpt(prompt, 
                  api_key,
                  max_tokens:int=2048, 
                  temperature:float=0.7,
                  logprobs:bool=False,
                  top_logprobs:int=1):
    response = openai.ChatCompletion.create(
    model="gpt-3.5-turbo",  # 调用gpt3.5
    # model="gpt-4",  # 调用gpt4
    api_key = api_key,
    max_tokens = max_tokens,
    logprobs = logprobs,
    temperature = temperature,
    top_logprobs = top_logprobs,
    messages=[
        {"role": "user", "content": prompt},
    ]
)
    answer = response.choices[0].message.content.strip()
    return answer

class Spark(object):
    def __init__(self):
        self.request_url = "wss://spark-api.xf-yun.com/v3.1/chat"
        self.domain = 'generalv3'
        # self.request_url = "wss://spark-api-n.xf-yun.com/v1.1/chat"
        # self.domain = 'industry'
        self.method = 'GET'
        self.api_key = '8fc84059dffbf29f12e6eef15d39fe2c'
        self.api_secret = 'ZWZiYjc4MzgzZWNmZDRkZDZhNTdhNjBm'

        self.app_id = "5f5b57a1"
        self.uid = "8fc84059dffbf29f12e6eef15d39fe2c"
        self.wss_url = self.assemble_auth_url(request_url=self.request_url,
                                              method=self.method,
                                              api_key=self.api_key,
                                              api_secret=self.api_secret)
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})

    @staticmethod
    def assemble_auth_url(request_url, method, api_key, api_secret):
        u = urlparse(request_url)
        host = u.hostname
        path = u.path
        now = datetime.now()
        date = format_date_time(mktime(now.timetuple()))
        signature_origin = "host: {}\ndate: {}\n{} {} HTTP/1.1".format(host, date, method, path)
        signature_sha = hmac.new(api_secret.encode('utf-8'), signature_origin.encode('utf-8'),
                                 digestmod=hashlib.sha256).digest()
        signature_sha = base64.b64encode(signature_sha).decode(encoding='utf-8')
        authorization_origin = "api_key=\"%s\", algorithm=\"%s\", headers=\"%s\", signature=\"%s\"" % (
            api_key, "hmac-sha256", "host date request-line", signature_sha)
        authorization = base64.b64encode(authorization_origin.encode('utf-8')).decode(encoding='utf-8')
        values = {
            "host": host,
            "date": date,
            "authorization": authorization
        }
        return request_url + "?" + urlencode(values)

    @staticmethod
    def generate_uid():
        """随机扰动uid """
        return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

    @retry(max_attempts=3, delay=5)
    def connect_spark(self, question, history=None):
        if history is None:
            history = []
        wss_url = self.assemble_auth_url(request_url=self.request_url,
                                         method=self.method,
                                         api_key=self.api_key,
                                         api_secret=self.api_secret)
        self.ws.connect(wss_url)
        new_talk = {"role": "user", "content": question}
        history.append(new_talk)
        # print("history:", history)
        # 发送请求数据
        req = {
            "header": {
                "app_id": self.app_id,
                "uid": self.uid
            },
            "parameter": {
                "chat": {
                    # "domain": "iflycode.ge",
                    "domain": self.domain,
                    "temperature": 0.4,
                    "top_k": 5,
                    "max_tokens": 2048,
                    "auditing": "default"
                }
            },
            "payload": {
                "message": {
                    "text": history
                }
            }
        }
        data = json.dumps(req)
        self.ws.send(data)

        # 接收结果
        recv = True
        res = ''
        while recv:
            data = json.loads(self.ws.recv())
            # print(data)
            # 解析结果的格式
            text = data["payload"]["choices"]["text"]
            content = text[0]["content"]
            res += content
            code = data["header"]["code"]
            status = data["header"]["status"]
            # 出错 或者 收到最后一个结果， 就要退出
            if code != 0 or status == 2:
                recv = False
            # yield content

        self.ws.close()
        talk = {"role": "assistant", "content": res}
        history.append(talk)
        return history, res
