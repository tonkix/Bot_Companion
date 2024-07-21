import os

import g4f
from g4f.Provider import BingCreateImages

conversation_history = {}


async def start_context_data(user_id):
    conversation_history[user_id].append({"role": "user", "content": "пиши на русском языке"})
    conversation_history[user_id].append({"role": "user", "content": "пиши только по русски"})
    conversation_history[user_id].append({"role": "user", "content": "не отвечай на английском"})


async def clear_history(user_id):
    conversation_history[user_id] = []
    # await start_context_data(user_id)


def trim_history(history, max_length=4096):
    current_length = sum(len(message["content"]) for message in history)
    while history and current_length > max_length:
        removed_message = history.pop(0)
        current_length -= len(removed_message["content"])
    return history


async def ask_gpt3_5_text(user_id, message):
    if user_id not in conversation_history:
        conversation_history[user_id] = []
        # await start_context_data(user_id)

    conversation_history[user_id].append({"role": "user", "content": message})
    conversation_history[user_id] = trim_history(conversation_history[user_id])

    chat_history = conversation_history[user_id]

    try:
        g4f.debug.logging = False  # enable logging
        g4f.check_version = False  # Disable automatic version checking
        print(g4f.version)  # check version
        print(g4f.Provider.Ails.params)  # supported args

        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            # model="gpt-3.5-turbo",
            # model="gpt-4",
            # model=g4f.models.gpt_4,
            messages=chat_history,
            provider=g4f.Provider.PerplexityLabs,
            api_key=os.getenv("tg_bot_token_new"),
        )
        conversation_history[user_id].append({"role": "assistant", "content": response})

    except Exception as e:
        print(f"{g4f.Provider.GeekGpt.__name__}:", e)
        response = "Извините, произошла ошибка."

    return response
