"""
Paying Module
Handles payment processing and subscription activation.
"""

import logging
import uuid
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any
from modules.admin_notifications import admin_notifications

logger = logging.getLogger(__name__)

class PayingModule:
    def __init__(self, db_manager, state_manager, bot_instance=None):
        self.db_manager = db_manager
        self.state_manager = state_manager
        self.bot_instance = bot_instance
        
        # Payment methods (simplified for demo)
        self.payment_methods = {
            "stripe": {
                "name": "Credit/Debit Card",
                "description": "Pay securely with Stripe",
                "icon": "💳"
            },
            "paypal": {
                "name": "PayPal",
                "description": "Pay with your PayPal account",
                "icon": "🅿️"
            },
            "crypto": {
                "name": "Cryptocurrency",
                "description": "Pay with Bitcoin or Ethereum",
                "icon": "₿"
            }
        }
    
    async def start_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the donation process"""
        user_id = update.effective_user.id
        
        # Get user's selected plan and goal
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan")
        user_goal = state_data.get("user_goal", "")
        final_target_goal = state_data.get("final_target_goal", user_goal)
        order_id = state_data.get("order_id", "")
        
        if not selected_plan:
            await self._handle_missing_plan(update, context)
            return
        
        # Get plan details
        plan_details = state_data.get("plan_details", {})
        
        await self._show_donation_request(update, context, selected_plan, plan_details, final_target_goal, order_id)
    
    async def _show_donation_request(self, update: Update, context: ContextTypes.DEFAULT_TYPE, plan_key: str, plan_details: Dict[str, Any], target_goal: str, order_id: str):
        """Show donation request with T-bank details"""
        user_id = update.effective_user.id
        
        # Truncate goal for display
        display_goal = target_goal[:100] + "..." if len(target_goal) > 100 else target_goal
        
        donation_text = f"""
💳 **Поддержка проекта HackReality**

**Заказ №{order_id}**
🎯 **Твоя цель:** "{display_goal}"
📋 **Выбранный план:** {plan_details.get('name', 'Unknown Plan')}
💰 **Сумма:** {plan_details.get('price', 'Unknown')}

**Для достижения твоей цели мне нужна твоя поддержка!**

🤖 **Как это работает:**
• Ты делаешь донат на указанный номер
• Я получаю уведомление о поддержке
• Сразу начинаю работать с твоей целью
• Помогаю тебе достичь результата!

**📱 Способ поддержки:**
**Т-Банк на номер:** `+79853659487`

**💡 Инструкция:**
1. Открой приложение Т-Банк
2. Выбери "Перевести"
3. Введи номер: `+79853659487`
4. Укажи сумму: {plan_details.get('price', 'согласно выбранному плану')}
5. Добавь комментарий: "Заказ {order_id}"
6. Подтверди перевод

**После перевода:**
• Нажми кнопку "Донат сделан" ниже
• Я проверю получение поддержки
• Начну работать с твоей целью!

Готов поддержать проект? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Донат сделан", callback_data="donation_made")],
            [InlineKeyboardButton("❓ Вопросы о донате", callback_data="donation_questions")],
            [InlineKeyboardButton("🔙 Изменить план", callback_data="change_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "donation_requested",
            "selected_plan": plan_key,
            "plan_details": plan_details,
            "target_goal": target_goal,
            "order_id": order_id
        })
        
        await update.message.reply_text(donation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages during donation process"""
        user_id = update.effective_user.id
        message_text = update.message.text.lower()
        
        # Get current payment state
        state_data = await self.db_manager.get_user_state_data(user_id)
        payment_state = state_data.get("payment_state", "overview")
        
        if payment_state == "donation_requested":
            # Check if user is confirming donation
            if any(word in message_text for word in ["сделан", "готов", "перевел", "отправил", "донат"]):
                await self._handle_donation_confirmation(update, context)
            else:
                await self._show_donation_help(update, context)
        else:
            await self._show_donation_help(update, context)
    
    async def _handle_donation_confirmation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle user's donation confirmation"""
        user_id = update.effective_user.id
        user_profile = await self.db_manager.get_user_profile(user_id)
        user_name = user_profile.get("first_name", "") if user_profile else ""
        
        # Get order details
        state_data = await self.db_manager.get_user_state_data(user_id)
        order_id = state_data.get("order_id", "")
        target_goal = state_data.get("target_goal", "")
        plan_details = state_data.get("plan_details", {})
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "donation_confirmed",
            "donation_confirmed_at": datetime.now().isoformat()
        })
        
        # Send admin notification
        await admin_notifications.notify_donation_confirmation(user_id, user_name, order_id, target_goal, plan_details)
        
        # Show waiting message to user
        waiting_text = f"""
⏳ **Проверяем получение поддержки...**

**Заказ №{order_id}**

Спасибо за подтверждение! Я уведомил администратора о твоем донате.

**Что происходит сейчас:**
• 📤 Отправлено уведомление администратору
• 🔍 Проверяется получение поддержки
• ⏰ Ожидаем подтверждение

**Обычно это занимает несколько минут.**

Как только администратор подтвердит получение поддержки, я сразу начну работать с твоей целью!

**Твоя цель:** "{target_goal[:80]}{'...' if len(target_goal) > 80 else ''}"

Ожидай подтверждения... 🤖
        """
        
        await update.message.reply_text(waiting_text, parse_mode='Markdown')
    
    
    async def _show_donation_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show donation help"""
        help_text = """
