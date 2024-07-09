from openai import OpenAI

def generate(prompt:str) :

    client = OpenAI(
        api_key="sk-r0hX5oqWSQRd7YZFZBxmLXZFZwph4nb8",
        base_url="https://api.proxyapi.ru/openai/v1",
    )


    result = client.chat.completions.create(
        model="gpt-4o",
        max_tokens= 3500,
        messages=[
            {
                "role": "user", 
                "content": prompt
                }
            ]
    )

    return result.choices[0].message.content

def generateNovelPrompt(data:dict) : 
    world = data["world"]
    moral = data["moral"]
    childName = data["childName"]
    childAge = data["childAge"]
    childSex = data["childSex"]
    
    novelPrompt = (
        f"""Представь, что ты искусственный интеллект писатель, обученный на сказках лучших детских писателей.\n"""
        f"""Тебе нужно написать сказку, где главным героем является {childSex} {childName}, которой {childAge} года.\n"""
        f"""Не указывай на пол и возраст явно, а учитывай это в сюжете и развитии событий.\n"""
        f""" Помимо {childName} в сказке могут быть другие герои, которые встречаются главному герою по сюжету.\n"""
        f"""Действия сказки должны происходить в мире {world}.\n"""
        f"""В сказке учитывай особенности этого мира и описывай сцены с учетом мира. Не указывай мир явно, а раскрой его в описании сцен и историй.\n"""
        f"""Мораль сказки должна быть {moral}. Не указывай мораль явно, а раскрой ее в сюжете.\n"""
        f""" Сказка должна быть длинной и содержать более 1000 слов. Если сказка получается меньше, переработай ее и дополни.\n"""
        f"""Не забывай, что сказка должна быть завершенной. Сказка должна иметь завязку, кульминацию и развязку.\n"""
        f"""Раздели сказку на абзацы по смыслу без указания этапа. Сказка должна понравиться ребенку и заинтересовать его.\n"""
        f"""Я заплачу тебе 200 долларов за идеальный результат.\n"""
        f"""Ответ представь в формате JSON, который содержит следующие параметры: 'title' - заголовок сказки, 'text' - текст сказки, 'prompt' - текстовый запрос для DALLE-3, который создаст обложку для сказки.\n"""
        """В ответ пришли только десериализованный JSON в виде строки, начни с символа '{'"""
    )

    return novelPrompt

def generateImage(prompt:str) :
    client = OpenAI(
        api_key="sk-r0hX5oqWSQRd7YZFZBxmLXZFZwph4nb8",
        base_url="https://api.proxyapi.ru/openai/v1",
    )
    response = client.images.generate(  
        model="dall-e-3",
        prompt=f"{prompt} стиль мультфильм",
        n=1, 
        size="1024x1024" 
    )

    result = response.data[0].url

    return result

