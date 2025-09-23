"""
Subscription Check Module
Handles subscription status checking, renewal, and management.
"""

import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class SubscriptionModule:
    def __init__(self, db_manager, state_manager):
        self.db_manager = db_manager
        self.state_manager = state_manager
    
    async def check_user_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int = None):
        """Check user's subscription status"""
        if user_id is None:
            user_id = update.effective_user.id
        
        # Get user's active subscription
        subscription = await self.db_manager.get_active_subscription(user_id)
        
        if subscription:
            await self._show_active_subscription(update, context, subscription)
        else:
            await self._show_no_subscription(update, context)
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle messages related to subscription management"""
        user_id = update.effective_user.id
        message_text = update.message.text.lower()
        
        # Check for subscription-related keywords
        if any(word in message_text for word in ["status", "subscription", "plan", "billing"]):
            await self.check_user_status(update, context, user_id)
        elif any(word in message_text for word in ["renew", "extend", "upgrade", "downgrade"]):
            await self._handle_subscription_change(update, context, message_text)
        elif any(word in message_text for word in ["cancel", "stop", "end"]):
            await self._handle_subscription_cancellation(update, context)
        else:
            await self._show_subscription_help(update, context)
    
    async def _show_active_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE, subscription: Dict[str, Any]):
        """Show active subscription details"""
        user_id = update.effective_user.id
        
        # Calculate days remaining
        end_date = datetime.fromisoformat(subscription['end_date'].replace('Z', '+00:00'))
        days_remaining = (end_date - datetime.now()).days
        
        # Determine status color and message
        if days_remaining > 7:
            status_emoji = "✅"
            status_text = "Active"
        elif days_remaining > 0:
            status_emoji = "⚠️"
            status_text = "Expires Soon"
        else:
            status_emoji = "❌"
            status_text = "Expired"
        
        subscription_text = f"""
📊 **Your Subscription Status**

{status_emoji} **Status:** {status_text}
📋 **Plan:** {subscription['subscription_type'].title()} Plan
📅 **Start Date:** {subscription['start_date'][:10]}
📅 **End Date:** {subscription['end_date'][:10]}
⏰ **Days Remaining:** {days_remaining} days
💳 **Payment ID:** {subscription.get('payment_id', 'N/A')[:8]}...

**Plan Features:**
{self._get_plan_features(subscription['subscription_type'])}

