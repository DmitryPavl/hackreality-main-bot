"""
UX Improvements Module
Provides enhanced user experience features and improvements.
"""

import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

class UXManager:
    """Centralized UX management and improvements"""
    
    def __init__(self, db_manager):
        self.db_manager = db_manager
        self.user_preferences = {}
        self.help_topics = {
            "onboarding": {
                "title": "🚀 Начало работы",
                "content": """
**Добро пожаловать в HackReality!**

Этот бот поможет вам достичь ваших целей через психологическую практику и пошаговые стратегии.

**Что вас ждет:**
• Знакомство с ботом и его возможностями
• Выбор подходящего плана работы
• Персонализированная настройка
• Регулярная поддержка и мотивация

**Готовы начать?** Просто следуйте инструкциям бота! 🎯
                """
            },
            "plans": {
                "title": "📋 Планы работы",
                "content": """
**Доступные планы:**

🚀 **Express (Экспресс)**
• 6 сообщений в день
• Результат за 1 неделю
• Интенсивная работа

⚡ **2-недельный**
• 1 сообщение в день
• Стабильный прогресс за 2 недели
• Сбалансированный подход

📝 **Regular (Обычный)**
• В разработке
• Устойчивый результат
• Долгосрочная работа

**Какой план выбрать?**
Выберите тот, который лучше всего подходит вашему ритму жизни и срочности цели.
                """
            },
            "payment": {
                "title": "💳 Оплата",
                "content": """
**Способы оплаты:**

🏦 **T-Bank**
• Перевод на номер: +79853659487
• Укажите цель в комментарии к переводу
• Подтвердите оплату в боте

**После оплаты:**
• Администратор подтвердит получение средств
• Вы получите доступ к выбранному плану
• Начнется персонализированная настройка

**Вопросы по оплате?** Обратитесь к администратору.
                """
            },
            "support": {
                "title": "🆘 Поддержка",
                "content": """
**Нужна помощь?**

📞 **Контакты:**
• Администратор: @dapavl
• Техническая поддержка через бота

**Частые вопросы:**
• Как изменить план? - Обратитесь к администратору
• Проблемы с оплатой? - Проверьте правильность номера
• Технические проблемы? - Перезапустите бота командой /start

**Мы всегда готовы помочь!** 🤝
                """
            }
        }
    
    async def show_help_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show interactive help menu"""
        try:
            keyboard = []
            for topic_id, topic in self.help_topics.items():
                keyboard.append([InlineKeyboardButton(topic["title"], callback_data=f"help_{topic_id}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Назад", callback_data="back_to_main")])
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            help_text = """
🆘 **Центр помощи HackReality**

Выберите интересующую вас тему:

• 🚀 Начало работы
• 📋 Планы работы  
• 💳 Оплата
• 🆘 Поддержка

**Или используйте команды:**
• /start - Начать заново
• /status - Проверить статус
• /help - Показать это меню
            """
            
            await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error showing help menu: {e}")
    
    async def show_help_topic(self, update: Update, context: ContextTypes.DEFAULT_TYPE, topic_id: str):
        """Show specific help topic"""
        try:
            if topic_id not in self.help_topics:
                await update.callback_query.answer("Тема не найдена")
                return
            
            topic = self.help_topics[topic_id]
            
            keyboard = [
                [InlineKeyboardButton("🔙 К списку тем", callback_data="help_menu")],
                [InlineKeyboardButton("🏠 Главное меню", callback_data="back_to_main")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await update.callback_query.edit_message_text(
                f"{topic['title']}\n\n{topic['content']}",
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error showing help topic: {e}")
    
    async def show_progress_indicator(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                    current_step: int, total_steps: int, step_name: str):
        """Show progress indicator for multi-step processes"""
        try:
            progress_percent = (current_step / total_steps) * 100
            progress_bar = self._create_progress_bar(progress_percent)
            
            progress_text = f"""
📊 **Прогресс: {step_name}**

{progress_bar} {progress_percent:.0f}%

**Шаг {current_step} из {total_steps}**

