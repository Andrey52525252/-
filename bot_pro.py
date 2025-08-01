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
OPTION1_INPUT, OPTION2_INPUT, OPTION3_INPUT, OPTION4_INPUT = range(5, 9)

# Шаблоны вопросов для разных опций
OPTION_QUESTIONS = {
    "option1": [
        "Введите температуру асфальта (°C):",
        "Введите температуру в тени (°C):",
        "Введите температуру переднего мотора (°C):",
        "Введите температуру заднего мотора (°C):",
        "Введите планируемое время движения (мин):",
        "Введите скорость движения (км/ч) (стандартная уборка - 2км/ч, максимальная скорость - 5 км/ч):"
    ],
    "option2": [
        "Введите температуру асфальта (°C):",
        "Введите температуру в тени (°C):",
        "Введите температуру переднего мотора (°C):",
        "Введите температуру заднего мотора (°C):",
        "Введите планируемое время движения (мин):",
        "Введите скорость движения (км/ч) (стандартная уборка - 2км/ч, максимальная скорость - 5 км/ч):"
    ],
    "option3": [
        "Введите температуру асфальта (°C):",
        "Введите температуру в тени (°C):",
        "Введите температуру переднего мотора (°C):",
        "Введите температуру заднего мотора (°C):",
        "Введите планируемое время движения (мин):",
        "Введите скорость движения (км/ч) (стандартная уборка - 2км/ч, максимальная скорость - 5 км/ч):"
    ],
    "option4": [
        "Введите температуру в ангаре (°C):",
        "Введите температуру переднего мотора (°C):",
        "Введите температуру заднего мотора (°C):",
        "Введите планируемое время стоянки (мин):"
    ]
}

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
    
    context.user_data.clear()
    
    if option in ["option1", "option2", "option3", "option4"]:
        context.user_data['current_option'] = option
        context.user_data['current_step'] = 0
        await query.edit_message_text(OPTION_QUESTIONS[option][0])
        
    elif option == "option5":
        context.user_data['current_step'] = INPUT_NUM1
        await query.edit_message_text("Введите температуру асфальта (°C):")

