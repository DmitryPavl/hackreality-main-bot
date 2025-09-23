"""
Setting Up Module
Handles the setup process to collect key texts and preferences from the client.
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, List
from modules.admin_notifications import admin_notifications

logger = logging.getLogger(__name__)

class SettingUpModule:
    def __init__(self, db_manager, state_manager, bot_instance=None):
        self.db_manager = db_manager
        self.state_manager = state_manager
        self.bot_instance = bot_instance
        
        # Setup steps for emotional state collection
        self.setup_steps = [
            "welcome",
            "collect_positive_feelings",
            "collect_nervous_feelings", 
            "collect_available_options",
            "transform_negative_feelings",
            "create_focus_statements",
            "complete_setup"
        ]
        
        # Key text categories
        self.key_text_categories = {
            "writing_style": {
                "name": "Writing Style Examples",
                "description": "Share examples of your preferred writing style",
                "examples": ["Blog posts", "Social media posts", "Emails", "Articles"]
            },
            "tone_voice": {
                "name": "Tone & Voice",
                "description": "Describe your preferred tone and voice",
                "examples": ["Professional", "Casual", "Friendly", "Authoritative", "Humorous"]
            },
            "content_types": {
                "name": "Content Types",
                "description": "What types of content do you need?",
                "examples": ["Educational", "Promotional", "Entertainment", "News", "How-to guides"]
            },
            "target_audience": {
                "name": "Target Audience",
                "description": "Who is your target audience?",
                "examples": ["Young professionals", "Students", "Business owners", "General public"]
            }
        }
    
    async def start_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the setup process after payment confirmation"""
        user_id = update.effective_user.id
        
        # Get user's goal and order information
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_goal = state_data.get("user_goal", "")
        final_target_goal = state_data.get("final_target_goal", user_goal)
        order_id = state_data.get("order_id", "")
        selected_plan = state_data.get("selected_plan", "")
        
        # Initialize setup data with emotional state collection
        await self.db_manager.update_user_state_data(user_id, {
            "setup_step": 0,
            "positive_feelings": [],
            "nervous_feelings": [],
            "available_options": [],
            "transformed_negatives": [],
            "focus_statements": [],
            "setup_completed": False,
            "user_goal": user_goal,
            "final_target_goal": final_target_goal,
            "order_id": order_id,
            "selected_plan": selected_plan,
            "current_question_type": "positive_feelings",
            "statements_collected": 0
        })
        
        await self._welcome_to_setup(update, context, final_target_goal, order_id)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages during emotional state setup"""
        user_id = update.effective_user.id
        message_text = update.message.text
        
        # Get current setup state
        state_data = await self.db_manager.get_user_state_data(user_id)
        current_question_type = state_data.get("current_question_type", "positive_feelings")
        
        # Check for flow control commands
        if message_text.lower() in ["готов", "дальше", "готово", "продолжить", "далее"]:
            await self._handle_flow_control(update, context, current_question_type)
            return
        
        if current_question_type == "positive_feelings":
            await self._process_positive_feeling_input(update, context, message_text)
        elif current_question_type == "nervous_feelings":
            await self._process_nervous_feeling_input(update, context, message_text)
        elif current_question_type == "available_options":
            await self._process_available_option_input(update, context, message_text)
        elif current_question_type == "transform_negative":
            await self._process_negative_transformation_input(update, context, message_text)
        elif current_question_type == "task_generation":
            await self._process_task_input(update, context, message_text)
        elif current_question_type == "task_selection":
            await self._process_task_selection_input(update, context, message_text)
        elif current_question_type == "task_response_collection":
            await self._process_task_response(update, context, message_text)
        elif current_question_type == "task_feelings_collection":
            await self._process_task_feelings(update, context, message_text)
        else:
            await self._show_setup_help(update, context)
    
    async def _handle_flow_control(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_question_type: str):
        """Handle flow control commands (готов, дальше, etc.)"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        if current_question_type == "positive_feelings":
            positive_count = len(state_data.get("positive_feelings", []))
            if positive_count >= 3:  # Minimum 3 positive feelings
                await self._move_to_nervous_feelings(update, context)
            else:
                await self._ask_for_minimum_positive(update, context, positive_count)
        
        elif current_question_type == "nervous_feelings":
            nervous_count = len(state_data.get("nervous_feelings", []))
            if nervous_count >= 2:  # Minimum 2 nervous feelings
                await self._move_to_available_options(update, context)
            else:
                await self._ask_for_minimum_nervous(update, context, nervous_count)
        
        elif current_question_type == "available_options":
            options_count = len(state_data.get("available_options", []))
            if options_count >= 2:  # Minimum 2 options
                await self._move_to_negative_transformation(update, context)
            else:
                await self._ask_for_minimum_options(update, context, options_count)
        
        elif current_question_type == "transform_negative":
            await self._create_focus_statements(update, context)
        
        elif current_question_type == "task_generation":
            await self._move_to_next_focus_statement(update, context)
    
    async def _ask_for_minimum_positive(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask for minimum positive feelings"""
        remaining = 3 - current_count
        text = f"""
⚠️ **Нужно еще {remaining} положительных чувств**

У меня есть только {current_count} положительных чувств, а нужно минимум 3 для создания качественных фокус-утверждений.

**Поделись еще {remaining} чувствами, которые ты испытаешь, когда достигнешь цели.**

**Примеры:**
• "Я буду чувствовать..."
• "Я почувствую..."
• "Мне будет..."

Это поможет мне лучше понять твою мотивацию! 😊
        """
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _ask_for_minimum_nervous(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask for minimum nervous feelings"""
        remaining = 2 - current_count
        text = f"""
⚠️ **Нужно еще {remaining} беспокойств**

У меня есть только {current_count} беспокойств, а нужно минимум 2 для работы с твоими страхами.

**Поделись еще {remaining} беспокойствами или страхами, связанными с твоей целью.**

**Примеры:**
• "Я боюсь..."
• "Меня беспокоит..."
• "Я нервничаю из-за..."

Это поможет мне превратить твои страхи в мотивацию! 😰
        """
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _ask_for_minimum_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask for minimum available options"""
        remaining = 2 - current_count
        text = f"""
⚠️ **Нужно еще {remaining} возможностей**

У меня есть только {current_count} возможностей, а нужно минимум 2 для понимания твоих целей.

**Поделись еще {remaining} возможностями, которые у тебя появятся после достижения цели.**

**Примеры:**
• "Я смогу..."
• "У меня будет..."
• "Я буду..."

Это поможет мне понять, что тебя мотивирует! 🚀
        """
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _welcome_to_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE, target_goal: str, order_id: str):
        """Welcome user to setup process"""
        # Truncate goal for display
        display_goal = target_goal[:80] + "..." if len(target_goal) > 80 else target_goal
        
        welcome_text = f"""
🎉 **Отлично! Донат подтвержден!**

**Заказ №{order_id}**
🎯 **Твоя цель:** "{display_goal}"

Теперь я готов помочь тебе достичь этой цели! Для этого мне нужно понять твои эмоции и чувства, связанные с этой целью.

**Что я буду изучать:**
✨ **Какие чувства ты испытаешь, когда достигнешь цели**
✨ **О чем ты беспокоишься или нервничаешь**
✨ **Какие возможности откроются для тебя**
✨ **Как превратить страхи в мотивацию**

Это поможет мне создать персонализированную поддержку, которая будет работать именно с твоими эмоциями и переживаниями! 🚀

Готов начать? Давай начнем с изучения твоих чувств!
        """
        
        keyboard = [
            [InlineKeyboardButton("Начнем! 🚀", callback_data="start_key_texts")],
            [InlineKeyboardButton("Что от меня нужно? ❓", callback_data="setup_explanation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_positive_feelings_collection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start collecting positive feelings when goal is achieved"""
        user_id = update.effective_user.id
        
        # Get user's goal for context
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        
        # Update setup step and question type
        await self.db_manager.update_user_state_data(user_id, {
            "setup_step": 1,
            "current_question_type": "positive_feelings",
            "statements_collected": 0
        })
        
        positive_feelings_text = f"""
😊 **Какие чувства ты испытаешь, когда достигнешь цели?**

**Твоя цель:** "{target_goal}"

Представь, что ты уже достиг этой цели. Какие эмоции и чувства ты испытаешь?

**Примеры того, что можно написать:**
• "Я буду чувствовать гордость за себя"
• "Я почувствую облегчение и радость"
• "Я буду уверен в себе и своих силах"
• "Я почувствую, что все возможно"
• "Я буду счастлив и удовлетворен"

**Поделись со мной до 7 таких утверждений о том, что ты будешь чувствовать!**

Начни с первого чувства... 💭
        """
        
        keyboard = [
            [InlineKeyboardButton("Понял! Начинаю! 😊", callback_data="ready_for_positive")],
            [InlineKeyboardButton("Нужны примеры? 💡", callback_data="positive_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(positive_feelings_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_positive_feeling_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process positive feeling input from user"""
        user_id = update.effective_user.id
        
        # Get current positive feelings
        state_data = await self.db_manager.get_user_state_data(user_id)
        positive_feelings = state_data.get("positive_feelings", [])
        
        # Check for duplicates
        is_duplicate = await self._check_duplicate_statement(message_text, positive_feelings)
        
        if is_duplicate:
            await self._handle_duplicate_statement(update, context, message_text, "positive_feelings")
            return
        
        # Add new feeling
        positive_feelings.append({
            "statement": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown")
        })
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {
            "positive_feelings": positive_feelings,
            "statements_collected": len(positive_feelings)
        })
        
        # Get plan type to determine limits
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan", "")
        
        # Set limits based on plan type
        if selected_plan == "regular":
            max_positive = 7  # Extended for Regular plan
        else:
            max_positive = 5  # Optimized for Express and 2-week plans
        
        # Check if we have enough positive feelings
        if len(positive_feelings) >= max_positive:
            await self._ask_if_finished_positive(update, context, len(positive_feelings))
        else:
            await self._ask_for_more_positive_feelings(update, context, len(positive_feelings), max_positive)
    
    async def _ask_for_more_positive_feelings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int, max_positive: int):
        """Ask for more positive feelings"""
        remaining = max_positive - current_count
        
        if remaining > 1:
            text = f"""
✅ **Отлично! Я записал это чувство.**

У меня уже есть {current_count} положительных чувств. Можешь поделиться еще {remaining} чувствами, которые ты испытаешь, когда достигнешь цели.

**Примеры:**
• "Я буду чувствовать..."
• "Я почувствую..."
• "Мне будет..."

Что еще ты будешь чувствовать? 😊
            """
        else:
            text = f"""
✅ **Превосходно! Нужно еще одно чувство.**

У меня уже есть {current_count} положительных чувств. Поделись еще одним чувством, которое ты испытаешь, когда достигнешь цели.

Это может быть:
• Последнее важное чувство
• Самое сильное переживание
• То, что тебя больше всего мотивирует

Какое твое последнее чувство? 🎯
            """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _check_duplicate_statement(self, new_statement: str, existing_statements: list) -> bool:
        """Check if statement is duplicate or very similar"""
        new_lower = new_statement.lower().strip()
        
        for existing in existing_statements:
            existing_lower = existing["statement"].lower().strip()
            
            # Check for exact match
            if new_lower == existing_lower:
                return True
            
            # Check for very similar statements (80% similarity)
            if self._calculate_similarity(new_lower, existing_lower) > 0.8:
                return True
        
        return False
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Calculate similarity between two texts"""
        # Simple word-based similarity
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 and not words2:
            return 1.0
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    async def _handle_duplicate_statement(self, update: Update, context: ContextTypes.DEFAULT_TYPE, statement: str, question_type: str):
        """Handle duplicate statement detection"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        # Get current count based on question type
        if question_type == "positive_feelings":
            current_count = len(state_data.get("positive_feelings", []))
            max_count = 7
            question_name = "положительных чувств"
        elif question_type == "nervous_feelings":
            current_count = len(state_data.get("nervous_feelings", []))
            max_count = 5
            question_name = "беспокойств"
        elif question_type == "available_options":
            current_count = len(state_data.get("available_options", []))
            max_count = 3
            question_name = "возможностей"
        else:
            current_count = 0
            max_count = 5
            question_name = "утверждений"
        
        text = f"""
⚠️ **Похожее утверждение уже есть!**

Я заметил, что это утверждение очень похоже на то, что ты уже сказал:

**Твое утверждение:** "{statement}"

**Что ты можешь сделать:**
• Подумать о другом, более конкретном чувстве
• Изменить формулировку
• Перейти к следующему вопросу

У меня уже есть {current_count} {question_name}. 

**Хочешь:**
• Попробовать еще раз с другим утверждением
• Перейти к следующему вопросу

Напиши "готов" или "дальше", если хочешь продолжить, или поделись другим утверждением.
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _ask_if_finished_positive(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask if user is finished with positive feelings"""
        text = f"""
✅ **Отлично! У меня есть {current_count} положительных чувств.**

Ты можешь поделиться еще несколькими, если хочешь, или мы можем перейти к следующему вопросу.

**Что ты хочешь сделать?**
• Поделиться еще положительными чувствами
• Перейти к следующему вопросу

Напиши "готов" или "дальше", если хочешь продолжить, или поделись еще одним чувством.
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _move_to_nervous_feelings(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to nervous feelings collection"""
        user_id = update.effective_user.id
        
        # Get user's goal for context
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        positive_count = len(state_data.get("positive_feelings", []))
        
        # Update question type
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "nervous_feelings",
            "statements_collected": 0
        })
        
        nervous_feelings_text = f"""
😰 **О чем ты беспокоишься или нервничаешь?**

**Твоя цель:** "{target_goal}"

Отлично! У меня есть {positive_count} положительных чувств. Теперь давай поговорим о том, что тебя беспокоит или вызывает тревогу в связи с этой целью.

**Примеры того, что можно написать:**
• "Я боюсь, что не справлюсь"
• "Меня беспокоит, что это займет слишком много времени"
• "Я нервничаю из-за того, что подумают другие"
• "Я переживаю, что у меня не хватит сил"
• "Меня тревожит, что я могу потерпеть неудачу"

**Поделись со мной несколькими утверждениями о том, что тебя беспокоит!**

Начни с первого беспокойства... 😰
        """
        
        keyboard = [
            [InlineKeyboardButton("Понял! Начинаю! 😰", callback_data="ready_for_nervous")],
            [InlineKeyboardButton("Нужны примеры? 💡", callback_data="nervous_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(nervous_feelings_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_nervous_feeling_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process nervous feeling input from user"""
        user_id = update.effective_user.id
        
        # Get current nervous feelings
        state_data = await self.db_manager.get_user_state_data(user_id)
        nervous_feelings = state_data.get("nervous_feelings", [])
        
        # Check for duplicates
        is_duplicate = await self._check_duplicate_statement(message_text, nervous_feelings)
        
        if is_duplicate:
            await self._handle_duplicate_statement(update, context, message_text, "nervous_feelings")
            return
        
        # Add new nervous feeling
        nervous_feelings.append({
            "statement": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown")
        })
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {
            "nervous_feelings": nervous_feelings,
            "statements_collected": len(nervous_feelings)
        })
        
        # Check if we have enough nervous feelings (3-5 is good)
        if len(nervous_feelings) >= 3:
            await self._ask_if_finished_nervous(update, context, len(nervous_feelings))
        else:
            await self._ask_for_more_nervous_feelings(update, context, len(nervous_feelings))
    
    async def _ask_for_more_nervous_feelings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask for more nervous feelings"""
        text = f"""
✅ **Понял, я записал это беспокойство.**

У меня уже есть {current_count} беспокойств. Поделись еще тем, что тебя беспокоит или вызывает тревогу.

**Примеры:**
• "Я боюсь..."
• "Меня беспокоит..."
• "Я нервничаю из-за..."

Что еще тебя беспокоит? 😰
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _ask_if_finished_nervous(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask if user is finished with nervous feelings"""
        text = f"""
✅ **Хорошо! У меня есть {current_count} беспокойств.**

Ты можешь поделиться еще несколькими, если хочешь, или мы можем перейти к следующему вопросу.

**Что ты хочешь сделать?**
• Поделиться еще беспокойствами
• Перейти к следующему вопросу

Напиши "готов" или "дальше", если хочешь продолжить, или поделись еще одним беспокойством.
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _move_to_available_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to available options collection"""
        user_id = update.effective_user.id
        
        # Get user's goal for context
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        nervous_count = len(state_data.get("nervous_feelings", []))
        
        # Update question type
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "available_options",
            "statements_collected": 0
        })
        
        available_options_text = f"""
🚀 **Какие возможности откроются для тебя?**

**Твоя цель:** "{target_goal}"

Отлично! У меня есть {nervous_count} беспокойств. Теперь давай подумаем о том, какие возможности и варианты откроются для тебя, когда ты достигнешь этой цели.

**Примеры того, что можно написать:**
• "Я смогу путешествовать по миру"
• "У меня будет больше времени для семьи"
• "Я смогу помогать другим людям"
• "Я буду финансово независимым"
• "Я смогу заниматься тем, что мне нравится"

**Поделись со мной 2-3 утверждениями о том, какие возможности у тебя появятся!**

Начни с первой возможности... 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Понял! Начинаю! 🚀", callback_data="ready_for_options")],
            [InlineKeyboardButton("Нужны примеры? 💡", callback_data="options_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(available_options_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_available_option_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process available option input from user"""
        user_id = update.effective_user.id
        
        # Get current available options
        state_data = await self.db_manager.get_user_state_data(user_id)
        available_options = state_data.get("available_options", [])
        
        # Check for duplicates
        is_duplicate = await self._check_duplicate_statement(message_text, available_options)
        
        if is_duplicate:
            await self._handle_duplicate_statement(update, context, message_text, "available_options")
            return
        
        # Add new option
        available_options.append({
            "statement": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown")
        })
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {
            "available_options": available_options,
            "statements_collected": len(available_options)
        })
        
        # Check if we have enough options (2-3 is good)
        if len(available_options) >= 2:
            await self._ask_if_finished_options(update, context, len(available_options))
        else:
            await self._ask_for_more_options(update, context, len(available_options))
    
    async def _ask_for_more_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask for more available options"""
        text = f"""
✅ **Отлично! Я записал эту возможность.**

У меня уже есть {current_count} возможностей. Поделись еще тем, какие возможности у тебя появятся.

**Примеры:**
• "Я смогу..."
• "У меня будет..."
• "Я буду..."

Какие еще возможности у тебя появятся? 🚀
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _ask_if_finished_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask if user is finished with available options"""
        text = f"""
✅ **Хорошо! У меня есть {current_count} возможностей.**

Ты можешь поделиться еще одной, если хочешь, или мы можем перейти к следующему этапу.

**Что ты хочешь сделать?**
• Поделиться еще одной возможностью
• Перейти к следующему этапу

Напиши "готов" или "дальше", если хочешь продолжить, или поделись еще одной возможностью.
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _move_to_negative_transformation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to negative transformation phase"""
        user_id = update.effective_user.id
        
        # Get user's data
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        positive_count = len(state_data.get("positive_feelings", []))
        nervous_count = len(state_data.get("nervous_feelings", []))
        options_count = len(state_data.get("available_options", []))
        
        # Update question type
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "transform_negative",
            "statements_collected": 0
        })
        
        transformation_text = f"""
🔄 **Превратим страхи в мотивацию!**

**Твоя цель:** "{target_goal}"

Отлично! У меня есть:
• {positive_count} положительных чувств
• {nervous_count} беспокойств  
• {options_count} возможностей

Теперь давай превратим твои беспокойства в позитивные фокус-утверждения! Для каждого беспокойства мы найдем, какое положительное чувство или состояние ты можешь испытать вместо этого.

**Пример:**
Беспокойство: "Я боюсь, что не справлюсь"
Позитивное состояние: "Я буду чувствовать уверенность в своих силах"

Давай начнем с первого беспокойства... 🔄
        """
        
        keyboard = [
            [InlineKeyboardButton("Начинаем трансформацию! 🔄", callback_data="start_transformation")],
            [InlineKeyboardButton("Показать мои беспокойства 📋", callback_data="show_nervous")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(transformation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_negative_transformation_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process negative transformation input from user"""
        user_id = update.effective_user.id
        
        # Get current data
        state_data = await self.db_manager.get_user_state_data(user_id)
        nervous_feelings = state_data.get("nervous_feelings", [])
        transformed_negatives = state_data.get("transformed_negatives", [])
        current_index = state_data.get("current_transformation_index", 0)
        
        # If we have a nervous feeling to transform
        if current_index < len(nervous_feelings):
            current_nervous = nervous_feelings[current_index]
            
            # Add transformation
            transformed_negatives.append({
                "original_nervous": current_nervous["statement"],
                "positive_transformation": message_text,
                "timestamp": context.bot_data.get("current_time", "unknown")
            })
            
            # Update state
            await self.db_manager.update_user_state_data(user_id, {
                "transformed_negatives": transformed_negatives,
                "current_transformation_index": current_index + 1
            })
            
            # Check if we have more to transform
            if current_index + 1 < len(nervous_feelings):
                await self._ask_for_next_transformation(update, context, current_index + 1, nervous_feelings)
            else:
                await self._create_focus_statements(update, context)
        else:
            await self._create_focus_statements(update, context)
    
    async def _ask_for_next_transformation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, index: int, nervous_feelings: list):
        """Ask for next transformation"""
        current_nervous = nervous_feelings[index]
        
        text = f"""
✅ **Отлично! Записал трансформацию.**

Теперь давай поработаем со следующим беспокойством:

**Беспокойство:** "{current_nervous['statement']}"

Какое положительное чувство или состояние ты можешь испытать вместо этого беспокойства?

**Примеры:**
• "Я буду чувствовать..."
• "Я почувствую..."
• "Мне будет..."

Какую позитивную трансформацию ты видишь? 🔄
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _create_focus_statements(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create final focus statements"""
        user_id = update.effective_user.id
        
        # Get all data
        state_data = await self.db_manager.get_user_state_data(user_id)
        positive_feelings = state_data.get("positive_feelings", [])
        available_options = state_data.get("available_options", [])
        transformed_negatives = state_data.get("transformed_negatives", [])
        
        # Create focus statements
        focus_statements = []
        
        # Add all positive feelings directly
        for feeling in positive_feelings:
            focus_statements.append(feeling["statement"])
        
        # Add all available options directly
        for option in available_options:
            focus_statements.append(option["statement"])
        
        # Add transformed negatives (positive transformations)
        for transformation in transformed_negatives:
            focus_statements.append(transformation["positive_transformation"])
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {
            "focus_statements": focus_statements,
            "current_question_type": "complete_setup"
        })
        
        # Show final focus statements
        await self._show_final_focus_statements(update, context, focus_statements)
    
    async def _show_final_focus_statements(self, update: Update, context: ContextTypes.DEFAULT_TYPE, focus_statements: list):
        """Show final focus statements"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        
        statements_text = f"""
🎯 **Твои фокус-утверждения готовы!**

**Твоя цель:** "{target_goal}"

Я создал для тебя {len(focus_statements)} фокус-утверждений, которые помогут тебе достичь цели:

**📋 Твои фокус-утверждения:**
        """
        
        # Add statements (limit to avoid message length issues)
        for i, statement in enumerate(focus_statements[:10], 1):  # Show first 10
            statements_text += f"\n**{i}.** {statement}"
        
        if len(focus_statements) > 10:
            statements_text += f"\n\n... и еще {len(focus_statements) - 10} утверждений"
        
        statements_text += """

**🎉 Отлично!** Теперь у меня есть твои фокус-утверждения, но нам нужно поработать немного глубже, чтобы создать материал для дальнейшей работы.

**Что дальше:**
Я создам персонализированный материал на основе твоих утверждений, который мы будем использовать в течение всего периода работы над твоей целью.

Готов продолжить создание материала? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Создать материал! 🚀", callback_data="create_material")],
            [InlineKeyboardButton("Посмотреть все утверждения 📋", callback_data="view_all_statements")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(statements_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_material_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start material creation phase"""
        user_id = update.effective_user.id
        
        # Get user's data
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        selected_plan = state_data.get("selected_plan", "")
        focus_statements = state_data.get("focus_statements", [])
        
        # Get plan details
        plan_details = {
            "extreme": {
                "name": "Экстремальный план",
                "duration": "10-15 минут каждые 2-3 часа",
                "period": "в течение недели",
                "approach": "интенсивная работа"
            },
            "2week": {
                "name": "2-недельный план", 
                "duration": "15 минут в день",
                "period": "в течение 2 недель",
                "approach": "стабильный прогресс"
            }
        }
        
        plan_info = plan_details.get(selected_plan, {
            "name": "Выбранный план",
            "duration": "регулярно",
            "period": "в течение периода",
            "approach": "персонализированная работа"
        })
        
        material_creation_text = f"""
🔧 **Создание персонализированного материала**

**Твоя цель:** "{target_goal}"
**Твой план:** {plan_info['name']} - {plan_info['approach']}

Отлично! У меня есть {len(focus_statements)} фокус-утверждений. Теперь мне нужно создать специальный материал для нашей работы.

**Что я буду создавать:**
✨ **Персонализированные сообщения** на основе твоих утверждений
✨ **Мотивационные тексты** для каждого этапа работы
✨ **Практические задания** связанные с твоей целью
✨ **Поддерживающие сообщения** в твоем стиле

**Как мы будем работать:**
• {plan_info['duration']}
• {plan_info['period']}
• Материал будет адаптирован под твои потребности
• Каждое сообщение будет связано с твоими фокус-утверждениями

**Это займет несколько минут...**

Создаю твой персонализированный материал... 🔧
        """
        
        keyboard = [
            [InlineKeyboardButton("Создать материал! 🔧", callback_data="start_creation")],
            [InlineKeyboardButton("Объяснить подробнее ❓", callback_data="explain_material")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(material_creation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _explain_material_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Explain material creation process"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan", "")
        
        explanation_text = f"""
📚 **Как создается персонализированный материал**

**Процесс создания:**

**1. Анализ твоих фокус-утверждений**
• Изучаю каждое утверждение
• Выделяю ключевые эмоции и мотивации
• Определяю твой стиль мышления

**2. Создание базового материала**
• Мотивационные сообщения для утра
• Поддерживающие тексты для сложных моментов
• Практические задания для прогресса
• Вдохновляющие напоминания о цели

**3. Адаптация под твой план**
• {selected_plan.upper()} план: интенсивная работа
• Частота сообщений под твой ритм
• Сложность заданий по твоим возможностям

**4. Персонализация**
• Использую твои слова и фразы
• Учитываю твои страхи и превращаю их в мотивацию
• Создаю материал в твоем стиле

**Результат:**
Уникальный набор сообщений и заданий, созданный специально для тебя и твоей цели!

Готов начать создание? 🔧
        """
        
        keyboard = [
            [InlineKeyboardButton("Начать создание! 🔧", callback_data="start_creation")],
            [InlineKeyboardButton("Назад к обзору 🔙", callback_data="back_to_statements")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(explanation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _create_personalized_material(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Create personalized material for the user"""
        user_id = update.effective_user.id
        
        # Get user's data
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        selected_plan = state_data.get("selected_plan", "")
        focus_statements = state_data.get("focus_statements", [])
        positive_feelings = state_data.get("positive_feelings", [])
        nervous_feelings = state_data.get("nervous_feelings", [])
        available_options = state_data.get("available_options", [])
        
        # Show creation progress
        creation_text = f"""
🔧 **Создаю твой персонализированный материал...**

**Анализирую твои данные:**
✅ {len(focus_statements)} фокус-утверждений
✅ {len(positive_feelings)} положительных чувств
✅ {len(nervous_feelings)} беспокойств
✅ {len(available_options)} возможностей

**Создаю материал для:**
🎯 Цель: "{target_goal}"
📋 План: {selected_plan.upper()}

**Процесс:**
1. Анализирую твои утверждения... ⏳
2. Создаю мотивационные сообщения... ⏳
3. Адаптирую под твой план... ⏳
4. Персонализирую материал... ⏳
5. Создаю задачи для каждого утверждения... ⏳

**⏰ Это займет еще около 10 минут.**

Мне нужно поработать с каждым твоим фокус-утверждением, чтобы создать конкретные задачи, которые помогут тебе достичь этого состояния.

Пожалуйста, подожди... ⏰
        """
        
        await update.callback_query.edit_message_text(creation_text, parse_mode='Markdown')
        
        # Simulate initial material creation process
        await asyncio.sleep(2)  # Simulate processing time
        
        # Start task generation phase
        await self._start_task_generation_phase(update, context, focus_statements)
    
    async def _start_task_generation_phase(self, update: Update, context: ContextTypes.DEFAULT_TYPE, focus_statements: list):
        """Start the task generation phase for each focus statement"""
        user_id = update.effective_user.id
        
        # Initialize task generation state
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "task_generation",
            "focus_statements": focus_statements,
            "current_focus_index": 0,
            "generated_tasks": [],
            "task_generation_started": True
        })
        
        # Start with first focus statement
        await self._ask_for_focus_statement_tasks(update, context, 0, focus_statements)
    
    async def _ask_for_focus_statement_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE, focus_index: int, focus_statements: list):
        """Ask user what should happen to feel a specific focus statement"""
        user_id = update.effective_user.id
        
        if focus_index >= len(focus_statements):
            # All focus statements processed, complete material creation
            await self._complete_material_creation(update, context)
            return
        
        # Get plan type to determine task limits
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan", "")
        
        # Set task limits based on plan type
        if selected_plan == "regular":
            max_tasks_per_focus = 3  # Extended for Regular plan
            task_text = "2-3 конкретными задачами"
        else:
            max_tasks_per_focus = 1  # Optimized for Express and 2-week plans
            task_text = "1 конкретной задачей"
        
        current_statement = focus_statements[focus_index]
        progress = focus_index + 1
        total = len(focus_statements)
        
        task_generation_text = f"""
🎯 **Создаем задачи для фокус-утверждения {progress} из {total}**

**Фокус-утверждение:** "{current_statement}"

Теперь мне нужно понять, что должно происходить, чтобы ты почувствовал это состояние.

**Вопрос:** Что должно случиться или что ты должен сделать, чтобы почувствовать: "{current_statement}"?

**Примеры того, что можно написать:**
• "Я должен получить предложение о работе"
• "Мне нужно пройти собеседование успешно"
• "Я должен обновить свое резюме"
• "Мне нужно отправить 5 заявок на работу"
• "Я должен подготовиться к интервью"

**Поделись {task_text} или действием, которое приведет к этому чувству.**

Начни с задачи... 📝
        """
        
        keyboard = [
            [InlineKeyboardButton("Начинаю! 📝", callback_data="start_tasks")],
            [InlineKeyboardButton("Нужны примеры? 💡", callback_data="task_examples")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(task_generation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_task_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process task input for current focus statement"""
        user_id = update.effective_user.id
        
        # Get current state
        state_data = await self.db_manager.get_user_state_data(user_id)
        current_focus_index = state_data.get("current_focus_index", 0)
        focus_statements = state_data.get("focus_statements", [])
        generated_tasks = state_data.get("generated_tasks", [])
        
        if current_focus_index >= len(focus_statements):
            return
        
        current_statement = focus_statements[current_focus_index]
        
        # Get current tasks for this focus statement
        current_focus_tasks = generated_tasks.get(str(current_focus_index), [])
        
        # Add new task
        task_id = len(current_focus_tasks) + 1
        new_task = {
            "task_id": f"{current_focus_index}_{task_id}",
            "focus_statement_id": current_focus_index,
            "focus_statement": current_statement,
            "task_number": task_id,
            "task_text": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown")
        }
        
        current_focus_tasks.append(new_task)
        generated_tasks[str(current_focus_index)] = current_focus_tasks
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {
            "generated_tasks": generated_tasks
        })
        
        # Get plan type to determine task limits
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan", "")
        
        # Set task limits based on plan type
        if selected_plan == "regular":
            max_tasks_per_focus = 3  # Extended for Regular plan
        else:
            max_tasks_per_focus = 1  # Optimized for Express and 2-week plans
        
        # Check if we have enough tasks for this focus statement
        if len(current_focus_tasks) >= max_tasks_per_focus:
            await self._ask_if_finished_focus_tasks(update, context, current_focus_index, focus_statements, current_focus_tasks)
        else:
            await self._ask_for_more_tasks(update, context, current_focus_index, focus_statements, current_focus_tasks, max_tasks_per_focus)
    
    async def _ask_for_more_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE, focus_index: int, focus_statements: list, current_tasks: list, max_tasks_per_focus: int):
        """Ask for more tasks for current focus statement"""
        current_statement = focus_statements[focus_index]
        remaining = max_tasks_per_focus - len(current_tasks)
        
        if remaining > 0:
            text = f"""
✅ **Отлично! Я записал эту задачу.**

**Фокус-утверждение:** "{current_statement}"

У меня уже есть {len(current_tasks)} задач для этого утверждения. Можешь поделиться еще {remaining} задачами.

**Примеры:**
• "Я должен..."
• "Мне нужно..."
• "Я должен сделать..."

Что еще должно произойти, чтобы ты почувствовал это состояние? 📝
            """
        else:
            # This shouldn't happen, but just in case
            text = f"""
✅ **Отлично! Я записал эту задачу.**

**Фокус-утверждение:** "{current_statement}"

У меня уже есть {len(current_tasks)} задач для этого утверждения. Готов перейти к следующему утверждению!
            """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _ask_if_finished_focus_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE, focus_index: int, focus_statements: list, current_tasks: list):
        """Ask if user is finished with current focus statement tasks"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan", "")
        
        current_statement = focus_statements[focus_index]
        progress = focus_index + 1
        total = len(focus_statements)
        
        # For Express and 2-week plans, automatically move to next focus statement
        if selected_plan != "regular":
            text = f"""
✅ **Отлично! У меня есть {len(current_tasks)} задача для этого утверждения.**

**Фокус-утверждение:** "{current_statement}"

**Прогресс:** {progress} из {total} утверждений обработано

Переходим к следующему фокус-утверждению... ⏭️
            """
            await update.message.reply_text(text, parse_mode='Markdown')
            
            # Automatically move to next focus statement
            await self._move_to_next_focus_statement(update, context)
            return
        
        # For Regular plan, ask if user wants to add more tasks
        text = f"""
✅ **Хорошо! У меня есть {len(current_tasks)} задач для этого утверждения.**

**Фокус-утверждение:** "{current_statement}"

Ты можешь поделиться еще одной задачей, если хочешь, или мы можем перейти к следующему фокус-утверждению.

**Прогресс:** {progress} из {total} утверждений обработано

**Что ты хочешь сделать?**
• Поделиться еще одной задачей
• Перейти к следующему утверждению

Напиши "готов" или "дальше", если хочешь продолжить, или поделись еще одной задачей.
        """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _move_to_next_focus_statement(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to next focus statement"""
        user_id = update.effective_user.id
        
        # Get current state
        state_data = await self.db_manager.get_user_state_data(user_id)
        current_focus_index = state_data.get("current_focus_index", 0)
        focus_statements = state_data.get("focus_statements", [])
        
        # Move to next focus statement
        next_index = current_focus_index + 1
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {
            "current_focus_index": next_index
        })
        
        # Ask for tasks for next focus statement
        await self._ask_for_focus_statement_tasks(update, context, next_index, focus_statements)
    
    async def _complete_material_creation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Complete material creation with all tasks"""
        user_id = update.effective_user.id
        
        # Get all data
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        selected_plan = state_data.get("selected_plan", "")
        focus_statements = state_data.get("focus_statements", [])
        positive_feelings = state_data.get("positive_feelings", [])
        nervous_feelings = state_data.get("nervous_feelings", [])
        available_options = state_data.get("available_options", [])
        generated_tasks = state_data.get("generated_tasks", {})
        
        # For Express and 2-week plans, add task selection phase
        if selected_plan in ["extreme", "2week"]:
            await self._start_task_selection_phase(update, context, generated_tasks, selected_plan)
        else:
            # For Regular plan, create material directly
            personalized_material = await self._generate_personalized_content_with_tasks(
                target_goal, selected_plan, focus_statements, 
                positive_feelings, nervous_feelings, available_options, generated_tasks
            )
            
            # Save material to database
            await self._save_personalized_material(user_id, personalized_material)
            
            # Show completion
            await self._show_material_completion(update, context, personalized_material)
    
    async def _start_task_selection_phase(self, update: Update, context: ContextTypes.DEFAULT_TYPE, generated_tasks: dict, selected_plan: str):
        """Start task selection phase for Express and 2-week plans"""
        user_id = update.effective_user.id
        
        # Set task selection limits based on plan
        if selected_plan == "extreme":
            required_tasks = 6
            plan_name = "Express"
        elif selected_plan == "2week":
            required_tasks = 2
            plan_name = "2-недельный"
        else:
            required_tasks = 3
            plan_name = "Regular"
        
        # Flatten all tasks into a single list for selection
        all_tasks = []
        for focus_id, tasks in generated_tasks.items():
            for task in tasks:
                task["focus_statement_id"] = int(focus_id)
                all_tasks.append(task)
        
        # Update state for task selection
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "task_selection",
            "all_tasks": all_tasks,
            "required_tasks": required_tasks,
            "selected_tasks": [],
            "task_selection_started": True
        })
        
        # Show task selection interface
        await self._show_task_selection_interface(update, context, all_tasks, required_tasks, plan_name)
    
    async def _show_task_selection_interface(self, update: Update, context: ContextTypes.DEFAULT_TYPE, all_tasks: list, required_tasks: int, plan_name: str):
        """Show task selection interface"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_tasks = state_data.get("selected_tasks", [])
        
        selection_text = f"""
🎯 **Выбор рабочих задач для {plan_name} плана**

**Твоя цель:** "{state_data.get('final_target_goal', '')}"

У меня есть {len(all_tasks)} задач, которые мы создали на основе твоих фокус-утверждений.

**Теперь выбери {required_tasks} задач, над которыми мы будем работать:**

**Выбранные задачи ({len(selected_tasks)}/{required_tasks}):**
        """
        
        if selected_tasks:
            for i, task in enumerate(selected_tasks, 1):
                selection_text += f"\n**{i}.** {task['task_text']}"
        else:
            selection_text += "\n*Пока не выбрано*"
        
        selection_text += f"""

**Доступные задачи для выбора:**
        """
        
        # Show available tasks (not yet selected)
        available_tasks = [task for task in all_tasks if task not in selected_tasks]
        for i, task in enumerate(available_tasks[:10], 1):  # Show first 10
            focus_statement = task.get('focus_statement', 'Unknown')
            selection_text += f"\n**{i}.** {task['task_text']}"
            selection_text += f"\n   *Фокус: {focus_statement}*"
        
        if len(available_tasks) > 10:
            selection_text += f"\n... и еще {len(available_tasks) - 10} задач"
        
        selection_text += f"""

**Как выбрать:**
• Напиши номер задачи (например: "1", "5", "12")
• Или напиши "готов", если выбрал достаточно
• Или напиши "сброс", чтобы начать заново

**Выбери {required_tasks - len(selected_tasks)} задач...** 📝
        """
        
        await update.message.reply_text(selection_text, parse_mode='Markdown')
    
    async def _process_task_selection_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process task selection input"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        all_tasks = state_data.get("all_tasks", [])
        selected_tasks = state_data.get("selected_tasks", [])
        required_tasks = state_data.get("required_tasks", 0)
        
        # Handle flow control commands
        if message_text.lower() in ["готов", "дальше", "готово"]:
            if len(selected_tasks) >= required_tasks:
                await self._complete_task_selection(update, context)
            else:
                remaining = required_tasks - len(selected_tasks)
                await update.message.reply_text(f"Нужно выбрать еще {remaining} задач. Продолжай выбор... 📝")
            return
        
        if message_text.lower() in ["сброс", "заново", "начать заново"]:
            await self.db_manager.update_user_state_data(user_id, {
                "selected_tasks": []
            })
            await self._show_task_selection_interface(update, context, all_tasks, required_tasks, "твоего")
            return
        
        # Try to parse task number
        try:
            task_number = int(message_text.strip())
            if 1 <= task_number <= len(all_tasks):
                # Get the task (convert to 0-based index)
                task = all_tasks[task_number - 1]
                
                # Check if already selected
                if task in selected_tasks:
                    await update.message.reply_text("Эта задача уже выбрана! Выбери другую. 🔄")
                    return
                
                # Add to selected tasks
                selected_tasks.append(task)
                
                # Update state
                await self.db_manager.update_user_state_data(user_id, {
                    "selected_tasks": selected_tasks
                })
                
                # Show updated selection
                await self._show_task_selection_interface(update, context, all_tasks, required_tasks, "твоего")
                
            else:
                await update.message.reply_text(f"Номер должен быть от 1 до {len(all_tasks)}. Попробуй еще раз. 🔢")
                
        except ValueError:
            await update.message.reply_text("Пожалуйста, введи номер задачи (например: 1, 5, 12) или команду. 📝")
    
    async def _complete_task_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Complete task selection and create final material"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        selected_tasks = state_data.get("selected_tasks", [])
        target_goal = state_data.get("final_target_goal", "")
        selected_plan = state_data.get("selected_plan", "")
        focus_statements = state_data.get("focus_statements", [])
        positive_feelings = state_data.get("positive_feelings", [])
        nervous_feelings = state_data.get("nervous_feelings", [])
        available_options = state_data.get("available_options", [])
        
        # Create final material with selected tasks
        personalized_material = await self._generate_personalized_content_with_selected_tasks(
            target_goal, selected_plan, focus_statements, 
            positive_feelings, nervous_feelings, available_options, selected_tasks
        )
        
        # Save material to database
        await self._save_personalized_material(user_id, personalized_material)
        
        # Show completion
        await self._show_material_completion(update, context, personalized_material)
    
    async def _generate_personalized_content_with_selected_tasks(self, target_goal: str, selected_plan: str, 
                                                               focus_statements: list, positive_feelings: list, 
                                                               nervous_feelings: list, available_options: list, 
                                                               selected_tasks: list) -> dict:
        """Generate personalized content with selected tasks"""
        
        # Extract key phrases from focus statements
        key_phrases = []
        for statement in focus_statements:
            key_phrases.append(statement)
        
        # Create material structure with selected tasks
        material = {
            "target_goal": target_goal,
            "selected_plan": selected_plan,
            "focus_statements": focus_statements,
            "key_phrases": key_phrases,
            "positive_feelings": [f["statement"] for f in positive_feelings],
            "nervous_feelings": [f["statement"] for f in nervous_feelings],
            "available_options": [f["statement"] for f in available_options],
            "selected_tasks": selected_tasks,
            "total_tasks": len(selected_tasks),
            "created_at": context.bot_data.get("current_time", "unknown"),
            "material_type": "personalized_goal_achievement_with_selected_tasks"
        }
        
        return material
    
    async def _generate_personalized_content_with_tasks(self, target_goal: str, selected_plan: str, 
                                                      focus_statements: list, positive_feelings: list, 
                                                      nervous_feelings: list, available_options: list, 
                                                      generated_tasks: dict) -> dict:
        """Generate personalized content with tasks based on user data"""
        
        # Extract key phrases from focus statements
        key_phrases = []
        for statement in focus_statements:
            key_phrases.append(statement)
        
        # Create material structure with tasks
        material = {
            "target_goal": target_goal,
            "selected_plan": selected_plan,
            "focus_statements": focus_statements,
            "key_phrases": key_phrases,
            "positive_feelings": [f["statement"] for f in positive_feelings],
            "nervous_feelings": [f["statement"] for f in nervous_feelings],
            "available_options": [f["statement"] for f in available_options],
            "generated_tasks": generated_tasks,
            "total_tasks": sum(len(tasks) for tasks in generated_tasks.values()),
            "created_at": context.bot_data.get("current_time", "unknown"),
            "material_type": "personalized_goal_achievement_with_tasks"
        }
        
        return material
    
    async def _generate_personalized_content(self, target_goal: str, selected_plan: str, 
                                           focus_statements: list, positive_feelings: list, 
                                           nervous_feelings: list, available_options: list) -> dict:
        """Generate personalized content based on user data"""
        
        # Extract key phrases from focus statements
        key_phrases = []
        for statement in focus_statements:
            key_phrases.append(statement)
        
        # Create material structure
        material = {
            "target_goal": target_goal,
            "selected_plan": selected_plan,
            "focus_statements": focus_statements,
            "key_phrases": key_phrases,
            "positive_feelings": [f["statement"] for f in positive_feelings],
            "nervous_feelings": [f["statement"] for f in nervous_feelings],
            "available_options": [f["statement"] for f in available_options],
            "created_at": context.bot_data.get("current_time", "unknown"),
            "material_type": "personalized_goal_achievement"
        }
        
        return material
    
    async def _save_personalized_material(self, user_id: int, material: dict):
        """Save personalized material to database"""
        try:
            # Save to user state data
            await self.db_manager.update_user_state_data(user_id, {
                "personalized_material": material,
                "material_created": True,
                "material_created_at": material["created_at"]
            })
            
            # Log material creation
            logger.info(f"Created personalized material for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving personalized material: {e}")
    
    async def _show_material_completion(self, update: Update, context: ContextTypes.DEFAULT_TYPE, material: dict):
        """Show material creation completion"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        order_id = state_data.get("order_id", "")
        
        total_tasks = material.get('total_tasks', 0)
        focus_statements_count = len(material.get('focus_statements', []))
        selected_plan = material.get('selected_plan', '')
        
        # Show different completion messages based on plan type
        if selected_plan in ["extreme", "2week"]:
            # For Express and 2-week plans, show selected tasks
            selected_tasks = material.get('selected_tasks', [])
            completion_text = f"""
🎉 **Материал создан успешно!**

**Заказ №{order_id}**
🎯 **Цель:** "{material['target_goal']}"
📋 **План:** {material['selected_plan'].upper()}

**Что создано:**
✅ Персонализированные мотивационные сообщения
✅ Поддерживающие тексты для сложных моментов
✅ Практические задания для прогресса
✅ Вдохновляющие напоминания о цели
✅ Материал адаптирован под твой план
✅ **{total_tasks} выбранных рабочих задач** для достижения цели

**Твои рабочие задачи:**
            """
            
            for i, task in enumerate(selected_tasks, 1):
                completion_text += f"\n**{i}.** {task['task_text']}"
            
            completion_text += """

**Готово к работе!** 🚀

Теперь у меня есть все необходимое для поддержки тебя в достижении цели. Материал создан на основе твоих фокус-утверждений и включает выбранные задачи, над которыми мы будем работать.

**Готов начать работу над твоей целью?** 💪
            """
        else:
            # For Regular plan, show all tasks
            completion_text = f"""
🎉 **Материал создан успешно!**

**Заказ №{order_id}**
🎯 **Цель:** "{material['target_goal']}"
📋 **План:** {material['selected_plan'].upper()}

**Что создано:**
✅ Персонализированные мотивационные сообщения
✅ Поддерживающие тексты для сложных моментов
✅ Практические задания для прогресса
✅ Вдохновляющие напоминания о цели
✅ Материал адаптирован под твой план
✅ **{total_tasks} конкретных задач** для {focus_statements_count} фокус-утверждений

**Готово к работе!** 🚀

Теперь у меня есть все необходимое для поддержки тебя в достижении цели. Материал создан на основе твоих фокус-утверждений и включает конкретные задачи, которые помогут тебе достичь каждого состояния.

**Готов начать работу над твоей целью?** 💪
            """
        
        keyboard = [
            [InlineKeyboardButton("Начать работу! 🚀", callback_data="complete_setup")],
            [InlineKeyboardButton("Посмотреть материал 📋", callback_data="view_material")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(completion_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_created_material(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show the created personalized material"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        material = state_data.get("personalized_material", {})
        
        if not material:
            text = "Материал еще не создан. Пожалуйста, сначала создайте материал."
            await update.callback_query.edit_message_text(text)
            return
        
        material_text = f"""
📋 **Твой персонализированный материал**

**🎯 Цель:** "{material.get('target_goal', 'Не указана')}"
**📋 План:** {material.get('selected_plan', 'Не указан').upper()}
**📅 Создан:** {material.get('created_at', 'Не указано')}

**📝 Фокус-утверждения ({len(material.get('focus_statements', []))}):**
        """
        
        # Show first 5 focus statements
        focus_statements = material.get('focus_statements', [])
        for i, statement in enumerate(focus_statements[:5], 1):
            material_text += f"\n**{i}.** {statement}"
        
        if len(focus_statements) > 5:
            material_text += f"\n\n... и еще {len(focus_statements) - 5} утверждений"
        
        material_text += f"""

**😊 Положительные чувства ({len(material.get('positive_feelings', []))}):**
        """
        
        # Show first 3 positive feelings
        positive_feelings = material.get('positive_feelings', [])
        for i, feeling in enumerate(positive_feelings[:3], 1):
            material_text += f"\n**{i}.** {feeling}"
        
        if len(positive_feelings) > 3:
            material_text += f"\n\n... и еще {len(positive_feelings) - 3} чувств"
        
        material_text += f"""

**🚀 Возможности ({len(material.get('available_options', []))}):**
        """
        
        # Show all available options
        available_options = material.get('available_options', [])
        for i, option in enumerate(available_options, 1):
            material_text += f"\n**{i}.** {option}"
        
        # Show tasks if available
        selected_plan = material.get('selected_plan', '')
        
        if selected_plan in ["extreme", "2week"]:
            # Show selected tasks for Express and 2-week plans
            selected_tasks = material.get('selected_tasks', [])
            if selected_tasks:
                material_text += f"""

**📋 Выбранные рабочие задачи ({len(selected_tasks)}):**
                """
                
                for i, task in enumerate(selected_tasks, 1):
                    focus_statement = task.get('focus_statement', 'Unknown')
                    material_text += f"\n**{i}.** {task['task_text']}"
                    material_text += f"\n   *Фокус: {focus_statement}*"
        else:
            # Show all tasks for Regular plan
            generated_tasks = material.get('generated_tasks', {})
            if generated_tasks:
                material_text += f"""

**📋 Созданные задачи ({material.get('total_tasks', 0)}):**
                """
                
                # Show tasks for first 3 focus statements
                for i, (focus_id, tasks) in enumerate(list(generated_tasks.items())[:3]):
                    if i < len(focus_statements):
                        focus_statement = focus_statements[int(focus_id)]
                        material_text += f"\n\n**Фокус-утверждение {int(focus_id)+1}:** \"{focus_statement}\""
                        for j, task in enumerate(tasks[:2], 1):  # Show first 2 tasks
                            material_text += f"\n• {task['task_text']}"
                        if len(tasks) > 2:
                            material_text += f"\n• ... и еще {len(tasks) - 2} задач"
                
                if len(generated_tasks) > 3:
                    material_text += f"\n\n... и еще {len(generated_tasks) - 3} фокус-утверждений с задачами"
        
        material_text += """

**✅ Материал готов к использованию!**

Этот материал будет использоваться для создания персонализированных сообщений и заданий в течение всего периода работы над твоей целью.
        """
        
        keyboard = [
            [InlineKeyboardButton("Начать работу! 🚀", callback_data="complete_setup")],
            [InlineKeyboardButton("Назад к обзору 🔙", callback_data="back_to_completion")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(material_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_key_text_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process key text input from user"""
        user_id = update.effective_user.id
        
        # Get current key texts
        state_data = await self.db_manager.get_user_state_data(user_id)
        key_texts = state_data.get("key_texts", [])
        
        # Add new text
        key_texts.append({
            "text": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown")
        })
        
        # Update state
        await self.db_manager.update_user_state_data(user_id, {"key_texts": key_texts})
        
        # Check if we have enough texts
        if len(key_texts) >= 3:
            await self._move_to_preferences(update, context)
        else:
            await self._ask_for_more_texts(update, context, len(key_texts))
    
    async def _ask_for_more_texts(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_count: int):
        """Ask for more key texts"""
        remaining = 3 - current_count
        
        if remaining > 1:
            text = f"""
✅ **Отлично! Я сохранил эту информацию.**

У меня уже есть {current_count} пример(ов). Поделись еще {remaining} примерами, чтобы я лучше понял тебя.

Ты можешь поделиться:
• Больше информации о себе
• Своими мыслями о цели
• Описанием своего подхода
• Любой другой информацией, которая поможет мне понять тебя

Что еще хочешь рассказать? 📝
            """
        else:
            text = """
✅ **Превосходно! Нужен еще один пример.**

У меня уже есть 2 примера. Поделись еще одним примером, чтобы завершить сбор информации.

Это может быть:
• Еще одна информация о себе
• Твои мысли о препятствиях
• Описание твоего стиля решения проблем
• Любая другая информация, которая поможет мне понять тебя

Какой твой последний пример? 🎯
            """
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _move_to_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to preferences collection"""
        user_id = update.effective_user.id
        
        # Get user's goal for context
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        
        # Update setup step
        await self.db_manager.update_user_state_data(user_id, {"setup_step": 2})
        
        preferences_text = f"""
🎉 **Информация собрана!**

Отлично! Теперь у меня есть достаточно информации о тебе. Теперь давай настроим твои предпочтения для достижения цели "{target_goal}":

**Я спрошу тебя о:**
• Как часто ты хочешь получать поддержку
• В какое время тебе удобно получать сообщения
• Какой формат помощи тебе больше подходит
• Есть ли особые требования или ограничения

Давай начнем с настройки твоих предпочтений! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("Настроить предпочтения! 🚀", callback_data="start_preferences")],
            [InlineKeyboardButton("Сначала посмотреть мою информацию 📝", callback_data="review_texts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(preferences_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_preferences_collection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start collecting user preferences"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        target_goal = state_data.get("final_target_goal", "")
        selected_plan = state_data.get("selected_plan", "")
        
        preferences_text = f"""
⚙️ **Настройка предпочтений для достижения цели**

Давай настроим, как я буду помогать тебе достичь цели "{target_goal}":

**1. Частота поддержки:**
• Часто (каждые 2-3 часа) - для быстрого прогресса
• Умеренно (2-3 раза в день) - стабильный темп
• По запросу - когда тебе нужна помощь

**2. Формат помощи:**
• Короткие мотивационные сообщения
• Подробные инструкции и советы
• Вопросы для размышления
• Практические задания

**3. Время получения сообщений:**
• Утром (6-10 утра)
• Днем (12-16 дня)
• Вечером (18-22 вечера)
• Гибко (в любое время)

**4. Стиль общения:**
• Строгий и требовательный
• Дружелюбный и поддерживающий
• Профессиональный и деловой
• Вдохновляющий и мотивирующий

Расскажи мне о своих предпочтениях! 🎯
        """
        
        await update.callback_query.edit_message_text(preferences_text, parse_mode='Markdown')
    
    async def _process_preference_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process preference input from user"""
        user_id = update.effective_user.id
        
        # Get current preferences
        state_data = await self.db_manager.get_user_state_data(user_id)
        preferences = state_data.get("preferences", {})
        
        # Simple keyword-based preference extraction
        message_lower = message_text.lower()
        
        # Frequency preference
        if any(word in message_lower for word in ["часто", "каждые", "быстро", "частый"]):
            preferences["frequency"] = "frequent"
        elif any(word in message_lower for word in ["умеренно", "стабильно", "2-3", "два-три"]):
            preferences["frequency"] = "moderate"
        elif any(word in message_lower for word in ["запросу", "нужно", "когда", "по необходимости"]):
            preferences["frequency"] = "on_demand"
        
        # Format preference
        if any(word in message_lower for word in ["короткие", "мотивационные", "краткие"]):
            preferences["format"] = "short_motivational"
        elif any(word in message_lower for word in ["подробные", "инструкции", "советы", "детальные"]):
            preferences["format"] = "detailed_instructions"
        elif any(word in message_lower for word in ["вопросы", "размышления", "рефлексия"]):
            preferences["format"] = "reflection_questions"
        elif any(word in message_lower for word in ["задания", "практические", "упражнения"]):
            preferences["format"] = "practical_tasks"
        
        # Time preference
        if any(word in message_lower for word in ["утром", "утро", "6-10", "раннее"]):
            preferences["time_preference"] = "morning"
        elif any(word in message_lower for word in ["днем", "день", "12-16", "полдень"]):
            preferences["time_preference"] = "afternoon"
        elif any(word in message_lower for word in ["вечером", "вечер", "18-22", "позднее"]):
            preferences["time_preference"] = "evening"
        elif any(word in message_lower for word in ["гибко", "любое", "когда", "время"]):
            preferences["time_preference"] = "flexible"
        
        # Communication style
        if any(word in message_lower for word in ["строгий", "требовательный", "жесткий"]):
            preferences["communication_style"] = "strict"
        elif any(word in message_lower for word in ["дружелюбный", "поддерживающий", "мягкий"]):
            preferences["communication_style"] = "friendly"
        elif any(word in message_lower for word in ["профессиональный", "деловой", "формальный"]):
            preferences["communication_style"] = "professional"
        elif any(word in message_lower for word in ["вдохновляющий", "мотивирующий", "энергичный"]):
            preferences["communication_style"] = "inspiring"
        
        # Update preferences
        await self.db_manager.update_user_state_data(user_id, {"preferences": preferences})
        
        # Check if we have enough preferences
        if len(preferences) >= 3:
            await self._move_to_review(update, context)
        else:
            await self._ask_for_more_preferences(update, context, preferences)
    
    async def _ask_for_more_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE, preferences: Dict[str, Any]):
        """Ask for more preferences"""
        missing = []
        
        if "frequency" not in preferences:
            missing.append("частота поддержки")
        if "format" not in preferences:
            missing.append("формат помощи")
        if "time_preference" not in preferences:
            missing.append("время получения сообщений")
        if "communication_style" not in preferences:
            missing.append("стиль общения")
        
        if missing:
            text = f"""
✅ **Хороший прогресс!**

Мне еще нужно узнать о:
• {', '.join(missing)}

Пожалуйста, расскажи больше о своих предпочтениях! 🎯
            """
        else:
            text = """
✅ **Предпочтения собраны!**

Отлично! У меня есть вся необходимая информация. Позволь показать тебе сводку твоей настройки.
            """
            await self._move_to_review(update, context)
            return
        
        await update.message.reply_text(text, parse_mode='Markdown')
    
    async def _move_to_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Move to setup review"""
        user_id = update.effective_user.id
        
        # Update setup step
        await self.db_manager.update_user_state_data(user_id, {"setup_step": 3})
        
        await self._show_setup_review(update, context)
    
    async def _show_setup_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show setup review"""
        user_id = update.effective_user.id
        
        # Get setup data
        state_data = await self.db_manager.get_user_state_data(user_id)
        key_texts = state_data.get("key_texts", [])
        preferences = state_data.get("preferences", {})
        target_goal = state_data.get("final_target_goal", "")
        order_id = state_data.get("order_id", "")
        
        # Format preferences for display
        frequency_map = {
            "frequent": "Часто (каждые 2-3 часа)",
            "moderate": "Умеренно (2-3 раза в день)",
            "on_demand": "По запросу"
        }
        
        format_map = {
            "short_motivational": "Короткие мотивационные сообщения",
            "detailed_instructions": "Подробные инструкции и советы",
            "reflection_questions": "Вопросы для размышления",
            "practical_tasks": "Практические задания"
        }
        
        time_map = {
            "morning": "Утром (6-10 утра)",
            "afternoon": "Днем (12-16 дня)",
            "evening": "Вечером (18-22 вечера)",
            "flexible": "Гибко (в любое время)"
        }
        
        style_map = {
            "strict": "Строгий и требовательный",
            "friendly": "Дружелюбный и поддерживающий",
            "professional": "Профессиональный и деловой",
            "inspiring": "Вдохновляющий и мотивирующий"
        }
        
        # Format review
        review_text = f"""
📋 **Обзор настройки**

**Заказ №{order_id}**
🎯 **Твоя цель:** "{target_goal}"

**✅ Собрана информация:** {len(key_texts)} примеров
**✅ Частота поддержки:** {frequency_map.get(preferences.get('frequency'), 'Не указано')}
**✅ Формат помощи:** {format_map.get(preferences.get('format'), 'Не указано')}
**✅ Время сообщений:** {time_map.get(preferences.get('time_preference'), 'Не указано')}
**✅ Стиль общения:** {style_map.get(preferences.get('communication_style'), 'Не указано')}

**🎯 Сводка твоей настройки:**
Теперь я понимаю твою цель, твой стиль и предпочтения. Я буду использовать эту информацию для создания персонализированной поддержки, которая поможет тебе достичь цели.

Готов завершить настройку и начать работу над твоей целью? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Завершить настройку", callback_data="complete_setup")],
            [InlineKeyboardButton("🔙 Изменить предпочтения", callback_data="edit_preferences")],
            [InlineKeyboardButton("📝 Посмотреть информацию", callback_data="review_texts")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(review_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _complete_setup(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Complete setup and start goal achievement process"""
        user_id = update.effective_user.id
        
        # Get setup data
        state_data = await self.db_manager.get_user_state_data(user_id)
        key_texts = [text["text"] for text in state_data.get("key_texts", [])]
        preferences = state_data.get("preferences", {})
        target_goal = state_data.get("final_target_goal", "")
        order_id = state_data.get("order_id", "")
        selected_plan = state_data.get("selected_plan", "")
        
        # Save to user settings
        await self.db_manager.update_user_settings(user_id, key_texts, preferences)
        
        # Update subscription status to active
        await self.db_manager.update_subscription_status(order_id, "active")
        
        # Send admin notification
        await admin_notifications.notify_setup_complete(user_id, order_id, target_goal, selected_plan)
        
        # Update state to active subscription
        await self.db_manager.set_user_state(user_id, "active_subscription", {
            "order_id": order_id,
            "target_goal": target_goal,
            "selected_plan": selected_plan,
            "setup_completed": True
        })
        
        # Show completion announcement and start timing confirmation
        await self._show_setup_completion_announcement(update, context, order_id, target_goal, selected_plan)
    
    async def _show_setup_completion_announcement(self, update: Update, context: ContextTypes.DEFAULT_TYPE, order_id: str, target_goal: str, selected_plan: str):
        """Show setup completion announcement and start timing confirmation"""
        user_id = update.effective_user.id
        
        # Get user's timezone and name
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_timezone = state_data.get("timezone", "UTC")
        user_name = state_data.get("first_name", "Друг")
        
        # Set timing schedule based on plan
        if selected_plan == "extreme":
            messages_per_day = 6
            time_interval = "каждые 2-3 часа"
            plan_name = "Express"
        elif selected_plan == "2week":
            messages_per_day = 1
            time_interval = "один раз в день"
            plan_name = "2-недельный"
        else:
            messages_per_day = 1
            time_interval = "один раз в день"
            plan_name = "Regular"
        
        announcement_text = f"""
🎉 **Поздравляю, {user_name}!**

**Мы завершили самую сложную часть!** 

Все настройки завершены, материал создан, и теперь мы готовы начать работу над твоей целью.

**Заказ №{order_id}**
🎯 **Твоя цель:** "{target_goal}"
📋 **План:** {plan_name}

**🚨 ВАЖНО: Для достижения цели нужна регулярность!**

Чтобы получить результат, тебе нужно поддерживать регулярность в работе. Я буду отправлять тебе сообщения {time_interval} в удобное для тебя время.

**📅 Расписание сообщений:**
• **{messages_per_day} сообщений в день**
• **Время:** В твоих комфортных часах (твоя временная зона: {user_timezone})
• **Регулярность:** Критически важна для результата!

**🎯 Сейчас мы попробуем первую задачу!**

Давай сначала подтвердим время, когда тебе удобно получать сообщения, а затем начнем с первой задачи, чтобы ты понял, как мы будем работать.

**Готов подтвердить время и начать первую задачу?** ⏰
        """
        
        keyboard = [
            [InlineKeyboardButton("Подтвердить время ⏰", callback_data="confirm_timing")],
            [InlineKeyboardButton("Изменить время 🕐", callback_data="change_timing")],
            [InlineKeyboardButton("Начать первую задачу! 🎯", callback_data="start_first_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(announcement_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _confirm_timing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm current timing schedule"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        selected_plan = state_data.get("selected_plan", "")
        user_timezone = state_data.get("timezone", "UTC")
        user_name = state_data.get("first_name", "Друг")
        
        # Set timing schedule based on plan
        if selected_plan == "extreme":
            messages_per_day = 6
            time_interval = "каждые 2-3 часа"
            plan_name = "Express"
        elif selected_plan == "2week":
            messages_per_day = 1
            time_interval = "один раз в день"
            plan_name = "2-недельный"
        else:
            messages_per_day = 1
            time_interval = "один раз в день"
            plan_name = "Regular"
        
        confirmation_text = f"""
✅ **Время подтверждено!**

**{user_name}, твое расписание:**
• **План:** {plan_name}
• **Сообщений в день:** {messages_per_day}
• **Интервал:** {time_interval}
• **Временная зона:** {user_timezone}
• **Время:** В твоих комфортных часах

**🎯 Теперь начнем с первой задачи!**

Я покажу тебе, как мы будем работать, и ты сможешь попробовать первую задачу.

**Готов начать первую задачу?** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Начать первую задачу! 🎯", callback_data="start_first_task")],
            [InlineKeyboardButton("Изменить время 🕐", callback_data="change_timing")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(confirmation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _change_timing(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow user to change timing schedule"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        selected_plan = state_data.get("selected_plan", "")
        user_timezone = state_data.get("timezone", "UTC")
        user_name = state_data.get("first_name", "Друг")
        
        # Set timing schedule based on plan
        if selected_plan == "extreme":
            messages_per_day = 6
            time_interval = "каждые 2-3 часа"
            plan_name = "Express"
        elif selected_plan == "2week":
            messages_per_day = 1
            time_interval = "один раз в день"
            plan_name = "2-недельный"
        else:
            messages_per_day = 1
            time_interval = "один раз в день"
            plan_name = "Regular"
        
        change_timing_text = f"""
🕐 **Настройка времени**

**{user_name}, текущее расписание:**
• **План:** {plan_name}
• **Сообщений в день:** {messages_per_day}
• **Интервал:** {time_interval}
• **Временная зона:** {user_timezone}

**Что ты хочешь изменить?**

**Варианты:**
• Изменить временную зону
• Изменить время начала работы
• Изменить интервал сообщений
• Оставить как есть

**Напиши, что хочешь изменить, или выбери вариант ниже:**
        """
        
        keyboard = [
            [InlineKeyboardButton("Изменить временную зону 🌍", callback_data="change_timezone")],
            [InlineKeyboardButton("Изменить время начала ⏰", callback_data="change_start_time")],
            [InlineKeyboardButton("Оставить как есть ✅", callback_data="confirm_timing")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(change_timing_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_first_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the first task to demonstrate the working process"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        selected_plan = state_data.get("selected_plan", "")
        target_goal = state_data.get("final_target_goal", "")
        user_name = state_data.get("first_name", "Друг")
        order_id = state_data.get("order_id", "")
        
        # Get first task from material
        material = state_data.get("personalized_material", {})
        
        if selected_plan in ["extreme", "2week"]:
            selected_tasks = material.get("selected_tasks", [])
            if selected_tasks:
                first_task = selected_tasks[0]
                task_text = first_task.get("task_text", "Первая задача")
                focus_statement = first_task.get("focus_statement", "Твое фокус-утверждение")
            else:
                task_text = "Начать работу над целью"
                focus_statement = "Достижение цели"
        else:
            # For Regular plan, use first focus statement
            focus_statements = material.get("focus_statements", [])
            if focus_statements:
                focus_statement = focus_statements[0]
                task_text = f"Начать работу над: {focus_statement}"
            else:
                task_text = "Начать работу над целью"
                focus_statement = "Достижение цели"
        
        # Save active task to database
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "task_work",
            "active_task": {
                "task_text": task_text,
                "focus_statement": focus_statement,
                "task_id": first_task.get("task_id", "first_task") if selected_plan in ["extreme", "2week"] else "first_task",
                "order_id": order_id,
                "started_at": context.bot_data.get("current_time", "unknown")
            }
        })
        
        first_task_text = f"""
🎯 **Первая задача - пробный запуск!**

**{user_name}, давай попробуем, как мы будем работать!**

**Твоя цель:** "{target_goal}"
**План:** {selected_plan.upper()}

**🎯 Задача:**
**{task_text}**

**Фокус-утверждение:** "{focus_statement}"

**Эта задача может быть сложной или не очень, но нам прямо сейчас надо сделать небольшое движение в этом направлении.**

**Что можно сделать прямо сейчас?** 

Даже если это просто назначить какую-то встречу или выбрать страну, в которую вы хотите полететь, если эта задача много путешествовать, например. 

То есть любое маленькое или не очень маленькое движение в этом направлении! 😊

**Попробуй сделать что-то прямо сейчас и напиши, что получилось!**

**Готов попробовать?** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Сделал движение! ✅", callback_data="task_movement_done")],
            [InlineKeyboardButton("Нужна помощь? ❓", callback_data="task_help")],
            [InlineKeyboardButton("Начать работу над целью! 🎯", callback_data="start_goal_work")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(first_task_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_task_movement_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task movement completion and ask for user response"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_name = state_data.get("first_name", "Друг")
        
        # Update state to collect user response
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "task_response_collection"
        })
        
        response_text = f"""
✅ **Отлично, {user_name}!**

Ты сделал движение в направлении задачи! 

**Теперь расскажи мне:**

**1. Что именно ты сделал?**
Опиши, какое движение ты сделал в направлении задачи.

**2. Как ты себя чувствуешь после этого?**
Поделись своими эмоциями и ощущениями.

**Примеры того, что можно написать:**
• "Я обновил резюме и отправил 3 заявки. Чувствую себя более уверенно и мотивированно!"
• "Я выбрал 3 страны для путешествия и начал изучать визы. Чувствую воодушевление!"
• "Я назначил встречу с менеджером на завтра. Чувствую небольшое волнение, но и радость!"

**Поделись своим опытом!** 📝
        """
        
        await update.callback_query.edit_message_text(response_text, parse_mode='Markdown')
    
    async def _process_task_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process user's task response and feelings"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        active_task = state_data.get("active_task", {})
        user_name = state_data.get("first_name", "Друг")
        selected_plan = state_data.get("selected_plan", "")
        
        # Store user response and feelings
        task_response = {
            "user_response": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown"),
            "task_id": active_task.get("task_id", "first_task"),
            "order_id": active_task.get("order_id", "")
        }
        
        # Update state with response
        await self.db_manager.update_user_state_data(user_id, {
            "task_response": task_response,
            "current_question_type": "task_feelings_collection"
        })
        
        # Ask about feelings
        feelings_text = f"""
📝 **Спасибо за ответ, {user_name}!**

Я записал твой ответ о том, что ты сделал.

**Теперь расскажи о своих чувствах:**

**Как ты себя чувствуешь после того, что сделал?**

**Примеры чувств:**
• "Чувствую гордость за себя"
• "Чувствую мотивацию продолжать"
• "Чувствую небольшое волнение, но это нормально"
• "Чувствую уверенность в своих силах"
• "Чувствую воодушевление и радость"

**Поделись своими эмоциями!** 😊
        """
        
        await update.message.reply_text(feelings_text, parse_mode='Markdown')
    
    async def _process_task_feelings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process user's feelings and provide reinforcement"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        task_response = state_data.get("task_response", {})
        active_task = state_data.get("active_task", {})
        user_name = state_data.get("first_name", "Друг")
        selected_plan = state_data.get("selected_plan", "")
        
        # Store feelings
        task_feelings = {
            "feelings": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown")
        }
        
        # Complete task data
        complete_task_data = {
            "task_response": task_response,
            "task_feelings": task_feelings,
            "active_task": active_task,
            "completed_at": context.bot_data.get("current_time", "unknown")
        }
        
        # Save complete task data
        await self.db_manager.update_user_state_data(user_id, {
            "complete_task_data": complete_task_data,
            "current_question_type": "task_completed"
        })
        
        # Provide reinforcement and remind of next iteration
        reinforcement_text = f"""
🎉 **Превосходно, {user_name}!**

Ты отлично справился с первой задачей! 

**Что ты сделал:**
{task_response.get('user_response', 'Движение в направлении цели')}

**Как ты себя чувствуешь:**
{message_text}

**🌟 Ты молодец!** Каждое движение в направлении цели - это шаг к успеху!

**Что дальше:**
Я буду отправлять тебе задачи согласно твоему расписанию ({selected_plan.upper()} план), и ты будешь делать такие же движения к своей цели.

**Регулярность - ключ к достижению цели!** 💪

**Готов начать регулярную работу над целью?** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Начать работу над целью! 🎯", callback_data="start_goal_work")],
            [InlineKeyboardButton("Посмотреть мой план 📋", callback_data="view_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(reinforcement_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _change_timezone(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow user to change timezone"""
        change_timezone_text = """
🌍 **Изменение временной зоны**

Напиши свою временную зону в одном из форматов:
• "UTC+3" (например, для Москвы)
• "Europe/Moscow"
• "Asia/Tokyo"
• "America/New_York"

Или напиши "отмена", чтобы вернуться назад.
        """
        
        keyboard = [
            [InlineKeyboardButton("Отмена ❌", callback_data="change_timing")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(change_timezone_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _change_start_time(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow user to change start time"""
        change_start_time_text = """
⏰ **Изменение времени начала**

Напиши время, когда тебе удобно начинать получать сообщения:
• "9:00" (9 утра)
• "10:30" (10:30 утра)
• "14:00" (2 дня)

Или напиши "отмена", чтобы вернуться назад.
        """
        
        keyboard = [
            [InlineKeyboardButton("Отмена ❌", callback_data="change_timing")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(change_start_time_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_task_completed(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task completion"""
        task_completed_text = """
✅ **Отлично! Задача выполнена!**

Ты понял, как мы будем работать! Теперь ты готов к регулярной работе над своей целью.

**Что дальше:**
Я буду отправлять тебе задачи согласно твоему расписанию, и ты будешь их выполнять.

**Готов начать регулярную работу над целью?** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Начать работу над целью! 🎯", callback_data="start_goal_work")],
            [InlineKeyboardButton("Посмотреть мой план 📋", callback_data="view_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(task_completed_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_task_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help for task completion"""
        task_help_text = """
❓ **Помощь с задачей**

**Как выполнить задачу:**
1. Прочитай задачу внимательно
2. Подумай, что нужно сделать
3. Выполни действие
4. Напиши, что получилось

**Примеры ответов:**
• "Я обновил резюме и отправил 3 заявки"
• "Я подготовился к собеседованию"
• "Я изучил информацию о компании"

**Если не получается:**
• Напиши, что именно сложно
• Попроси подсказку
• Попробуй другой подход

**Готов попробовать?** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Попробовать снова! 🎯", callback_data="start_first_task")],
            [InlineKeyboardButton("Начать работу над целью! 🚀", callback_data="start_goal_work")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(task_help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_goal_work(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start regular goal work"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        target_goal = state_data.get("final_target_goal", "")
        selected_plan = state_data.get("selected_plan", "")
        user_name = state_data.get("first_name", "Друг")
        
        start_work_text = f"""
🚀 **Начинаем работу над целью!**

**{user_name}, поздравляю!**

Ты завершил настройку и готов к достижению своей цели!

**Твоя цель:** "{target_goal}"
**План:** {selected_plan.upper()}

**Что происходит дальше:**
Я буду отправлять тебе задачи согласно твоему расписанию. Ты будешь их выполнять и двигаться к своей цели.

**Регулярность - ключ к успеху!** 💪

**Готов начать путь к своей цели?** 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("Начать путь к цели! 🎯", callback_data="start_goal_work")],
            [InlineKeyboardButton("Посмотреть мой план 📋", callback_data="view_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(start_work_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    
    async def _show_setup_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show setup help"""
        help_text = """
❓ **Setup Help**

I'm here to help you complete your setup! Here's what I need:

**For Key Texts:**
• Share examples of your writing style
• Provide links to content you like
• Describe your brand voice

**For Preferences:**
• Tell me your content length preference
• Share topics you're interested in
• Let me know your posting schedule

Use the buttons below or type your responses directly! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Share Key Texts", callback_data="start_key_texts")],
            [InlineKeyboardButton("⚙️ Set Preferences", callback_data="start_preferences")],
            [InlineKeyboardButton("📋 Review Setup", callback_data="review_setup")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "start_key_texts":
            await self._start_positive_feelings_collection(update, context)
        elif query.data == "ready_for_positive":
            await self._start_positive_feelings_collection(update, context)
        elif query.data == "ready_for_nervous":
            await self._move_to_nervous_feelings(update, context)
        elif query.data == "ready_for_options":
            await self._move_to_available_options(update, context)
        elif query.data == "start_transformation":
            await self._start_transformation_process(update, context)
        elif query.data == "complete_setup":
            await self._complete_setup(update, context)
        elif query.data == "setup_explanation":
            await self._show_setup_explanation(update, context)
        elif query.data == "positive_examples":
            await self._show_positive_examples(update, context)
        elif query.data == "nervous_examples":
            await self._show_nervous_examples(update, context)
        elif query.data == "options_examples":
            await self._show_options_examples(update, context)
        elif query.data == "show_nervous":
            await self._show_nervous_review(update, context)
        elif query.data == "view_all_statements":
            await self._show_all_focus_statements(update, context)
        elif query.data == "create_material":
            await self._start_material_creation(update, context)
        elif query.data == "explain_material":
            await self._explain_material_creation(update, context)
        elif query.data == "start_creation":
            await self._create_personalized_material(update, context)
        elif query.data == "view_material":
            await self._show_created_material(update, context)
        elif query.data == "back_to_statements":
            await self._show_final_focus_statements(update, context, state_data.get("focus_statements", []))
        elif query.data == "start_tasks":
            await self._ask_for_focus_statement_tasks(update, context, state_data.get("current_focus_index", 0), state_data.get("focus_statements", []))
        elif query.data == "task_examples":
            await self._show_task_examples(update, context)
        elif query.data == "confirm_timing":
            await self._confirm_timing(update, context)
        elif query.data == "change_timing":
            await self._change_timing(update, context)
        elif query.data == "start_first_task":
            await self._start_first_task(update, context)
        elif query.data == "change_timezone":
            await self._change_timezone(update, context)
        elif query.data == "change_start_time":
            await self._change_start_time(update, context)
        elif query.data == "task_completed":
            await self._handle_task_completed(update, context)
        elif query.data == "task_help":
            await self._show_task_help(update, context)
        elif query.data == "start_goal_work":
            await self._start_goal_work(update, context)
        elif query.data == "task_movement_done":
            await self._handle_task_movement_done(update, context)
    
    async def _show_task_examples(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show examples of tasks for focus statements"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        current_focus_index = state_data.get("current_focus_index", 0)
        focus_statements = state_data.get("focus_statements", [])
        
        if current_focus_index < len(focus_statements):
            current_statement = focus_statements[current_focus_index]
        else:
            current_statement = "твое фокус-утверждение"
        
        examples_text = f"""
💡 **Примеры задач для фокус-утверждения**

**Фокус-утверждение:** "{current_statement}"

**Примеры того, что можно написать:**

**Для чувства гордости:**
• "Я должен успешно завершить проект"
• "Мне нужно получить положительную обратную связь"
• "Я должен преодолеть сложную задачу"

**Для чувства уверенности:**
• "Я должен подготовиться к презентации"
• "Мне нужно изучить новую тему"
• "Я должен попрактиковаться в навыке"

**Для чувства облегчения:**
• "Я должен завершить важную задачу"
• "Мне нужно решить проблему"
• "Я должен сдать экзамен"

**Для возможности путешествовать:**
• "Я должен накопить деньги на поездку"
• "Мне нужно получить отпуск"
• "Я должен спланировать маршрут"

**Главное:** Задачи должны быть конкретными и выполнимыми!

Готов поделиться своими задачами? 📝
        """
        
        keyboard = [
            [InlineKeyboardButton("Готов! Начинаю! 📝", callback_data="start_tasks")],
            [InlineKeyboardButton("Назад к задаче 🔙", callback_data="back_to_task")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(examples_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_setup_explanation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed setup explanation"""
        explanation_text = """
📚 **Setup Process Explained**

**Step 1: Key Texts Collection**
I'll ask you to share examples of content that represents your style. This helps me understand:
• Your writing tone and voice
• Your preferred content structure
• Your communication style
• Your brand personality

**Step 2: Preferences Setup**
I'll collect information about:
• Content length preferences
• Topics you're interested in
• When you prefer to receive content
• Any specific requirements

**Step 3: Review & Confirm**
You'll review everything before we proceed to payment.

This process ensures your content is perfectly tailored to your needs! 🎯
        """
        
        keyboard = [[InlineKeyboardButton("Got it! Let's start! 🚀", callback_data="start_key_texts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(explanation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_text_examples(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show examples of key texts"""
        examples_text = """
💡 **Key Text Examples**

Here are some examples of what you can share:

**Blog Post Example:**
"5 Tips for Better Time Management in 2024..."

**Social Media Post:**
"Just finished an amazing project! Here's what I learned..."

**Email Example:**
"Hi team, I wanted to share some exciting updates..."

**Brand Voice Description:**
"We're professional yet approachable, always focusing on practical solutions..."

**Content You Admire:**
"Check out this article that perfectly captures our style: [link]"

Share any of these types of examples! 📝
        """
        
        keyboard = [[InlineKeyboardButton("Ready to share! 📝", callback_data="ready_for_texts")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(examples_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_text_review(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show review of collected texts"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        key_texts = state_data.get("key_texts", [])
        
        if not key_texts:
            text = "No key texts collected yet. Please share some examples first!"
        else:
            text = f"**📝 Key Texts Collected ({len(key_texts)}):**\n\n"
            for i, text_data in enumerate(key_texts, 1):
                text += f"**{i}.** {text_data['text'][:100]}{'...' if len(text_data['text']) > 100 else ''}\n\n"
        
        keyboard = [
            [InlineKeyboardButton("✅ Looks good!", callback_data="complete_setup")],
            [InlineKeyboardButton("🔙 Back to Setup", callback_data="back_to_setup")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _edit_preferences(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Allow user to edit preferences"""
        user_id = update.effective_user.id
        
        # Reset preferences
        await self.db_manager.update_user_state_data(user_id, {"preferences": {}})
        
        edit_text = """
✏️ **Edit Preferences**

Let's update your preferences. Please tell me:

**1. Content Length:** Short, Medium, or Long?
**2. Topics:** What topics interest you?
**3. Posting Schedule:** When do you prefer to receive content?

Please share your updated preferences! 🎯
        """
        
        await update.callback_query.edit_message_text(edit_text, parse_mode='Markdown')
