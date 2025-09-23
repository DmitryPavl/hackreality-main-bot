"""
Iteration Module
Handles regular task delivery, goal achievement, and user progress tracking.
"""

import logging
import asyncio
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

class IterationModule:
    def __init__(self, db_manager, state_manager, bot_instance=None):
        self.db_manager = db_manager
        self.state_manager = state_manager
        self.bot_instance = bot_instance
        
        # Plan-specific delivery schedules
        self.plan_schedules = {
            "extreme": {
                "name": "Express",
                "messages_per_day": 6,
                "interval_hours": 3,
                "description": "Интенсивная работа каждые 2-3 часа"
            },
            "2week": {
                "name": "2-недельный",
                "messages_per_day": 1,
                "interval_hours": 24,
                "description": "Стабильный прогресс раз в день"
            },
            "regular": {
                "name": "Regular",
                "messages_per_day": 1,
                "interval_hours": 24,
                "description": "Устойчивый результат раз в день"
            }
        }
        
        # Task delivery templates
        self.task_templates = {
            "motivation": [
                "💪 **Время двигаться к цели!**",
                "🚀 **Пора действовать!**",
                "⚡ **Энергия для достижения цели!**",
                "🎯 **Фокус на результате!**"
            ],
            "reminder": [
                "⏰ **Напоминание о твоей цели**",
                "🔔 **Время для движения вперед**",
                "📢 **Не забывай о своей мечте**",
                "💡 **Момент для действий**"
            ],
            "support": [
                "🤗 **Поддержка на пути к цели**",
                "💝 **Верю в твой успех**",
                "🌟 **Ты на правильном пути**",
                "💪 **Продолжай движение**"
            ]
        }
        
        # Periodic reminder texts (without examples)
        self.periodic_reminders = [
            "Эта задача может быть сложной или не очень, но нам прямо сейчас надо сделать небольшое движение в этом направлении, что можно сделать прямо сейчас?",
            "Сейчас важно сделать хотя бы маленький шаг в направлении этой задачи. Что ты можешь сделать прямо сейчас?",
            "Давай сделаем небольшое движение к твоей цели. Что можно предпринять в данный момент?",
            "Пора действовать! Что ты можешь сделать прямо сейчас для продвижения к цели?",
            "Каждый шаг важен. Что ты можешь сделать в этом направлении прямо сейчас?",
            "Время для действий! Что можно предпринять для движения к цели?",
            "Даже маленький шаг имеет значение. Что ты можешь сделать сейчас?",
            "Пора двигаться вперед! Что можно сделать в направлении этой задачи?"
        ]
        
        # Check-in questions for periodic evaluations
        self.checkin_questions = {
            "feelings": [
                "Как ты себя чувствуешь в целом?",
                "Какие эмоции ты испытываешь сейчас?",
                "Как изменилось твое настроение?",
                "Что ты чувствуешь по поводу своей цели?"
            ],
            "progress": [
                "Как продвигается работа над твоей целью?",
                "Какие изменения ты замечаешь?",
                "Что изменилось в твоей ситуации?",
                "Как развивается твоя цель?"
            ],
            "rational_steps": [
                "Какие рациональные шаги ты предпринял для достижения цели?",
                "Что конкретно ты сделал для продвижения к цели?",
                "Какие практические действия ты выполнил?",
                "Какие шаги ты сделал в направлении цели?"
            ]
        }
        
        # Final evaluation questions
        self.final_evaluation_questions = {
            "feelings": [
                "Какие чувства у тебя сейчас по поводу достижения цели?",
                "Как ты себя чувствуешь после завершения плана?",
                "Какие эмоции ты испытываешь?",
                "Что ты чувствуешь по поводу проделанной работы?"
            ],
            "results": [
                "Какие результаты ты достиг?",
                "Что конкретно ты получил?",
                "Какие изменения произошли?",
                "Что ты смог достичь?"
            ],
            "overall": [
                "Как ты оцениваешь весь процесс?",
                "Что было самым важным?",
                "Что ты понял о себе?",
                "Как изменилась твоя жизнь?"
            ]
        }
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages from active users during goal achievement"""
        user_id = update.effective_user.id
        message_text = update.message.text.lower()
        
        # Get user's current state
        state_data = await self.db_manager.get_user_state_data(user_id)
        current_question_type = state_data.get("current_question_type", "")
        
        # Handle different interaction types
        if current_question_type == "task_response_collection":
            await self._handle_task_response(update, context, message_text)
        elif current_question_type == "task_feelings_collection":
            await self._handle_task_feelings(update, context, message_text)
        elif current_question_type == "checkin_response":
            await self._handle_checkin_response(update, context, message_text)
        elif current_question_type == "final_evaluation_response":
            await self._handle_final_evaluation_response(update, context, message_text)
        elif any(word in message_text for word in ["задача", "task", "сделал", "выполнил"]):
            await self._handle_task_completion(update, context, message_text)
        elif any(word in message_text for word in ["помощь", "help", "поддержка", "support"]):
            await self._show_task_help(update, context)
        elif any(word in message_text for word in ["прогресс", "progress", "статус", "status"]):
            await self._show_progress_status(update, context)
        elif any(word in message_text for word in ["расписание", "schedule", "время", "time"]):
            await self._show_delivery_schedule(update, context)
        else:
            await self._handle_general_task_message(update, context, message_text)
    
    async def deliver_task(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Deliver a task to user according to their plan schedule"""
        try:
            # Get user's subscription and material
            subscription = await self.db_manager.get_active_subscription(user_id)
            if not subscription:
                logger.warning(f"No active subscription for user {user_id}")
                return False
            
            # Get user's personalized material
            state_data = await self.db_manager.get_user_state_data(user_id)
            material = state_data.get("personalized_material", {})
            selected_plan = state_data.get("selected_plan", "")
            target_goal = state_data.get("final_target_goal", "")
            user_name = state_data.get("first_name", "Друг")
            
            if not material:
                logger.warning(f"No personalized material for user {user_id}")
                return False
            
            # Get next task based on plan
            task_data = await self._get_next_task(user_id, material, selected_plan)
            if not task_data:
                logger.warning(f"No tasks available for user {user_id}")
                return False
            
            # Create task message
            task_message = await self._create_task_message(user_id, task_data, target_goal, user_name, selected_plan)
            
            # Send task to user
            await self._send_task_to_user(user_id, task_message, context)
            
            # Save active task
            await self.db_manager.update_user_state_data(user_id, {
                "active_task": task_data,
                "current_question_type": "task_work",
                "last_task_delivered": context.bot_data.get("current_time", "unknown")
            })
            
            # Update delivery statistics
            await self._update_delivery_stats(user_id, selected_plan)
            
            logger.info(f"Task delivered to user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error delivering task to user {user_id}: {e}")
            return False
    
    async def _get_next_task(self, user_id: int, material: dict, selected_plan: str) -> dict:
        """Get next task for user based on their plan and progress"""
        try:
            # Get user's task history
            task_history = await self.db_manager.get_user_task_history(user_id)
            completed_tasks = [task.get("task_id") for task in task_history if task.get("status") == "completed"]
            
            # Get available tasks based on plan
            if selected_plan in ["extreme", "2week"]:
                selected_tasks = material.get("selected_tasks", [])
                available_tasks = [task for task in selected_tasks if task.get("task_id") not in completed_tasks]
            else:
                # For Regular plan, use all generated tasks
                generated_tasks = material.get("generated_tasks", {})
                available_tasks = []
                for focus_id, tasks in generated_tasks.items():
                    for task in tasks:
                        if task.get("task_id") not in completed_tasks:
                            available_tasks.append(task)
            
            if not available_tasks:
                # All tasks completed, create a new one or cycle through
                if selected_plan in ["extreme", "2week"]:
                    selected_tasks = material.get("selected_tasks", [])
                    if selected_tasks:
                        # Cycle through tasks
                        task_index = len(completed_tasks) % len(selected_tasks)
                        return selected_tasks[task_index]
                else:
                    # For Regular plan, cycle through all tasks
                    generated_tasks = material.get("generated_tasks", {})
                    all_tasks = []
                    for focus_id, tasks in generated_tasks.items():
                        all_tasks.extend(tasks)
                    if all_tasks:
                        task_index = len(completed_tasks) % len(all_tasks)
                        return all_tasks[task_index]
                return None
            
            # Return next available task
            return available_tasks[0]
            
        except Exception as e:
            logger.error(f"Error getting next task for user {user_id}: {e}")
            return None
    
    async def _create_task_message(self, user_id: int, task_data: dict, target_goal: str, user_name: str, selected_plan: str) -> str:
        """Create personalized task message"""
        task_text = task_data.get("task_text", "Работа над целью")
        focus_statement = task_data.get("focus_statement", "Достижение цели")
        
        # Choose template based on plan and time
        template_type = random.choice(["motivation", "reminder", "support"])
        template = random.choice(self.task_templates[template_type])
        
        # Get plan info
        plan_info = self.plan_schedules.get(selected_plan, {})
        plan_name = plan_info.get("name", selected_plan.upper())
        
        # Create message
        message = f"""
{template}

**{user_name}, время работать над твоей целью!**

**🎯 Твоя цель:** "{target_goal}"
**📋 План:** {plan_name}

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
        
        return message
    
    async def _send_task_to_user(self, user_id: int, task_message: str, context: ContextTypes.DEFAULT_TYPE):
        """Send task message to user"""
        try:
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("Сделал движение! ✅", callback_data="task_movement_done")],
                [InlineKeyboardButton("Нужна помощь? ❓", callback_data="task_help")],
                [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await context.bot.send_message(
                chat_id=user_id,
                text=task_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error sending task to user {user_id}: {e}")
    
    async def _update_delivery_stats(self, user_id: int, selected_plan: str):
        """Update delivery statistics"""
        try:
            # Get current stats
            stats = await self.db_manager.get_user_delivery_stats(user_id)
            if not stats:
                stats = {
                    "total_deliveries": 0,
                    "completed_tasks": 0,
                    "plan": selected_plan
                }
            
            # Update stats
            stats["total_deliveries"] += 1
            stats["last_delivery"] = datetime.now().isoformat()
            
            # Save stats
            await self.db_manager.update_user_delivery_stats(user_id, stats)
            
        except Exception as e:
            logger.error(f"Error updating delivery stats for user {user_id}: {e}")
    
    async def _handle_task_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle user's task response"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        active_task = state_data.get("active_task", {})
        user_name = state_data.get("first_name", "Друг")
        
        # Store user response
        task_response = {
            "user_response": message_text,
            "timestamp": context.bot_data.get("current_time", "unknown"),
            "task_id": active_task.get("task_id", "unknown"),
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
    
    async def _handle_task_feelings(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle user's feelings and provide reinforcement"""
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
        
        # Update task completion stats
        await self._update_task_completion_stats(user_id, active_task.get("task_id", ""))
        
        # Provide reinforcement and remind of next iteration
        await self._provide_reinforcement(update, context, task_response, message_text, selected_plan, user_name)
    
    async def _provide_reinforcement(self, update: Update, context: ContextTypes.DEFAULT_TYPE, task_response: dict, feelings: str, selected_plan: str, user_name: str):
        """Provide reinforcement and remind of next iteration"""
        # Get plan info
        plan_info = self.plan_schedules.get(selected_plan, {})
        plan_name = plan_info.get("name", selected_plan.upper())
        interval_hours = plan_info.get("interval_hours", 24)
        
        # Calculate next delivery time
        next_delivery = datetime.now() + timedelta(hours=interval_hours)
        next_delivery_str = next_delivery.strftime("%H:%M")
        
        reinforcement_text = f"""
🎉 **Превосходно, {user_name}!**

Ты отлично справился с задачей! 

**Что ты сделал:**
{task_response.get('user_response', 'Движение в направлении цели')}

**Как ты себя чувствуешь:**
{feelings}

**🌟 Ты молодец!** Каждое движение в направлении цели - это шаг к успеху!

**Что дальше:**
Я буду отправлять тебе следующую задачу согласно твоему расписанию ({plan_name} план).

**Следующая задача:** примерно в {next_delivery_str}

**Регулярность - ключ к достижению цели!** 💪

**Продолжай в том же духе!** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")],
            [InlineKeyboardButton("Мой план 📋", callback_data="view_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(reinforcement_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _update_task_completion_stats(self, user_id: int, task_id: str):
        """Update task completion statistics"""
        try:
            # Get current stats
            stats = await self.db_manager.get_user_delivery_stats(user_id)
            if not stats:
                stats = {"completed_tasks": 0}
            
            # Update stats
            stats["completed_tasks"] += 1
            stats["last_completion"] = datetime.now().isoformat()
            
            # Save stats
            await self.db_manager.update_user_delivery_stats(user_id, stats)
            
            # Save task completion record
            await self.db_manager.save_task_completion(user_id, task_id, "completed")
            
        except Exception as e:
            logger.error(f"Error updating task completion stats for user {user_id}: {e}")
    
    async def _handle_task_completion(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle task completion messages"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_name = state_data.get("first_name", "Друг")
        
        # Update state to collect response
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
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
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

**Главное - сделать любое движение в направлении цели!** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Понял! Готов действовать! 🎯", callback_data="ready_to_act")],
            [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(task_help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_progress_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show user's progress status"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        # Get user stats
        stats = await self.db_manager.get_user_delivery_stats(user_id)
        selected_plan = state_data.get("selected_plan", "")
        target_goal = state_data.get("final_target_goal", "")
        user_name = state_data.get("first_name", "Друг")
        
        # Get plan info
        plan_info = self.plan_schedules.get(selected_plan, {})
        plan_name = plan_info.get("name", selected_plan.upper())
        
        # Calculate progress
        total_deliveries = stats.get("total_deliveries", 0) if stats else 0
        completed_tasks = stats.get("completed_tasks", 0) if stats else 0
        completion_rate = (completed_tasks / total_deliveries * 100) if total_deliveries > 0 else 0
        
        progress_text = f"""
