# 🤖 HackReality Telegram Bot

A comprehensive Telegram bot for goal achievement and personal development, featuring psychological practices and structured coaching.

## 🎯 Features

- **Complete User Onboarding** - Welcome message, disclaimer, age collection, timezone detection
- **Goal-Oriented Subscriptions** - Three plans: Extreme, 2-week, and Regular
- **Payment Processing** - T-Bank donation system with admin confirmation
- **Personalized Setup** - Emotional state collection and focus statement creation
- **Task-Based Iterations** - Structured task delivery and progress tracking
- **Admin Management** - Comprehensive admin bot for monitoring and statistics
- **Real-time Notifications** - Admin notifications for all user activities

## 📋 Plans Available

### 🚀 Extreme Plan
- **Duration:** 1 week
- **Frequency:** 6 times per day (every 2-3 hours)
- **Focus:** Quick, intensive goal achievement
- **Price:** Donation-based

### 📅 2-Week Plan
- **Duration:** 2 weeks
- **Frequency:** 1 time per day
- **Focus:** Steady, sustainable progress
- **Price:** Donation-based

### 🎯 Regular Plan
- **Duration:** 30 days
- **Frequency:** 1 time per day
- **Focus:** Detailed, comprehensive development
- **Status:** In development

## 🏗️ Architecture

### Main Bot (@HackRealityBot)
- User-facing functionality
- Complete onboarding flow
- Goal collection and plan selection
- Payment processing
- Setup and material creation
- Task delivery and iteration

### Admin Bot (@hackrealityadminbot)
- Admin commands and monitoring
- User statistics and health checks
- Security and performance monitoring
- Comprehensive analytics
- Real-time notifications

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Telegram Bot Token
- Admin Bot Token

### Installation
```bash
git clone https://github.com/yourusername/hackreality-bot.git
cd hackreality-bot
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration
```bash
cp .env.example .env
nano .env
```

Add your bot tokens:
```env
TELEGRAM_BOT_TOKEN=your_main_bot_token
ADMIN_BOT_TOKEN=your_admin_bot_token
ADMIN_USER_ID=your_telegram_id
ADMIN_TELEGRAM_ID=your_telegram_id
```

### Run Locally
```bash
# Start main bot
python main.py

# Start admin bot (separate terminal)
python admin_bot_complete.py
```

## 🌐 Deployment

### Heroku (Recommended)
```bash
# Deploy to Heroku
./deploy_heroku.sh
```

### AWS EC2
```bash
# Deploy to AWS EC2
./deploy_aws.sh SERVER_IP KEY_FILE.pem
```

### Docker
```bash
# Deploy with Docker
docker-compose -f docker-compose.production.yml up -d
```

## 📊 Monitoring

### Admin Commands
- `/admin_stats` - Bot statistics
- `/admin_health` - System health
- `/admin_security` - Security report
- `/admin_performance` - Performance metrics
- `/admin_analytics` - User analytics

### Real-time Notifications
- New user registrations
- Regular plan requests
- Donation confirmations
- Setup completions
- System errors

## 🔧 Modules

### Core Modules
- `main.py` - Main bot application
- `admin_bot_complete.py` - Admin bot application
- `database.py` - Database management
- `user_state.py` - User state management

### Feature Modules
- `onboarding.py` - User onboarding flow
- `option.py` - Plan selection and goal collection
- `paying.py` - Payment processing
- `settingup.py` - Setup and material creation
- `iteration.py` - Task delivery and progress tracking

### Utility Modules
- `admin_notifications.py` - Admin notification service
- `monitoring.py` - System monitoring
- `security.py` - Security management
- `performance.py` - Performance optimization
- `analytics.py` - User analytics
- `error_handler.py` - Error handling

## 🧪 Testing

```bash
# Run tests
python run_tests.py

# Run with coverage
pytest --cov=modules tests/
```

## 📈 Analytics

The bot tracks:
- User engagement metrics
- Conversion funnels
- Feature usage statistics
- Goal achievement rates
- Admin notification effectiveness

## 🔒 Security

- Rate limiting
- Content validation
- User blocking capabilities
- Suspicious activity detection
- Input sanitization

## 💰 Cost

### Development
- **Free** - Run locally

### Production
- **Heroku:** $5-10/month
- **AWS EC2:** Free tier (12 months) or $5/month
- **Other VPS:** $5-10/month

## 📱 Bot Usernames

- **Main Bot:** @HackRealityBot
- **Admin Bot:** @hackrealityadminbot

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🆘 Support

For support, contact the admin through @hackrealityadminbot or create an issue in the repository.

## 🎉 Acknowledgments

Built with ❤️ for helping people achieve their goals and overcome challenges through structured psychological practices.

---

**Ready to help people achieve their dreams! 🌟**