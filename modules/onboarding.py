"""
Onboarding Module
Handles the initial user onboarding process to inform clients about the bot's purpose.
"""

import logging
import requests
import json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OnboardingModule:
    def __init__(self, db_manager, state_manager):
        self.db_manager = db_manager
        self.state_manager = state_manager
        self.onboarding_steps = [
            self._welcome_message,
            self._explain_purpose,
            self._show_disclaimer,
            self._collect_user_age,
            self._collect_city_info,
            self._confirm_timezone,
            self._confirm_messaging,
            self._get_ready_confirmation
        ]
        self.current_step = 0
    
    async def _send_message(self, update, context, text, reply_markup=None, parse_mode='Markdown'):
        """Helper method to send messages in both message and callback query contexts"""
        logger.info(f"_send_message called - update.message: {update.message is not None}, update.callback_query: {update.callback_query is not None}")
        
        if update.message:
            logger.info("Sending message via update.message.reply_text")
            await update.message.reply_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        else:
            logger.info("Sending message via update.callback_query.edit_message_text")
            await update.callback_query.edit_message_text(text, parse_mode=parse_mode, reply_markup=reply_markup)
        
        logger.info("_send_message completed")
    
    async def start_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the onboarding process"""
        user_id = update.effective_user.id
        
        # Get user's Telegram profile info
        user_profile = await self.db_manager.get_user_profile(user_id)
        first_name = user_profile.get('first_name', '') if user_profile else ''
        last_name = user_profile.get('last_name', '') if user_profile else ''
        full_name = f"{first_name} {last_name}".strip()
        
        # Initialize user data with default language
        state_data = {
            "onboarding_step": 0,
            "language": "ru",
            "user_name": full_name,
            "user_age": None,
            "city": None,
            "timezone": None,
            "messaging_confirmed": False
        }
        
        # Set user state to onboarding
        logger.info(f"Setting user {user_id} state to 'onboarding' with data: {state_data}")
        await self.db_manager.set_user_state(user_id, "onboarding", state_data)
        
        # Verify state was set
        verify_state = await self.db_manager.get_user_state(user_id)
        logger.info(f"Verified user {user_id} state after setting: {verify_state}")
        
        # Start with welcome message
        logger.info(f"Starting onboarding for user {user_id}, calling _welcome_message")
        await self._welcome_message(update, context)
        logger.info(f"Welcome message call completed for user {user_id}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages during onboarding"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Get current onboarding step
        state_data = await self.db_manager.get_user_state_data(user_id)
        current_step = state_data.get("onboarding_step", 0)
        
        # Handle specific step inputs
        if current_step == 2:  # Age collection step
            await self._process_age_input(update, context, message_text)
        elif current_step == 3:  # City collection step
            await self._process_city_input(update, context, message_text)
        elif current_step == 3.5:  # Timezone input step
            await self._process_timezone_input(update, context, message_text)
        elif current_step == 3.6:  # Custom timezone input step
            await self._process_custom_timezone(update, context, message_text)
        elif current_step == 4:  # Timezone confirmation step
            await self._process_timezone_confirmation(update, context, message_text)
        elif current_step == 5:  # Messaging confirmation step
            await self._process_messaging_confirmation(update, context, message_text)
        else:
            # Continue to next step
            if current_step < len(self.onboarding_steps) - 1:
                await self.db_manager.update_user_state_data(user_id, {"onboarding_step": current_step + 1})
                await self.onboarding_steps[current_step + 1](update, context)
            else:
                # Onboarding complete, move to option selection
                await self._complete_onboarding(update, context)
    
    async def _welcome_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Send welcome message"""
        user_id = update.effective_user.id
        logger.info(f"Sending welcome message to user {user_id}")
        
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_name = state_data.get("user_name", "")
        logger.info(f"User name from state: '{user_name}'")
        
        if user_name:
            welcome_text = f"""
🎉 **Привет, {user_name}!**

Я **HackReality** - бот, который помогает людям достичь своей мечты и преодолеть сложности. Причем практически любые.

Наш мир так устроен, что большинство наших проблем, даже кажется неразрешимых, или неслучающихся мечт, связаны с нами, нашим мышлением и нашей личностью.

В большинстве случаев ситуацию можно переломить, уделив немного внимания себе и работе с собой, чтобы ситуация изменилась! У меня есть такой способ! 😉

Готов узнать больше? 🚀
            """
        else:
            welcome_text = """
🎉 **Приветствую тебя!**

Я **HackReality** - бот, который помогает людям достичь своей мечты и преодолеть сложности. Причем практически любые.

Наш мир так устроен, что большинство наших проблем, даже кажется неразрешимых, или неслучающихся мечт, связаны с нами, нашим мышлением и нашей личностью.

В большинстве случаев ситуацию можно переломить, уделив немного внимания себе и работе с собой, чтобы ситуация изменилась! У меня есть такой способ! 😉

Готов узнать больше? 🚀
            """
        
        keyboard = [[InlineKeyboardButton("Да, расскажи больше! 🚀", callback_data="continue_onboarding")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        logger.info(f"About to send welcome message to user {user_id}")
        await self._send_message(update, context, welcome_text, reply_markup)
        logger.info(f"Welcome message sent to user {user_id}")
    
    async def _explain_purpose(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Explain the bot's main purpose"""
        purpose_text = """
🎯 **Как я работаю:**

Я помогаю тебе изменить свою реальность через:
• 🔍 Анализ твоих текущих проблем и целей
• 🧠 Работу с мышлением и убеждениями
• 💪 Развитие личностных качеств
• 🎯 Пошаговые стратегии достижения мечты
• 📱 Регулярную поддержку и мотивацию

Я не просто даю советы - я помогаю тебе реально изменить свою жизнь! ✨

Готов начать работу над собой? 🚀
        """
        
        keyboard = [[InlineKeyboardButton("Да, готов! 🎯", callback_data="continue_onboarding")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self._send_message(update, context, purpose_text, reply_markup)
    
    async def _show_disclaimer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show important disclaimer about psychological practice"""
        disclaimer_text = """
⚠️ **ВАЖНОЕ УВЕДОМЛЕНИЕ**

**HackReality** - это психологическая практика, направленная на личностное развитие и достижение целей.

**📋 ОТВЕТСТВЕННОСТЬ:**
• Все действия, решения и изменения в вашей жизни осуществляются **исключительно под вашу ответственность**
• Вы самостоятельно принимаете решения о выполнении предложенных задач и упражнений
• Мы не несем ответственности за последствия ваших действий или бездействия
• При возникновении серьезных психологических проблем рекомендуется обратиться к квалифицированному специалисту

**🎯 ЦЕЛЬ СЕРВИСА:**
• Предоставление инструментов для личностного развития
• Поддержка в достижении поставленных целей
• Помощь в изменении мышления и подхода к жизни
• Мотивация и сопровождение на пути к мечте

**✅ ПОДТВЕРЖДЕНИЕ:**
Продолжая использование сервиса, вы подтверждаете, что:
• Понимаете характер психологической практики
• Принимаете полную ответственность за свои действия
• Согласны с условиями использования

**Готовы продолжить с пониманием этих условий?** 🤝
        """
        
        keyboard = [
            [InlineKeyboardButton("Да, понимаю и принимаю ✅", callback_data="accept_disclaimer")],
            [InlineKeyboardButton("Нужно больше информации ❓", callback_data="disclaimer_help")],
            [InlineKeyboardButton("Отменить ❌", callback_data="cancel_onboarding")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await self._send_message(update, context, disclaimer_text, reply_markup)
    
    async def _collect_user_age(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect user's age"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_name = state_data.get("user_name", "")
        
        if user_name:
            age_text = f"""
👋 **Приятно познакомиться, {user_name}!**

Чтобы я мог лучше понимать тебя и создавать более подходящий контент, расскажи мне свой возраст.

**Просто напиши свой возраст:**
• Например: "25" или "тридцать лет"
• Или укажи возрастной диапазон: "25-30"

Это поможет мне адаптировать контент под твою возрастную группу! 🎯
            """
        else:
            age_text = """
👋 **Приятно познакомиться!**

Чтобы я мог лучше понимать тебя и создавать более подходящий контент, расскажи мне свой возраст.

**Просто напиши свой возраст:**
• Например: "25" или "тридцать лет"
• Или укажи возрастной диапазон: "25-30"

Это поможет мне адаптировать контент под твою возрастную группу! 🎯
            """
        
        await self._send_message(update, context, age_text)
    
    async def _process_age_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, age_input: str):
        """Process age input from user"""
        user_id = update.effective_user.id
        
        # Extract age from input
        age = self._extract_age_from_text(age_input)
        
        if age:
            # Update user data
            await self.db_manager.update_user_state_data(user_id, {
                "user_age": age
            })
            
            # Move to city collection
            await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 3})
            await self._collect_city_info(update, context)
        else:
            await self._handle_invalid_age(update, context, age_input)
    
    def _extract_age_from_text(self, text: str) -> Optional[int]:
        """Extract age from text input"""
        import re
        
        # Remove extra spaces and convert to lowercase
        text = text.strip().lower()
        
        # Try to find numbers
        numbers = re.findall(r'\d+', text)
        
        if numbers:
            age = int(numbers[0])
            # Validate age range
            if 13 <= age <= 100:
                return age
        
        # Try to parse written numbers (basic Russian)
        age_mapping = {
            "тринадцать": 13, "четырнадцать": 14, "пятнадцать": 15,
            "шестнадцать": 16, "семнадцать": 17, "восемнадцать": 18,
            "девятнадцать": 19, "двадцать": 20, "двадцать один": 21,
            "двадцать два": 22, "двадцать три": 23, "двадцать четыре": 24,
            "двадцать пять": 25, "тридцать": 30, "сорок": 40,
            "пятьдесят": 50, "шестьдесят": 60, "семьдесят": 70
        }
        
        for word, age in age_mapping.items():
            if word in text:
                return age
        
        return None
    
    async def _handle_invalid_age(self, update: Update, context: ContextTypes.DEFAULT_TYPE, age_input: str):
        """Handle invalid age input"""
        invalid_text = f"""
❌ **Не понял твой возраст**

Я не смог определить возраст из "{age_input}".

**Попробуй еще раз:**
• Напиши просто число: "25"
• Или словами: "двадцать пять"
• Или диапазон: "25-30"

**Примеры:**
• "25" - для 25 лет
• "тридцать" - для 30 лет
• "18-25" - для возрастного диапазона

Пожалуйста, укажи свой возраст! 🎯
        """
        
        await update.message.reply_text(invalid_text, parse_mode='Markdown')
    
    async def _collect_city_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Collect user's city information"""
        city_text = """
🌍 **Откуда ты?**

Чтобы я мог отправлять тебе сообщения в удобное время, мне нужно знать твой город.

**Просто напиши название своего города:**
• Москва
• Санкт-Петербург  
• Екатеринбург
• Новосибирск
• Или любой другой город

Это поможет мне определить твой часовой пояс и отправлять сообщения тогда, когда тебе удобно! ⏰
        """
        
        await update.message.reply_text(city_text, parse_mode='Markdown')
    
    async def _confirm_timezone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm timezone information"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        city = state_data.get("city", "твой город")
        timezone_name = state_data.get("timezone_name", "Московское время")
        timezone_offset = state_data.get("timezone_offset", "+03:00")
        
        timezone_text = f"""
⏰ **Часовой пояс определен!**

Отлично! Я нашел информацию о твоем городе:

**Город:** {city}
**Часовой пояс:** {timezone_name} ({timezone_offset})

**Я буду отправлять тебе сообщения:**
• Утром: 8:00 - 10:00 (по твоему времени)
• Днем: 12:00 - 14:00 (по твоему времени)
• Вечером: 18:00 - 20:00 (по твоему времени)

Это правильный часовой пояс и удобное время для тебя? 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("Да, все правильно! ✅", callback_data="timezone_ok")],
            [InlineKeyboardButton("Изменить время ⏰", callback_data="change_time")],
            [InlineKeyboardButton("Неправильный город 🌍", callback_data="wrong_city")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(timezone_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _confirm_messaging(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm messaging preferences"""
        messaging_text = """
📱 **Подтверждение отправки сообщений**

Я буду отправлять тебе:
• 🎯 Ежедневные задания и упражнения
• 💡 Мотивационные сообщения
• 📊 Отчеты о прогрессе
• 🆘 Поддержку в сложные моменты

**Важно:** Я буду отправлять сообщения автоматически в удобное для тебя время.

Ты согласен получать эти сообщения? 🤝
        """
        
        keyboard = [
            [InlineKeyboardButton("Да, согласен! ✅", callback_data="messaging_ok")],
            [InlineKeyboardButton("Нет, не хочу ❌", callback_data="messaging_no")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(messaging_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_city_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, city_input: str):
        """Process city input from user"""
        user_id = update.effective_user.id
        
        # Show loading message
        loading_text = """
🔍 **Определяю часовой пояс...**

Пожалуйста, подожди, я ищу информацию о твоем городе в интернете... ⏳
        """
        
        await update.message.reply_text(loading_text, parse_mode='Markdown')
        
        try:
            # Get timezone information from internet
            timezone_info = await self._get_timezone_from_city(city_input)
            
            if timezone_info:
                # Update user data with city and timezone
                await self.db_manager.update_user_state_data(user_id, {
                    "city": city_input,
                    "timezone": timezone_info["timezone"],
                    "timezone_offset": timezone_info["offset"],
                    "timezone_name": timezone_info["name"]
                })
                
                # Move to timezone confirmation
                await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 4})
                await self._confirm_timezone(update, context)
            else:
                # Handle case when city not found
                await self._handle_city_not_found(update, context, city_input)
                
        except Exception as e:
            logger.error(f"Error getting timezone for city {city_input}: {e}")
            await self._handle_timezone_error(update, context, city_input)
    
    async def _get_timezone_from_city(self, city_name: str) -> Dict[str, Any]:
        """Get timezone information for a city from internet"""
        try:
            # Use OpenWeatherMap Geocoding API to get coordinates
            geocoding_url = "http://api.openweathermap.org/geo/1.0/direct"
            geocoding_params = {
                "q": city_name,
                "limit": 1,
                "appid": "your_openweather_api_key"  # You'll need to add this to your .env
            }
            
            # For demo purposes, we'll use a free timezone API
            # In production, you should use a proper API key
            timezone_url = f"http://worldtimeapi.org/api/timezone"
            
            # Get list of available timezones
            response = requests.get(timezone_url, timeout=10)
            if response.status_code == 200:
                timezones = response.json()
                
                # Simple mapping for common cities (fallback)
                city_timezone_mapping = {
                    "москва": "Europe/Moscow",
                    "санкт-петербург": "Europe/Moscow",
                    "питер": "Europe/Moscow",
                    "екатеринбург": "Asia/Yekaterinburg",
                    "новосибирск": "Asia/Novosibirsk",
                    "красноярск": "Asia/Krasnoyarsk",
                    "иркутск": "Asia/Irkutsk",
                    "владивосток": "Asia/Vladivostok",
                    "хабаровск": "Asia/Vladivostok",
                    "самара": "Europe/Samara",
                    "казань": "Europe/Moscow",
                    "нижний новгород": "Europe/Moscow",
                    "челябинск": "Asia/Yekaterinburg",
                    "омск": "Asia/Omsk",
                    "ростов-на-дону": "Europe/Moscow",
                    "уфа": "Asia/Yekaterinburg",
                    "волгоград": "Europe/Moscow",
                    "пермь": "Asia/Yekaterinburg",
                    "краснодар": "Europe/Moscow",
                    "саратов": "Europe/Moscow"
                }
                
                city_lower = city_name.lower().strip()
                timezone_name = city_timezone_mapping.get(city_lower, "Europe/Moscow")
                
                # Get timezone details
                timezone_details_url = f"http://worldtimeapi.org/api/timezone/{timezone_name}"
                timezone_response = requests.get(timezone_details_url, timeout=10)
                
                if timezone_response.status_code == 200:
                    timezone_data = timezone_response.json()
                    
                    return {
                        "timezone": timezone_name,
                        "offset": timezone_data.get("utc_offset", "+03:00"),
                        "name": timezone_data.get("timezone", timezone_name),
                        "city": city_name
                    }
            
            # Fallback to default
            return {
                "timezone": "Europe/Moscow",
                "offset": "+03:00",
                "name": "Московское время",
                "city": city_name
            }
            
        except Exception as e:
            logger.error(f"Error fetching timezone data: {e}")
            return None
    
    async def _handle_city_not_found(self, update: Update, context: ContextTypes.DEFAULT_TYPE, city_input: str):
        """Handle case when city is not found"""
        not_found_text = f"""
❌ **Город не найден**

К сожалению, я не смог найти информацию о городе "{city_input}".

**Попробуй еще раз:**
• Напиши название города на русском языке
• Укажи страну, если город не в России
• Проверь правильность написания

Например: "Москва", "Санкт-Петербург", "Нью-Йорк, США"
        """
        
        await update.message.reply_text(not_found_text, parse_mode='Markdown')
    
    async def _handle_timezone_error(self, update: Update, context: ContextTypes.DEFAULT_TYPE, city_input: str):
        """Handle timezone detection error"""
        error_text = f"""
⚠️ **Ошибка определения часового пояса**

Произошла ошибка при определении часового пояса для "{city_input}".

**Что делать:**
• Попробуй написать город еще раз
• Используй более точное название
• Или выбери ближайший крупный город

Я установлю московское время по умолчанию, но ты сможешь изменить его позже.

Попробуй еще раз! 🔄
        """
        
        # Set default timezone
        user_id = update.effective_user.id
        await self.db_manager.update_user_state_data(user_id, {
            "city": city_input,
            "timezone": "Europe/Moscow",
            "timezone_offset": "+03:00",
            "timezone_name": "Московское время"
        })
        
        await update.message.reply_text(error_text, parse_mode='Markdown')
    
    async def _process_timezone_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: str):
        """Process timezone confirmation response"""
        user_id = update.effective_user.id
        
        if any(word in response.lower() for word in ["да", "да", "отлично", "хорошо", "подходит"]):
            # Move to messaging confirmation
            await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 5})
            await self._confirm_messaging(update, context)
        else:
            # Ask for time preferences
            await self._ask_time_preferences(update, context)
    
    async def _process_messaging_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response: str):
        """Process messaging confirmation response"""
        user_id = update.effective_user.id
        
        if any(word in response.lower() for word in ["да", "согласен", "хорошо", "давай"]):
            # Confirm messaging
            await self.db_manager.update_user_state_data(user_id, {
                "messaging_confirmed": True,
                "onboarding_step": 6
            })
            await self._get_ready_confirmation(update, context)
        else:
            # Handle rejection
            await self._handle_messaging_rejection(update, context)
    
    async def _ask_time_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask user for time preferences"""
        time_text = """
⏰ **Какое время тебе удобно?**

Выбери удобные часы для получения сообщений:

**Утренние часы:**
• 7:00 - 9:00
• 8:00 - 10:00
• 9:00 - 11:00

**Дневные часы:**
• 12:00 - 14:00
• 13:00 - 15:00

**Вечерние часы:**
• 18:00 - 20:00
• 19:00 - 21:00
• 20:00 - 22:00

Напиши, какое время тебе больше подходит! 🕐
        """
        
        await update.message.reply_text(time_text, parse_mode='Markdown')
    
    async def _handle_messaging_rejection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messaging rejection"""
        rejection_text = """
😔 **Понятно...**

Если ты передумаешь, ты всегда можешь:
• Написать мне в любое время
• Изменить настройки уведомлений
• Отключить автоматические сообщения

Но помни: регулярная поддержка - это ключ к успеху! 💪

Хочешь продолжить без автоматических сообщений? 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("Да, продолжить 🚀", callback_data="continue_without_messaging")],
            [InlineKeyboardButton("Передумал, хочу сообщения ✅", callback_data="messaging_ok")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(rejection_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_wrong_city(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle when user says the city is wrong"""
        wrong_city_text = """
⏰ **Понятно, давай укажем часовой пояс напрямую!**

Вместо города, просто скажи мне свой часовой пояс.

**Выбери свой часовой пояс:**
• **МСК** - Москва, СПб, Казань (+3)
• **ЕКТ** - Екатеринбург, Челябинск (+5)
• **НВС** - Новосибирск (+7)
• **КРС** - Красноярск (+7)
• **ИРК** - Иркутск (+8)
• **ВЛД** - Владивосток (+10)
• **САМ** - Самара (+4)
• **ОМС** - Омск (+6)
• **Другой** - если твой город не в списке

Напиши сокращение (например: МСК) или "другой" 🤔
        """
        
        # Set state to timezone input
        user_id = update.effective_user.id
        await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 3.5})  # Special step for timezone input
        
        await update.callback_query.edit_message_text(wrong_city_text, parse_mode='Markdown')
    
    async def _handle_disclaimer_acceptance(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle disclaimer acceptance"""
        user_id = update.effective_user.id
        
        # Update user state to record disclaimer acceptance
        await self.db_manager.update_user_state_data(user_id, {
            "disclaimer_accepted": True,
            "disclaimer_accepted_at": context.bot_data.get("current_time", "unknown")
        })
        
        # Continue to next step (age collection) - Force deployment update
        await self._collect_user_age(update, context)
    
    async def _handle_disclaimer_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle disclaimer help request"""
        help_text = """
📚 **Дополнительная информация о сервисе**

**🔬 Что такое психологическая практика?**
Это работа с вашим мышлением, эмоциями и поведением для достижения личных целей и улучшения качества жизни.

**🛡️ Ваша безопасность:**
• Все упражнения и техники безопасны для психического здоровья
• Мы не заменяем профессиональную психотерапию
• При серьезных проблемах рекомендуем обратиться к специалисту
• Вы всегда можете остановить процесс

**⚖️ Правовые аспекты:**
• Сервис предоставляется "как есть"
• Мы не гарантируем конкретные результаты
• Вы несете ответственность за свои решения
• Рекомендуем консультацию с врачом при необходимости

**💡 Как это работает:**
• Анализ ваших целей и препятствий
• Персональные техники развития
• Поддержка и мотивация
• Отслеживание прогресса

**Есть еще вопросы?** 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("Понятно, продолжаем ✅", callback_data="accept_disclaimer")],
            [InlineKeyboardButton("Назад к условиям ↩️", callback_data="back_to_disclaimer")],
            [InlineKeyboardButton("Отменить ❌", callback_data="cancel_onboarding")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        query = update.callback_query
        await query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_onboarding_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle onboarding cancellation"""
        cancellation_text = """
😔 **Понимаю ваше решение**

Если вы передумаете, я всегда буду здесь, чтобы помочь вам достичь ваших целей.

**HackReality** - это инструмент для тех, кто готов изменить свою жизнь к лучшему.

**До свидания!** 👋

*Если хотите начать заново, просто напишите /start*
        """
        
        query = update.callback_query
        await query.edit_message_text(cancellation_text, parse_mode='Markdown')
        
        # Reset user state
        user_id = update.effective_user.id
        await self.db_manager.set_user_state(user_id, "idle", {})
    
    async def _process_timezone_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, timezone_input: str):
        """Process direct timezone input from user"""
        user_id = update.effective_user.id
        
        # Timezone mapping
        timezone_mapping = {
            "мск": {"timezone": "Europe/Moscow", "offset": "+03:00", "name": "Московское время"},
            "ект": {"timezone": "Asia/Yekaterinburg", "offset": "+05:00", "name": "Екатеринбургское время"},
            "нвс": {"timezone": "Asia/Novosibirsk", "offset": "+07:00", "name": "Новосибирское время"},
            "крс": {"timezone": "Asia/Krasnoyarsk", "offset": "+07:00", "name": "Красноярское время"},
            "ирк": {"timezone": "Asia/Irkutsk", "offset": "+08:00", "name": "Иркутское время"},
            "влд": {"timezone": "Asia/Vladivostok", "offset": "+10:00", "name": "Владивостокское время"},
            "сам": {"timezone": "Europe/Samara", "offset": "+04:00", "name": "Самарское время"},
            "омс": {"timezone": "Asia/Omsk", "offset": "+06:00", "name": "Омское время"}
        }
        
        timezone_lower = timezone_input.lower().strip()
        
        if timezone_lower in timezone_mapping:
            timezone_info = timezone_mapping[timezone_lower]
            
            # Update user data
            await self.db_manager.update_user_state_data(user_id, {
                "city": "Пользователь указал часовой пояс напрямую",
                "timezone": timezone_info["timezone"],
                "timezone_offset": timezone_info["offset"],
                "timezone_name": timezone_info["name"]
            })
            
            # Move to timezone confirmation
            await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 4})
            await self._confirm_timezone(update, context)
            
        elif timezone_lower in ["другой", "other", "иной"]:
            await self._ask_custom_timezone(update, context)
        else:
            # Try to parse as custom timezone
            await self._process_custom_timezone(update, context, timezone_input)
    
    async def _ask_custom_timezone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask for custom timezone"""
        custom_text = """
