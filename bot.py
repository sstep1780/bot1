import os
import logging
import asyncio
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove, InlineKeyboardButton, InlineKeyboardMarkup, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes, CallbackQueryHandler
from telegram.request import HTTPXRequest
from dotenv import load_dotenv

load_dotenv()

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния разговора
(SERVICES, GENDER, FIO, BIRTH_DATE, EMAIL, PHONE, SOCIAL_MEDIA, REASON, PHYSICAL_STATE, 
 CHILDREN, CHILDREN_AGE, ALLERGY, ALLERGY_DETAILS, MENTAL_STATE, MENTAL_STATE_DETAILS,
 SKIN_PROBLEMS, DRYNESS, SWEATING, VASCULAR, HEAVY_LEGS, SLEEP_DURATION, BACK_PAIN, 
 JOINT_PAIN, MORNING_TASTE, ILLNESS_FREQUENCY, STRESS, STOOL_URINATION, PRESSURE,
 PRESSURE_PREDISPOSITION, HEART_PAIN, WOMEN_CYCLE, INJURIES, CHRONIC_DISEASES,
 RELATIVES_DISEASES, CURRENT_WEIGHT, COMFORT_WEIGHT, BODY_TEMPERATURE, SHORTNESS_BREATH,
 AIR_LACK, THROAT_LUMP) = range(40)

user_data_storage = {}