❓ **Помощь с донатом**

**Как сделать донат:**
1. Открой приложение Т-Банк
2. Выбери "Перевести"
3. Введи номер: `+79853659487`
4. Укажи нужную сумму
5. Добавь комментарий с номером заказа
6. Подтверди перевод

**После перевода:**
• Нажми кнопку "Донат сделан"
• Или напиши "готов", "сделан", "перевел"

**Нужна помощь?**
• Проверь правильность номера
• Убедись, что сумма указана верно
• Добавь комментарий с номером заказа

Готов сделать донат? 💳
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Донат сделан", callback_data="donation_made")],
            [InlineKeyboardButton("❓ Вопросы о донате", callback_data="donation_questions")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_donation_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show donation questions and answers"""
        questions_text = """
❓ **Вопросы о донате:**

**В: Как сделать донат?**
О: Открой Т-Банк → "Перевести" → введи номер +79853659487 → укажи сумму → добавь комментарий с номером заказа.

**В: Безопасно ли это?**
О: Да! Т-Банк - это официальное приложение банка с защитой данных.

**В: Что если я ошибся с суммой?**
О: Напиши администратору, и мы решим вопрос индивидуально.

**В: Когда начнется работа над целью?**
О: Как только администратор подтвердит получение доната.

**В: Можно ли отменить донат?**
О: Если донат еще не подтвержден, можно отменить. После подтверждения - работа начинается.

**В: Что если донат не дошел?**
О: Администратор проверит и сообщит. Если донат не получен, можно повторить.

Готов сделать донат? 💳
        """
        
        keyboard = [
            [InlineKeyboardButton("✅ Донат сделан", callback_data="donation_made")],
            [InlineKeyboardButton("🔙 Назад к донату", callback_data="back_to_donation")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(questions_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_payment_overview(self, update: Update, context: ContextTypes.DEFAULT_TYPE, plan_key: str, plan_details: Dict[str, Any]):
        """Show payment overview"""
        user_id = update.effective_user.id
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "overview",
            "selected_plan": plan_key,
            "plan_details": plan_details
        })
        
        overview_text = f"""
💳 **Payment Overview**

**Selected Plan:** {plan_details.get('name', 'Unknown Plan')}
**Duration:** {plan_details.get('duration', 'Unknown')}
**Price:** {plan_details.get('price', 'Unknown')}

**What's Included:**
{chr(10).join([f"✅ {feature}" for feature in plan_details.get('features', [])])}

**Payment Methods Available:**
• 💳 Credit/Debit Card (Stripe)
• 🅿️ PayPal
• ₿ Cryptocurrency

Ready to proceed with payment? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay with Card", callback_data="pay_stripe")],
            [InlineKeyboardButton("🅿️ Pay with PayPal", callback_data="pay_paypal")],
            [InlineKeyboardButton("₿ Pay with Crypto", callback_data="pay_crypto")],
            [InlineKeyboardButton("❓ Payment Questions", callback_data="payment_questions")],
            [InlineKeyboardButton("🔙 Change Plan", callback_data="change_plan")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(overview_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_payment_method_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Process payment method selection"""
        user_id = update.effective_user.id
        
        # Simple keyword-based payment method detection
        if any(word in message_text for word in ["card", "credit", "debit", "stripe"]):
            await self._start_stripe_payment(update, context)
        elif any(word in message_text for word in ["paypal", "pay pal"]):
            await self._start_paypal_payment(update, context)
        elif any(word in message_text for word in ["crypto", "bitcoin", "ethereum", "btc", "eth"]):
            await self._start_crypto_payment(update, context)
        else:
            await self._show_payment_method_help(update, context)
    
    async def _start_stripe_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start Stripe payment process"""
        user_id = update.effective_user.id
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "stripe_payment",
            "payment_method": "stripe"
        })
        
        stripe_text = """
💳 **Stripe Payment**

You've chosen to pay with a credit or debit card. This is processed securely through Stripe.

**Payment Details:**
• Secure SSL encryption
• PCI DSS compliant
• No card details stored on our servers
• Instant payment processing

**To proceed:**
1. Click the payment button below
2. Enter your card details securely
3. Complete the payment
4. Your subscription will be activated immediately

Ready to pay? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay Now with Stripe", callback_data="process_stripe_payment")],
            [InlineKeyboardButton("🔙 Choose Different Method", callback_data="back_to_payment_methods")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(stripe_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_paypal_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start PayPal payment process"""
        user_id = update.effective_user.id
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "paypal_payment",
            "payment_method": "paypal"
        })
        
        paypal_text = """
🅿️ **PayPal Payment**

You've chosen to pay with PayPal. This is processed securely through PayPal's platform.

**Payment Details:**
• Secure PayPal authentication
• Buyer protection included
• No need to share card details
• Instant payment processing

**To proceed:**
1. Click the payment button below
2. Log in to your PayPal account
3. Complete the payment
4. Your subscription will be activated immediately

Ready to pay? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("🅿️ Pay Now with PayPal", callback_data="process_paypal_payment")],
            [InlineKeyboardButton("🔙 Choose Different Method", callback_data="back_to_payment_methods")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(paypal_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_crypto_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start cryptocurrency payment process"""
        user_id = update.effective_user.id
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "crypto_payment",
            "payment_method": "crypto"
        })
        
        crypto_text = """
₿ **Cryptocurrency Payment**

You've chosen to pay with cryptocurrency. We accept Bitcoin and Ethereum.

**Payment Details:**
• Decentralized and secure
• Lower fees than traditional methods
• Privacy-focused
• Instant blockchain confirmation

**To proceed:**
1. Click the payment button below
2. Choose your cryptocurrency
3. Send payment to the provided address
4. Your subscription will be activated after confirmation

Ready to pay? 🚀
        """
        
        keyboard = [
            [InlineKeyboardButton("₿ Pay with Bitcoin", callback_data="process_btc_payment")],
            [InlineKeyboardButton("Ξ Pay with Ethereum", callback_data="process_eth_payment")],
            [InlineKeyboardButton("🔙 Choose Different Method", callback_data="back_to_payment_methods")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(crypto_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _process_payment(self, update: Update, context: ContextTypes.DEFAULT_TYPE, payment_method: str):
        """Process the actual payment (simulated)"""
        user_id = update.effective_user.id
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "processing",
            "payment_method": payment_method
        })
        
        # Simulate payment processing
        processing_text = """
⏳ **Processing Payment...**

Please wait while we process your payment. This usually takes a few seconds.

**Status:** Processing...
**Method:** {payment_method}
**Time:** {current_time}

Do not close this chat or navigate away during processing.
        """.format(
            payment_method=payment_method.title(),
            current_time=datetime.now().strftime("%H:%M:%S")
        )
        
        await update.callback_query.edit_message_text(processing_text, parse_mode='Markdown')
        
        # Simulate payment processing delay
        import asyncio
        await asyncio.sleep(2)
        
        # Simulate successful payment
        await self._handle_payment_success(update, context, payment_method)
    
    async def _handle_payment_success(self, update: Update, context: ContextTypes.DEFAULT_TYPE, payment_method: str):
        """Handle successful payment"""
        user_id = update.effective_user.id
        
        # Get plan details
        state_data = await self.db_manager.get_user_state_data(user_id)
        selected_plan = state_data.get("selected_plan")
        plan_details = state_data.get("plan_details", {})
        
        # Generate payment ID
        payment_id = str(uuid.uuid4())
        
        # Create subscription
        subscription_id = await self.db_manager.create_subscription(
            user_id, selected_plan, payment_id
        )
        
        # Update user state to active
        await self.db_manager.set_user_state(user_id, "active", {
            "subscription_id": subscription_id,
            "payment_method": payment_method,
            "payment_id": payment_id
        })
        
        success_text = f"""
🎉 **Payment Successful!**

**Payment Details:**
• Method: {payment_method.title()}
• Plan: {plan_details.get('name', 'Unknown')}
• Payment ID: {payment_id[:8]}...
• Status: ✅ Confirmed

**Your subscription is now active!** 🚀

I'll start creating personalized content for you based on your preferences and key texts. You'll receive your first content soon!

**What's Next:**
• Your subscription is active
• I'll analyze your key texts
• Content will be delivered according to your plan
• You can check your status anytime with /status

Welcome to your personalized content journey! ✨
        """
        
        keyboard = [
            [InlineKeyboardButton("🎯 Start Receiving Content", callback_data="start_content")],
            [InlineKeyboardButton("📊 Check Status", callback_data="check_status")],
            [InlineKeyboardButton("❓ Get Help", callback_data="get_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(success_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_payment_failure(self, update: Update, context: ContextTypes.DEFAULT_TYPE, error_message: str):
        """Handle payment failure"""
        user_id = update.effective_user.id
        
        # Update payment state
        await self.db_manager.update_user_state_data(user_id, {
            "payment_state": "failed",
            "payment_error": error_message
        })
        
        failure_text = f"""
❌ **Payment Failed**

We encountered an issue processing your payment:

**Error:** {error_message}

**What you can do:**
• Try a different payment method
• Check your payment details
• Contact support if the problem persists

Let's try again! 🔄
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Try Again", callback_data="retry_payment")],
            [InlineKeyboardButton("💳 Different Method", callback_data="back_to_payment_methods")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(failure_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_payment_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment help"""
        help_text = """
❓ **Payment Help**

I'm here to help you complete your payment! Here's what you can do:

**Payment Methods:**
• 💳 Credit/Debit Card (Stripe)
• 🅿️ PayPal
• ₿ Cryptocurrency

**Common Issues:**
• Check your card details
• Ensure sufficient funds
• Verify your PayPal account
• Check cryptocurrency balance

**Need Support?**
Contact our support team for assistance with payment issues.

Use the buttons below or type your payment method! 💳
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay with Card", callback_data="pay_stripe")],
            [InlineKeyboardButton("🅿️ Pay with PayPal", callback_data="pay_paypal")],
            [InlineKeyboardButton("₿ Pay with Crypto", callback_data="pay_crypto")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_payment_method_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment method help"""
        help_text = """
💳 **Payment Method Help**

Please choose one of the following payment methods:

**Type or click:**
• "Card" or "💳" for Credit/Debit Card
• "PayPal" or "🅿️" for PayPal
• "Crypto" or "₿" for Cryptocurrency

**Or use the buttons below to select your preferred method!**

Which payment method would you like to use? 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Credit/Debit Card", callback_data="pay_stripe")],
            [InlineKeyboardButton("🅿️ PayPal", callback_data="pay_paypal")],
            [InlineKeyboardButton("₿ Cryptocurrency", callback_data="pay_crypto")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_missing_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle case where no plan is selected"""
        missing_plan_text = """
❌ **No Plan Selected**

It looks like you haven't selected a subscription plan yet. Let's go back and choose a plan first.

**Available Plans:**
• 🚀 Extreme Plan - $99/month
• ⚡ 2-Week Plan - $49/month
• 📝 Regular Plan - $19/month

Let's select your plan! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Extreme Plan", callback_data="select_extreme")],
            [InlineKeyboardButton("⚡ 2-Week Plan", callback_data="select_2week")],
            [InlineKeyboardButton("📝 Regular Plan", callback_data="select_regular")],
            [InlineKeyboardButton("🔙 Back to Plans", callback_data="back_to_plans")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(missing_plan_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "donation_made":
            await self._handle_donation_confirmation(update, context)
        elif query.data == "donation_questions":
            await self._show_donation_questions(update, context)
        elif query.data == "pay_stripe":
            await self._start_stripe_payment(update, context)
        elif query.data == "pay_paypal":
            await self._start_paypal_payment(update, context)
        elif query.data == "pay_crypto":
            await self._start_crypto_payment(update, context)
        elif query.data == "process_stripe_payment":
            await self._process_payment(update, context, "stripe")
        elif query.data == "process_paypal_payment":
            await self._process_payment(update, context, "paypal")
        elif query.data == "process_btc_payment":
            await self._process_payment(update, context, "bitcoin")
        elif query.data == "process_eth_payment":
            await self._process_payment(update, context, "ethereum")
        elif query.data == "back_to_payment_methods":
            await self._show_payment_overview(update, context, "selected_plan", {})
        elif query.data == "retry_payment":
            await self._show_payment_overview(update, context, "selected_plan", {})
        elif query.data == "payment_questions":
            await self._show_payment_questions(update, context)
        elif query.data == "contact_support":
            await self._show_support_contact(update, context)
        elif query.data == "start_content":
            await self._start_content_delivery(update, context)
        elif query.data == "check_status":
            await self._check_user_status(update, context)
        elif query.data == "get_help":
            await self._show_help(update, context)
    
    async def _show_payment_questions(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show payment questions and answers"""
        questions_text = """
❓ **Payment Questions & Answers:**

**Q: Is my payment secure?**
A: Yes! All payments are processed through secure, encrypted channels.

**Q: What payment methods do you accept?**
A: We accept credit/debit cards, PayPal, and major cryptocurrencies.

**Q: When will my subscription start?**
A: Your subscription starts immediately after successful payment.

**Q: Can I get a refund?**
A: Yes, we offer a 7-day money-back guarantee.

**Q: How often will I be charged?**
A: Subscriptions are billed monthly and auto-renew unless cancelled.

**Q: Can I change my plan later?**
A: Yes! You can upgrade or downgrade your plan at any time.

Ready to proceed with payment? 💳
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay with Card", callback_data="pay_stripe")],
            [InlineKeyboardButton("🅿️ Pay with PayPal", callback_data="pay_paypal")],
            [InlineKeyboardButton("₿ Pay with Crypto", callback_data="pay_crypto")],
            [InlineKeyboardButton("🔙 Back to Payment", callback_data="back_to_payment_methods")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(questions_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_support_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show support contact information"""
        support_text = """
🆘 **Contact Support**

Need help with your payment? Our support team is here to assist you!

**Contact Methods:**
• 📧 Email: support@yourbot.com
• 💬 Live Chat: Available 24/7
• 📞 Phone: +1 (555) 123-4567
• 🕒 Hours: Monday-Friday, 9 AM - 6 PM EST

**Common Issues:**
• Payment declined
• Subscription not activated
• Billing questions
• Technical problems

**Response Time:**
• Email: Within 24 hours
• Live Chat: Immediate
• Phone: Immediate during business hours

We're here to help! 🤝
        """
        
        keyboard = [
            [InlineKeyboardButton("💬 Start Live Chat", callback_data="start_live_chat")],
            [InlineKeyboardButton("📧 Send Email", callback_data="send_email")],
            [InlineKeyboardButton("🔙 Back to Payment", callback_data="back_to_payment_methods")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(support_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _start_content_delivery(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start content delivery process"""
        start_text = """
🎯 **Content Delivery Started!**

Great! I'm now analyzing your key texts and preferences to create personalized content for you.

**What's Happening:**
• 🔍 Analyzing your writing style
• 🎨 Creating personalized content
• ⏰ Scheduling delivery according to your plan
• ✨ Optimizing for your preferences

**Your First Content:**
You'll receive your first personalized content within the next few hours!

**Stay Tuned:**
• Check your messages regularly
• Provide feedback to improve content
• Use /status to check your subscription

Welcome to your personalized content journey! 🚀
        """
        
        await update.callback_query.edit_message_text(start_text, parse_mode='Markdown')
    
    async def _check_user_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check user status"""
        user_id = update.effective_user.id
        
        # Get user's active subscription
        subscription = await self.db_manager.get_active_subscription(user_id)
        
        if subscription:
            status_text = f"""
📊 **Your Status**

**Subscription:** {subscription['subscription_type'].title()} Plan
**Status:** ✅ Active
**Start Date:** {subscription['start_date']}
**End Date:** {subscription['end_date']}
**Payment Method:** {subscription.get('payment_id', 'Unknown')}

**Next Steps:**
• Content delivery is active
• Check your messages for new content
• Provide feedback to improve quality

Everything looks great! 🎉
            """
        else:
            status_text = """
📊 **Your Status**

**Subscription:** No active subscription
**Status:** ❌ Inactive

**To activate:**
• Complete the payment process
• Choose a subscription plan
• Set up your preferences

Let's get you started! 🚀
            """
        
        await update.callback_query.edit_message_text(status_text, parse_mode='Markdown')
    
    async def _show_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show help information"""
        help_text = """
❓ **Help & Support**

**Available Commands:**
• /start - Begin the bot setup
• /help - Show this help message
• /status - Check your subscription status

**Bot Features:**
• Personalized content creation
• Multiple subscription plans
• Secure payment processing
• 24/7 support

**Need More Help?**
• Contact support for technical issues
• Check our FAQ for common questions
• Use the buttons below for quick actions

How can I help you today? 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Check Status", callback_data="check_status")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("❓ FAQ", callback_data="show_faq")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
