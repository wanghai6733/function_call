from zhipuai import ZhipuAI
import requests
import json



# 查询天气函数
def fetch_real_weather(location: str, unit: str = "celsius"):
    """调用真实的天气 API 获取天气信息"""
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={WEATHER_API_KEY}&units={'metric' if unit == 'celsius' else 'imperial'}"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        weather_desc = data["weather"][0]["description"]
        temp = data["main"]["temp"]
        return f"The weather in {location} is {weather_desc} with a temperature of {temp}°{unit[0].upper()}."
    else:
        return f"Sorry, I couldn't fetch the weather for {location}."


# 解析调用工具
tool2func = {
    "get_weather":fetch_real_weather,
}
def parse_res(res):
    for tool in res.tool_calls:
        func = tool2func[tool.function.name]
        message = {"role": "tool", 
         "content": func(**json.loads(tool.function.arguments)),
         "tool_call_id":tool.id}
        messages.append(message)

# 初始配置

client = ZhipuAI(api_key=ZHIPU_API_KEY)
system_prompt = "你是一个天气查询小助手，请注意调用函数get_weather时，传入的参数需要翻译为英文。"
messages = []
messages.append({"role": "system", "content": system_prompt})

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get the weather for a location, all the parameters Must be translated in English.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "City name, e.g., New York;City name must be translated in English, e.g.,北京->Beijing"},
                    "unit": {"type": "string", "enum": ["celsius", "fahrenheit"]}
                },
                "required": ["location"]
            }
        }
    },
]


# 会话
# sample 1 
# query = input("user")
# messages.append({"role": "user", "content": "i want to know the weather of shanghai and capital of China"})
# response = client.chat.completions.create(
#             model="glm-4-plus",  # 填写需要调用的模型名称
#             messages=messages,
#             tools=tools,
#         )
# res = response.choices[0].message
# print(res)

while True:
    query = input("user:")
    messages.append({"role": "user", "content": query})
    while True:
        response = client.chat.completions.create(
            model="glm-4-plus",  # 填写需要调用的模型名称
            messages=messages,
            tools=tools,
        )
        res = response.choices[0].message
        messages.append(res.model_dump())

        if res.tool_calls != None:
            parse_res(res)
        else:
            print(f"assistant:{res.content}") 
            break
    
    # print(messages)
        


