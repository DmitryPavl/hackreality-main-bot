"""
Option Module
Handles subscription plan selection with three main scenarios: Extreme, 2-week, and Regular.
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any
from modules.admin_notifications import admin_notifications

logger = logging.getLogger(__name__)

class OptionModule:
    def __init__(self, db_manager, state_manager, bot_instance=None):
        self.db_manager = db_manager
        self.state_manager = state_manager
        self.bot_instance = bot_instance
        
        # Define goal-oriented subscription plans
        self.subscription_plans = {
            "extreme": {
                "name": "Экстремальный план",
                "duration": "7 дней",
                "price": "₽4,990",
                "approach": "10-15 минут каждые 2-3 часа",
                "result_time": "Результат может быть достигнут в течение недели",
                "features": [
                    "Интенсивная работа над целью",
                    "10-15 минут каждые 2-3 часа",
                    "Максимальная скорость достижения",
                    "Приоритетная поддержка",
                    "Неограниченные правки",
                    "Индивидуальные техники работы с реальностью"
                ],
                "description": "Для тех, кто готов к интенсивной работе и хочет достичь цели максимально быстро."
            },
            "2week": {
                "name": "2-недельный план",
                "duration": "14 дней",
                "price": "₽2,490",
                "approach": "15 минут в день",
                "result_time": "Стабильный прогресс за 2 недели",
                "features": [
                    "Ежедневная работа над целью",
                    "15 минут в день",
                    "Сбалансированный подход",
                    "Стандартная поддержка",
                    "3 правки на контент",
                    "Стандартные техники трансформации"
                ],
                "description": "Отличный выбор для стабильного прогресса в достижении цели."
            },
            "regular": {
                "name": "Обычный план",
                "duration": "30 дней",
                "price": "₽990",
                "approach": "Раз в день, более детальный подход",
                "result_time": "Устойчивый результат за месяц",
                "features": [
                    "Ежедневная работа над целью",
                    "Более детальный и устойчивый подход",
                    "Глубокое погружение в проблему",
                    "Базовая поддержка",
                    "1 правка на контент",
                    "Мягкие техники трансформации"
                ],
                "description": "Идеально для тех, кто предпочитает глубокий и устойчивый подход к достижению цели."
            }
        }
    
    async def start_option_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the goal collection and option selection process"""
        user_id = update.effective_user.id
        
        # Get user profile for personalized greeting
        user_profile = await self.db_manager.get_user_profile(user_id)
        user_name = user_profile.get("first_name", "") if user_profile else ""
        
        # Update user state to goal collection
        await self.db_manager.set_user_state(user_id, "option_selection", {"step": "goal_collection"})
        
        await self._collect_user_goal(update, context, user_name)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages during option selection"""
        user_id = update.effective_user.id
        message_text = update.message.text
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        current_step = user_state_data.get("step", "goal_collection")
        
        if current_step == "goal_collection":
            # Store user's goal and move to plan selection
            await self._process_goal_input(update, context, message_text)
        elif current_step == "plan_selection":
            # Handle plan selection
            message_text_lower = message_text.lower()
            if any(plan in message_text_lower for plan in ["extreme", "экстремальный", "2week", "2-week", "2-недельный", "двухнедельный", "regular", "basic", "обычный", "стандартный"]):
                if "extreme" in message_text_lower or "экстремальный" in message_text_lower:
                    await self._select_plan(update, context, "extreme")
                elif "2week" in message_text_lower or "2-week" in message_text_lower or "2-недельный" in message_text_lower or "двухнедельный" in message_text_lower:
                    await self._select_plan(update, context, "2week")
                elif "regular" in message_text_lower or "basic" in message_text_lower or "обычный" in message_text_lower or "стандартный" in message_text_lower:
                    await self._select_plan(update, context, "regular")
            else:
                # Show help message
                await self._show_help_message(update, context)
        elif current_step == "goal_validation":
            # Handle goal validation response
            await self._process_goal_validation(update, context, message_text)
        elif current_step == "intermediate_goal_collection":
            # Handle intermediate goal input
            await self._process_intermediate_goal(update, context, message_text)
    
    async def _show_plan_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_name: str = ""):
        """Show overview of all available plans"""
        user_id = update.effective_user.id
        
        if user_name:
            greeting = f"Привет, {user_name}! 👋\n\n"
        else:
            greeting = ""
        
        # Get personalized recommendation
        recommendation = await self._get_personalized_recommendation(user_id)
            
        overview_text = f"""
{greeting}💎 **Выбери свой идеальный план трансформации**