# Получаем ID админов из .env
def get_admin_ids():
    admin_ids_str = os.getenv('ADMIN_IDS', '')
    if admin_ids_str:
        return [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
    return []

def clean_answer(text):
    """Убирает эмодзи из ответов"""
    return text.replace('✅ ', '').replace('❌ ', '').replace('👩 ', '').replace('👨 ', '').replace('💆‍♀️ ', '').replace('🩺 ', '').replace('🧠 ', '')

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        ['💆‍♀️ Массаж'],
        ['🩺 Консультация'], 
        ['🧠 Невролог']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "🏥 <b>Добро пожаловать в анкету здоровья!</b>\n\n"
        "🎯 <b>На какую процедуру хотели бы записаться?</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return SERVICES

async def services(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['services'] = clean_answer(update.message.text)
    keyboard = [['👩 Женский', '👨 Мужской']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        "👤 <b>Укажите ваш пол:</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return GENDER

async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['gender'] = clean_answer(update.message.text)
    await update.message.reply_text(
        "👤 <b>Введите ваше Ф.И.О:</b>",
        reply_markup=ReplyKeyboardRemove(),
        parse_mode='HTML'
    )
    return FIO

async def fio(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['fio'] = update.message.text
    await update.message.reply_text(
        "📅 <b>Введите дату рождения</b>\nНапример: 15.03.1990",
        parse_mode='HTML'
    )
    return BIRTH_DATE

async def birth_date(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['birth_date'] = update.message.text
    await update.message.reply_text(
        "📧 <b>Введите вашу электронную почту:</b>",
        parse_mode='HTML'
    )
    return EMAIL

async def email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['email'] = update.message.text
    await update.message.reply_text(
        "📱 <b>Введите номер телефона</b>\nНапример: +79991234567",
        parse_mode='HTML'
    )
    return PHONE

async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['phone'] = update.message.text
    await update.message.reply_text(
        "💬 <b>Укажите ваши социальные сети:</b>\nВКонтакте (Ф.И.О) и/или Instagram (@юзернейм)",
        parse_mode='HTML'
    )
    return SOCIAL_MEDIA

async def social_media(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['social_media'] = update.message.text
    await update.message.reply_text(
        "📝 <b>Опишите причину обращения:</b>\nЧто вас беспокоит? Какие симптомы?",
        parse_mode='HTML'
    )
    return REASON

async def reason(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['reason'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("😢 1 - Очень плохо", callback_data='phys_1'),
         InlineKeyboardButton("😕 2 - Плохо", callback_data='phys_2')],
        [InlineKeyboardButton("😐 3 - Нормально", callback_data='phys_3'),
         InlineKeyboardButton("🙂 4 - Хорошо", callback_data='phys_4')],
        [InlineKeyboardButton("😊 5 - Отлично", callback_data='phys_5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💪 <b>Оцените ваше физическое состояние:</b>\nОт 1 (очень плохо) до 5 (отлично)",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return PHYSICAL_STATE

async def physical_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    state_value = query.data.split('_')[1]
    context.user_data['physical_state'] = state_value
    
    state_emoji = {'1': '😢 Очень плохо', '2': '😕 Плохо', '3': '😐 Нормально', '4': '🙂 Хорошо', '5': '😊 Отлично'}
    keyboard = [['✅ Есть', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    try:
        await query.edit_message_text(f"💪 Физическое состояние: {state_emoji.get(state_value, state_value)}", parse_mode='HTML')
    except:
        pass
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="👶 <b>Есть ли у вас дети?</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return CHILDREN

async def children(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = clean_answer(update.message.text)
    context.user_data['children'] = answer
    
    if answer == 'Есть':
        await update.message.reply_text(
            "👶 <b>Укажите возраст детей:</b>\nНапример: 5 лет, 10 лет",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        return CHILDREN_AGE
    else:
        context.user_data['children_age'] = 'Нет детей'
        keyboard = [['✅ Да', '❌ Нет']]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(
            "🤧 <b>Есть ли у вас аллергия?</b>",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return ALLERGY

async def children_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['children_age'] = update.message.text
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "🤧 <b>Есть ли у вас аллергия?</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return ALLERGY

async def allergy(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    answer = clean_answer(update.message.text)
    context.user_data['allergy'] = answer
    
    if answer == 'Да':
        await update.message.reply_text(
            "🤧 <b>Опишите на что у вас аллергия:</b>",
            reply_markup=ReplyKeyboardRemove(),
            parse_mode='HTML'
        )
        return ALLERGY_DETAILS
    else:
        context.user_data['allergy_details'] = 'Нет аллергии'
        keyboard = [
            [InlineKeyboardButton("😢 1 - Очень плохо", callback_data='mental_1'),
             InlineKeyboardButton("😕 2 - Плохо", callback_data='mental_2')],
            [InlineKeyboardButton("😐 3 - Нормально", callback_data='mental_3'),
             InlineKeyboardButton("🙂 4 - Хорошо", callback_data='mental_4')],
            [InlineKeyboardButton("😊 5 - Отлично", callback_data='mental_5')]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "🧠 <b>Оцените ваше психическое состояние:</b>\nОт 1 (очень плохо) до 5 (отлично)",
            reply_markup=reply_markup,
            parse_mode='HTML'
        )
        return MENTAL_STATE

async def allergy_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['allergy_details'] = update.message.text
    keyboard = [
        [InlineKeyboardButton("😢 1 - Очень плохо", callback_data='mental_1'),
         InlineKeyboardButton("😕 2 - Плохо", callback_data='mental_2')],
        [InlineKeyboardButton("😐 3 - Нормально", callback_data='mental_3'),
         InlineKeyboardButton("🙂 4 - Хорошо", callback_data='mental_4')],
        [InlineKeyboardButton("😊 5 - Отлично", callback_data='mental_5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "🧠 <b>Оцените ваше психическое состояние:</b>\nОт 1 (очень плохо) до 5 (отлично)",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return MENTAL_STATE

async def mental_state(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    state_value = query.data.split('_')[1]
    context.user_data['mental_state'] = state_value
    
    state_emoji = {'1': '😢 Очень плохо', '2': '😕 Плохо', '3': '😐 Нормально', '4': '🙂 Хорошо', '5': '😊 Отлично'}
    try:
        await query.edit_message_text(f"🧠 Психическое состояние: {state_emoji.get(state_value, state_value)}", parse_mode='HTML')
    except:
        pass
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🧠 <b>Опишите подробнее ваше психическое состояние:</b>\nКак вы себя чувствуете эмоционально?",
        parse_mode='HTML'
    )
    return MENTAL_STATE_DETAILS

async def mental_state_details(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['mental_state_details'] = update.message.text
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "🩹 <b>Есть ли проблемы на коже?</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return SKIN_PROBLEMS

async def skin_problems(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['skin_problems'] = clean_answer(update.message.text)
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "🦶 <b>Есть ли сухость на пятках, локтях, заеды?</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return DRYNESS

async def dryness(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['dryness'] = clean_answer(update.message.text)
    keyboard = [
        [InlineKeyboardButton("1 - Минимальное", callback_data='sweat_1'),
         InlineKeyboardButton("2 - Слабое", callback_data='sweat_2')],
        [InlineKeyboardButton("3 - Среднее", callback_data='sweat_3'),
         InlineKeyboardButton("4 - Сильное", callback_data='sweat_4')],
        [InlineKeyboardButton("5 - Очень сильное", callback_data='sweat_5')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "💦 <b>Оцените потоотделение:</b>\nОт 1 (минимальное) до 5 (очень сильное)",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return SWEATING

async def sweating(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    sweat_value = query.data.split('_')[1]
    context.user_data['sweating'] = sweat_value
    
    sweat_labels = {'1': 'Минимальное', '2': 'Слабое', '3': 'Среднее', '4': 'Сильное', '5': 'Очень сильное'}
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    try:
        await query.edit_message_text(f"💦 Потоотделение: {sweat_labels.get(sweat_value, sweat_value)}", parse_mode='HTML')
    except:
        pass
    
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🕸️ <b>Есть ли сосудистая сетка (звёздочки) на лице, теле?</b>",
        reply_markup=reply_markup,
        parse_mode='HTML'
    )
    return VASCULAR

# Остальные функции (сокращенно для экономии места)
async def vascular(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['vascular'] = clean_answer(update.message.text)
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🦵 <b>Бывает ли тяжесть в ногах?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return HEAVY_LEGS

async def heavy_legs(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['heavy_legs'] = clean_answer(update.message.text)
    await update.message.reply_text("😴 <b>Укажите продолжительность сна:</b>\nНапример: 7-8 часов", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return SLEEP_DURATION

async def sleep_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['sleep_duration'] = update.message.text
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🔙 <b>Есть ли боли в спине?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return BACK_PAIN

async def back_pain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['back_pain'] = clean_answer(update.message.text)
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🦴 <b>Есть ли боли в суставах?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return JOINT_PAIN

async def joint_pain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['joint_pain'] = clean_answer(update.message.text)
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("👅 <b>Есть ли с утра неприятный привкус или сухость во рту?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return MORNING_TASTE

async def morning_taste(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['morning_taste'] = clean_answer(update.message.text)
    keyboard = [['Очень часто', 'Часто'], ['Редко', 'Очень редко']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🤒 <b>Как часто болеете (ОРВИ, ОРЗ)?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return ILLNESS_FREQUENCY

async def illness_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['illness_frequency'] = update.message.text
    await update.message.reply_text("😰 <b>Опишите уровень стресса:</b>", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return STRESS

async def stress(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['stress'] = update.message.text
    await update.message.reply_text("🚽 <b>Сколько раз в день стул? Как часто мочеиспускание?</b>", parse_mode='HTML')
    return STOOL_URINATION

async def stool_urination(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['stool_urination'] = update.message.text
    await update.message.reply_text("🩺 <b>Какое давление обычно?</b>\nНапример: 120/80", parse_mode='HTML')
    return PRESSURE

async def pressure(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['pressure'] = update.message.text
    keyboard = [['Повышенное', 'Пониженное', 'Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("📊 <b>Есть ли предрасположенность к повышенному/пониженному давлению?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return PRESSURE_PREDISPOSITION

async def pressure_predisposition(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['pressure_predisposition'] = update.message.text
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("💔 <b>Есть ли боли в сердце?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return HEART_PAIN

async def heart_pain(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['heart_pain'] = clean_answer(update.message.text)
    gender = context.user_data.get('gender')
    
    if gender == 'Женский':
        await update.message.reply_text("🩸 <b>Укажите информацию о цикле и ПМС:</b>", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
        return WOMEN_CYCLE
    else:
        context.user_data['women_cycle'] = 'Не применимо'
        await update.message.reply_text("🤕 <b>Какие травмы были?</b>\nЕсли не было, напишите 'нет'", reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
        return INJURIES

async def women_cycle(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['women_cycle'] = update.message.text
    await update.message.reply_text("🤕 <b>Какие травмы были?</b>\nЕсли не было, напишите 'нет'", parse_mode='HTML')
    return INJURIES

async def injuries(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['injuries'] = update.message.text
    await update.message.reply_text("🏥 <b>Хронические заболевания:</b>", parse_mode='HTML')
    return CHRONIC_DISEASES

async def chronic_diseases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['chronic_diseases'] = update.message.text
    await update.message.reply_text("👨‍👩‍👧‍👦 <b>Какие заболевания у родственников?</b>", parse_mode='HTML')
    return RELATIVES_DISEASES

async def relatives_diseases(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['relatives_diseases'] = update.message.text
    await update.message.reply_text("⚖️ <b>Ваш вес на сегодня (в кг):</b>", parse_mode='HTML')
    return CURRENT_WEIGHT

async def current_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['current_weight'] = update.message.text
    await update.message.reply_text("⚖️ <b>Ваш комфортный вес (в кг):</b>", parse_mode='HTML')
    return COMFORT_WEIGHT

async def comfort_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['comfort_weight'] = update.message.text
    keyboard = [
        ['36.6'],
        ['От 37 до 38', 'От 38 до 39'],
        ['Выше 39']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🌡️ <b>Какая температура тела в данный момент?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return BODY_TEMPERATURE

async def body_temperature(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['body_temperature'] = update.message.text
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🫁 <b>Бывает ли одышка?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return SHORTNESS_BREATH

async def shortness_breath(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['shortness_breath'] = clean_answer(update.message.text)
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("😮‍💨 <b>Бывает ли ощущение, что не хватает воздуха?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return AIR_LACK

async def air_lack(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['air_lack'] = clean_answer(update.message.text)
    keyboard = [['✅ Да', '❌ Нет']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text("🫣 <b>Бывает ли ощущение комка в горле?</b>", reply_markup=reply_markup, parse_mode='HTML')
    return THROAT_LUMP

async def throat_lump(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['throat_lump'] = clean_answer(update.message.text)
    
    user_id = update.effective_user.id
    username = update.effective_user.username or "Не указан"
    first_name = update.effective_user.first_name or ""
    user_data_storage[user_id] = context.user_data.copy()
    
    # Формируем ОДНО красивое сообщение для админов
    admin_message = f"🆕 <b>НОВАЯ АНКЕТА!</b>\n"
    admin_message += f"━━━━━━━━━━━━━━━━━━━━\n"
    admin_message += f"👤 {first_name} @{username} (ID: {user_id})\n"
    admin_message += f"🎯 <b>ПРОЦЕДУРА:</b> {context.user_data.get('services')}\n\n"
    
    admin_message += f"📋 <b>ЛИЧНЫЕ ДАННЫЕ:</b>\n"
    admin_message += f"• Ф.И.О: {context.user_data.get('fio')}\n"
    admin_message += f"• Пол: {context.user_data.get('gender')}\n"
    admin_message += f"• Дата рождения: {context.user_data.get('birth_date')}\n"
    admin_message += f"• Email: {context.user_data.get('email')}\n"
    admin_message += f"• Телефон: {context.user_data.get('phone')}\n"
    admin_message += f"• Соц. сети: {context.user_data.get('social_media')}\n\n"
    
    admin_message += f"📝 <b>ПРИЧИНА:</b> {context.user_data.get('reason')}\n\n"
    
    admin_message += f"💪 <b>СОСТОЯНИЕ:</b>\n"
    admin_message += f"• Физ: {context.user_data.get('physical_state')}/5\n"
    admin_message += f"• Псих: {context.user_data.get('mental_state')}/5 ({context.user_data.get('mental_state_details')})\n"
    admin_message += f"• Стресс: {context.user_data.get('stress')}\n\n"
    
    admin_message += f"🏥 <b>ЗДОРОВЬЕ:</b>\n"
    admin_message += f"• Дети: {context.user_data.get('children')}"
    if context.user_data.get('children') == 'Есть':
        admin_message += f" ({context.user_data.get('children_age')})"
    admin_message += f"\n"
    if context.user_data.get('gender') == 'Женский':
        admin_message += f"• Цикл/ПМС: {context.user_data.get('women_cycle')}\n"
    admin_message += f"• Аллергия: {context.user_data.get('allergy')}"
    if context.user_data.get('allergy') == 'Да':
        admin_message += f" ({context.user_data.get('allergy_details')})"
    admin_message += f"\n"
    admin_message += f"• Хронические: {context.user_data.get('chronic_diseases')}\n"
    admin_message += f"• Травмы: {context.user_data.get('injuries')}\n"
    admin_message += f"• Болеет: {context.user_data.get('illness_frequency')}\n\n"
    
    admin_message += f"🩺 <b>СИМПТОМЫ:</b>\n"
    admin_message += f"• Кожа: {context.user_data.get('skin_problems')}, Сухость: {context.user_data.get('dryness')}\n"
    admin_message += f"• Пот: {context.user_data.get('sweating')}/5, Сосуды: {context.user_data.get('vascular')}\n"
    admin_message += f"• Ноги: {context.user_data.get('heavy_legs')}, Спина: {context.user_data.get('back_pain')}\n"
    admin_message += f"• Суставы: {context.user_data.get('joint_pain')}, Сердце: {context.user_data.get('heart_pain')}\n"
    admin_message += f"• Одышка: {context.user_data.get('shortness_breath')}, Воздух: {context.user_data.get('air_lack')}\n"
    admin_message += f"• Горло: {context.user_data.get('throat_lump')}, Рот утром: {context.user_data.get('morning_taste')}\n\n"
    
    admin_message += f"💊 <b>ДОПОЛНИТЕЛЬНО:</b>\n"
    admin_message += f"• Сон: {context.user_data.get('sleep_duration')}\n"
    admin_message += f"• Стул/моча: {context.user_data.get('stool_urination')}\n"
    admin_message += f"• Давление: {context.user_data.get('pressure')} ({context.user_data.get('pressure_predisposition')})\n"
    admin_message += f"• Вес: {context.user_data.get('current_weight')} кг (комфорт: {context.user_data.get('comfort_weight')} кг)\n"
    admin_message += f"• Температура: {context.user_data.get('body_temperature')}\n"
    admin_message += f"• Родственники: {context.user_data.get('relatives_diseases')}\n"
    
    # Отправляем админам
    admin_ids = get_admin_ids()
    for admin_id in admin_ids:
        try:
            await context.bot.send_message(chat_id=admin_id, text=admin_message, parse_mode='HTML')
            logger.info(f"✅ Анкета отправлена админу {admin_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки админу {admin_id}: {e}")
    
    # Сообщение пользователю
    summary = "✅ <b>Анкета успешно заполнена!</b>\n\n"
    summary += "Спасибо за ваши ответы! 🙏\n"
    summary += "Ваша анкета отправлена нашим специалистам.\n\n"
    summary += "📞 <b>Мы свяжемся с вами в ближайшее время!</b>\n\n"
    summary += f"━━━━━━━━━━━━━━━━━━━━\n"
    summary += f"📋 <b>Ваши контактные данные:</b>\n"
    summary += f"👤 {context.user_data.get('fio')}\n"
    summary += f"📱 {context.user_data.get('phone')}\n"
    summary += f"📧 {context.user_data.get('email')}\n"
    summary += f"🎯 Процедура: {context.user_data.get('services')}\n"
    
    await update.message.reply_text(summary, reply_markup=ReplyKeyboardRemove(), parse_mode='HTML')
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Анкетирование отменено. Для начала заново используйте /start", reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def main() -> None:
    token = os.getenv('BOT_TOKEN')
    if not token:
        logger.error("BOT_TOKEN не найден в переменных окружения!")
        return
    
    # Создаем бот с увеличенным таймаутом
    request = HTTPXRequest(connect_timeout=30.0, read_timeout=30.0, write_timeout=30.0)
    application = Application.builder().token(token).request(request).build()
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            SERVICES: [MessageHandler(filters.TEXT & ~filters.COMMAND, services)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            FIO: [MessageHandler(filters.TEXT & ~filters.COMMAND, fio)],
            BIRTH_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth_date)],
            EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, email)],
            PHONE: [MessageHandler(filters.TEXT & ~filters.COMMAND, phone)],
            SOCIAL_MEDIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, social_media)],
            REASON: [MessageHandler(filters.TEXT & ~filters.COMMAND, reason)],
            PHYSICAL_STATE: [CallbackQueryHandler(physical_state)],
            CHILDREN: [MessageHandler(filters.TEXT & ~filters.COMMAND, children)],
            CHILDREN_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, children_age)],
            ALLERGY: [MessageHandler(filters.TEXT & ~filters.COMMAND, allergy)],
            ALLERGY_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, allergy_details)],
            MENTAL_STATE: [CallbackQueryHandler(mental_state)],
            MENTAL_STATE_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, mental_state_details)],
            SKIN_PROBLEMS: [MessageHandler(filters.TEXT & ~filters.COMMAND, skin_problems)],
            DRYNESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, dryness)],
            SWEATING: [CallbackQueryHandler(sweating)],
            VASCULAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, vascular)],
            HEAVY_LEGS: [MessageHandler(filters.TEXT & ~filters.COMMAND, heavy_legs)],
            SLEEP_DURATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, sleep_duration)],
            BACK_PAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, back_pain)],
            JOINT_PAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, joint_pain)],
            MORNING_TASTE: [MessageHandler(filters.TEXT & ~filters.COMMAND, morning_taste)],
            ILLNESS_FREQUENCY: [MessageHandler(filters.TEXT & ~filters.COMMAND, illness_frequency)],
            STRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, stress)],
            STOOL_URINATION: [MessageHandler(filters.TEXT & ~filters.COMMAND, stool_urination)],
            PRESSURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, pressure)],
            PRESSURE_PREDISPOSITION: [MessageHandler(filters.TEXT & ~filters.COMMAND, pressure_predisposition)],
            HEART_PAIN: [MessageHandler(filters.TEXT & ~filters.COMMAND, heart_pain)],
            WOMEN_CYCLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, women_cycle)],
            INJURIES: [MessageHandler(filters.TEXT & ~filters.COMMAND, injuries)],
            CHRONIC_DISEASES: [MessageHandler(filters.TEXT & ~filters.COMMAND, chronic_diseases)],
            RELATIVES_DISEASES: [MessageHandler(filters.TEXT & ~filters.COMMAND, relatives_diseases)],
            CURRENT_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, current_weight)],
            COMFORT_WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, comfort_weight)],
            BODY_TEMPERATURE: [MessageHandler(filters.TEXT & ~filters.COMMAND, body_temperature)],
            SHORTNESS_BREATH: [MessageHandler(filters.TEXT & ~filters.COMMAND, shortness_breath)],
            AIR_LACK: [MessageHandler(filters.TEXT & ~filters.COMMAND, air_lack)],
            THROAT_LUMP: [MessageHandler(filters.TEXT & ~filters.COMMAND, throat_lump)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    logger.info("🚀 Бот запущен!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()