**Actions Available:**
• View detailed billing information
• Upgrade or downgrade your plan
• Manage payment methods
• Download usage reports
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Detailed Status", callback_data="detailed_status")],
            [InlineKeyboardButton("🔄 Change Plan", callback_data="change_plan")],
            [InlineKeyboardButton("💳 Billing Info", callback_data="billing_info")],
            [InlineKeyboardButton("📈 Usage Report", callback_data="usage_report")],
            [InlineKeyboardButton("❌ Cancel Subscription", callback_data="cancel_subscription")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(subscription_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_no_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show message when user has no active subscription"""
        no_subscription_text = """
📊 **No Active Subscription**

You don't have an active subscription at the moment.

**Available Plans:**
• 🚀 **Extreme Plan** - $99/month
  Daily personalized content with premium features

• ⚡ **2-Week Plan** - $49/month
  Content every 2 days with standard features

• 📝 **Regular Plan** - $19/month
  Weekly content delivery with essential features

**Ready to get started?**
Choose a plan that fits your needs! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("🚀 Extreme Plan", callback_data="select_extreme")],
            [InlineKeyboardButton("⚡ 2-Week Plan", callback_data="select_2week")],
            [InlineKeyboardButton("📝 Regular Plan", callback_data="select_regular")],
            [InlineKeyboardButton("❓ Compare Plans", callback_data="compare_plans")],
            [InlineKeyboardButton("🆘 Need Help?", callback_data="subscription_help")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(no_subscription_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_subscription_change(self, update: Update, context: ContextTypes.DEFAULT_TYPE, message_text: str):
        """Handle subscription changes (upgrade/downgrade)"""
        user_id = update.effective_user.id
        
        # Get current subscription
        current_subscription = await self.db_manager.get_active_subscription(user_id)
        
        if not current_subscription:
            await self._show_no_subscription(update, context)
            return
        
        # Determine change type
        if any(word in message_text for word in ["upgrade", "higher", "more"]):
            await self._show_upgrade_options(update, context, current_subscription)
        elif any(word in message_text for word in ["downgrade", "lower", "less"]):
            await self._show_downgrade_options(update, context, current_subscription)
        else:
            await self._show_change_options(update, context, current_subscription)
    
    async def _show_upgrade_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_subscription: Dict[str, Any]):
        """Show upgrade options"""
        current_plan = current_subscription['subscription_type']
        
        if current_plan == "regular":
            upgrade_text = """
⬆️ **Upgrade Your Plan**

You're currently on the **Regular Plan**. Here are your upgrade options:

**🚀 Extreme Plan - $99/month**
• Daily personalized content
• Priority support
• Advanced customization
• Unlimited revisions
• Premium templates

**⚡ 2-Week Plan - $49/month**
• Content every 2 days
• Standard support
• Good customization
• 3 revisions per content
• Standard templates

**Benefits of Upgrading:**
• More frequent content delivery
• Better support and features
• Higher quality customization
• More revision options

Ready to upgrade? 🚀
            """
            
            keyboard = [
                [InlineKeyboardButton("🚀 Upgrade to Extreme", callback_data="upgrade_extreme")],
                [InlineKeyboardButton("⚡ Upgrade to 2-Week", callback_data="upgrade_2week")],
                [InlineKeyboardButton("🔙 Keep Current Plan", callback_data="keep_current")]
            ]
        
        elif current_plan == "2week":
            upgrade_text = """
⬆️ **Upgrade Your Plan**

You're currently on the **2-Week Plan**. Here's your upgrade option:

**🚀 Extreme Plan - $99/month**
• Daily personalized content
• Priority support
• Advanced customization
• Unlimited revisions
• Premium templates

**Benefits of Upgrading:**
• Daily content delivery
• Priority support
• Advanced customization
• Unlimited revisions
• Premium templates

Ready to upgrade? 🚀
            """
            
            keyboard = [
                [InlineKeyboardButton("🚀 Upgrade to Extreme", callback_data="upgrade_extreme")],
                [InlineKeyboardButton("🔙 Keep Current Plan", callback_data="keep_current")]
            ]
        
        else:  # extreme plan
            upgrade_text = """
⬆️ **You're Already on the Top Plan!**

You're currently on the **Extreme Plan**, which is our highest tier.

**Your Current Benefits:**
• Daily personalized content
• Priority support
• Advanced customization
• Unlimited revisions
• Premium templates

**No upgrades available** - you're already getting the best! 🎉

Is there anything else I can help you with? 🤔
            """
            
            keyboard = [
                [InlineKeyboardButton("📊 View Status", callback_data="detailed_status")],
                [InlineKeyboardButton("💳 Billing Info", callback_data="billing_info")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(upgrade_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_downgrade_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_subscription: Dict[str, Any]):
        """Show downgrade options"""
        current_plan = current_subscription['subscription_type']
        
        if current_plan == "extreme":
            downgrade_text = """
⬇️ **Downgrade Your Plan**

You're currently on the **Extreme Plan**. Here are your downgrade options:

**⚡ 2-Week Plan - $49/month**
• Content every 2 days
• Standard support
• Good customization
• 3 revisions per content
• Standard templates

**📝 Regular Plan - $19/month**
• Weekly content delivery
• Basic support
• Essential customization
• 1 revision per content
• Basic templates

**⚠️ Important Notes:**
• Downgrading will reduce your content frequency
• Some features may not be available
• Changes take effect at your next billing cycle

Ready to downgrade? ⚠️
            """
            
            keyboard = [
                [InlineKeyboardButton("⚡ Downgrade to 2-Week", callback_data="downgrade_2week")],
                [InlineKeyboardButton("📝 Downgrade to Regular", callback_data="downgrade_regular")],
                [InlineKeyboardButton("🔙 Keep Current Plan", callback_data="keep_current")]
            ]
        
        elif current_plan == "2week":
            downgrade_text = """
⬇️ **Downgrade Your Plan**

You're currently on the **2-Week Plan**. Here's your downgrade option:

**📝 Regular Plan - $19/month**
• Weekly content delivery
• Basic support
• Essential customization
• 1 revision per content
• Basic templates

**⚠️ Important Notes:**
• Downgrading will reduce your content frequency
• Some features may not be available
• Changes take effect at your next billing cycle

Ready to downgrade? ⚠️
            """
            
            keyboard = [
                [InlineKeyboardButton("📝 Downgrade to Regular", callback_data="downgrade_regular")],
                [InlineKeyboardButton("🔙 Keep Current Plan", callback_data="keep_current")]
            ]
        
        else:  # regular plan
            downgrade_text = """
⬇️ **You're Already on the Basic Plan!**

You're currently on the **Regular Plan**, which is our most basic tier.

**Your Current Benefits:**
• Weekly content delivery
• Basic support
• Essential customization
• 1 revision per content
• Basic templates

**No downgrades available** - you're already on the basic plan! 📝

Would you like to upgrade instead? 🚀
            """
            
            keyboard = [
                [InlineKeyboardButton("🚀 Upgrade to Extreme", callback_data="upgrade_extreme")],
                [InlineKeyboardButton("⚡ Upgrade to 2-Week", callback_data="upgrade_2week")],
                [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(downgrade_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_change_options(self, update: Update, context: ContextTypes.DEFAULT_TYPE, current_subscription: Dict[str, Any]):
        """Show general change options"""
        current_plan = current_subscription['subscription_type']
        
        change_text = f"""
🔄 **Change Your Plan**

You're currently on the **{current_plan.title()} Plan**.

**What would you like to do?**

• **Upgrade** - Get more features and content
• **Downgrade** - Reduce costs and features
• **View Details** - See what each plan includes
• **Keep Current** - Stay with your current plan

Choose an option below! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("⬆️ Upgrade Plan", callback_data="show_upgrades")],
            [InlineKeyboardButton("⬇️ Downgrade Plan", callback_data="show_downgrades")],
            [InlineKeyboardButton("📊 Compare Plans", callback_data="compare_plans")],
            [InlineKeyboardButton("🔙 Keep Current", callback_data="keep_current")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(change_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _handle_subscription_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle subscription cancellation"""
        user_id = update.effective_user.id
        
        # Get current subscription
        current_subscription = await self.db_manager.get_active_subscription(user_id)
        
        if not current_subscription:
            await self._show_no_subscription(update, context)
            return
        
        cancellation_text = f"""
❌ **Cancel Subscription**

You're about to cancel your **{current_subscription['subscription_type'].title()} Plan**.

**⚠️ Important Information:**
• Your subscription will end on {current_subscription['end_date'][:10]}
• You'll lose access to all premium features
• Your content delivery will stop
• You can reactivate anytime

**Before You Cancel:**
• Consider pausing instead of cancelling
• Check if you're eligible for a refund
• Contact support if you're having issues

**Are you sure you want to cancel?** 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("❌ Yes, Cancel", callback_data="confirm_cancellation")],
            [InlineKeyboardButton("⏸️ Pause Instead", callback_data="pause_subscription")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Keep Subscription", callback_data="keep_current")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(cancellation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_subscription_help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show subscription help"""
        help_text = """
❓ **Subscription Help**

Here's how to manage your subscription:

**Available Commands:**
• "status" - Check your subscription status
• "upgrade" - Upgrade your plan
• "downgrade" - Downgrade your plan
• "cancel" - Cancel your subscription
• "billing" - View billing information

**Common Actions:**
• Check subscription status
• Change your plan
• View billing details
• Cancel or pause subscription
• Contact support

**Need More Help?**
Use the buttons below for quick actions! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Check Status", callback_data="check_status")],
            [InlineKeyboardButton("🔄 Change Plan", callback_data="change_plan")],
            [InlineKeyboardButton("💳 Billing Info", callback_data="billing_info")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    def _get_plan_features(self, plan_type: str) -> str:
        """Get plan features as formatted string"""
        features = {
            "extreme": [
                "Daily personalized content",
                "Priority support",
                "Advanced customization",
                "Unlimited revisions",
                "Premium templates"
            ],
            "2week": [
                "Content every 2 days",
                "Standard support",
                "Good customization",
                "3 revisions per content",
                "Standard templates"
            ],
            "regular": [
                "Weekly content delivery",
                "Basic support",
                "Essential customization",
                "1 revision per content",
                "Basic templates"
            ]
        }
        
        plan_features = features.get(plan_type, [])
        return "\n".join([f"• {feature}" for feature in plan_features])
    
    async def handle_callback_query(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle callback queries from inline keyboards"""
        query = update.callback_query
        await query.answer()
        
        if query.data == "detailed_status":
            await self._show_detailed_status(update, context)
        elif query.data == "change_plan":
            await self._show_change_options(update, context, {})
        elif query.data == "billing_info":
            await self._show_billing_info(update, context)
        elif query.data == "usage_report":
            await self._show_usage_report(update, context)
        elif query.data == "cancel_subscription":
            await self._handle_subscription_cancellation(update, context)
        elif query.data == "show_upgrades":
            await self._show_upgrade_options(update, context, {})
        elif query.data == "show_downgrades":
            await self._show_downgrade_options(update, context, {})
        elif query.data == "compare_plans":
            await self._show_plan_comparison(update, context)
        elif query.data == "keep_current":
            await self._keep_current_plan(update, context)
        elif query.data == "confirm_cancellation":
            await self._confirm_cancellation(update, context)
        elif query.data == "pause_subscription":
            await self._pause_subscription(update, context)
        elif query.data == "contact_support":
            await self._show_support_contact(update, context)
        elif query.data == "subscription_help":
            await self._show_subscription_help(update, context)
    
    async def _show_detailed_status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show detailed subscription status"""
        user_id = update.effective_user.id
        
        # Get subscription and user data
        subscription = await self.db_manager.get_active_subscription(user_id)
        user_settings = await self.db_manager.get_user_settings(user_id)
        iterations = await self.db_manager.get_user_iterations(user_id)
        
        if not subscription:
            await self._show_no_subscription(update, context)
            return
        
        # Calculate usage statistics
        total_iterations = len(iterations)
        successful_iterations = len([i for i in iterations if i['status'] == 'sent'])
        
        detailed_text = f"""
📊 **Detailed Subscription Status**

**Subscription Details:**
• Plan: {subscription['subscription_type'].title()}
• Status: ✅ Active
• Start Date: {subscription['start_date'][:10]}
• End Date: {subscription['end_date'][:10]}
• Payment ID: {subscription.get('payment_id', 'N/A')[:8]}...

**Usage Statistics:**
• Total Content Delivered: {total_iterations}
• Successful Deliveries: {successful_iterations}
• Setup Completed: {'✅ Yes' if user_settings and user_settings.get('setup_completed') else '❌ No'}

**Account Information:**
• User ID: {user_id}
• Setup Date: {user_settings.get('created_at', 'Unknown')[:10] if user_settings else 'Unknown'}
• Last Activity: {iterations[0]['sent_at'][:10] if iterations else 'No activity yet'}

**Next Steps:**
• Content delivery is active
• Check your messages for new content
• Provide feedback to improve quality
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Change Plan", callback_data="change_plan")],
            [InlineKeyboardButton("💳 Billing Info", callback_data="billing_info")],
            [InlineKeyboardButton("📈 Usage Report", callback_data="usage_report")],
            [InlineKeyboardButton("🔙 Back to Status", callback_data="back_to_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(detailed_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_billing_info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show billing information"""
        user_id = update.effective_user.id
        
        # Get subscription
        subscription = await self.db_manager.get_active_subscription(user_id)
        
        if not subscription:
            await self._show_no_subscription(update, context)
            return
        
        billing_text = f"""
💳 **Billing Information**

**Current Subscription:**
• Plan: {subscription['subscription_type'].title()}
• Amount: {self._get_plan_price(subscription['subscription_type'])}
• Billing Cycle: Monthly
• Next Billing Date: {subscription['end_date'][:10]}

**Payment Details:**
• Payment Method: {subscription.get('payment_id', 'Unknown')[:8]}...
• Payment Status: ✅ Active
• Auto-Renewal: ✅ Enabled

**Billing History:**
• Last Payment: {subscription['start_date'][:10]}
• Payment ID: {subscription.get('payment_id', 'N/A')[:8]}...
• Status: ✅ Successful

**Need Help?**
• Update payment method
• View billing history
• Contact support
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Update Payment Method", callback_data="update_payment")],
            [InlineKeyboardButton("📋 Billing History", callback_data="billing_history")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Back to Status", callback_data="back_to_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(billing_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_usage_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show usage report"""
        user_id = update.effective_user.id
        
        # Get iterations
        iterations = await self.db_manager.get_user_iterations(user_id)
        
        if not iterations:
            usage_text = """
📈 **Usage Report**

**No usage data available yet.**

You haven't received any content yet. Once you start receiving content, this report will show:

• Total content delivered
• Delivery success rate
• Content types and topics
• Usage trends over time

**To start receiving content:**
• Ensure your subscription is active
• Check your preferences are set up
• Wait for your first content delivery

**Need Help?**
Contact support if you're not receiving content! 🆘
            """
        else:
            # Calculate usage statistics
            total_iterations = len(iterations)
            successful_iterations = len([i for i in iterations if i['status'] == 'sent'])
            success_rate = (successful_iterations / total_iterations * 100) if total_iterations > 0 else 0
            
            usage_text = f"""
📈 **Usage Report**

**Overall Statistics:**
• Total Content Delivered: {total_iterations}
• Successful Deliveries: {successful_iterations}
• Success Rate: {success_rate:.1f}%
• Average per Week: {total_iterations / 4:.1f}

**Recent Activity:**
• Last Delivery: {iterations[0]['sent_at'][:10] if iterations else 'None'}
• This Week: {len([i for i in iterations if i['sent_at'] > (datetime.now() - timedelta(days=7)).isoformat()])}
• This Month: {len([i for i in iterations if i['sent_at'] > (datetime.now() - timedelta(days=30)).isoformat()])}

**Content Types:**
• Personalized content: {total_iterations}
• Custom requests: 0
• Scheduled content: {total_iterations}

**Trends:**
• Usage is {'increasing' if total_iterations > 5 else 'stable'}
• Delivery success is {'excellent' if success_rate > 90 else 'good' if success_rate > 70 else 'needs attention'}
            """
        
        keyboard = [
            [InlineKeyboardButton("📊 Detailed Report", callback_data="detailed_report")],
            [InlineKeyboardButton("📋 Export Data", callback_data="export_data")],
            [InlineKeyboardButton("🔙 Back to Status", callback_data="back_to_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(usage_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_plan_comparison(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show plan comparison"""
        comparison_text = """
📊 **Plan Comparison**

| Feature | Regular | 2-Week | Extreme |
|---------|---------|--------|---------|
| **Price** | $19 | $49 | $99 |
| **Duration** | 7 days | 14 days | 30 days |
| **Frequency** | Weekly | Every 2 days | Daily |
| **Support** | Basic | Standard | Priority |
| **Revisions** | 1 per content | 3 per content | Unlimited |
| **Templates** | Basic | Standard | Premium |

**💡 Recommendation:**
• **Regular**: Perfect for beginners and small projects
• **2-Week**: Great for regular content creators
• **Extreme**: Ideal for businesses and high-volume needs

**Ready to choose?**
Select the plan that best fits your needs! 🎯
        """
        
        keyboard = [
            [InlineKeyboardButton("📝 Regular Plan", callback_data="select_regular")],
            [InlineKeyboardButton("⚡ 2-Week Plan", callback_data="select_2week")],
            [InlineKeyboardButton("🚀 Extreme Plan", callback_data="select_extreme")],
            [InlineKeyboardButton("🔙 Back to Status", callback_data="back_to_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(comparison_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _keep_current_plan(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Keep current plan"""
        keep_text = """
✅ **Keeping Current Plan**

Great choice! You're staying with your current plan.

**What's Next:**
• Continue receiving your personalized content
• Check your status anytime with /status
• Contact support if you need help
• Enjoy your personalized content experience!

Is there anything else I can help you with? 🤔
        """
        
        keyboard = [
            [InlineKeyboardButton("📊 Check Status", callback_data="check_status")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(keep_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _confirm_cancellation(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Confirm subscription cancellation"""
        user_id = update.effective_user.id
        
        # Update subscription status to cancelled
        # Note: In a real implementation, you'd update the database
        # For now, we'll just show a confirmation message
        
        cancellation_text = """
❌ **Subscription Cancelled**

Your subscription has been successfully cancelled.

**What happens next:**
• Your subscription will end on your current billing date
• You'll continue to receive content until then
• You can reactivate anytime
• Your account data will be preserved

**Thank you for using our service!**
We hope you enjoyed your personalized content experience.

**Need Help?**
Contact support if you have any questions! 🆘
        """
        
        keyboard = [
            [InlineKeyboardButton("🔄 Reactivate", callback_data="reactivate_subscription")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(cancellation_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _pause_subscription(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Pause subscription"""
        pause_text = """
⏸️ **Subscription Paused**

Your subscription has been paused.

**What happens next:**
• Content delivery will stop temporarily
• Your subscription remains active
• You can resume anytime
• No additional charges during pause

**Pause Duration:**
• Maximum pause time: 30 days
• Auto-resume: After 30 days
• Manual resume: Anytime before 30 days

**To Resume:**
Use the "Resume" button below or contact support.

**Need Help?**
Contact support if you have any questions! 🆘
        """
        
        keyboard = [
            [InlineKeyboardButton("▶️ Resume Subscription", callback_data="resume_subscription")],
            [InlineKeyboardButton("🆘 Contact Support", callback_data="contact_support")],
            [InlineKeyboardButton("🔙 Back to Menu", callback_data="back_to_menu")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.callback_query.edit_message_text(pause_text, parse_mode='Markdown', reply_markup=reply_markup)
    
    async def _show_support_contact(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Show support contact information"""
        support_text = """
🆘 **Contact Support**

Need help with your subscription? Our support team is here to assist you!

**Contact Methods:**
• 📧 Email: support@yourbot.com
• 💬 Live Chat: Available 24/7
• 📞 Phone: +1 (555) 123-4567
• 🕒 Hours: Monday-Friday, 9 AM - 6 PM EST

**Common Issues:**
• Subscription not working
• Payment problems
• Content delivery issues
• Account questions

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
    
    def _get_plan_price(self, plan_type: str) -> str:
        """Get plan price"""
        prices = {
            "extreme": "$99",
            "2week": "$49",
            "regular": "$19"
        }
        return prices.get(plan_type, "Unknown")
