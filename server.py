import asyncio
from aiogram import Bot, Dispatcher, executor, types
from cleaner import find_bots, find_inactive
from telethon.client import TelegramClient
from config import API_TOKEN, api_id, api_hash, CHANNEL, ME

bot = Bot(API_TOKEN, parse_mode='Html')
loop = asyncio.get_event_loop()
dp = Dispatcher(bot, loop=loop)


def delete_user_kb(user_id):
    kb = types.InlineKeyboardMarkup()
    kb.add(types.InlineKeyboardButton('Удалить из канала', callback_data=f'del:{user_id}'))
    return kb


@dp.callback_query_handler(text_startswith='del:')
async def del_user(query: types.CallbackQuery):
    try:
        user_id = int(query.data.split(':')[-1])
        await bot.kick_chat_member(CHANNEL, user_id)
        await query.answer('Удален')
    except:
        await query.answer('Ошибка')


@dp.message_handler(commands='days')
async def set_max_days_ago(msg: types.Message):
    try:
        days = int(msg.text.split()[-1])
        await msg.answer('Начинаю сбор')
        async for inactive_user in find_inactive(app, days):
            user_id, user_string, time_diff = inactive_user
            days = time_diff // (60 * 60 * 24)
            text = f'{user_string}:\n[Не был в сети больше {int(days)} дн.]'
            await msg.answer(text, reply_markup=delete_user_kb(user_id))
    except Exception as e:
        print(e)
        await msg.answer('Ошибка, отправтье /days [число]')


@dp.message_handler(commands='start')
async def cmd_start(msg: types.Message):
    await msg.answer("Приветствую, начинаю работу")


async def kick_bots(app, channel):
    while True:
        try:
            results = []
            async for user_bot in find_bots(app, channel):
                user_id = user_bot[0]
                print(user_bot)
                try:
                    results.append(user_bot[1])
                    await bot.kick_chat_member(channel, user_id)
                except:
                    print('Ошибка, не могу удалить')
            if results:
                text = '• ' + '\n• '.join(results)
                await bot.send_message(ME, text)
            await asyncio.sleep(60 * 60)
        except:
            await asyncio.sleep(60)
            print('Неизвестная ошибка')


if __name__ == '__main__':
    app = TelegramClient('account', api_id, api_hash)
    app.start()
    dp.loop.create_task(kick_bots(app, CHANNEL))
    executor.start_polling(dp, skip_updates=True)