📊 **Твой прогресс**

**{user_name}, вот твоя статистика:**

**🎯 Цель:** "{target_goal}"
**📋 План:** {plan_name}

**📈 Статистика:**
• **Задач получено:** {total_deliveries}
• **Задач выполнено:** {completed_tasks}
• **Процент выполнения:** {completion_rate:.1f}%

**🌟 Ты молодец!** Каждая выполненная задача приближает тебя к цели!

**Регулярность - ключ к успеху!** 💪
        """
        
        keyboard = [
            [InlineKeyboardButton("Продолжить работу! 🚀", callback_data="continue_work")],
            [InlineKeyboardButton("Мой план 📋", callback_data="view_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(progress_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_delivery_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show delivery schedule information"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        
        selected_plan = state_data.get("selected_plan", "")
        user_timezone = state_data.get("timezone", "UTC")
        user_name = state_data.get("first_name", "Друг")
        
        # Get plan info
        plan_info = self.plan_schedules.get(selected_plan, {})
        plan_name = plan_info.get("name", selected_plan.upper())
        messages_per_day = plan_info.get("messages_per_day", 1)
        interval_hours = plan_info.get("interval_hours", 24)
        description = plan_info.get("description", "")
        
        schedule_text = f"""
📅 **Твое расписание**

**{user_name}, вот твое расписание доставки задач:**

**📋 План:** {plan_name}
**📝 Описание:** {description}

**⏰ Расписание:**
• **Сообщений в день:** {messages_per_day}
• **Интервал:** каждые {interval_hours} часов
• **Временная зона:** {user_timezone}
• **Время:** В твоих комфортных часах

**Регулярность критически важна для достижения цели!** 💪

