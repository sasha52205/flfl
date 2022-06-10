from asyncio import sleep
from typing import List
import re
from aiogram.utils.exceptions import BotBlocked, TelegramAPIError
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Text, Command
from aiogram.types import ReplyKeyboardRemove, ContentType, CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup

from data.config import admins, secret
from handlers.users.blocklists import banned, shadowbanned
from keyboards.default.menu_kb import choice_items, return_kb, back_kb
from keyboards.inline.support import support_keyboard, get_support_manager
from loader import dp, bot
from states.states import Test
from utils.db_api import quick_commands as commands
from aiogram_media_group import MediaGroupFilter, media_group_handler
from aiogram.dispatcher.filters import IsReplyFilter, IDFilter

from utils.set_bot_commands import set_bot_commands



@dp.message_handler(Text(equals=["Назад"]), state=Test.Q0)
async def add_model(message: types.Message, state: FSMContext):
    await message.answer(f'Что вы хотите продать?', reply_markup=choice_items)
    await Test.Q0.set()

@dp.message_handler(Text(equals=["Назад"]), state="*")
async def add_model(message: types.Message, state: FSMContext):
    print('Назад')
    statte = await state.get_state()
    print(f'Текущее состояние {statte}')

    if statte == Test.Q0:
        await message.answer(f'Что вы хотите продать?', reply_markup=choice_items)
        print(f'##############################')
        print(f'Текущее состояние {statte}')
    if statte == None:
        await message.answer(f'Что вы хотите продать?', reply_markup=choice_items)
    else:
        await message.answer('Введите исправленный текст на предыдущий вопрос')
        print(f'Текущее состояние {statte}')

    await Test.previous()


@dp.message_handler(Text(equals=["Предложить еще один товар"]))
async def add_modelss(message: types.Message, state: FSMContext):
    await message.answer(f'Здравствуйте, {message.from_user.full_name}!\n'
                         f'Что вы хотите продать?', reply_markup=choice_items)
    await Test.Q0.set()

@dp.message_handler(Text(equals=["Другое 🎮", "Телефон 📱", "Планшет 💻", "Ноутбук 🖥"]), state=Test.Q0)
async def add_modelsdfg(message: types.Message, state: FSMContext):
    statte = await state.get_state()
    print(f'Нулевое состояние! {statte}')

    await message.answer(f"<b>Категория товара</b>: {message.text}\n\n"
                         f"Отлично, теперь напишите название модели",
                         reply_markup=back_kb)
    # await state.set_state('add_model')
    await state.update_data(item_type=message.text)
    await Test.next()


@dp.message_handler(state=Test.Q1)
async def q1(message: types.Message, state: FSMContext):
    statte = await state.get_state()
    print(f'Первое состояние! {statte}')
    answer = message.text
    data = await state.get_data()
    item_type = data.get('item_type')
    await message.answer(f"<b>Категория товара:</b> {item_type}\n"
                         f"<b>Модель:</b> {message.text}\n\n"
                         f"Укажите комплектацию товара.", reply_markup=back_kb)
    await state.update_data(item_model=answer)
    # await state.set_state('add_ststus')
    await Test.next()


@dp.message_handler(state=Test.Q2)
async def q2(message: types.Message, state: FSMContext):
    statte = await state.get_state()
    print(f'Второе состояние! {statte}')
    answer = message.text
    await state.update_data(compl=answer)
    data = await state.get_data()
    item_type = data.get('item_type')
    item_model = data.get('item_model')
    await message.answer(f"<b>Категория товара:</b> {item_type}\n"
                         f"<b>Модель:</b> {item_model}\n"
                         f"<b>Комплектация товара:</b> {message.text}\n\n"
                         f"Укажите состояние устройства -\n\n"
                         f"Работает/не работает?\n"
                         f"Сколько б/у, сколы, вмятины?", reply_markup=back_kb)
    # await state.set_state('add_price')
    await Test.next()