🌍 **Укажи свой часовой пояс**

Напиши свой часовой пояс в одном из форматов:

**Варианты:**
• **UTC+3** (для Москвы)
• **UTC+5** (для Екатеринбурга)
• **UTC-5** (для Нью-Йорка)
• **GMT+3** (альтернативный формат)
• **+3** (сокращенный формат)

Или просто напиши разницу с Москвой:
• **+2** (на 2 часа больше Москвы)
• **-3** (на 3 часа меньше Москвы)
• **0** (как в Москве)

Например: "UTC+3" или "+2" 🕐
        """
        
        # Set state to custom timezone input
        user_id = update.effective_user.id
        await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 3.6})
        
        await update.message.reply_text(custom_text, parse_mode='Markdown')
    
    async def _handle_invalid_timezone(self, update: Update, context: ContextTypes.DEFAULT_TYPE, timezone_input: str):
        """Handle invalid timezone input"""
        invalid_text = f"""
❌ **Не понял твой часовой пояс**

Я не смог распознать "{timezone_input}".

**Попробуй еще раз:**
• Напиши сокращение: МСК, ЕКТ, НВС, КРС, ИРК, ВЛД, САМ, ОМС
• Или напиши "другой" для других вариантов
• Или укажи разницу с Москвой: +2, -3, 0