**Следующая задача будет доставлена согласно этому расписанию.** ⏰
        """
        
        keyboard = [
            [InlineKeyboardButton("Понял! Готов к работе! 🚀", callback_data="ready_to_work")],
            [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(schedule_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_general_task_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle general messages during task work"""
        user_id = update.effective_user.id
        state_data = await self.db_manager.get_user_state_data(user_id)
        user_name = state_data.get("first_name", "Друг")
        
        response_text = f"""
🤖 **Привет, {user_name}!**

Я здесь, чтобы помочь тебе достичь твоей цели!

**Что я могу сделать:**
• 🎯 Отправить тебе задачу для работы
• 📊 Показать твой прогресс
• 📅 Рассказать о расписании
• ❓ Помочь с выполнением задач

**Просто напиши:**
• "задача" - получить задачу
• "прогресс" - посмотреть статистику
• "расписание" - узнать время доставки
• "помощь" - получить поддержку

**Готов работать над целью?** 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("Получить задачу! 🎯", callback_data="get_task")],
            [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")],
            [InlineKeyboardButton("Расписание 📅", callback_data="show_schedule")],
            [InlineKeyboardButton("Помощь ❓", callback_data="get_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def start_scheduled_iterations(self, user_id: int, context: ContextTypes.DEFAULT_TYPE):
        """Start scheduled iterations for user based on their plan"""
        try:
            # Get user's subscription and plan
            subscription = await self.db_manager.get_active_subscription(user_id)
            if not subscription:
                logger.warning(f"No active subscription for user {user_id}")
                return False
            
            state_data = await self.db_manager.get_user_state_data(user_id)
            selected_plan = state_data.get("selected_plan", "")
            user_timezone = state_data.get("timezone", "UTC")
            user_name = state_data.get("first_name", "Друг")
            
            # Get plan info
            plan_info = self.plan_schedules.get(selected_plan, {})
            if not plan_info:
                logger.warning(f"Unknown plan for user {user_id}: {selected_plan}")
                return False
            
            # Calculate iteration schedule
            if selected_plan == "extreme":
                # Express plan: 6 times a day for a week
                await self._schedule_express_iterations(user_id, context, user_timezone, user_name)
                # Schedule check-ins every 2 days for Express plan
                await self._schedule_periodic_checkins(user_id, context, user_timezone, user_name, selected_plan, 2)
            elif selected_plan == "2week":
                # 2-week plan: 1 time a day for 2 weeks
                await self._schedule_2week_iterations(user_id, context, user_timezone, user_name)
                # Schedule check-ins every 3 days for 2-week plan
                await self._schedule_periodic_checkins(user_id, context, user_timezone, user_name, selected_plan, 3)
            else:
                # Regular plan: 1 time a day
                await self._schedule_regular_iterations(user_id, context, user_timezone, user_name)
                # Schedule check-ins every 3 days for Regular plan
                await self._schedule_periodic_checkins(user_id, context, user_timezone, user_name, selected_plan, 3)
            
            logger.info(f"Started scheduled iterations for user {user_id} with plan {selected_plan}")
            return True
            
        except Exception as e:
            logger.error(f"Error starting scheduled iterations for user {user_id}: {e}")
            return False
    
    async def _schedule_express_iterations(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, user_timezone: str, user_name: str):
        """Schedule Express plan iterations: 6 times a day for a week"""
        try:
            # Express plan: 6 times a day for 7 days = 42 iterations
            total_iterations = 42
            iterations_per_day = 6
            
            # Calculate delivery times (every 3-4 hours during awake hours)
            # Assuming awake hours: 8:00, 11:00, 14:00, 17:00, 20:00, 23:00
            delivery_hours = [8, 11, 14, 17, 20, 23]
            
            # Schedule iterations
            for day in range(7):  # 7 days
                for hour in delivery_hours:
                    # Calculate delivery time
                    delivery_time = datetime.now().replace(hour=hour, minute=0, second=0, microsecond=0)
                    delivery_time += timedelta(days=day)
                    
                    # Schedule the iteration
                    await self._schedule_single_iteration(user_id, context, delivery_time, user_name, "extreme")
            
            # Store iteration schedule
            await self.db_manager.update_user_state_data(user_id, {
                "scheduled_iterations": {
                    "plan": "extreme",
                    "total_iterations": total_iterations,
                    "iterations_per_day": iterations_per_day,
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=7)).isoformat(),
                    "delivery_hours": delivery_hours,
                    "completed_iterations": 0
                }
            })
            
        except Exception as e:
            logger.error(f"Error scheduling Express iterations for user {user_id}: {e}")
    
    async def _schedule_2week_iterations(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, user_timezone: str, user_name: str):
        """Schedule 2-week plan iterations: 1 time a day for 2 weeks"""
        try:
            # 2-week plan: 1 time a day for 14 days = 14 iterations
            total_iterations = 14
            iterations_per_day = 1
            
            # Calculate delivery time (e.g., 10:00 AM daily)
            delivery_hour = 10
            
            # Schedule iterations
            for day in range(14):  # 14 days
                # Calculate delivery time
                delivery_time = datetime.now().replace(hour=delivery_hour, minute=0, second=0, microsecond=0)
                delivery_time += timedelta(days=day)
                
                # Schedule the iteration
                await self._schedule_single_iteration(user_id, context, delivery_time, user_name, "2week")
            
            # Store iteration schedule
            await self.db_manager.update_user_state_data(user_id, {
                "scheduled_iterations": {
                    "plan": "2week",
                    "total_iterations": total_iterations,
                    "iterations_per_day": iterations_per_day,
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=14)).isoformat(),
                    "delivery_hour": delivery_hour,
                    "completed_iterations": 0
                }
            })
            
        except Exception as e:
            logger.error(f"Error scheduling 2-week iterations for user {user_id}: {e}")
    
    async def _schedule_regular_iterations(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, user_timezone: str, user_name: str):
        """Schedule Regular plan iterations: 1 time a day"""
        try:
            # Regular plan: 1 time a day (ongoing)
            total_iterations = 30  # 30 days
            iterations_per_day = 1
            
            # Calculate delivery time (e.g., 10:00 AM daily)
            delivery_hour = 10
            
            # Schedule iterations
            for day in range(30):  # 30 days
                # Calculate delivery time
                delivery_time = datetime.now().replace(hour=delivery_hour, minute=0, second=0, microsecond=0)
                delivery_time += timedelta(days=day)
                
                # Schedule the iteration
                await self._schedule_single_iteration(user_id, context, delivery_time, user_name, "regular")
            
            # Store iteration schedule
            await self.db_manager.update_user_state_data(user_id, {
                "scheduled_iterations": {
                    "plan": "regular",
                    "total_iterations": total_iterations,
                    "iterations_per_day": iterations_per_day,
                    "start_date": datetime.now().isoformat(),
                    "end_date": (datetime.now() + timedelta(days=30)).isoformat(),
                    "delivery_hour": delivery_hour,
                    "completed_iterations": 0
                }
            })
            
        except Exception as e:
            logger.error(f"Error scheduling Regular iterations for user {user_id}: {e}")
    
    async def _schedule_single_iteration(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, delivery_time: datetime, user_name: str, plan: str):
        """Schedule a single iteration"""
        try:
            # Calculate delay until delivery time
            now = datetime.now()
            if delivery_time <= now:
                delivery_time += timedelta(days=1)  # Schedule for next day if time has passed
            
            delay_seconds = (delivery_time - now).total_seconds()
            
            # Schedule the iteration
            context.job_queue.run_once(
                callback=lambda ctx: self._execute_scheduled_iteration(ctx, user_id, user_name, plan),
                when=delay_seconds,
                name=f"iteration_{user_id}_{delivery_time.isoformat()}"
            )
            
            logger.info(f"Scheduled iteration for user {user_id} at {delivery_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling single iteration for user {user_id}: {e}")
    
    async def _execute_scheduled_iteration(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_name: str, plan: str):
        """Execute a scheduled iteration"""
        try:
            # Get user's current state and material
            state_data = await self.db_manager.get_user_state_data(user_id)
            material = state_data.get("personalized_material", {})
            target_goal = state_data.get("final_target_goal", "")
            
            if not material:
                logger.warning(f"No personalized material for user {user_id}")
                return
            
            # Get next task based on plan
            task_data = await self._get_next_scheduled_task(user_id, material, plan)
            if not task_data:
                logger.warning(f"No tasks available for scheduled iteration for user {user_id}")
                return
            
            # Create scheduled task message
            task_message = await self._create_scheduled_task_message(user_id, task_data, target_goal, user_name, plan)
            
            # Send task to user
            await self._send_scheduled_task_to_user(user_id, task_message, context)
            
            # Save active task
            await self.db_manager.update_user_state_data(user_id, {
                "active_task": task_data,
                "current_question_type": "task_work",
                "last_scheduled_delivery": datetime.now().isoformat()
            })
            
            # Update iteration progress
            await self._update_iteration_progress(user_id)
            
            logger.info(f"Executed scheduled iteration for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error executing scheduled iteration for user {user_id}: {e}")
    
    async def _get_next_scheduled_task(self, user_id: int, material: dict, plan: str) -> dict:
        """Get next task for scheduled iteration"""
        try:
            # Get user's task history
            task_history = await self.db_manager.get_user_task_history(user_id)
            completed_tasks = [task.get("task_id") for task in task_history if task.get("status") == "completed"]
            
            # Get available tasks based on plan
            if plan in ["extreme", "2week"]:
                selected_tasks = material.get("selected_tasks", [])
                available_tasks = [task for task in selected_tasks if task.get("task_id") not in completed_tasks]
            else:
                # For Regular plan, use all generated tasks
                generated_tasks = material.get("generated_tasks", {})
                available_tasks = []
                for focus_id, tasks in generated_tasks.items():
                    for task in tasks:
                        if task.get("task_id") not in completed_tasks:
                            available_tasks.append(task)
            
            if not available_tasks:
                # All tasks completed, cycle through
                if plan in ["extreme", "2week"]:
                    selected_tasks = material.get("selected_tasks", [])
                    if selected_tasks:
                        task_index = len(completed_tasks) % len(selected_tasks)
                        return selected_tasks[task_index]
                else:
                    generated_tasks = material.get("generated_tasks", {})
                    all_tasks = []
                    for focus_id, tasks in generated_tasks.items():
                        all_tasks.extend(tasks)
                    if all_tasks:
                        task_index = len(completed_tasks) % len(all_tasks)
                        return all_tasks[task_index]
                return None
            
            # Return next available task
            return available_tasks[0]
            
        except Exception as e:
            logger.error(f"Error getting next scheduled task for user {user_id}: {e}")
            return None
    
    async def _create_scheduled_task_message(self, user_id: int, task_data: dict, target_goal: str, user_name: str, plan: str) -> str:
        """Create scheduled task message with periodic reminder"""
        task_text = task_data.get("task_text", "Работа над целью")
        focus_statement = task_data.get("focus_statement", "Достижение цели")
        
        # Choose random periodic reminder
        periodic_reminder = random.choice(self.periodic_reminders)
        
        # Get plan info
        plan_info = self.plan_schedules.get(plan, {})
        plan_name = plan_info.get("name", plan.upper())
        
        # Create message
        message = f"""
