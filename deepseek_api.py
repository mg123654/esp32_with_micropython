# deepseek_api.py
# 用于与DeepSeek API交互的接口模块

# 缓冲区用于存储API响应
response_buffer = ""

# 输入缓冲区用于存储待发送文本
input_buffer = ""

def set_input(text):
    """
    设置要发送到DeepSeek API的文本
    """
    global input_buffer
    input_buffer = text

def get_response():
    """
    获取最近一次DeepSeek API响应的文本
    """
    global response_buffer
    return response_buffer


import urequests

# DeepSeek API 公开接口（如需更换请修改此处）
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
# 请将 YOUR_API_KEY 替换为你的 DeepSeek API-KEY
DEEPSEEK_API_KEY = "YOUR_API_KEY"

def send_to_deepseek():
    """
    发送 input_buffer 到 DeepSeek API，并将响应写入 response_buffer
    """
    global input_buffer, response_buffer
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer {}".format(DEEPSEEK_API_KEY)
    }
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": input_buffer}
        ]
    }
    try:
        resp = urequests.post(DEEPSEEK_API_URL, json=data, headers=headers)
        if resp.status_code == 200:
            result = resp.json()
            # 解析标准API返回结构
            if "choices" in result and len(result["choices"]) > 0:
                response_buffer = result["choices"][0]["message"]["content"]
            else:
                response_buffer = "[API无有效回复]"
        else:
            response_buffer = "[HTTP错误] {}".format(resp.status_code)
        resp.close()
    except Exception as e:
        response_buffer = "[请求异常] {}".format(e)