async def handle_number_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает ввод чисел для всех опций"""
    user_data = context.user_data
    current_option = user_data.get('current_option')
    
    # Обработка для option1-option4
    if current_option in ["option1", "option2", "option3", "option4"]:
        try:
            num = float(update.message.text)
            step = user_data['current_step']
            
            # Сохраняем значение
            user_data[f'step{step}'] = num
            user_data['current_step'] += 1
            
            # Получаем список вопросов для текущей опции
            questions = OPTION_QUESTIONS[current_option]
            
            # Если остались вопросы - задаем следующий
            if user_data['current_step'] < len(questions):
                await update.message.reply_text(questions[user_data['current_step']])
            else:
                # Все данные получены - выполняем расчет
                # Создаем именованные переменные для всех опций
                if current_option == "option1":
                    Tasphalt = user_data['step0']
                    Tshadow = user_data['step1']
                    Tfront = user_data['step2']
                    Tback = user_data['step3']
                    time = user_data['step4']
                    speed = user_data['step5']
                    alphaFront = 0.3566      #альфа и каппа - коэффициенты, найденные из экспериментальных данных
                    alphaBack = 0.3566       #коэффициенты доопределить!!! 
                    kappa = 45.7        #альфа - коэффициент пропорциональности между разностью Т и V*каппа, каппа - период затухания
                    Tstreet = Tasphalt * 0.567 + Tshadow * 0.433   #температура, к которой стремятся выключенные моторы, найдена экспериментально

                    T0front = Tstreet + speed * alphaFront * kappa   #температура теплового баланса у работающего двигателя, 
                    T0back = Tstreet + speed * alphaBack * kappa     #найдена аналитически
                    #по нынешним данным каппа одинаковая для всех, но возможно это не так!!!
                    TfrontFinal = round(T0front - (T0front - Tfront) * math.exp(-time / kappa))
                    TbackFinal = round(T0back - (T0back - Tback) * math.exp(-time / kappa))
                    
                    result = (
                        f"Температура асфальта: {Tasphalt}°C\n"
                        f"Температура в тени: {Tshadow}°C\n"
                        f"Начальная температура переднего мотора: {Tfront}°C\n"
                        f"Начальная температура заднего мотора: {Tback}°C\n"
                        f"Время движения: {time} мин\n"
                        f"Скорость движения: {speed} км/ч\n\n"
                        f"Итоговая температура переднего мотора: {TfrontFinal}°C\n"
                        f"Итоговая температура заднего мотора: {TbackFinal}°C\n"
                    )
                    
                elif current_option == "option2":

                    Tasphalt = user_data['step0']
                    Tshadow = user_data['step1']
                    Tfront = user_data['step2']
                    Tback = user_data['step3']
                    time = user_data['step4']
                    speed = user_data['step5']
                    alphaFront = 0.3566      #альфа и каппа - коэффициенты, найденные из экспериментальных данных
                    alphaBack = 0.3566       #коэффициенты доопределить!!! 
                    kappa = 45.7        #альфа - коэффициент пропорциональности между разностью Т и V*каппа, каппа - период затухания
                    Tstreet = Tasphalt * 0.567 + Tshadow * 0.433   #температура, к которой стремятся выключенные моторы, найдена экспериментально

                    T0front = Tstreet + speed * alphaFront * kappa   #температура теплового баланса у работающего двигателя, 
                    T0back = Tstreet + speed * alphaBack * kappa     #найдена аналитически
                    #по нынешним данным каппа одинаковая для всех, но возможно это не так!!!
                    TfrontFinal = round(T0front - (T0front - Tfront) * math.exp(-time / kappa))
                    TbackFinal = round(T0back - (T0back - Tback) * math.exp(-time / kappa))
                    
                    result = (
                        f"Температура асфальта: {Tasphalt}°C\n"
                        f"Температура в тени: {Tshadow}°C\n"
                        f"Температура переднего мотора: {Tfront}°C\n"
                        f"Температура заднего мотора: {Tback}°C\n"
                        f"Время движения: {time} мин\n"
                        f"Скорость движения: {speed} км/ч\n\n"
                        f"Итоговая температура переднего мотора: {TfrontFinal}°C\n"
                        f"Итоговая температура заднего мотора: {TbackFinal}°C\n"
                    )
                    
                elif current_option == "option3":
                    Tasphalt = user_data['step0']
                    Tshadow = user_data['step1']
                    Tfront = user_data['step2']
                    Tback = user_data['step3']
                    time = user_data['step4']
                    speed = user_data['step5']
                    alphaFront = 0.3566      #альфа и каппа - коэффициенты, найденные из экспериментальных данных
                    alphaBack = 0.3566       #коэффициенты доопределить!!! 
                    kappa = 45.7        #альфа - коэффициент пропорциональности между разностью Т и V*каппа, каппа - период затухания
                    Tstreet = Tasphalt * 0.567 + Tshadow * 0.433   #температура, к которой стремятся выключенные моторы, найдена экспериментально

                    T0front = Tstreet + speed * alphaFront * kappa   #температура теплового баланса у работающего двигателя, 
                    T0back = Tstreet + speed * alphaBack * kappa     #найдена аналитически
                    #по нынешним данным каппа одинаковая для всех, но возможно это не так!!!
                    TfrontFinal = round(T0front - (T0front - Tfront) * math.exp(-time / kappa))
                    TbackFinal = round(T0back - (T0back - Tback) * math.exp(-time / kappa))
                    
                    result = (
                        f"Температура асфальта: {Tasphalt}°C\n"
                        f"Температура в тени: {Tshadow}°C\n"
                        f"Начальная температура переднего мотора: {Tfront}°C\n"
                        f"Начальная температура заднего мотора: {Tback}°C\n"
                        f"Время движения: {time} мин\n"
                        f"Скорость движения: {speed} км/ч\n\n"
                        f"Итоговая температура переднего мотора: {TfrontFinal}°C\n"
                        f"Итоговая температура заднего мотора: {TbackFinal}°C\n"
                    )
                    
                elif current_option == "option4":
                    Tgarage = user_data['step0']
                    Tfront = user_data['step1']
                    Tback = user_data['step2']
                    time = user_data['step4']
                    kappa = 45.7      #нашли эмпирически

                    TfrontFinal = round(Tgarage - (Tgarage - Tfront) * math.exp(-time / kappa))
                    TbackFinal = round(Tgarage - (Tgarage - Tback) * math.exp(-time / kappa))
                    
                    result = (
                        f"Температура в ангаре: {Tasphalt}°C\n"
                        f"Начальная температура переднего мотора: {Tfront}°C\n"
                        f"Начальная температура заднего мотора: {Tback}°C\n"
                        f"Время стоянки: {time} мин\n"
                        f"Итоговая температура переднего мотора: {TfrontFinal}°C\n"
                        f"Итоговая температура заднего мотора: {TbackFinal}°C\n"
                    )
                
                await update.message.reply_text(result)
                user_data.clear()
                
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите число!")
    
    # Обработка для option5
    elif 'current_step' in user_data:
        current_step = user_data.get('current_step')
        
        try:
            num = float(update.message.text)
            
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
                
                # Создаем именованные переменные
                Tasphalt = user_data['num1']
                Tshadow = user_data['num2']
                Tfront = user_data['num3']
                Tback = user_data['num4']
                time = user_data['num5']
                
                # Оригинальный расчет для option5
                T0 = Tasphalt * 0.567 + Tshadow * 0.433
                TFrontFinal = round(T0 + (Tfront - T0) * math.exp(-time/45.7))
                TBackFinal = round(T0 + (Tback - T0) * math.exp(-time/45.7))
                
                result = (
                    f"Температура асфальта: {Tasphalt}°C\n"
                    f"Температура в тени: {Tshadow}°C\n"
                    f"Температура переднего мотора: {Tfront}°C\n"
                    f"Температура заднего мотора: {Tback}°C\n"
                    f"Время стоянки: {time} мин\n\n"
                    f"Температура переднего мотора в конце стоянки: {TFrontFinal}°C\n"
                    f"Температура заднего мотора в конце стоянки: {TBackFinal}°C"
                )
                
                await update.message.reply_text(result)
                user_data.clear()
        
        except ValueError:
            await update.message.reply_text("Пожалуйста, введите число!")

def main():
    application = Application.builder().token(TOKEN).build()
    
    # Регистрация обработчиков
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(handle_selection))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_number_input))
    
    logger.info("Бот запущен и слушает обновления...")
    application.run_polling()

if __name__ == "__main__":
    main()