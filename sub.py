import logging

from aiogram import types
from aiogram.dispatcher.handler import CancelHandler
from aiogram.dispatcher.middlewares import BaseMiddleware

from data.config import channels
from keyboards.inline.subscription import check_button
from loader import bot
from utils.misc import subscription


class BigBrother(BaseMiddleware):
    async def on_process_message(self, message: types.Message, data: dict):
        logging.info(f"5. Process Message")
        for channel in channels:
            status = await subscription.check(user_id=message.from_user.id,
                                              channel=channel)
            channel = await bot.get_chat(channel)
            if status:
                pass
            else:
                channels_format = str()
                for channel in channels:
                    chat = await bot.get_chat(channel)
                    invite_link = await chat.export_invite_link()
                    channels_format += f"Канал <a href='{invite_link}'>{chat.title}</a>\n\n"

                await message.answer(f"Вам необходимо подписаться на следующие каналы: \n"
                                     f"{channels_format}",
                                     reply_markup=check_button,
                                     disable_web_page_preview=True)
                raise CancelHandler()