🎯 **Время работать над твоей целью!**

**{user_name}, чтобы достичь цели, сейчас мы работаем над задачей.**

**🎯 Твоя цель:** "{target_goal}"
**📋 План:** {plan_name}

**🎯 Задача:**
**{task_text}**

**Фокус-утверждение:** "{focus_statement}"

**{periodic_reminder}**

**Попробуй сделать что-то прямо сейчас и напиши, что получилось!**

**Готов попробовать?** 🚀
        """
        
        return message
    
    async def _send_scheduled_task_to_user(self, user_id: int, task_message: str, context: ContextTypes.DEFAULT_TYPE):
        """Send scheduled task message to user"""
        try:
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("Сделал движение! ✅", callback_data="task_movement_done")],
                [InlineKeyboardButton("Нужна помощь? ❓", callback_data="task_help")],
                [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await context.bot.send_message(
                chat_id=user_id,
                text=task_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error sending scheduled task to user {user_id}: {e}")
    
    async def _update_iteration_progress(self, user_id: int):
        """Update iteration progress"""
        try:
            # Get current iteration data
            state_data = await self.db_manager.get_user_state_data(user_id)
            scheduled_iterations = state_data.get("scheduled_iterations", {})
            
            if scheduled_iterations:
                # Update completed iterations
                scheduled_iterations["completed_iterations"] += 1
                
                # Save updated data
                await self.db_manager.update_user_state_data(user_id, {
                    "scheduled_iterations": scheduled_iterations
                })
                
                logger.info(f"Updated iteration progress for user {user_id}: {scheduled_iterations['completed_iterations']}")
            
        except Exception as e:
            logger.error(f"Error updating iteration progress for user {user_id}: {e}")
    
    async def _schedule_periodic_checkins(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, user_timezone: str, user_name: str, plan: str, checkin_interval_days: int):
        """Schedule periodic check-ins every 2-3 days"""
        try:
            # Calculate plan duration
            if plan == "extreme":
                plan_duration_days = 7
            elif plan == "2week":
                plan_duration_days = 14
            else:
                plan_duration_days = 30
            
            # Calculate number of check-ins
            num_checkins = plan_duration_days // checkin_interval_days
            
            # Schedule check-ins
            for i in range(num_checkins):
                checkin_day = (i + 1) * checkin_interval_days
                # Schedule check-in at 9:00 AM
                checkin_time = datetime.now().replace(hour=9, minute=0, second=0, microsecond=0)
                checkin_time += timedelta(days=checkin_day)
                
                # Schedule the check-in
                await self._schedule_single_checkin(user_id, context, checkin_time, user_name, plan, i + 1)
            
            # Schedule final evaluation
            final_evaluation_time = datetime.now().replace(hour=10, minute=0, second=0, microsecond=0)
            final_evaluation_time += timedelta(days=plan_duration_days)
            await self._schedule_final_evaluation(user_id, context, final_evaluation_time, user_name, plan)
            
            logger.info(f"Scheduled {num_checkins} check-ins for user {user_id} with plan {plan}")
            
        except Exception as e:
            logger.error(f"Error scheduling periodic check-ins for user {user_id}: {e}")
    
    async def _schedule_single_checkin(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, checkin_time: datetime, user_name: str, plan: str, checkin_number: int):
        """Schedule a single check-in"""
        try:
            # Calculate delay until check-in time
            now = datetime.now()
            if checkin_time <= now:
                checkin_time += timedelta(days=1)  # Schedule for next day if time has passed
            
            delay_seconds = (checkin_time - now).total_seconds()
            
            # Schedule the check-in
            context.job_queue.run_once(
                callback=lambda ctx: self._execute_periodic_checkin(ctx, user_id, user_name, plan, checkin_number),
                when=delay_seconds,
                name=f"checkin_{user_id}_{checkin_time.isoformat()}"
            )
            
            logger.info(f"Scheduled check-in {checkin_number} for user {user_id} at {checkin_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling single check-in for user {user_id}: {e}")
    
    async def _schedule_final_evaluation(self, user_id: int, context: ContextTypes.DEFAULT_TYPE, evaluation_time: datetime, user_name: str, plan: str):
        """Schedule final evaluation"""
        try:
            # Calculate delay until evaluation time
            now = datetime.now()
            if evaluation_time <= now:
                evaluation_time += timedelta(days=1)  # Schedule for next day if time has passed
            
            delay_seconds = (evaluation_time - now).total_seconds()
            
            # Schedule the final evaluation
            context.job_queue.run_once(
                callback=lambda ctx: self._execute_final_evaluation(ctx, user_id, user_name, plan),
                when=delay_seconds,
                name=f"final_evaluation_{user_id}_{evaluation_time.isoformat()}"
            )
            
            logger.info(f"Scheduled final evaluation for user {user_id} at {evaluation_time}")
            
        except Exception as e:
            logger.error(f"Error scheduling final evaluation for user {user_id}: {e}")
    
    async def _execute_periodic_checkin(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_name: str, plan: str, checkin_number: int):
        """Execute a periodic check-in"""
        try:
            # Get user's current state
            state_data = await self.db_manager.get_user_state_data(user_id)
            target_goal = state_data.get("final_target_goal", "")
            
            # Create check-in message
            checkin_message = await self._create_checkin_message(user_id, target_goal, user_name, plan, checkin_number)
            
            # Send check-in to user
            await self._send_checkin_to_user(user_id, checkin_message, context)
            
            # Update state for check-in response
            await self.db_manager.update_user_state_data(user_id, {
                "current_question_type": "checkin_response",
                "checkin_number": checkin_number,
                "checkin_started": datetime.now().isoformat()
            })
            
            logger.info(f"Executed periodic check-in {checkin_number} for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error executing periodic check-in for user {user_id}: {e}")
    
    async def _execute_final_evaluation(self, context: ContextTypes.DEFAULT_TYPE, user_id: int, user_name: str, plan: str):
        """Execute final evaluation"""
        try:
            # Get user's current state
            state_data = await self.db_manager.get_user_state_data(user_id)
            target_goal = state_data.get("final_target_goal", "")
            
            # Create final evaluation message
            evaluation_message = await self._create_final_evaluation_message(user_id, target_goal, user_name, plan)
            
            # Send final evaluation to user
            await self._send_final_evaluation_to_user(user_id, evaluation_message, context)
            
            # Update state for final evaluation response
            await self.db_manager.update_user_state_data(user_id, {
                "current_question_type": "final_evaluation_response",
                "final_evaluation_started": datetime.now().isoformat()
            })
            
            logger.info(f"Executed final evaluation for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error executing final evaluation for user {user_id}: {e}")
    
    async def _create_checkin_message(self, user_id: int, target_goal: str, user_name: str, plan: str, checkin_number: int) -> str:
        """Create periodic check-in message"""
        # Get plan info
        plan_info = self.plan_schedules.get(plan, {})
        plan_name = plan_info.get("name", plan.upper())
        
        # Choose random questions
        feelings_question = random.choice(self.checkin_questions["feelings"])
        progress_question = random.choice(self.checkin_questions["progress"])
        rational_steps_question = random.choice(self.checkin_questions["rational_steps"])
        
        message = f"""
📊 **Периодическая проверка #{checkin_number}**

**{user_name}, давай проверим, как дела с твоей целью!**

**🎯 Твоя цель:** "{target_goal}"
**📋 План:** {plan_name}

**Вопросы для размышления:**

**1. {feelings_question}**
Поделись своими чувствами и эмоциями.

**2. {progress_question}**
Расскажи о том, что изменилось.

**3. {rational_steps_question}**
Напомню, что важно делать не только эмоциональные, но и рациональные шаги для достижения цели.

**Поделись своими мыслями по всем трем вопросам!** 📝
        """
        
        return message
    
    async def _create_final_evaluation_message(self, user_id: int, target_goal: str, user_name: str, plan: str) -> str:
        """Create final evaluation message"""
        # Get plan info
        plan_info = self.plan_schedules.get(plan, {})
        plan_name = plan_info.get("name", plan.upper())
        
        # Choose random questions
        feelings_question = random.choice(self.final_evaluation_questions["feelings"])
        results_question = random.choice(self.final_evaluation_questions["results"])
        overall_question = random.choice(self.final_evaluation_questions["overall"])
        
        message = f"""
