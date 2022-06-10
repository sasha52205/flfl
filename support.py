from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Command

from data.config import admins, secret
from keyboards.inline.support import support_keyboard, support_callback, get_support_manager
from loader import dp, bot

from utils.db_api import quick_commands as commands



@dp.message_handler(Command("support"))
async def ask_support(message: types.Message):
    text = "Хотите написать сообщение техподдержке? Нажмите на кнопку ниже!"
    keyboard = await support_keyboard(messages="one")
    await message.answer(text, reply_markup=keyboard)


@dp.callback_query_handler(support_callback.filter(messages="one"), state='*')
async def send_to_support(call: types.CallbackQuery, state: FSMContext, callback_data: dict):
    await call.answer()
    user_id = int(callback_data.get("user_id"))
    print(user_id)

    await call.message.answer("Введите текст сообщения для отправки.")
    await state.set_state("wait_for_support_message")
    await state.update_data(second_id=user_id)


@dp.message_handler(state="wait_for_support_message", content_types=types.ContentTypes.ANY)
async def get_support_message(message: types.Message, state: FSMContext):
    data = await state.get_data()
    second_id = data.get("second_id")
    supports_ids = []
    users = await commands.select_all_supports()
    keyboard = await support_keyboard(messages="one", user_id=message.from_user.id)
    for i in users:
        supports_ids.append(i.id)
    if second_id in supports_ids:
        sup = await commands.select_user(id=second_id)
        await bot.send_message(text=f'Пользователь написал:\n\n'+message.text+f'\n\n'+f'Оператор:\n @{sup.name}\nПользователь: @{message.from_user.username}',
                               chat_id=secret)
        await bot.send_message(text=f'Сообщение от пользователя: @{message.from_user.username}\n'
                                    f'#id{message.from_user.id}\n\n'
                                    f'🔽   🔽   🔽', chat_id=second_id)

        await message.copy_to(second_id, reply_markup=keyboard)
        await message.answer("Вы отправили это сообщение!")
    else:
        sup = await commands.select_user(id=message.from_user.id)
        usr = await commands.select_user(id=second_id)
        await bot.send_message(
            text=f'Оператор ответил:\n\n' + message.text + f'\n\n' + f'Оператор:\n @{sup.name}\nПользователь: @{usr.name}',
            chat_id=secret)
        await bot.send_message(second_id,
                               f"<b>📌Сообщение от оператора!</b>\n\nВы можете ответить нажав на кнопку ниже")
        keyboard = await support_keyboard(messages="one", user_id=message.from_user.id)
        await message.copy_to(second_id, reply_markup=keyboard)

        await message.answer("Вы отправили это сообщение!")

    await state.reset_state()
