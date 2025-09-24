# 🚀 Automatic Deployment Setup Guide

This guide will help you set up automatic deployment from GitHub to Heroku using GitHub Actions.

## 📋 Prerequisites

1. ✅ GitHub repositories created:
   - `hackreality-main-bot`
   - `hackreality-admin-bot`
2. ✅ Heroku apps created:
   - `hackreality-main-bot`
   - `hackreality-admin-bot`
3. ✅ Heroku API Key

## 🔑 Step 1: Get Your Heroku API Key

1. Go to [Heroku Account Settings](https://dashboard.heroku.com/account)
2. Scroll down to "API Key" section
3. Click "Reveal" to show your API key
4. Copy the API key (starts with a long string of characters)

## 🔧 Step 2: Configure GitHub Secrets

### For Main Bot Repository:

1. Go to: `https://github.com/DmitryPavl/hackreality-main-bot`
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `HEROKU_API_KEY` | `your-heroku-api-key-here` | Your Heroku API key |
| `HEROKU_APP_NAME` | `hackreality-main-bot` | Your Heroku app name |

### For Admin Bot Repository:

1. Go to: `https://github.com/DmitryPavl/hackreality-admin-bot`
2. Click **Settings** tab
3. Click **Secrets and variables** → **Actions**
4. Click **New repository secret**
5. Add these secrets:

| Secret Name | Value | Description |
|-------------|-------|-------------|
| `HEROKU_API_KEY` | `your-heroku-api-key-here` | Your Heroku API key |
| `HEROKU_APP_NAME` | `hackreality-admin-bot` | Your Heroku app name |

## 📝 Step 3: Update Workflow Files

### Update Main Bot Workflow:

1. Edit `.github/workflows/deploy.yml` in `hackreality-main-bot`
2. Replace `your-email@example.com` with your actual email
3. Ensure `heroku_app_name` matches your Heroku app name

### Update Admin Bot Workflow:

1. Edit `.github/workflows/deploy.yml` in `hackreality-admin-bot`
2. Replace `your-email@example.com` with your actual email
3. Ensure `heroku_app_name` matches your Heroku app name

## 🚀 Step 4: Enable Automatic Deployment

### For Main Bot:

1. Go to your Heroku dashboard
2. Select `hackreality-main-bot` app
3. Go to **Deploy** tab
4. In "Deployment method" section:
   - Select **GitHub**
   - Connect to `DmitryPavl/hackreality-main-bot`
   - ✅ **Enable Automatic Deploys** from `main` branch
   - ✅ **Wait for CI to pass before deploy**

### For Admin Bot:

1. Go to your Heroku dashboard
2. Select `hackreality-admin-bot` app
3. Go to **Deploy** tab
4. In "Deployment method" section:
   - Select **GitHub**
   - Connect to `DmitryPavl/hackreality-admin-bot`
   - ✅ **Enable Automatic Deploys** from `main` branch
   - ✅ **Wait for CI to pass before deploy**

## ✅ Step 5: Test Automatic Deployment

1. Make a small change to your code (like updating a comment)
2. Commit and push to GitHub:
   ```bash
   git add .
   git commit -m "Test automatic deployment"
   git push origin main
   ```
3. Go to GitHub Actions tab to see the deployment progress
4. Check Heroku logs to confirm successful deployment

## 🔍 Monitoring Deployments

### GitHub Actions:
- Go to your repository
- Click **Actions** tab
- See deployment history and logs

### Heroku:
- Go to your app dashboard
- Click **Activity** tab
- See deployment history

## 🛠️ Troubleshooting

### Common Issues:

1. **"App not found" error:**
   - Check that Heroku app names match in workflow files
   - Verify apps exist in your Heroku account

2. **"API key invalid" error:**
   - Regenerate Heroku API key
   - Update GitHub secrets

3. **"Build failed" error:**
   - Check Heroku logs for specific errors
   - Verify all dependencies are in `requirements.txt`

4. **"Deployment timeout" error:**
   - Check if your app is sleeping (free tier)
   - Consider upgrading to paid dyno

### Getting Help:

- Check GitHub Actions logs for detailed error messages
- Check Heroku logs: `heroku logs --tail -a your-app-name`
- Verify environment variables are set in Heroku

## 🎯 Benefits of Automatic Deployment

✅ **No manual deployment needed**  
✅ **Consistent deployments**  
✅ **Automatic testing before deployment**  
✅ **Deployment history tracking**  
✅ **Easy rollback if needed**  

## 📚 Next Steps

Once automatic deployment is working:

1. Set up monitoring and alerts
2. Configure staging environment
3. Add automated testing
4. Set up database backups
5. Configure logging and analytics

---

**🎉 Congratulations! Your bots will now automatically deploy whenever you push changes to GitHub!**
