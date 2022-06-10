from data.config import admins
from utils.set_bot_commands import set_bot_commands
from loader import db
from utils.db_api import db_gino


async def on_startup(dp):
    import filters
    filters.setup(dp)

    import middlewares
    middlewares.setup_ml(dp)


    from utils.notify_admins import on_startup_notify
    print("Подключаем БД")
    await db_gino.on_startup(dp)
    print("Готово")

   # print("Чистим базу")
   # await db.gino.drop_all()

    print("Готово")

    print("Создаем таблицы")
    await db.gino.create_all()

    print("Готово")
    await on_startup_notify(dp)
    await set_bot_commands(dp, admins)


if __name__ == '__main__':
    from aiogram import executor
    from handlers import dp

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