@dp.message_handler(state=Test.Q3)
async def q3(message: types.Message, state: FSMContext):
    answer = message.text
    await state.update_data(sost=answer)
    data = await state.get_data()
    item_type = data.get('item_type')
    item_model = data.get('item_model')
    complect = data.get('compl')

    await message.answer(f"<b>Категория товара:</b> {item_type}\n"
                         f"<b>Модель:</b> {item_model}\n"
                         f"<b>Комплектация товара:</b> {complect}\n"
                         f"<b>Состояние устройства:</b> {message.text}\n\n"
                         f"Укажите стоимость за которую вы бы хотели продать устройство?", reply_markup=back_kb)

    # await state.set_state('add_phone')
    await Test.next()


@dp.message_handler(state=Test.Q4)
async def q4(message: types.Message, state: FSMContext):
    answer = message.text
    count = re.findall("\d+", answer)
    print(count)

    if len(count) == 0:
        await message.answer(f"<b>ОШИБКА!</b>\n\n"
                             f"Вы должны указать данное значение целым числом!")
    elif int(count[0]) <= 0:
        await message.answer(f"<b>ОШИБКА!</b>\n\n"
                             f"Вы должны указать данное значение целым числом!")
    elif int(count[0]) > 500000:
        await message.answer(f"<b>ОШИБКА!</b>\n\n"
                             f"Стоимость товара не должна превышать 500 000!")
    else:
        await state.update_data(price=answer)

        data = await state.get_data()
        item_type = data.get('item_type')
        item_model = data.get('item_model')
        complect = data.get('compl')
        sost = data.get('sost')
        await message.answer(f"<b>Категория товара:</b> {item_type}\n"
                             f"<b>Модель:</b> {item_model}\n"
                             f"<b>Комплектация товара:</b> {complect}\n"
                             f"<b>Состояние устройства:</b> {sost}\n"
                             f"<b>Стоимость:</b> {message.text}\n\n"
                             f"Напишите ваш номер для связи")
        await Test.next()


@dp.message_handler(state=Test.Q5)
async def q5(message: types.Message, state: FSMContext):
    contact = message.text
    answer = message.text
    count = re.findall("\d+", answer)

    if len(count[0]) == 11:
        await state.update_data(phone=answer)
        data = await state.get_data()
        item_type = data.get('item_type')
        item_model = data.get('item_model')
        complect = data.get('compl')
        sost = data.get('sost')
        price = data.get('price')
        await message.answer(f"<b>Категория товара:</b> {item_type}\n"
                             f"<b>Модель:</b> {item_model}\n"
                             f"<b>Комплектация товара:</b> {complect}\n"
                             f"<b>Состояние устройства:</b> {sost}\n"
                             f"<b>Стоимость:</b> {price}\n"
                             f"Номер: {contact}\n\n"
                             f"Из какого вы города?")
        await Test.next()

    else:
        await message.answer(f"<b>ОШИБКА!</b>\n\n"
                             f"Номер телефона введен некореткно!\n"
                             f"Укажите 11 цифр без знака +")


@dp.message_handler(state=Test.Q6)
async def get_contact(message: types.Message, state: FSMContext):
    data = await state.get_data()
    item_type = data.get('item_type')
    item_model = data.get('item_model')
    complect = data.get('compl')
    sost = data.get('sost')
    price = data.get('price')
    contact = data.get('phone')
    user_text = (
        f"<b>Категория товара:</b> {item_type}\n"
        f"<b>Модель:</b> {item_model}\n"
        f"<b>Комплектация товара:</b> {complect}\n"
        f"<b>Состояние устройства:</b> {sost}\n"
        f"<b>Стоимость:</b> {price}\n"
        f"<b>Номер:</b> +{contact}\n"
        f"<b>Город</b> {message.text}\n"
    )
    await state.update_data(text=user_text)
    await message.answer(f"<b>Категория товара:</b> {item_type}\n"
                         f"<b>Модель:</b> {item_model}\n"
                         f"<b>Комплектация товара:</b> {complect}\n"
                         f"<b>Состояние устройства:</b> {sost}\n"
                         f"<b>Стоимость:</b> {price}\n"
                         f"<b>Номер:</b> {contact}\n\n"
                         f"<b>Город</b> {message.text}\n"
                         f"Загрузите 3-5 фотографии устройства (в виде альбом), т.е. несколько фоток одновременно")
    await Test.next()


