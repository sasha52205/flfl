from aiogram import Dispatcher
from .sub import BigBrother

def setup_ml(dp: Dispatcher):
    dp.middleware.setup(BigBrother())