🎉 **Финальная оценка плана**

**{user_name}, поздравляю! Ты завершил свой план!**

**🎯 Твоя цель:** "{target_goal}"
**📋 План:** {plan_name}

**Время подвести итоги:**

**1. {feelings_question}**
Поделись своими чувствами по поводу достижения цели.

**2. {results_question}**
Расскажи о результатах, которых ты достиг.

**3. {overall_question}**
Поделись общими впечатлениями о процессе.

**Это важный момент для размышления! Поделись своими мыслями!** 🌟
        """
        
        return message
    
    async def _send_checkin_to_user(self, user_id: int, checkin_message: str, context: ContextTypes.DEFAULT_TYPE):
        """Send check-in message to user"""
        try:
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("Начать проверку 📝", callback_data="start_checkin")],
                [InlineKeyboardButton("Показать прогресс 📊", callback_data="show_progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await context.bot.send_message(
                chat_id=user_id,
                text=checkin_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error sending check-in to user {user_id}: {e}")
    
    async def _send_final_evaluation_to_user(self, user_id: int, evaluation_message: str, context: ContextTypes.DEFAULT_TYPE):
        """Send final evaluation message to user"""
        try:
            # Create keyboard
            keyboard = [
                [InlineKeyboardButton("Начать финальную оценку 🎉", callback_data="start_final_evaluation")],
                [InlineKeyboardButton("Показать итоговый прогресс 📊", callback_data="show_final_progress")]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            # Send message
            await context.bot.send_message(
                chat_id=user_id,
                text=evaluation_message,
                parse_mode='Markdown',
                reply_markup=reply_markup
            )
            
        except Exception as e:
            logger.error(f"Error sending final evaluation to user {user_id}: {e}")
    
    async def _handle_task_movement_done(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle task movement completion"""
        user_id = update.effective_user.id
        
        # Update state to collect task response
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "task_response_collection"
        })
        
        response_text = """
🎯 **Отлично! Ты сделал движение!**

Теперь расскажи мне, что именно ты сделал:

**Что ты предпринял для выполнения задачи?**
• Какие конкретные действия выполнил?
• Что получилось?
• С какими трудностями столкнулся?

**Поделись подробностями!** 📝
        """
        
        await update.callback_query.edit_message_text(response_text, parse_mode='Markdown')
    
    async def _start_checkin_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start check-in response collection"""
        user_id = update.effective_user.id
        
        # Update state to collect check-in response
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "checkin_response"
        })
        
        response_text = """
📝 **Начинаем проверку!**

Поделись своими мыслями по всем трем вопросам:

**1. Как ты себя чувствуешь в целом?**
**2. Как продвигается работа над твоей целью?**
**3. Какие рациональные шаги ты предпринял?**

