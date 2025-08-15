import os

from dotenv import load_dotenv
from telegram.ext import (ApplicationBuilder, CallbackQueryHandler,
                          CommandHandler, MessageHandler, filters)

from gpt import *
from util import *

# Загрузка переменных окружения
load_dotenv(override=True)

# Инициализация диалога
dialog = Dialog()
dialog.mode = None
dialog.list = []
dialog.count = 0
dialog.user = {}

# Получение токенов из переменных окружения
TOKEN_AI = os.getenv("OPEN_AI_TOKEN")
chatgpt = ChatGptService(token=TOKEN_AI)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
app = ApplicationBuilder().token(TOKEN).build()


async def start(update, context):
    """
    Обрабатывает команду /start.
    Устанавливает режим диалога на 'main' и отображает главное меню.
    """
    dialog.mode = "main"
    text = load_message("main")

    await send_photo(update, context, "main")
    await send_text(update, context, text)

    await show_main_menu(
        update,
        context,
        {
            "start": "главное меню бота",
            "profile": "генерация Tinder-профиля 😎",
            "opener": "сообщение для знакомства 🥰",
            "message": "переписка от вашего имени 😈",
            "date": "переписка со звездами 🔥",
            "gpt": "задать вопрос чату GPT 🧠",
        },
    )


async def gpt(update, context):
    """
    Обрабатывает команду /gpt.
    Устанавливает режим диалога на 'gpt' и отображает информацию о GPT.
    """
    dialog.mode = "gpt"
    text = load_message("gpt")

    await send_photo(update, context, "gpt")
    await send_text(update, context, text)


async def profile(update, context):
    """
    Обрабатывает команду /profile.
    Устанавливает режим диалога на 'profile' и отображает информацию о генерации профиля.
    Очищает данные пользователя и запрашивает возраст.
    """
    dialog.mode = "profile"
    text = load_message("profile")

    await send_photo(update, context, "profile")
    await send_text(update, context, text)

    dialog.user.clear()  # Очищаем данные пользователя
    dialog.count = 0  # Сбрасываем счетчик вопросов

    await send_text(update, context, "Сколько вам лет?")


async def opener(update, context):
    """
    Обрабатывает команду /opener.
    Устанавливает режим диалога на 'opener' и отображает информацию о сообщении для знакомства.
    Очищает данные пользователя и запрашивает имя девушки.
    """
    dialog.mode = "opener"
    text = load_message("opener")

    await send_photo(update, context, "opener")
    await send_text(update, context, text)

    dialog.user.clear()  # Очищаем данные пользователя
    dialog.count = 0  # Сбрасываем счетчик вопросов

    await send_text(update, context, "Имя девушки?")


async def date(update, context):
    """
    Обрабатывает команду /date.
    Устанавливает режим диалога на 'date' и отображает информацию о переписке со звездами.
    """
    dialog.mode = "date"
    text = load_message("date")

    await send_photo(update, context, "date")
    await send_text_buttons(
        update,
        context,
        text,
        {
            "date_grande": "Ариана Гранде",
            "date_robbie": "Марго Робби",
            "date_zendaya": "Зендея",
            "date_gosling": "Райан Гослинг",
            "date_hardy": "Том Харди",
        },
    )


async def message(update, context):
    """
    Обрабатывает команду /message.
    Устанавливает режим диалога на 'message' и отображает информацию о переписке от имени пользователя.
    Очищает список сообщений.
    """
    dialog.mode = "message"
    text = load_message("message")

    await send_photo(update, context, "message")
    await send_text_buttons(
        update,
        context,
        text,
        {
            "message_next": "Следующее сообщение",
            "message_date": "Пригласить на свидание",
        },
    )
    dialog.list.clear()  # Очищаем список сообщений


async def hello(update, context):
    """
    Обрабатывает текстовые сообщения от пользователя.
    В зависимости от режима диалога, вызывает соответствующую функцию.
    Если режим не установлен, отправляет приветственное сообщение.
    """
    if dialog.mode == "gpt":
        await gpt_dialog(update, context)
    elif dialog.mode == "date":
        await date_dialog(update, context)
    elif dialog.mode == "message":
        await message_dialog(update, context)
    elif dialog.mode == "profile":
        await profile_dialog(update, context)
    elif dialog.mode == "opener":
        await opener_dialog(update, context)
    else:
        await send_text(update, context, "*Привет*")
        await send_text(update, context, "Вы написали " + update.message.text)
        await send_photo(update, context, "avatar_main")


async def gpt_dialog(update, context):
    """
    Обрабатывает текстовые сообщения в режиме 'gpt'.
    Отправляет запрос к ChatGPT и возвращает ответ пользователю.
    Если текст пустой, запрашивает ввод.
    """
    try:
        text = update.message.text
        if not text:
            await send_text(update, context, "Пожалуйста, введите текст.")
            return

        prompt = load_prompt("gpt")
        answer = await chatgpt.send_question(prompt, text)
        await send_text(update, context, answer)
    except Exception as e:
        await send_text(update, context, "Произошла ошибка. Попробуйте еще раз.")
        print(f"Error in gpt_dialog: {e}")


