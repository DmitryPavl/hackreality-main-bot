# 📁 GitHub Setup for Heroku Deployment

## Easy Way: Using GitHub Desktop

### Step 1: Download GitHub Desktop
1. Go to [desktop.github.com](https://desktop.github.com)
2. Download and install GitHub Desktop
3. Create a GitHub account (if you don't have one)

### Step 2: Create Repository
1. Open GitHub Desktop
2. Click "Create a new repository on GitHub"
3. **Repository name:** `hackreality-bot`
4. **Description:** `HackReality Telegram Bot`
5. **Local path:** Leave as default
6. Click "Create repository"

### Step 3: Add Your Bot Files
1. GitHub Desktop will open your repository folder
2. Copy all your bot files to this folder:
   ```bash
   cp -r /Users/dmitrypavlyuchenkov/TelegramBot/* /path/to/your/repository/
   ```
3. In GitHub Desktop, you'll see all your files listed
4. Add a commit message: "Initial HackReality bot files"
5. Click "Commit to main"
6. Click "Publish repository"

## Alternative: Using Web Interface

### Step 1: Create Repository on GitHub.com
1. Go to [github.com](https://github.com)
2. Click "New repository"
3. **Repository name:** `hackreality-bot`
4. **Description:** `HackReality Telegram Bot`
5. **Visibility:** Public or Private (your choice)
6. Click "Create repository"

### Step 2: Upload Files
1. Click "uploading an existing file"
2. Drag and drop all your bot files
3. Add commit message: "Initial HackReality bot files"
4. Click "Commit changes"

## What Files to Upload

Make sure these files are in your repository:

### Required Files:
- `main.py` (main bot)
- `admin_bot_complete.py` (admin bot)
- `heroku_main.py` (Heroku launcher for main bot)
- `heroku_admin.py` (Heroku launcher for admin bot)
- `Procfile` (main bot process file)
- `Procfile.admin` (admin bot process file)
- `requirements.txt` (Python dependencies)
- `runtime.txt` (Python version)
- `app.json` (main bot configuration)
- `app_admin.json` (admin bot configuration)
- All files in `modules/` folder
- `.env.example` (environment template)

### Optional Files:
- `README.md` (documentation)
- `DEPLOYMENT.md` (deployment guide)
- `tests/` folder (if you have tests)

## Next Steps

Once your repository is created and files are uploaded:

1. **Go to Heroku.com**
2. **Create two apps:**
   - `hackreality-bot-main`
   - `hackreality-bot-admin`
3. **Connect GitHub repository**
4. **Set environment variables**
5. **Deploy both apps**

## Repository Structure

Your repository should look like this:

```
hackreality-bot/
├── main.py
├── admin_bot_complete.py
├── heroku_main.py
├── heroku_admin.py
├── Procfile
├── Procfile.admin
├── requirements.txt
├── runtime.txt
├── app.json
├── app_admin.json
├── .env.example
├── modules/
│   ├── database.py
│   ├── onboarding.py
│   ├── option.py
│   ├── paying.py
│   ├── settingup.py
│   ├── iteration.py
│   ├── admin_notifications.py
│   └── ...
└── README.md
```

## 🎉 Ready for Heroku!

Once your files are on GitHub, you can deploy to Heroku using the web interface!