Я предлагаю три варианта подписки, разработанные для разных уровней готовности к изменениям:

**🚀 Экстремальный план** - ₽4,990/месяц
• Ежедневный персональный контент
• Максимальная скорость изменений

**⚡ 2-недельный план** - ₽2,490/месяц  
• Контент каждые 2 дня
• Сбалансированный подход

**📝 Обычный план** - ₽990/месяц
• Еженедельная доставка контента
• Мягкое введение в изменения

Каждый план поможет тебе "взломать" свою реальность и достичь мечты! 🎯

{recommendation}

Давай посмотрим детальное сравнение! 👇
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Сравнить планы", callback_data="compare_plans")],
            [InlineKeyboardButton("🚀 Экстремальный", callback_data="plan_extreme")],
            [InlineKeyboardButton("⚡ 2-недельный", callback_data="plan_2week")],
            [InlineKeyboardButton("📝 Обычный", callback_data="plan_regular")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(overview_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_plan_details(self, update: Update, context: ContextTypes.DEFAULT_TYPE, plan_key: str):
        """Show detailed information about a specific plan"""
        plan = self.subscription_plans[plan_key]
        
        features_text = "\n".join([f"✅ {feature}" for feature in plan["features"]])
        
        details_text = f"""
🎯 **{plan['name']}**

💰 **Цена:** {plan['price']} на {plan['duration']}

📋 **Описание:**
{plan['description']}

✨ **Что включено:**
{features_text}

Готов выбрать этот план? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton(f"✅ Выбрать {plan['name']}", callback_data=f"select_{plan_key}")],
            [InlineKeyboardButton("🔙 Назад к планам", callback_data="back_to_plans")],
            [InlineKeyboardButton("❓ Задать вопросы", callback_data="ask_plan_questions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(details_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_plan_comparison(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed comparison of all plans"""
        comparison_text = """
📊 **Сравнение планов**

| Характеристика | Обычный | 2-недельный | Экстремальный |
|----------------|---------|-------------|---------------|
| **Цена** | ₽990 | ₽2,490 | ₽4,990 |
| **Длительность** | 7 дней | 14 дней | 30 дней |
| **Частота** | Еженедельно | Каждые 2 дня | Ежедневно |
| **Поддержка** | Базовая | Стандартная | Приоритетная |
| **Правки** | 1 на контент | 3 на контент | Без ограничений |
| **Шаблоны** | Базовые | Стандартные | Премиум |

**💡 Рекомендации:**
• **Обычный**: Идеально для начинающих и мягкого старта
• **2-недельный**: Отлично для стабильных изменений
• **Экстремальный**: Для тех, кто готов к кардинальным переменам

Какой план тебя больше интересует? 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Обычный план", callback_data="plan_regular")],
            [InlineKeyboardButton("⚡ 2-недельный план", callback_data="plan_2week")],
            [InlineKeyboardButton("🚀 Экстремальный план", callback_data="plan_extreme")],
            [InlineKeyboardButton("🔙 Назад к обзору", callback_data="back_to_overview")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(comparison_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _select_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE, plan_key: str):
        """Handle plan selection"""
        user_id = update.effective_user.id
        plan = self.subscription_plans[plan_key]
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        
        user_goal = user_state_data.get("user_goal", "")
        order_id = user_state_data.get("current_order_id", "")
        
        # Update user state with selected plan
        await self.db_manager.update_user_state_data(user_id, {
            "selected_plan": plan_key,
            "plan_details": plan
        })
        
        # For Extreme and 2-week plans, validate goal realism
        if plan_key in ["extreme", "2week"]:
            await self._validate_goal_realism(update, context, user_goal, plan_key, order_id)
        elif plan_key == "regular":
            # For Regular plan, show development notice
            await self._handle_regular_development(update, context, user_goal, order_id)
        else:
            # For other plans, proceed directly to confirmation
            await self._show_plan_confirmation(update, context, user_goal, plan_key, order_id)
    
    async def _validate_goal_realism(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_goal: str, plan_key: str, order_id: str):
        """Validate if the goal is realistic for the selected plan"""
        user_id = update.effective_user.id
        plan = self.subscription_plans[plan_key]
        
        # Truncate goal for display
        display_goal = user_goal[:80] + "..." if len(user_goal) > 80 else user_goal
        
        validation_text = f"""
🤔 **Важный вопрос о твоей цели**

**Заказ №{order_id}**
🎯 **Твоя цель:** "{display_goal}"
📋 **Выбранный план:** {plan['name']} - {plan['result_time']}

**Скажи честно:** Ты действительно веришь, что эта цель может быть достигнута в нашей вселенной за указанное время?

Если твоя цель кажется слишком амбициозной или нереалистичной, я предлагаю:

**🎯 Установить промежуточную цель** - серьезный шаг к твоей мечте, который:
• Реально достижим за выбранное время
• Даст тебе ощущение реального прогресса
• Приблизит к основной цели
• Покажет, что ты действительно движешься вперед

**Примеры промежуточных целей:**
• Вместо "стать миллионером" → "заработать первые 100,000 рублей"
• Вместо "найти любовь всей жизни" → "пойти на 3 свидания"
• Вместо "стать знаменитым" → "создать контент, который понравится 1000 людям"

**Что ты выберешь?**
1️⃣ Оставить текущую цель
2️⃣ Установить промежуточную цель
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Оставить текущую цель", callback_data="keep_original_goal")],
            [InlineKeyboardButton("🎯 Установить промежуточную", callback_data="set_intermediate_goal")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update state to goal validation
        await self.db_manager.update_user_state_data(user_id, {"step": "goal_validation"})
        
        await update.message.reply_text(validation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_plan_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_goal: str, plan_key: str, order_id: str):
        """Show plan confirmation"""
        user_id = update.effective_user.id
        plan = self.subscription_plans[plan_key]
        
        # Truncate goal for display
        display_goal = user_goal[:80] + "..." if len(user_goal) > 80 else user_goal
        
        confirmation_text = f"""
🎉 **Отличный выбор!**

**Заказ №{order_id}**
🎯 **Цель:** "{display_goal}"
📋 **План:** {plan['name']} - {plan['price']}
⏱️ **Подход:** {plan['approach']}
🎯 **Результат:** {plan['result_time']}

**Что дальше:**
1️⃣ Обработаю платеж безопасно
2️⃣ Начну работать с твоей целью
3️⃣ Буду доставлять персональный контент
4️⃣ Помогу достичь результата!

Готов оплатить и начать работу над целью? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Оплатить и начать", callback_data="confirm_plan")],
            [InlineKeyboardButton("🔙 Изменить план", callback_data="back_to_plans")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(confirmation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _confirm_plan_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm plan selection and move to payment"""
        user_id = update.effective_user.id
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        
        # Use final target goal (could be original or intermediate)
        final_target_goal = user_state_data.get("final_target_goal", user_state_data.get("user_goal", ""))
        order_id = user_state_data.get("current_order_id", "")
        selected_plan = user_state_data.get("selected_plan", "")
        plan_details = user_state_data.get("plan_details", {})
        
        # Create subscription in database with final target goal
        subscription_created = await self.db_manager.create_subscription(
            user_id=user_id,
            order_id=order_id,
            user_goal=final_target_goal,
            subscription_type=selected_plan,
            plan_details=plan_details
        )
        
        if not subscription_created:
            await update.callback_query.edit_message_text(
                "❌ Произошла ошибка при создании заказа. Попробуйте еще раз.",
                parse_mode='Markdown'
            )
            return
        
        # Move to payment phase
        await self.db_manager.set_user_state(user_id, "payment", {
            "order_id": order_id,
            "user_goal": final_target_goal,
            "original_goal": user_state_data.get("original_goal", ""),
            "selected_plan": selected_plan,
            "plan_details": plan_details
        })
        
        confirmation_text = f"""
🎊 **План подтвержден!**

**Заказ №{order_id} готов к оплате!**

Теперь переходим к безопасной оплате, чтобы начать работу над твоей целью.

После подтверждения платежа я сразу начну создавать персональный контент для достижения твоей цели! ✨
        """
        
        await update.callback_query.edit_message_text(confirmation_text, parse_mode='Markdown')
        
        # Import here to avoid circular imports
        from modules.paying import PayingModule
        paying_module = PayingModule(self.db_manager, self.state_manager)
        await paying_module.start_payment(update, context)
    
    async def _show_help_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help message for plan selection"""
        help_text = """
❓ **Нужна помощь с выбором?**

Вот как выбрать план:

**Напиши или нажми:**
• "Экстремальный" или "🚀" для Экстремального плана
• "2-недельный" или "⚡" для 2-недельного плана  
• "Обычный" или "📝" для Обычного плана

**Или используй кнопки ниже, чтобы изучить каждый план подробно!**

О каком плане ты хочешь узнать больше? 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Экстремальный план", callback_data="plan_extreme")],
            [InlineKeyboardButton("⚡ 2-недельный план", callback_data="plan_2week")],
            [InlineKeyboardButton("📝 Обычный план", callback_data="plan_regular")],
            [InlineKeyboardButton("📊 Сравнить все планы", callback_data="compare_plans")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "compare_plans":
            await self._show_plan_comparison(update, context)
        elif query.data == "back_to_plans":
            await self._show_plan_overview(update, context)
        elif query.data == "back_to_overview":
            await self._show_plan_overview(update, context)
        elif query.data.startswith("plan_"):
            plan_key = query.data.split("_")[1]
            await self._show_plan_details(update, context, plan_key)
        elif query.data.startswith("select_"):
            plan_key = query.data.split("_")[1]
            await self._select_plan(update, context, plan_key)
        elif query.data == "confirm_plan":
            await self._confirm_plan_selection(update, context)
        elif query.data == "ask_plan_questions":
            await self._handle_plan_questions(update, context)
    
    async def _handle_plan_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle questions about plans"""
        questions_text = """
❓ **Вопросы и ответы о планах:**

**В: Могу ли я изменить план позже?**
О: Да! Ты можешь повысить или понизить план в любое время.

**В: Что если я не буду доволен?**
О: Мы предлагаем 7-дневную гарантию возврата денег на все планы.

**В: Как работает оплата?**
О: Планы оплачиваются ежемесячно и автоматически продлеваются, если не отменены.

**В: Могу ли я приостановить подписку?**
О: Да, ты можешь приостановить на срок до 30 дней в год.

**В: Какие способы оплаты вы принимаете?**
О: Мы принимаем все основные банковские карты и PayPal.

Готов выбрать план сейчас? 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Экстремальный план", callback_data="plan_extreme")],
            [InlineKeyboardButton("⚡ 2-недельный план", callback_data="plan_2week")],
            [InlineKeyboardButton("📝 Обычный план", callback_data="plan_regular")],
            [InlineKeyboardButton("🔙 Назад к планам", callback_data="back_to_plans")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(questions_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _get_personalized_recommendation(self, user_id: int) -> str:
        """Get personalized plan recommendation based on user profile"""
        user_profile = await self.db_manager.get_user_profile(user_id)
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        
        if not user_profile:
            return ""
        
        age = user_state_data.get("user_age")
        city = user_profile.get("city", "")
        
        recommendation = ""
        
        if age:
            if age < 25:
                recommendation = "💡 **Рекомендация для твоего возраста:** Начни с Обычного плана - он идеально подходит для молодых людей, которые только начинают свой путь трансформации!"
            elif age < 35:
                recommendation = "💡 **Рекомендация для твоего возраста:** 2-недельный план будет отличным выбором - сбалансированный подход для активного периода жизни!"
            else:
                recommendation = "💡 **Рекомендация для твоего возраста:** Экстремальный план поможет максимально эффективно использовать время для кардинальных изменений!"
        
        if city:
            if "москв" in city.lower() or "спб" in city.lower() or "санкт" in city.lower():
                recommendation += "\n\n🏙️ **Для жителей больших городов:** Рекомендую более интенсивные планы - в мегаполисе изменения происходят быстрее!"
            elif "екатеринбург" in city.lower() or "новосибирск" in city.lower() or "красноярск" in city.lower():
                recommendation += "\n\n🌆 **Для региональных центров:** 2-недельный план обеспечит стабильный прогресс!"
        
        return recommendation
    
    async def _collect_user_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_name: str = ""):
        """Collect user's goal"""
        if user_name:
            greeting = f"Привет, {user_name}! 👋\n\n"
        else:
            greeting = ""
            
        goal_text = f"""
{greeting}🎯 **Расскажи мне о своей цели!**

Каждое достижение начинается с четкого понимания того, чего ты хочешь достичь.

**Поделись со мной:**
• Какую цель ты хочешь достичь?
• Что именно ты хочешь изменить в своей жизни?
• Какая мечта кажется тебе сейчас недостижимой?

**Примеры целей:**
• Найти работу мечты
• Построить отношения
• Избавиться от страхов
• Достичь финансовой стабильности
• Найти свое призвание
• Улучшить здоровье

Напиши свою цель, и я помогу тебе выбрать лучший способ ее достижения! 🚀

*Напоминаю: все действия и решения остаются под вашей ответственностью* ⚖️
        """
        
        await update.message.reply_text(goal_text, parse_mode='Markdown')
    
    async def _process_goal_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, goal_text: str):
        """Process user's goal input"""
        user_id = update.effective_user.id
        
        # Store the goal in user state data
        await self.db_manager.update_user_state_data(user_id, {
            "user_goal": goal_text,
            "step": "plan_selection"
        })
        
        # Create a new order/subscription for this goal
        order_id = await self._create_new_order(user_id, goal_text)
        
        # Show plan overview with goal context
        user_profile = await self.db_manager.get_user_profile(user_id)
        user_name = user_profile.get("first_name", "") if user_profile else ""
        
        await self._show_plan_overview_with_goal(update, context, user_name, goal_text, order_id)
    
    async def _create_new_order(self, user_id: int, goal_text: str) -> str:
        """Create a new order/subscription for the goal"""
        import uuid
        from datetime import datetime
        
        order_id = str(uuid.uuid4())[:8]  # Short unique order ID
        
        # Store order information in user state data
        await self.db_manager.update_user_state_data(user_id, {
            "current_order_id": order_id,
            "order_created_at": datetime.now().isoformat(),
            "order_status": "pending_payment"
        })
        
        logger.info(f"Created new order {order_id} for user {user_id} with goal: {goal_text[:50]}...")
        return order_id
    
    async def _show_plan_overview_with_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_name: str, goal_text: str, order_id: str):
        """Show plan overview with user's goal context"""
        user_id = update.effective_user.id
        
        if user_name:
            greeting = f"Отлично, {user_name}! 👋\n\n"
        else:
            greeting = "Отлично! 👋\n\n"
        
        # Get personalized recommendation
        recommendation = await self._get_personalized_recommendation(user_id)
        
        # Truncate goal if too long
        display_goal = goal_text[:100] + "..." if len(goal_text) > 100 else goal_text
            
        overview_text = f"""
{greeting}🎯 **Твоя цель:** "{display_goal}"

💎 **Выбери план для достижения этой цели:**

Я предлагаю три подхода к работе с твоей целью:

**🚀 Экстремальный план** - ₽4,990
• 10-15 минут каждые 2-3 часа
• Результат может быть достигнут в течение недели

**⚡ 2-недельный план** - ₽2,490  
• 15 минут в день
• Стабильный прогресс за 2 недели

**📝 Обычный план** - ₽990
• Раз в день, более детальный подход
• Устойчивый результат за месяц

**Заказ №{order_id}** - каждый план работает только с одной целью до завершения.

{recommendation}

Какой подход тебе больше подходит? 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Сравнить планы", callback_data="compare_plans")],
            [InlineKeyboardButton("🚀 Экстремальный", callback_data="plan_extreme")],
            [InlineKeyboardButton("⚡ 2-недельный", callback_data="plan_2week")],
            [InlineKeyboardButton("📝 Обычный", callback_data="plan_regular")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(overview_text, parse_mode='Markdown', reply_markup=reply_markup)
    async def _process_goal_validation(self, update: Update, context: ContextTypes.DEFAULT_TYPE, response_text: str):
        """Process user's response to goal validation"""
        user_id = update.effective_user.id
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        
        # Check if user wants to set intermediate goal
        if any(word in response_text.lower() for word in ["промежуточную", "альтернативную", "другую", "частичную", "шаг", "часть"]):
            await self._ask_for_intermediate_goal(update, context)
        else:
            # User wants to keep original goal
            await self._keep_original_goal(update, context)
    
    async def _ask_for_intermediate_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Ask user to provide intermediate goal"""
        user_id = update.effective_user.id
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        original_goal = user_state_data.get("user_goal", "")
        
        intermediate_goal_text = f"""
🎯 **Отлично! Давай установим промежуточную цель**

**Твоя основная мечта:** "{original_goal}"

Теперь подумай и напиши **промежуточную цель** - серьезный шаг к твоей мечте, который:

✅ **Реально достижим** за выбранное время
✅ **Даст ощущение прогресса** - ты почувствуешь, что движешься вперед
✅ **Приблизит к основной цели** - это будет важный шаг к мечте
✅ **Мотивирует продолжать** - после достижения захочется идти дальше

**Примеры хороших промежуточных целей:**
• "Найти 3 интересные вакансии и подать заявки"
• "Пойти на 2 свидания с разными людьми"
• "Создать первый контент и получить 100 лайков"
• "Найти 5 способов дополнительного заработка"
• "Начать заниматься спортом 3 раза в неделю"

**Напиши свою промежуточную цель:**
        """
        
        # Update state to intermediate goal collection
        await self.db_manager.update_user_state_data(user_id, {"step": "intermediate_goal_collection"})
        
        await update.message.reply_text(intermediate_goal_text, parse_mode='Markdown')
    
    async def _keep_original_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Keep the original goal and proceed to confirmation"""
        user_id = update.effective_user.id
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        
        user_goal = user_state_data.get("user_goal", "")
        selected_plan = user_state_data.get("selected_plan", "")
        order_id = user_state_data.get("current_order_id", "")
        
        # Store final target goal (same as original)
        await self.db_manager.update_user_state_data(user_id, {
            "final_target_goal": user_goal,
            "step": "plan_selection"
        })
        
        # Show plan confirmation
        await self._show_plan_confirmation(update, context, user_goal, selected_plan, order_id)
    
    async def _process_intermediate_goal(self, update: Update, context: ContextTypes.DEFAULT_TYPE, intermediate_goal: str):
        """Process intermediate goal input"""
        user_id = update.effective_user.id
        user_state_data = await self.db_manager.get_user_state_data(user_id)
        
        original_goal = user_state_data.get("user_goal", "")
        selected_plan = user_state_data.get("selected_plan", "")
        order_id = user_state_data.get("current_order_id", "")
        
        # Store final target goal (intermediate goal becomes the target)
        await self.db_manager.update_user_state_data(user_id, {
            "final_target_goal": intermediate_goal,
            "original_goal": original_goal,  # Keep original for reference
            "step": "plan_selection"
        })
        
        # Show plan confirmation with intermediate goal
        await self._show_plan_confirmation(update, context, intermediate_goal, selected_plan, order_id)
    
    async def _handle_regular_development(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_goal: str, order_id: str):
        """Handle Regular plan development notice"""
        user_id = update.effective_user.id
        user_profile = await self.db_manager.get_user_profile(user_id)
        user_name = user_profile.get("first_name", "") if user_profile else ""
        
        # Truncate goal for display
        display_goal = user_goal[:80] + "..." if len(user_goal) > 80 else user_goal
        
        development_text = f"""
🚧 **Обычный план в разработке**

**Заказ №{order_id}**
🎯 **Твоя цель:** "{display_goal}"

К сожалению, **Обычный план** сейчас находится в процессе разработки и пока недоступен.

**Что это означает:**
• Мы работаем над созданием более детального и устойчивого подхода
• План будет включать глубокую работу с твоей целью
• Ожидаем запуск в ближайшее время

**Твоя заявка сохранена!** 📝
Мы уведомили администратора о твоем интересе к Обычному плану.

**Пока что предлагаем выбрать один из доступных планов:**

**🚀 Экстремальный план** - ₽4,990
• 10-15 минут каждые 2-3 часа
• Результат может быть достигнут в течение недели

**⚡ 2-недельный план** - ₽2,490
• 15 минут в день
• Стабильный прогресс за 2 недели

Какой план тебе больше подходит? 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Экстремальный план", callback_data="plan_extreme")],
            [InlineKeyboardButton("⚡ 2-недельный план", callback_data="plan_2week")],
            [InlineKeyboardButton("🔙 Назад к планам", callback_data="back_to_plans")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Send notification to admin
        await admin_notifications.notify_regular_plan_request(user_id, user_name, user_goal, order_id)
        
        # Reset to plan selection step
        await self.db_manager.update_user_state_data(user_id, {"step": "plan_selection"})
        
        await update.message.reply_text(development_text, parse_mode='Markdown', reply_markup=reply_markup)
    