async def date_dialog(update, context):
    """
    Обрабатывает текстовые сообщения в режиме 'date'.
    Отправляет сообщение от имени девушки и получает ответ от ChatGPT.
    """
    text = update.message.text

    my_message = await send_text(update, context, "Девушка набирает текст...")
    answer = await chatgpt.add_message(text)

    await my_message.edit_text(answer)


async def message_dialog(update, context):
    """
    Обрабатывает текстовые сообщения в режиме 'message'.
    Сохраняет сообщения пользователя в списке для дальнейшего использования.
    """
    text = update.message.text
    dialog.list.append(text)  # Добавляем сообщение в список


async def profile_dialog(update, context):
    """
    Обрабатывает текстовые сообщения в режиме 'profile'.
    Сохраняет информацию о пользователе и задает последовательные вопросы.
    После завершения опроса генерирует профиль с помощью ChatGPT.
    """
    text = update.message.text
    dialog.count += 1  # Увеличиваем счетчик вопросов

    if dialog.count == 1:
        dialog.user["age"] = text
        await send_text(update, context, "Кем вы работаете?")
    elif dialog.count == 2:
        dialog.user["occupation"] = text
        await send_text(update, context, "У вас есть хобби? Какое?")
    elif dialog.count == 3:
        dialog.user["hobby"] = text
        await send_text(update, context, "Что вам НЕ нравится в людях?")
    elif dialog.count == 4:
        dialog.user["annoys"] = text
        await send_text(update, context, "Цели знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

        prompt = load_prompt("profile")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(
            update,
            context,
            "ЧатGPT занимается генерацией вашего профиля, подождите пару секунд...",
        )
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def opener_dialog(update, context):
    """
    Обрабатывает текстовые сообщения в режиме 'opener'.
    Сохраняет информацию о девушке и генерирует первое сообщение.
    """
    text = update.message.text
    dialog.count += 1  # Увеличиваем счетчик вопросов

    if dialog.count == 1:
        dialog.user["name"] = text
        await send_text(update, context, "Сколько ей лет?")
    elif dialog.count == 2:
        dialog.user["age"] = text
        await send_text(update, context, "Оцени её внешность: 1-10 баллов!")
    elif dialog.count == 3:
        dialog.user["handsome"] = text
        await send_text(update, context, "Кем она работает?")
    elif dialog.count == 4:
        dialog.user["occupation"] = text
        await send_text(update, context, "Цели знакомства?")
    elif dialog.count == 5:
        dialog.user["goals"] = text

        prompt = load_prompt("opener")
        user_info = dialog_user_info_to_str(dialog.user)

        my_message = await send_text(
            update,
            context,
            "ЧатGPT занимается генерацией первого сообщения, подождите пару секунд...",
        )
        answer = await chatgpt.send_question(prompt, user_info)
        await my_message.edit_text(answer)


async def hello_button(update, context):
    """
    Обрабатывает нажатия кнопок в диалоге.
    В зависимости от нажатой кнопки, запускает или останавливает процесс.
    """
    query = update.callback_query.data
    await update.callback_query.answer()

    if query == "start":
        await send_text(update, context, "Процесс запущен")
    elif query == "stop":
        await send_text(update, context, "Процесс остановлен")
    else:
        await send_text(update, context, "Неизвестная команда")


async def date_button(update, context):
    """
    Обработчик нажатия кнопки для выбора звезды.
    Отправляет фото и текст, а также устанавливает соответствующий промпт для ChatGPT.
    """
    query = update.callback_query.data
    await update.callback_query.answer()

    await send_photo(update, context, query)
    await send_text(
        update,
        context,
        "Отличный выбор! Пригласите партнера на свидание за 5 сообщений",
    )

    prompt = load_prompt(query)
    chatgpt.set_prompt(prompt)


async def message_button(update, context):
    """
    Обработчик нажатия кнопки для получения следующего сообщения.
    Отправляет запрос к ChatGPT с историей сообщений пользователя.
    """
    query = update.callback_query.data
    await update.callback_query.answer()

    # Проверка нажатой кнопки
    if query == "message_next":
        prompt = load_prompt("message_next")
    elif query == "message_date":
        prompt = load_prompt("message_date")
    else:
        await send_text(update, context, "Неизвестная команда")
        return

    # Проверка истории сообщений
    if not dialog.list:
        await send_text(update, context, "Нет сообщений для обработки.")
        return

    user_chat_history = "\n\n".join(dialog.list)

    my_message = await send_text(
        update, context, "ChatGPT думает над вариантами ответа..."
    )

    try:
        answer = await chatgpt.send_question(prompt, user_chat_history)
        await my_message.edit_text(answer)
    except Exception as e:
        await my_message.edit_text("Произошла ошибка при получении ответа.")


# Добавление обработчиков команд
app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("gpt", gpt))
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("opener", opener))
app.add_handler(CommandHandler("message", message))
app.add_handler(CommandHandler("date", date))

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, hello))

app.add_handler(CallbackQueryHandler(hello_button, pattern="^hello_.*"))
app.add_handler(CallbackQueryHandler(date_button, pattern="^date_.*"))
app.add_handler(CallbackQueryHandler(message_button, pattern="^message_.*"))

# Запуск бота
app.run_polling()
