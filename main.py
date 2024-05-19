import asyncio
import logging
import sys
from os import getenv
from typing import Any, Dict
from kandinsky import kandynsky,delete_files


from aiogram import Bot, Dispatcher, F, Router, html
from aiogram.enums import ParseMode
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import (
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    FSInputFile,

)

import config

TOKEN = getenv(config.tg_token)

form_router = Router()


class Form(StatesGroup):
    name = State()
    like_bots = State()
    language = State()


@form_router.message(CommandStart())
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer(
        "Привет ,я Бот который написан для генерации уникального изображения с помощью нейросети."
        "\n\nКандинский,укажите пожалуйста ваш промпт !\n\nПромпт - это описание картинки которую вы хотите создать."
        "\nДля лучшего результата советуем сделать описание как можно более подробным\nПример хорошего промпта : \n\n' Красивая рыжая девушка в бикини на пляже ,добродушно улыбается,в красивых очках ,позади океан и виднеются корабли,фотореализм.'",
        reply_markup=ReplyKeyboardRemove(),
    )


@form_router.message(Command("отмена"))
@form_router.message(F.text.casefold() == "отмена")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    """
    Allow user to cancel any action
    """
    current_state = await state.get_state()
    if current_state is None:
        return

    logging.info("Cancelling state %r", current_state)
    await state.clear()
    await message.answer(
        "Отменено,что бы сгенерировать изображение введите команду /start",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="/start"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    await state.update_data(name=message.text)
    await state.set_state(Form.like_bots)
    await message.answer(
        f"Промпт, {html.quote(message.text)}!\nПринят ,хотите продолжить ?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="Да"),
                    KeyboardButton(text="Нет"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


@form_router.message(Form.like_bots, F.text.casefold() == "нет")
async def process_dont_like_write_bots(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.clear()
    await message.answer(
        "Ничего страшного.\nМожешь попробовать позднее. Просто введи команду /start",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="/start"),
                ]
            ],
            resize_keyboard=True,
        ),
    )




@form_router.message(Form.like_bots, F.text.casefold() == "да")
async def process_like_write_bots(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.language)
    data = await state.get_data()

    await message.reply(
        "Отлично !\nЭто может занять несколько минут...",
        reply_markup=ReplyKeyboardRemove(),
    )
    await show_summary(message=message, data=data)

async def show_summary(message: Message, data: Dict[str, Any]) -> None:
    name = data["name"]
    chat_id = message.chat.id
    # await message.bot.send_chat_action(chat_id=message.chat.id,action = ChatAction.UPL)
    file_patch = await kandynsky(name)
    # await delete_files()
    image = FSInputFile(path=file_patch)
    text = f"Картинка по вашему промпту : ' {html.quote(name)}'"




    await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
    await message.reply_photo(photo=image)
    await message.answer(
        "Спасибо за использование моего бота!\n\nЕсли хотите сгенерировать новое изображение введите команду /start",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [
                    KeyboardButton(text="/start"),
                ]
            ],
            resize_keyboard=True,
        ),
    )


async def main():
    bot = Bot(token=config.tg_token, parse_mode=ParseMode.HTML)
    dp = Dispatcher()
    dp.include_router(form_router)

    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())