Продолжайте следовать инструкциям! 🎯
            """
            
            await update.message.reply_text(progress_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing progress indicator: {e}")
    
    def _create_progress_bar(self, percent: float, length: int = 10) -> str:
        """Create a visual progress bar"""
        try:
            filled = int((percent / 100) * length)
            empty = length - filled
            return "█" * filled + "░" * empty
        except Exception as e:
            logger.error(f"Error creating progress bar: {e}")
            return "░" * 10
    
    async def show_encouragement_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                       message_type: str = "general"):
        """Show encouraging messages to motivate users"""
        try:
            encouragement_messages = {
                "general": [
                    "🌟 Ты на правильном пути! Продолжай двигаться к своей цели!",
                    "💪 Каждый шаг приближает тебя к мечте! Ты молодец!",
                    "🎯 Твоя решимость впечатляет! Продолжай в том же духе!",
                    "✨ Ты делаешь отличную работу! Верь в себя!",
                    "🚀 Твоя мотивация вдохновляет! Не останавливайся!"
                ],
                "milestone": [
                    "🎉 Поздравляю с достижением! Ты прошел важный этап!",
                    "🏆 Отличная работа! Ты показал настоящую силу воли!",
                    "⭐ Ты превзошел ожидания! Продолжай в том же духе!",
                    "🎊 Впечатляющий результат! Ты на верном пути!",
                    "👏 Браво! Твоя настойчивость приносит плоды!"
                ],
                "challenge": [
                    "💎 Сложности делают нас сильнее! Ты справишься!",
                    "🔥 Испытания - это возможность расти! Вперед!",
                    "⚡ Ты сильнее, чем думаешь! Не сдавайся!",
                    "🌟 Каждое препятствие - это ступенька к успеху!",
                    "💪 Твоя сила воли поможет преодолеть любые трудности!"
                ]
            }
            
            import random
            messages = encouragement_messages.get(message_type, encouragement_messages["general"])
            message = random.choice(messages)
            
            await update.message.reply_text(f"💝 **Поддержка**\n\n{message}", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing encouragement message: {e}")
    
    async def show_tip_of_the_day(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show daily tip for users"""
        try:
            tips = [
                "💡 **Совет дня:** Начинайте день с постановки одной маленькой цели. Достижение даже небольшой цели даст вам энергию для больших свершений!",
                "💡 **Совет дня:** Ведите дневник успехов. Записывайте каждый день, что хорошего произошло. Это поможет сохранить позитивный настрой!",
                "💡 **Совет дня:** Окружите себя людьми, которые верят в ваши мечты. Их поддержка поможет вам двигаться вперед!",
                "💡 **Совет дня:** Разбивайте большие цели на маленькие шаги. Каждый шаг приближает вас к успеху!",
                "💡 **Совет дня:** Не бойтесь ошибок. Они - это уроки, которые делают вас мудрее и сильнее!",
                "💡 **Совет дня:** Визуализируйте свой успех каждый день. Представьте, как вы достигаете своей цели!",
                "💡 **Совет дня:** Благодарите за то, что у вас есть. Благодарность привлекает больше хорошего в вашу жизнь!"
            ]
            
            import random
            tip = random.choice(tips)
            
            await update.message.reply_text(tip, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing tip of the day: {e}")
    
    async def show_motivational_quote(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show motivational quote"""
        try:
            quotes = [
                "🌟 'Единственный способ делать великую работу - это любить то, что ты делаешь.' - Стив Джобс",
                "💪 'Успех - это способность переходить от одной неудачи к другой, не теряя энтузиазма.' - Уинстон Черчилль",
                "🎯 'Будущее принадлежит тем, кто верит в красоту своих мечтаний.' - Элеонора Рузвельт",
                "🚀 'Не бойтесь отказываться от хорошего ради великого.' - Джон Рокфеллер",
                "✨ 'Ваше время ограничено, не тратьте его, живя чужой жизнью.' - Стив Джобс",
                "💎 'Лучшее время посадить дерево было 20 лет назад. Следующее лучшее время - сейчас.' - Китайская пословица",
                "🔥 'Не ждите подходящего момента. Создавайте его.' - Джордж Бернард Шоу"
            ]
            
            import random
            quote = random.choice(quotes)
            
            await update.message.reply_text(f"💭 **Мотивационная цитата**\n\n{quote}", parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing motivational quote: {e}")
    
    async def show_quick_actions_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show quick actions menu for easy navigation"""
        try:
            keyboard = [
                [InlineKeyboardButton("📊 Мой прогресс", callback_data="show_progress")],
                [InlineKeyboardButton("💡 Совет дня", callback_data="tip_of_day")],
                [InlineKeyboardButton("💭 Мотивация", callback_data="motivational_quote")],
                [InlineKeyboardButton("🆘 Помощь", callback_data="help_menu")],
                [InlineKeyboardButton("⚙️ Настройки", callback_data="settings_menu")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            menu_text = """
🎛️ **Быстрые действия**

Выберите, что вас интересует:

• 📊 Посмотреть свой прогресс
• 💡 Получить совет дня
• 💭 Прочитать мотивационную цитату
• 🆘 Получить помощь
• ⚙️ Настройки

**Или просто продолжайте общение с ботом!** 😊
            """
            
            await update.message.reply_text(menu_text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error showing quick actions menu: {e}")
    
    async def personalize_message(self, user_id: int, base_message: str) -> str:
        """Personalize message based on user data"""
        try:
            # Get user profile
            profile = await self.db_manager.get_user_profile(user_id)
            if not profile:
                return base_message
            
            # Get user's name
            first_name = profile.get('first_name', '')
            if first_name:
                personalized_message = base_message.replace('ты', f'{first_name}')
                personalized_message = personalized_message.replace('Ты', f'{first_name}')
                return personalized_message
            
            return base_message
            
        except Exception as e:
            logger.error(f"Error personalizing message: {e}")
            return base_message
    
    async def show_achievement_badge(self, update: Update, context: ContextTypes.DEFAULT_TYPE, 
                                   achievement: str, description: str):
        """Show achievement badge for user accomplishments"""
        try:
            badge_text = f"""
🏆 **ДОСТИЖЕНИЕ РАЗБЛОКИРОВАНО!**

**{achievement}**

{description}

**Поздравляем!** 🎉

Продолжайте в том же духе! Каждое достижение приближает вас к вашей главной цели! 🌟
            """
            
            await update.message.reply_text(badge_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error showing achievement badge: {e}")
    
    async def show_reminder_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show reminder setup for users"""
        try:
            keyboard = [
                [InlineKeyboardButton("⏰ Настроить напоминания", callback_data="setup_reminders")],
                [InlineKeyboardButton("🔕 Отключить напоминания", callback_data="disable_reminders")],
                [InlineKeyboardButton("📅 Изменить время", callback_data="change_reminder_time")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            reminder_text = """
⏰ **Настройка напоминаний**

Хотите получать напоминания о работе с ботом?

**Доступные опции:**
• ⏰ Настроить напоминания
• 🔕 Отключить напоминания  
• 📅 Изменить время напоминаний

**Напоминания помогут вам:**
• Не забывать о работе над целью
• Поддерживать регулярность
• Достигать лучших результатов

Выберите подходящий вариант! 🎯
            """
            
            await update.message.reply_text(reminder_text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error showing reminder setup: {e}")
    
    async def show_feedback_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show feedback request to users"""
        try:
            keyboard = [
                [InlineKeyboardButton("⭐ Отлично", callback_data="feedback_excellent")],
                [InlineKeyboardButton("👍 Хорошо", callback_data="feedback_good")],
                [InlineKeyboardButton("😐 Нормально", callback_data="feedback_ok")],
                [InlineKeyboardButton("👎 Плохо", callback_data="feedback_bad")],
                [InlineKeyboardButton("💬 Написать отзыв", callback_data="feedback_text")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            feedback_text = """
📝 **Оцените работу бота**

Как вам работа с HackReality?

Ваша обратная связь поможет нам улучшить сервис и сделать его еще более полезным для достижения ваших целей!

**Выберите оценку или напишите свой отзыв:**
            """
            
            await update.message.reply_text(feedback_text, parse_mode='Markdown', reply_markup=reply_markup)
            
        except Exception as e:
            logger.error(f"Error showing feedback request: {e}")