**Напиши свой ответ, и я сохраню его для анализа прогресса!** ✨
        """
        
        await update.callback_query.edit_message_text(response_text, parse_mode='Markdown')
    
    async def _start_final_evaluation_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start final evaluation response collection"""
        user_id = update.effective_user.id
        
        # Update state to collect final evaluation response
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "final_evaluation_response"
        })
        
        response_text = """
🎉 **Начинаем финальную оценку!**

Поделись своими мыслями по всем трем вопросам:

**1. Какие чувства у тебя сейчас по поводу достижения цели?**
**2. Какие результаты ты достиг?**
**3. Как ты оцениваешь весь процесс?**

**Это важный момент для размышления! Напиши свой ответ!** 🌟
        """
        
        await update.callback_query.edit_message_text(response_text, parse_mode='Markdown')
    
    async def _show_final_progress(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show final progress summary"""
        user_id = update.effective_user.id
        
        # Get user's progress data
        state_data = await self.db_manager.get_user_state_data(user_id)
        scheduled_iterations = state_data.get("scheduled_iterations", {})
        
        completed_iterations = scheduled_iterations.get("completed_iterations", 0)
        total_iterations = scheduled_iterations.get("total_iterations", 0)
        plan = scheduled_iterations.get("plan", "unknown")
        
        progress_text = f"""
🎉 **Итоговый прогресс**

**📊 Статистика выполнения:**
• Выполнено итераций: {completed_iterations} из {total_iterations}
• План: {plan.upper()}
• Процент выполнения: {(completed_iterations/total_iterations*100):.1f}%

**🌟 Поздравляю с завершением плана!**

Ты проделал отличную работу и достиг значительного прогресса в достижении своей цели!

**Спасибо за доверие к HackReality!** 🙏
        """
        
        await update.callback_query.edit_message_text(progress_text, parse_mode='Markdown')
    
    async def _handle_checkin_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle check-in response from user"""
        user_id = update.effective_user.id
        
        # Store check-in response
        await self.db_manager.store_user_message(
            user_id=user_id,
            message_text=message_text,
            message_type="checkin_response",
            module_context="iteration",
            state_context="periodic_checkin"
        )
        
        # Get check-in number
        state_data = await self.db_manager.get_user_state_data(user_id)
        checkin_number = state_data.get("checkin_number", 1)
        
        # Reset question type
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "task_work"
        })
        
        response_text = f"""
✅ **Спасибо за ответ!**

Я сохранил твои мысли по проверке #{checkin_number}.

**Твои размышления очень важны для отслеживания прогресса!**

Продолжай работать над своей целью, и я буду поддерживать тебя на этом пути! 💪

**Следующая задача придет согласно твоему расписанию.** ⏰
        """
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    async def _handle_final_evaluation_response(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle final evaluation response from user"""
        user_id = update.effective_user.id
        
        # Store final evaluation response
        await self.db_manager.store_user_message(
            user_id=user_id,
            message_text=message_text,
            message_type="final_evaluation_response",
            module_context="iteration",
            state_context="final_evaluation"
        )
        
        # Mark plan as completed
        await self.db_manager.update_user_state_data(user_id, {
            "current_question_type": "plan_completed",
            "plan_completed_at": context.bot_data.get("current_time", "unknown")
        })
        
        response_text = """
🎉 **Поздравляю с завершением плана!**

Спасибо за твои искренние ответы! Я сохранил твою финальную оценку.

**Ты проделал отличную работу!** 🌟

**Что дальше:**
• Ты можешь продолжить работу над своей целью самостоятельно
• Или начать новый план, если хочешь достичь других целей
• Просто напиши /start для нового путешествия

**Спасибо за доверие к HackReality!** 🙏

*Твоя мечта стала ближе благодаря твоим усилиям!* ✨
        """
        
        await update.message.reply_text(response_text, parse_mode='Markdown')
    
    async def _handle_content_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle content requests from users"""
        user_id = update.effective_user.id
        
        # Check if user has active subscription
        subscription = await self.db_manager.get_active_subscription(user_id)
        if not subscription:
            await self._show_no_subscription_message(update, context)
            return
        
        # Determine content type
        content_type = self._determine_content_type(message_text)
        
        # Generate content
        await self._generate_and_send_content(update, context, user_id, content_type)
    
    async def _handle_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle user feedback"""
        user_id = update.effective_user.id
        
        # Extract feedback sentiment
        sentiment = self._extract_feedback_sentiment(message_text)
        
        # Store feedback
        await self._store_feedback(user_id, sentiment, message_text)
        
        # Respond to feedback
        await self._respond_to_feedback(update, context, sentiment)
    
    async def _handle_schedule_inquiry(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle schedule inquiries"""
        user_id = update.effective_user.id
        
        # Get user's subscription and settings
        subscription = await self.db_manager.get_active_subscription(user_id)
        user_settings = await self.db_manager.get_user_settings(user_id)
        
        if not subscription:
            await self._show_no_subscription_message(update, context)
            return
        
        # Calculate next delivery
        next_delivery = await self._calculate_next_delivery(subscription, user_settings)
        
        # Show schedule information
        await self._show_schedule_info(update, context, subscription, next_delivery)
    
    async def _handle_general_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle general messages from users"""
        user_id = update.effective_user.id
        
        # Check if user has active subscription
        subscription = await self.db_manager.get_active_subscription(user_id)
        if not subscription:
            await self._show_no_subscription_message(update, context)
            return
        
        # Provide helpful response
        response_text = """
🤖 **I'm here to help!**

I can assist you with:
• 📝 Creating personalized content
• 📊 Checking your delivery schedule
• 💬 Providing feedback on content
• ❓ Answering questions

**What would you like to do?**
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Request Content", callback_data="request_content")],
            [InlineKeyboardButton("📊 Check Schedule", callback_data="check_schedule")],
            [InlineKeyboardButton("💬 Give Feedback", callback_data="give_feedback")],
            [InlineKeyboardButton("❓ Get Help", callback_data="get_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _generate_and_send_content(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, content_type: str):
        """Generate and send personalized content to user"""
        # Get user's key texts and preferences
        user_settings = await self.db_manager.get_user_settings(user_id)
        subscription = await self.db_manager.get_active_subscription(user_id)
        
        if not user_settings or not subscription:
            await self._show_setup_required_message(update, context)
            return
        
        # Generate content based on user's style and preferences
        content = await self._generate_content(user_settings, subscription, content_type)
        
        # Send content to user
        await self._send_content_to_user(update, context, content, content_type)
        
        # Log iteration
        await self._log_iteration(user_id, content, content_type)
    
    async def _generate_content(self, user_settings: Dict[str, Any], subscription: Dict[str, Any], content_type: str) -> str:
        """Generate personalized content based on user settings"""
        # Get user's key texts and preferences
        key_texts = user_settings.get('key_texts', [])
        preferences = user_settings.get('preferences', {})
        
        # Determine content length based on preferences
        content_length = preferences.get('content_length', 'medium')
        
        # Generate content based on type and length
        if content_type == "blog_post":
            content = self._generate_blog_post(key_texts, preferences, content_length)
        elif content_type == "social_media":
            content = self._generate_social_media_post(key_texts, preferences, content_length)
        elif content_type == "email":
            content = self._generate_email_content(key_texts, preferences, content_length)
        else:  # article
            content = self._generate_article(key_texts, preferences, content_length)
        
        return content
    
    def _generate_blog_post(self, key_texts: List[str], preferences: Dict[str, Any], content_length: str) -> str:
        """Generate blog post content"""
        # Extract topics from preferences
        topics = preferences.get('topics', ['general'])
        topic = topics[0] if topics else 'general'
        
        # Generate content based on length
        if content_length == "short":
            content = f"""
# {topic.title()} Tips for Success

Based on your preferences, here are some key insights about {topic}:

**Key Point 1:** Understanding the fundamentals is crucial for success in {topic}.

**Key Point 2:** Consistent practice and application lead to better results.

**Key Point 3:** Learning from others' experiences can accelerate your progress.

**Conclusion:** Focus on these core principles to improve your {topic} skills.

*This content was personalized based on your writing style and preferences.*
            """
        elif content_length == "long":
            content = f"""
# The Complete Guide to {topic.title()}

## Introduction

In today's fast-paced world, understanding {topic} has become more important than ever. This comprehensive guide will walk you through everything you need to know to master {topic} and achieve your goals.

## Understanding the Basics

Before diving deep into advanced concepts, it's essential to understand the fundamental principles of {topic}. These basics form the foundation upon which all advanced techniques are built.

### Key Principles

1. **Principle One:** The first principle involves understanding the core concepts and how they relate to your specific situation.

2. **Principle Two:** The second principle focuses on practical application and real-world implementation.

3. **Principle Three:** The third principle emphasizes continuous learning and adaptation.

## Advanced Strategies

Once you've mastered the basics, you can move on to more advanced strategies that will help you excel in {topic}.

### Strategy 1: Advanced Technique
This strategy involves more complex approaches that require deeper understanding and practice.

### Strategy 2: Optimization Methods
These methods help you optimize your approach for better results and efficiency.

### Strategy 3: Innovation and Creativity
This strategy encourages thinking outside the box and developing unique solutions.

## Practical Implementation

Theory is important, but practical implementation is where the real value lies. Here's how to apply what you've learned:

### Step 1: Planning
Start by creating a detailed plan that outlines your goals and the steps needed to achieve them.

### Step 2: Execution
Implement your plan with consistency and attention to detail.

### Step 3: Evaluation
Regularly evaluate your progress and make adjustments as needed.

## Common Challenges and Solutions

Every journey has its challenges. Here are some common obstacles you might face and how to overcome them:

### Challenge 1: Getting Started
**Solution:** Start small and build momentum gradually.

### Challenge 2: Maintaining Consistency
**Solution:** Create systems and routines that support your goals.

### Challenge 3: Overcoming Plateaus
**Solution:** Vary your approach and seek new learning opportunities.

## Conclusion

Mastering {topic} is a journey that requires dedication, practice, and continuous learning. By following the principles and strategies outlined in this guide, you'll be well on your way to achieving your goals.

Remember, success in {topic} comes from consistent effort and a willingness to adapt and grow. Keep learning, keep practicing, and keep pushing yourself to new heights.

*This content was personalized based on your writing style and preferences.*
            """
        else:  # medium
            content = f"""
# {topic.title()}: A Practical Guide

## Getting Started with {topic}

{topic.title()} is an essential skill that can significantly impact your success. Whether you're a beginner or looking to improve your existing knowledge, this guide will help you understand the key concepts and practical applications.

## Key Concepts

**Understanding the Fundamentals**
The first step in mastering {topic} is understanding its core principles. These fundamentals provide the foundation for all advanced techniques and strategies.

**Practical Application**
Theory without practice is incomplete. Learning how to apply {topic} concepts in real-world situations is crucial for success.

**Continuous Improvement**
The field of {topic} is constantly evolving. Staying updated with the latest trends and techniques is essential for long-term success.

## Implementation Strategies

1. **Start Small:** Begin with simple concepts and gradually work your way up to more complex topics.

2. **Practice Regularly:** Consistent practice is key to mastering any skill, including {topic}.

3. **Seek Feedback:** Getting input from others can help you identify areas for improvement.

4. **Stay Curious:** Maintain a curious mindset and always look for new learning opportunities.

## Common Pitfalls to Avoid

- **Overcomplicating:** Don't make things more complex than they need to be.
- **Skipping Basics:** Ensure you have a solid foundation before moving to advanced topics.
- **Lack of Practice:** Theory alone won't make you proficient in {topic}.

## Moving Forward

As you continue your journey with {topic}, remember that progress takes time. Be patient with yourself and celebrate small victories along the way.

**Next Steps:**
- Review the concepts covered in this guide
- Practice the techniques discussed
- Seek additional resources for deeper learning
- Connect with others who share your interest in {topic}

*This content was personalized based on your writing style and preferences.*
            """
        
        return content
    
    def _generate_social_media_post(self, key_texts: List[str], preferences: Dict[str, Any], content_length: str) -> str:
        """Generate social media post content"""
        topics = preferences.get('topics', ['general'])
        topic = topics[0] if topics else 'general'
        
        if content_length == "short":
            content = f"""
🚀 Quick {topic.title()} Tip!

Just learned something amazing about {topic} that I had to share:

✅ Key insight: Understanding the basics is crucial
✅ Pro tip: Practice consistently for better results
✅ Bonus: Learn from others' experiences

What's your favorite {topic} tip? Share below! 👇

#{topic} #tips #learning
            """
        else:  # medium or long
            content = f"""
🎯 {topic.title()} Success Story!

I've been working on improving my {topic} skills, and here's what I've learned:

📚 **The Learning Process:**
• Start with fundamentals
• Practice regularly
• Seek feedback
• Stay curious

💡 **Key Insights:**
• Consistency beats intensity
• Small steps lead to big changes
• Community support matters

🚀 **Results:**
The improvement has been incredible! My {topic} skills have grown significantly, and I'm excited to continue this journey.

**What's your experience with {topic}?** I'd love to hear your story! 💬

#{topic} #success #learning #growth
            """
        
        return content
    
    def _generate_email_content(self, key_texts: List[str], preferences: Dict[str, Any], content_length: str) -> str:
        """Generate email content"""
        topics = preferences.get('topics', ['general'])
        topic = topics[0] if topics else 'general'
        
        if content_length == "short":
            content = f"""
Subject: Quick Update on {topic.title()}

Hi there,

I wanted to share a quick update about {topic}:

• Progress: Making steady improvements
• Next steps: Focus on practical application
• Timeline: Expecting results within 2-3 weeks

Let me know if you have any questions!

Best regards,
[Your Name]
            """
        else:  # medium or long
            content = f"""
Subject: {topic.title()} Progress Report and Next Steps

Hi there,

I hope this email finds you well. I wanted to provide you with a comprehensive update on our {topic} project and outline the next steps.

## Current Progress

We've made significant progress in understanding and implementing {topic} strategies. The key achievements include:

• **Foundation Building:** We've established a solid understanding of the core concepts
• **Practical Application:** Successfully implemented several key techniques
• **Results:** Initial results show promising improvements

## Key Insights

Through this process, we've learned several important lessons:

1. **Consistency is Key:** Regular practice and application yield the best results
2. **Community Matters:** Learning from others' experiences accelerates progress
3. **Adaptation is Essential:** Being flexible and adjusting our approach as needed

## Next Steps

Looking ahead, here's what we plan to focus on:

• **Advanced Techniques:** Dive deeper into more sophisticated strategies
• **Optimization:** Fine-tune our current approach for better results
• **Expansion:** Explore new areas and opportunities within {topic}

## Timeline

We expect to see significant improvements within the next 2-3 weeks, with continued progress over the following months.

## Questions and Feedback

I'd love to hear your thoughts on our progress and any suggestions you might have. Your input is invaluable to our success.

Please don't hesitate to reach out if you have any questions or concerns.

Best regards,
[Your Name]

P.S. I'll keep you updated on our progress and any new developments.
            """
        
        return content
    
    def _generate_article(self, key_texts: List[str], preferences: Dict[str, Any], content_length: str) -> str:
        """Generate article content"""
        topics = preferences.get('topics', ['general'])
        topic = topics[0] if topics else 'general'
        
        if content_length == "short":
            content = f"""
# {topic.title()}: Essential Insights

## Introduction

{topic.title()} plays a crucial role in today's world. Understanding its key principles can help you achieve better results and make more informed decisions.

## Key Points

**Point 1: Fundamentals Matter**
Understanding the basics is essential for success in {topic}. These fundamentals provide the foundation for all advanced techniques.

**Point 2: Practice Makes Perfect**
Consistent practice and application are key to mastering {topic}. Regular engagement with the concepts leads to better understanding and results.

**Point 3: Continuous Learning**
The field of {topic} is constantly evolving. Staying updated with the latest trends and techniques is crucial for long-term success.

## Conclusion

By focusing on these key principles, you can improve your {topic} skills and achieve your goals. Remember, progress takes time, so be patient and consistent in your efforts.

*This content was personalized based on your writing style and preferences.*
            """
        else:  # medium or long
            content = f"""
# {topic.title()}: A Comprehensive Guide

## Introduction

In today's rapidly changing world, understanding {topic} has become more important than ever. This comprehensive guide will provide you with the knowledge and tools you need to succeed in {topic}.

## Understanding the Basics

Before diving into advanced concepts, it's essential to understand the fundamental principles of {topic}. These basics form the foundation upon which all advanced techniques are built.

### Core Principles

1. **Principle of Foundation:** Understanding the core concepts and how they relate to your specific situation.

2. **Principle of Application:** Learning how to apply {topic} concepts in real-world situations.

3. **Principle of Growth:** Continuously learning and adapting to new developments in the field.

## Advanced Strategies

Once you've mastered the basics, you can move on to more advanced strategies that will help you excel in {topic}.

### Strategy 1: Advanced Techniques
This strategy involves more complex approaches that require deeper understanding and practice.

### Strategy 2: Optimization Methods
These methods help you optimize your approach for better results and efficiency.

### Strategy 3: Innovation and Creativity
This strategy encourages thinking outside the box and developing unique solutions.

## Practical Implementation

Theory is important, but practical implementation is where the real value lies. Here's how to apply what you've learned:

### Step 1: Planning
Start by creating a detailed plan that outlines your goals and the steps needed to achieve them.

### Step 2: Execution
Implement your plan with consistency and attention to detail.

### Step 3: Evaluation
Regularly evaluate your progress and make adjustments as needed.

## Common Challenges and Solutions

Every journey has its challenges. Here are some common obstacles you might face and how to overcome them:

### Challenge 1: Getting Started
**Solution:** Start small and build momentum gradually.

### Challenge 2: Maintaining Consistency
**Solution:** Create systems and routines that support your goals.

### Challenge 3: Overcoming Plateaus
**Solution:** Vary your approach and seek new learning opportunities.

## Best Practices

To maximize your success in {topic}, consider these best practices:

• **Stay Updated:** Keep up with the latest trends and developments
• **Network:** Connect with others who share your interest in {topic}
• **Practice Regularly:** Consistent practice is key to mastery
• **Seek Feedback:** Get input from others to improve your approach

## Conclusion

Mastering {topic} is a journey that requires dedication, practice, and continuous learning. By following the principles and strategies outlined in this guide, you'll be well on your way to achieving your goals.

Remember, success in {topic} comes from consistent effort and a willingness to adapt and grow. Keep learning, keep practicing, and keep pushing yourself to new heights.

*This content was personalized based on your writing style and preferences.*
            """
        
        return content
    
    async def _send_content_to_user(self, update: Update, context: ContextTypes.DEFAULT_TYPE, content: str, content_type: str):
        """Send generated content to user"""
        # Format content for Telegram
        formatted_content = f"""
📝 **Your Personalized {content_type.replace('_', ' ').title()}**

{content}

---
*Generated based on your preferences and writing style*
        """
        
        # Add feedback buttons
        keyboard = [
            [InlineKeyboardButton("👍 Like", callback_data="feedback_like"), InlineKeyboardButton("👎 Dislike", callback_data="feedback_dislike")],
            [InlineKeyboardButton("💬 Give Feedback", callback_data="give_feedback"), InlineKeyboardButton("🔄 Request Another", callback_data="request_another")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(formatted_content, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _log_iteration(self, user_id: int, content: str, content_type: str):
        """Log iteration in database"""
        # Get current iteration number
        iterations = await self.db_manager.get_user_iterations(user_id)
        iteration_number = len(iterations) + 1
        
        # Log the iteration
        await self.db_manager.log_iteration(user_id, iteration_number, content, "sent")
        
        logger.info(f"Logged iteration {iteration_number} for user {user_id}")
    
    async def _calculate_next_delivery(self, subscription: Dict[str, Any], user_settings: Dict[str, Any]) -> datetime:
        """Calculate next content delivery time"""
        # Get subscription type
        subscription_type = subscription['subscription_type']
        
        # Calculate delivery frequency
        if subscription_type == "extreme":
            frequency_hours = 24  # Daily
        elif subscription_type == "2week":
            frequency_hours = 48  # Every 2 days
        else:  # regular
            frequency_hours = 168  # Weekly
        
        # Get last delivery time
        iterations = await self.db_manager.get_user_iterations(subscription['user_id'])
        if iterations:
            last_delivery = datetime.fromisoformat(iterations[0]['sent_at'].replace('Z', '+00:00'))
            next_delivery = last_delivery + timedelta(hours=frequency_hours)
        else:
            # First delivery
            next_delivery = datetime.now() + timedelta(hours=1)
        
        return next_delivery
    
    async def _show_schedule_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subscription: Dict[str, Any], next_delivery: datetime):
        """Show schedule information to user"""
        subscription_type = subscription['subscription_type']
        
        # Format next delivery time
        next_delivery_str = next_delivery.strftime("%Y-%m-%d %H:%M")
        
        # Calculate time until next delivery
        time_until = next_delivery - datetime.now()
        hours_until = int(time_until.total_seconds() / 3600)
        
        schedule_text = f"""
📅 **Your Content Schedule**

**Current Plan:** {subscription_type.title()}
**Next Delivery:** {next_delivery_str}
**Time Until Next:** {hours_until} hours

**Delivery Frequency:**
• {self._get_delivery_frequency(subscription_type)}

**Content Types:**
• Blog posts
• Social media content
• Email content
• Articles

**Need Content Now?**
You can request additional content anytime! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Request Content Now", callback_data="request_content")],
            [InlineKeyboardButton("🔄 Change Schedule", callback_data="change_schedule")],
            [InlineKeyboardButton("📊 View History", callback_data="view_history")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(schedule_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    def _get_delivery_frequency(self, subscription_type: str) -> str:
        """Get delivery frequency description"""
        frequencies = {
            "extreme": "Daily content delivery",
            "2week": "Content every 2 days",
            "regular": "Weekly content delivery"
        }
        return frequencies.get(subscription_type, "Unknown")
    
    def _determine_content_type(self, message_text: str) -> str:
        """Determine content type from message"""
        if any(word in message_text for word in ["blog", "post", "article"]):
            return "blog_post"
        elif any(word in message_text for word in ["social", "media", "twitter", "facebook", "instagram"]):
            return "social_media"
        elif any(word in message_text for word in ["email", "mail", "message"]):
            return "email"
        else:
            return "article"
    
    def _extract_feedback_sentiment(self, message_text: str) -> str:
        """Extract feedback sentiment from message"""
        positive_words = ["good", "great", "excellent", "amazing", "love", "like", "perfect", "awesome"]
        negative_words = ["bad", "terrible", "awful", "hate", "dislike", "wrong", "poor", "horrible"]
        
        message_lower = message_text.lower()
        
        positive_count = sum(1 for word in positive_words if word in message_lower)
        negative_count = sum(1 for word in negative_words if word in message_lower)
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"
    
    async def _store_feedback(self, user_id: int, sentiment: str, feedback_text: str):
        """Store user feedback"""
        # In a real implementation, you'd store this in the database
        logger.info(f"Stored feedback from user {user_id}: {sentiment} - {feedback_text}")
    
    async def _respond_to_feedback(self, update: Update, context: ContextTypes.DEFAULT_TYPE, sentiment: str):
        """Respond to user feedback"""
        if sentiment == "positive":
            response = """
👍 **Thank you for the positive feedback!**

I'm glad you're enjoying the content! Your feedback helps me improve and create even better content for you.

**What's Next?**
• I'll continue creating content in this style
• Feel free to request specific types of content
• Your preferences will be updated based on your feedback

Keep the feedback coming! 🚀
            """
        elif sentiment == "negative":
            response = """
👎 **Thank you for the honest feedback!**

I appreciate you taking the time to share your thoughts. Your feedback is valuable and helps me improve.

**How I Can Help:**
• I can adjust the content style and approach
• You can request specific changes or improvements
• I'll learn from your feedback to create better content

**What would you like me to change?** Let me know so I can improve! 🔄
            """
        else:  # neutral
            response = """
💬 **Thank you for your feedback!**

I appreciate you sharing your thoughts. Your input helps me understand your preferences better.

**How I Can Improve:**
• I can adjust the content style and approach
• You can request specific changes or improvements
• I'll continue learning from your feedback

**What would you like me to focus on?** Let me know your preferences! 🎯
            """
        
        keyboard = [
            [InlineKeyboardButton("📝 Request Different Content", callback_data="request_content")],
            [InlineKeyboardButton("⚙️ Update Preferences", callback_data="update_preferences")],
            [InlineKeyboardButton("💬 Give More Feedback", callback_data="give_feedback")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(response, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_no_subscription_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show message when user has no active subscription"""
        no_subscription_text = """
❌ **No Active Subscription**

You don't have an active subscription to receive personalized content.

**To get started:**
• Choose a subscription plan
• Complete the setup process
• Start receiving personalized content

**Available Plans:**
• 🚀 Extreme Plan - $99/month
• ⚡ 2-Week Plan - $49/month
• 📝 Regular Plan - $19/month

Ready to get started? 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Extreme Plan", callback_data="select_extreme")],
            [InlineKeyboardButton("⚡ 2-Week Plan", callback_data="select_2week")],
            [InlineKeyboardButton("📝 Regular Plan", callback_data="select_regular")],
            [InlineKeyboardButton("❓ Compare Plans", callback_data="compare_plans")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(no_subscription_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_setup_required_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show message when setup is required"""
        setup_text = """
⚠️ **Setup Required**

Your subscription is active, but your preferences haven't been set up yet.

**To receive personalized content:**
• Complete the setup process
• Share your key texts and preferences
• Start receiving customized content

**Setup includes:**
• Writing style preferences
• Content type preferences
• Delivery schedule preferences

Let's get you set up! 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Start Setup", callback_data="start_setup")],
            [InlineKeyboardButton("❓ Learn More", callback_data="learn_setup")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(setup_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_iteration_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show iteration help"""
        help_text = """
❓ **Content and Iteration Help**

Here's how to get the most out of your personalized content:

**Available Commands:**
• "content" - Request new content
• "schedule" - Check your delivery schedule
• "feedback" - Provide feedback on content
• "help" - Show this help message

**Content Types:**
• 📝 Blog posts
• 📱 Social media content
• 📧 Email content
• 📄 Articles

**Feedback Options:**
• 👍 Like content
• 👎 Dislike content
• 💬 Provide detailed feedback
• 🔄 Request different content

**Need More Help?**
Use the buttons below for quick actions! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Request Content", callback_data="request_content")],
            [InlineKeyboardButton("📊 Check Schedule", callback_data="check_schedule")],
            [InlineKeyboardButton("💬 Give Feedback", callback_data="give_feedback")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "request_content":
            await self._handle_content_request(update, context, "content")
        elif query.data == "check_schedule":
            await self._handle_schedule_inquiry(update, context)
        elif query.data == "give_feedback":
            await self._show_feedback_form(update, context)
        elif query.data == "get_help":
            await self._show_iteration_help(update, context)
        elif query.data == "feedback_like":
            await self._handle_feedback(update, context, "like")
        elif query.data == "feedback_dislike":
            await self._handle_feedback(update, context, "dislike")
        elif query.data == "request_another":
            await self._handle_content_request(update, context, "content")
        elif query.data == "change_schedule":
            await self._show_schedule_options(update, context)
        elif query.data == "view_history":
            await self._show_content_history(update, context)
        elif query.data == "update_preferences":
            await self._show_preference_update(update, context)
        elif query.data == "contact_support":
            await self._show_support_contact(update, context)
        elif query.data == "task_movement_done":
            await self._handle_task_movement_done(update, context)
        elif query.data == "task_help":
            await self._show_task_help(update, context)
        elif query.data == "show_progress":
            await self._show_progress_status(update, context)
        elif query.data == "start_checkin":
            await self._start_checkin_response(update, context)
        elif query.data == "start_final_evaluation":
            await self._start_final_evaluation_response(update, context)
        elif query.data == "show_final_progress":
            await self._show_final_progress(update, context)
    
    async def _show_feedback_form(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show feedback form"""
        feedback_text = """
💬 **Provide Feedback**

I'd love to hear your thoughts on the content I've created for you!

**What would you like to share?**
• What you liked about the content
• What could be improved
• Suggestions for future content
• Any other feedback

**Your feedback helps me:**
• Create better content for you
• Understand your preferences
• Improve the personalization

Please share your thoughts! 🎯
        """
        
        await update.callback_query.edit_message_text(feedback_text, parse_mode='Markdown')
    
    async def _show_schedule_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show schedule options"""
        schedule_text = """
📅 **Schedule Options**

You can customize your content delivery schedule:

**Current Options:**
• 📅 Keep current schedule
• ⏰ Change delivery time
• 📊 Adjust frequency
• 🎯 Set specific content types

**Need Help?**
Contact support if you need assistance with scheduling.

**What would you like to change?** 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("⏰ Change Time", callback_data="change_time")],
            [InlineKeyboardButton("📊 Adjust Frequency", callback_data="adjust_frequency")],
            [InlineKeyboardButton("🎯 Set Content Types", callback_data="set_content_types")],
            [InlineKeyboardButton("🔙 Keep Current", callback_data="keep_current_schedule")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(schedule_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_content_history(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show content history"""
        user_id = update.effective_user.id
        
        # Get user's iterations
        iterations = await self.db_manager.get_user_iterations(user_id)
        
        if not iterations:
            history_text = """
📊 **Content History**

No content has been delivered yet.

**Once you start receiving content, this will show:**
• All content delivered to you
• Delivery dates and times
• Content types and topics
• Your feedback and ratings

**To start receiving content:**
• Ensure your subscription is active
• Complete the setup process
• Wait for your first content delivery

**Need Help?**
Contact support if you're not receiving content! 🆘
            """
        else:
            # Format history
            history_text = f"""
📊 **Content History**

**Total Content Delivered:** {len(iterations)}

**Recent Content:**
            """
            
            # Show last 5 iterations
            for i, iteration in enumerate(iterations[:5]):
                history_text += f"""
**{i+1}.** {iteration['content'][:100]}{'...' if len(iteration['content']) > 100 else ''}
   📅 {iteration['sent_at'][:10]} | Status: {iteration['status']}
            """
            
            if len(iterations) > 5:
                history_text += f"\n... and {len(iterations) - 5} more items"
        
        keyboard = [
            [InlineKeyboardButton("📝 Request New Content", callback_data="request_content")],
            [InlineKeyboardButton("📊 Detailed Report", callback_data="detailed_report")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(history_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_preference_update(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show preference update options"""
        preference_text = """
⚙️ **Update Preferences**

You can update your content preferences anytime:

**Available Updates:**
• 📝 Writing style preferences
• 🎯 Content type preferences
• ⏰ Delivery schedule preferences
• 📊 Content length preferences

**How It Works:**
• Your preferences are used to personalize content
• Updates take effect immediately
• You can change preferences anytime

**What would you like to update?** 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Writing Style", callback_data="update_writing_style")],
            [InlineKeyboardButton("🎯 Content Types", callback_data="update_content_types")],
            [InlineKeyboardButton("⏰ Delivery Schedule", callback_data="update_delivery_schedule")],
            [InlineKeyboardButton("📊 Content Length", callback_data="update_content_length")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(preference_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_support_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show support contact information"""
        support_text = """
🆘 **Contact Support**

Need help with your content or subscription? Our support team is here to assist you!

**Contact Methods:**
• 📧 Email: support@yourbot.com
• 💬 Live Chat: Available 24/7
• 📞 Phone: +1 (555) 123-4567
• 🕒 Hours: Monday-Friday, 9 AM - 6 PM EST

**Common Issues:**
• Content not being delivered
• Subscription problems
• Preference updates
• Technical issues

**Response Time:**
• Email: Within 24 hours
• Live Chat: Immediate
• Phone: Immediate during business hours

**We're here to help!** 🤝
        """
        
        keyboard = [
            [InlineKeyboardButton("💬 Start Live Chat", callback_data="start_live_chat")],
            [InlineKeyboardButton("📧 Send Email", callback_data="send_email")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(support_text, parse_mode='Markdown', reply_markup=reply_markup)
