# 🍎 macOS Setup Guide for Heroku Deployment

## Step 1: Install Homebrew

Homebrew is a package manager for macOS that makes installing development tools easy.

### Install Homebrew:
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

This command will:
- Download and install Homebrew
- Add Homebrew to your PATH
- Install Xcode Command Line Tools (if needed)

### After installation, add Homebrew to your PATH:
```bash
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc
```

## Step 2: Install Heroku CLI

Once Homebrew is installed, install Heroku CLI:

```bash
brew tap heroku/brew && brew install heroku
```

## Step 3: Verify Installation

Check if everything is installed correctly:

```bash
brew --version
heroku --version
```

## Step 4: Login to Heroku

```bash
heroku login
```

This will open a browser window for you to login to your Heroku account.

## Step 5: Deploy Your Bot

```bash
cd /Users/dmitrypavlyuchenkov/TelegramBot
./deploy_heroku.sh
```

## Alternative: Manual Heroku CLI Installation

If you prefer not to install Homebrew, you can download Heroku CLI directly:

1. Go to [devcenter.heroku.com/articles/heroku-cli](https://devcenter.heroku.com/articles/heroku-cli)
2. Download the macOS installer
3. Run the installer
4. Follow the installation prompts

## Troubleshooting

### If Homebrew installation fails:
```bash
# Try with different method
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### If PATH issues occur:
```bash
# Add to your shell profile
echo 'export PATH="/opt/homebrew/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### If Heroku CLI doesn't work:
```bash
# Reinstall
brew uninstall heroku
brew install heroku/brew/heroku
```

## Quick Commands Summary

```bash
# 1. Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# 2. Add to PATH
echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zshrc
source ~/.zshrc

# 3. Install Heroku CLI
brew tap heroku/brew && brew install heroku

# 4. Login to Heroku
heroku login

# 5. Deploy your bot
cd /Users/dmitrypavlyuchenkov/TelegramBot
./deploy_heroku.sh
```

## 🎉 Ready to Deploy!

Once you complete these steps, your HackReality bot will be running on Heroku!
