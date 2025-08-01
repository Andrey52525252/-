import logging
import math
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = "8353872360:AAG1dZQbOXDA4fawYDvLVGFSYGWYCLNWDDU" 

# Константы для состояний
INPUT_NUM1, INPUT_NUM2, INPUT_NUM3, INPUT_NUM4, INPUT_NUM5 = range(5)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветствие и кнопки выбора"""
    user = update.effective_user
    logger.info(f"Пользователь {user.id} запустил бота")
    
    keyboard = [
        [InlineKeyboardButton("Уборка с поливомоечной рейкой", callback_data="option1")],
        [InlineKeyboardButton("Движение с пустым баком", callback_data="option2")],
        [InlineKeyboardButton("Движение с полным баком", callback_data="option3")],
        [InlineKeyboardButton("Стоянка в ангаре", callback_data="option4")],
        [InlineKeyboardButton("Стоянка на улице", callback_data="option5")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, {user.first_name}! Я назову температуру, до которой нагреется или остынет мотор.\n\n"
        "Чем планируете заниматься?",
        reply_markup=reply_markup
    )

async def handle_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает выбор пользователя"""
    query = update.callback_query
    await query.answer()
    option = query.data
    
    if option == "option1":
        await query.edit_message_text("Поздравляю! Вы выбрали Уборку с поливомоечной рейкой 🎉")
    elif option == "option2":
        await query.edit_message_text("Отличный выбор! Движение с пустым баком 👍")
    elif option == "option3":
        await query.edit_message_text("Вау! Вы выбрали Движение с полным баком! 🔥")
    elif option == "option4":
        await query.edit_message_text("Вариант Стоянка в ангаре - мудрое решение! 💡")
    elif option == "option5":
        # Начинаем процесс ввода чисел
        context.user_data.clear()
        context.user_data['current_step'] = INPUT_NUM1
        await query.edit_message_text("Введите температуру асфальта (°C):")

async def handle_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод чисел для option5"""
    user_data = context.user_data
    current_step = user_data.get('current_step')
    
    if current_step is None:
        return  # Не наш процесс
    
    try:
        num = float(update.message.text)
        
        # Сохраняем число и переходим к следующему шагу
        if current_step == INPUT_NUM1:
            user_data['num1'] = num
            user_data['current_step'] = INPUT_NUM2
            await update.message.reply_text("Введите температуру в тени (°C):")
            
        elif current_step == INPUT_NUM2:
            user_data['num2'] = num
            user_data['current_step'] = INPUT_NUM3
            await update.message.reply_text("Введите температуру переднего мотора (°C):")
            
        elif current_step == INPUT_NUM3:
            user_data['num3'] = num
            user_data['current_step'] = INPUT_NUM4
            await update.message.reply_text("Введите температуру заднего мотора (°C):")
            
        elif current_step == INPUT_NUM4:
            user_data['num4'] = num
            user_data['current_step'] = INPUT_NUM5
            await update.message.reply_text("Введите планируемое время стоянки (мин):")
            
        elif current_step == INPUT_NUM5:
            user_data['num5'] = num
            
            # Вычисляем сумму
            Tasphalt = user_data['num1']
            Tshadow = user_data['num2']
            Tfront = user_data['num3']
            Tback = user_data['num4']
            time = user_data['num5']
            T0 = Tasphalt * 0.567 + Tshadow * 0.433

            TFrontFinal = round(T0 + (Tfront - T0) * math.exp(-time/45.7))
            TBackFinal = round(T0 + (Tback - T0) * math.exp(-time/45.7))
            
            # Формируем результат
            result = (
                f"Результат расчета:\n"
                f"Температура асфальта: {user_data['num1']}°C\n"
                f"Температура в тени: {user_data['num2']}°C\n"
                f"Температура переднего мотора: {user_data['num3']}°C\n"
                f"Температура заднего мотора: {user_data['num4']}°C\n"
                f"Время стоянки: {user_data['num5']} мин\n\n"
                f"Температура переднего мотора в конце стоянки: {TFrontFinal}\n"
                f"Температура заднего мотора в конце стоянки: {TBackFinal}"
            )
            
            await update.message.reply_text(result)
            
            # Завершаем процесс
            user_data.clear()
    
    except ValueError:
        await update.message.reply_text("Пожалуйста, введите число!")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_selection))
    
    # Обработчик для ввода чисел
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number_input))
    
    logger.info("Бот запущен и слушает обновления...")
    application.run_polling()

if __name__ == "__main__":
    main()