**Примеры:**
• "МСК" - для Москвы
• "другой" - для других городов
• "+2" - если на 2 часа больше Москвы
        """
        
        await update.message.reply_text(invalid_text, parse_mode='Markdown')
    
    async def _process_custom_timezone(self, update: Update, context: ContextTypes.DEFAULT_TYPE, timezone_input: str):
        """Process custom timezone input"""
        user_id = update.effective_user.id
        
        try:
            # Parse different timezone formats
            timezone_info = self._parse_custom_timezone(timezone_input)
            
            if timezone_info:
                # Update user data
                await self.db_manager.update_user_state_data(user_id, {
                    "city": "Пользователь указал часовой пояс напрямую",
                    "timezone": timezone_info["timezone"],
                    "timezone_offset": timezone_info["offset"],
                    "timezone_name": timezone_info["name"]
                })
                
                # Move to timezone confirmation
                await self.db_manager.update_user_state_data(user_id, {"onboarding_step": 4})
                await self._confirm_timezone(update, context)
            else:
                await self._handle_invalid_timezone(update, context, timezone_input)
                
        except Exception as e:
            logger.error(f"Error processing custom timezone {timezone_input}: {e}")
            await self._handle_invalid_timezone(update, context, timezone_input)
    
    def _parse_custom_timezone(self, timezone_input: str) -> Optional[Dict[str, Any]]:
        """Parse custom timezone input"""
        import re
        
        timezone_input = timezone_input.strip().upper()
        
        # Parse UTC format (UTC+3, UTC-5, etc.)
        utc_match = re.match(r'UTC([+-]?\d+)', timezone_input)
        if utc_match:
            offset_hours = int(utc_match.group(1))
            return self._create_timezone_info(offset_hours)
        
        # Parse GMT format (GMT+3, GMT-5, etc.)
        gmt_match = re.match(r'GMT([+-]?\d+)', timezone_input)
        if gmt_match:
            offset_hours = int(gmt_match.group(1))
            return self._create_timezone_info(offset_hours)
        
        # Parse simple format (+3, -5, 0, etc.)
        simple_match = re.match(r'([+-]?\d+)', timezone_input)
        if simple_match:
            offset_hours = int(simple_match.group(1))
            return self._create_timezone_info(offset_hours)
        
        return None
    
    def _create_timezone_info(self, offset_hours: int) -> Dict[str, Any]:
        """Create timezone info from offset hours"""
        # Convert to timezone name
        if offset_hours == 3:
            timezone_name = "Europe/Moscow"
            display_name = "Московское время"
        elif offset_hours == 5:
            timezone_name = "Asia/Yekaterinburg"
            display_name = "Екатеринбургское время"
        elif offset_hours == 7:
            timezone_name = "Asia/Novosibirsk"
            display_name = "Новосибирское время"
        elif offset_hours == 8:
            timezone_name = "Asia/Irkutsk"
            display_name = "Иркутское время"
        elif offset_hours == 10:
            timezone_name = "Asia/Vladivostok"
            display_name = "Владивостокское время"
        elif offset_hours == 4:
            timezone_name = "Europe/Samara"
            display_name = "Самарское время"
        elif offset_hours == 6:
            timezone_name = "Asia/Omsk"
            display_name = "Омское время"
        else:
            # Generic timezone
            timezone_name = f"Etc/GMT{offset_hours:+d}"
            display_name = f"UTC{offset_hours:+d}"
        
        # Format offset
        offset_str = f"{offset_hours:+03d}:00"
        
        return {
            "timezone": timezone_name,
            "offset": offset_str,
            "name": display_name
        }
    
    async def _show_features(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show key features"""
        features_text = """
✨ **Key Features:**

🔹 **Personalized Content**: Content created specifically for your style and needs
🔹 **Multiple Plans**: Choose from Extreme, 2-week, or Regular subscription options
🔹 **Smart Learning**: I learn from your preferences to improve over time
🔹 **Flexible Delivery**: Content delivered when and how you want it
🔹 **Quality Assurance**: All content is reviewed and optimized for your goals

Ready to see what plan works best for you? 🎯
        """
        
        keyboard = [[InlineKeyboardButton("Show me the plans! 💎", callback_data="continue_onboarding")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(features_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _get_ready_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Get confirmation that user is ready to proceed"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_name = state_data.get("user_name", "")
        user_age = state_data.get("user_age", "")
        city = state_data.get("city", "твой город")
        messaging_confirmed = state_data.get("messaging_confirmed", False)
        
        # Format age display
        age_display = f"{user_age} лет" if user_age else "не указан"
        
        ready_text = f"""
🎊 **Отлично, {user_name}! Мы готовы начать!**

Теперь я знаю:
• 👤 Твое имя: {user_name}
• 🎂 Твой возраст: {age_display}
• 🌍 Твой город: {city}
• ⏰ Твой часовой пояс
• 📱 {'Согласие на получение сообщений' if messaging_confirmed else 'Работа без автоматических сообщений'}

**Что дальше?**
1️⃣ Выбор подходящего плана
2️⃣ Настройка твоих целей
3️⃣ Начало работы над собой
4️⃣ Реальное изменение твоей жизни!

Готов начать свой путь к мечте? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Да, начинаем! 🎯", callback_data="start_option_selection")],
            [InlineKeyboardButton("У меня есть вопросы ❓", callback_data="ask_questions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(ready_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _complete_onboarding(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Complete onboarding and move to option selection"""
        user_id = update.effective_user.id
        
        # Get user data to pass to next module
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        # Update user state to option selection
        await self.db_manager.set_user_state(user_id, "option_selection", state_data)
        
        completion_text = """
🎉 **Онбординг завершен!**

Отлично! Теперь давай найдем идеальный план для тебя. Я покажу тебе три варианта подписки и помогу выбрать тот, который лучше всего подходит для твоих целей.

Переходим к выбору плана! 💎
        """
        
        await update.message.reply_text(completion_text, parse_mode='Markdown')
        
        # Import here to avoid circular imports
        from modules.option import OptionModule
        option_module = OptionModule(self.db_manager, self.state_manager)
        await option_module.start_option_selection(update, context)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "continue_onboarding":
            # Advance to next step
            user_id = update.effective_user.id
            logger.info(f"continue_onboarding callback for user {user_id}")
            state_data = await self.db_manager.get_user_state_data(user_id)
            current_step = state_data.get("onboarding_step", 0)
            logger.info(f"User {user_id} current_step: {current_step}, state_data: {state_data}")
            
            # Update to next step
            await self.db_manager.update_user_state_data(user_id, {"onboarding_step": current_step + 1})
            
            # Call next step
            if current_step + 1 < len(self.onboarding_steps):
                await self.onboarding_steps[current_step + 1](update, context)
            else:
                # Onboarding complete
                await self._complete_onboarding(update, context)
        elif query.data == "start_option_selection":
            await self._complete_onboarding(update, context)
        elif query.data == "ask_questions":
            await self._handle_questions(update, context)
        elif query.data == "timezone_ok":
            await self._process_timezone_confirmation(update, context, "да")
        elif query.data == "change_time":
            await self._ask_time_preferences(update, context)
        elif query.data == "messaging_ok":
            await self._process_messaging_confirmation(update, context, "да")
        elif query.data == "messaging_no":
            await self._process_messaging_confirmation(update, context, "нет")
        elif query.data == "continue_without_messaging":
            await self._process_messaging_confirmation(update, context, "продолжить")
        elif query.data == "wrong_city":
            await self._handle_wrong_city(update, context)
        elif query.data == "accept_disclaimer":
            await self._handle_disclaimer_acceptance(update, context)
        elif query.data == "disclaimer_help":
            await self._handle_disclaimer_help(update, context)
        elif query.data == "cancel_onboarding":
            await self._handle_onboarding_cancellation(update, context)
        elif query.data == "back_to_disclaimer":
            await self._show_disclaimer(update, context)
    
    async def _handle_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user questions"""
        questions_text = """
❓ **Часто задаваемые вопросы:**

**Q: Как работает изменение реальности?**
A: Я анализирую твои проблемы и цели, затем даю пошаговые стратегии для их решения через работу с мышлением и личностью.

**Q: Могу ли я изменить план позже?**
A: Да! Ты можешь изменить свой план в любое время.

**Q: Какие типы поддержки ты предоставляешь?**
A: Я даю ежедневные задания, мотивационные сообщения, отчеты о прогрессе и поддержку в сложные моменты.

**Q: Как часто ты будешь отправлять сообщения?**
A: Это зависит от выбранного плана - от ежедневных (Экстремальный) до еженедельных (Обычный).

Готов продолжить? 🚀
        """
        
        keyboard = [[InlineKeyboardButton("Да, продолжаем! 🎯", callback_data="start_option_selection")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(questions_text, parse_mode='Markdown', reply_markup=reply_markup)
