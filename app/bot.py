import os

from telebot.async_telebot import AsyncTeleBot

import utils
import keyboards as kb

token = os.environ.get("TELEGRAM_API_TOKEN", '')
bot = AsyncTeleBot(token)

conversation_states = {}


@bot.message_handler(commands=['start'])
async def start(message):
    text = f"""\
Hello, {message.from_user.first_name}
Welcome to <b><u>LinkShortener</u></b> Bot
"""
    await utils.add_user(message.from_user)
    await bot.send_message(message.chat.id, text, parse_mode='HTML', reply_markup=kb.keyboard_main)


@bot.message_handler(commands=['create'])
async def create_short_link(message):
    await bot.reply_to(message, "Enter your long link:")
    conversation_states[message.chat.id] = "action_create"


@bot.message_handler(commands=['update'])
async def update_short_link(message):
    await bot.reply_to(message, "Enter your short link:")
    conversation_states[message.chat.id] = "action_update_short"


@bot.message_handler(commands=['get_all'])
async def get_all_long_links(message):
    all_links = await utils.get_all_user_links(message.from_user.id)
    for link in all_links:
        reply_text = f"{link['short_url']} ---> {link['long_url']}"
        await bot.reply_to(message, reply_text)


@bot.message_handler(func=lambda message: True)
async def handle_text(message):
    chat_id = message.chat.id
    user_text = message.text
    reply_text = "  "

    if chat_id in conversation_states:
        if conversation_states[chat_id] == "action_create":
            long_url = user_text.replace(' ', '')
            short_url = await utils.add_short_link(long_url, user_id=message.from_user.id)
            reply_text = f"Created short url: {short_url}"
            del conversation_states[chat_id]

        elif conversation_states[chat_id] == "action_update_short":
            reply_text = "pass"
            del conversation_states[chat_id]
    else:
        short_url = message.text.replace(' ', '')
        long_url = await utils.get_long_link(short_url)
        if long_url:
            reply_text = f"Corresponding long url: {long_url}"
        else:
            reply_text = "Link does not exist"

    await bot.reply_to(message, reply_text, reply_markup=kb.keyboard_main)


import asyncio
asyncio.run(bot.polling())