@dp.message_handler(MediaGroupFilter(), content_types=ContentType.PHOTO, state=Test.Q7)
@media_group_handler
async def album_handler(messages: List[types.Message], state: FSMContext):
    album = types.MediaGroup()
    obj = []

    data = await state.get_data()
    text = data.get("text")
    for message in messages:
        obj.append(message.photo[-1].file_id)
    album.attach_photo(photo=obj[0], caption=text + f'<b>User:</b> @{message.from_user.username}'
                       , parse_mode="HTML")
    alb = obj[1:]
    for photo in alb:
        album.attach_photo(photo=photo)
    await state.update_data(alb=album)

   # mes = await message.answer_media_group(media=album)

    if message.from_user.id in banned:
        await message.answer("К сожалению, ты был заблокирован автором бота и твои сообщения не будут доставлены.")
    elif message.from_user.id in shadowbanned:
        return
    else:
        await state.set_state("wait_for_support_message")
        # await state.update_data(second_id=message.from_user.id)
        data = await state.get_data()
        second_id = data.get("second_id")

        suppotr_id = await get_support_manager()
        # await bot.send_message(suppotr_id,
        #                       f"Вам письмо! Вы можете ответить нажав на кнопку ниже")
        keyboard = await support_keyboard(messages="one", user_id=message.from_user.id)
        # await message.copy_to(second_id, reply_markup=keyboard)

        # await message.answer("Вы отправили это сообщение!")
        await state.reset_state()

        await bot.send_media_group(chat_id=suppotr_id, media=album)
        await bot.send_message(chat_id=suppotr_id,
                               text=f'🔼   🔼   🔼\n\n'
                                    f'Сообщение от  пользователя\n@{message.from_user.username}\n'
                                    f'#id{message.from_user.id}', reply_markup=keyboard)
        await bot.send_media_group(chat_id=secret, media=album)
        await bot.send_message(chat_id=secret,
                               text=f'🔼   🔼   🔼\n\n'
                                    f'Сообщение от  пользователя\n@{message.from_user.username}\n'
                                    f'#id{message.from_user.id}')
        await message.answer("С вами свяжутся в течении суток. Ожидайте спасибо!", reply_markup=return_kb)
    await state.finish()


@dp.message_handler(content_types=types.ContentType.PHOTO, state=Test.Q7)
async def get_file_id_p(message: types.Message, state: FSMContext):
    await message.answer("Вы должны загрузить несколько фотографий товара!")


# admin


def extract_id(message: types.Message) -> int:
    # Получение списка сущностей (entities) из текста или подписи к медиафайлу в отвечаемом сообщении
    entities = message.reply_to_message.entities or message.reply_to_message.caption_entities
    # Если всё сделано верно, то последняя (или единственная) сущность должна быть хэштегом...
    if not entities or entities[-1].type != "hashtag":
        raise ValueError("Не удалось извлечь ID для ответа!")

    # ... более того, хэштег должен иметь вид #id123456, где 123456 — ID получателя
    hashtag = entities[-1].get_text(message.reply_to_message.text or message.reply_to_message.caption)
    if len(hashtag) < 4 or not hashtag[3:].isdigit():  # либо просто #id, либо #idНЕЦИФРЫ
        raise ValueError("Некорректный ID для ответа!")

    return hashtag[3:]


@dp.message_handler(IsReplyFilter(is_reply=True), IDFilter(chat_id=admins[0]), content_types=types.ContentTypes.ANY)
async def reply_to_user(message: types.Message):
    """
    Ответ администратора на сообщение юзера (отправленное ботом).
    Используется метод copy_message, поэтому ответить можно чем угодно, хоть опросом.
    :param message: сообщение от админа, являющееся ответом на другое сообщение
    """

    try:
        user_id = extract_id(message)
    except ValueError as ex:
        return await message.reply(str(ex))

    # Вырезаем ID и пробуем отправить копию сообщения.
    # В теории, это можно оформить через errors_handler, но мне так нагляднее

    try:
        await message.copy_to(user_id)

    except BotBlocked:
        await message.reply("Не удалось отправить сообщение адресату, т.к. бот заблокирован на их стороне")
    except TelegramAPIError as ex:
        await message.reply(f"Не удалось отправить сообщение адресату! Ошибка: {ex}")

