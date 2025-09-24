# 🔧 Manual GitHub Workflow Setup

Since the GitHub token doesn't have workflow permissions, here's how to set up the workflow files manually:

## 📁 Step 1: Create Workflow Directory

1. Go to your GitHub repository: `https://github.com/DmitryPavl/hackreality-main-bot`
2. Click **Add file** → **Create new file**
3. Type: `.github/workflows/deploy.yml`
4. Copy the content below:

```yaml
name: Deploy to Heroku

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests (if any)
      run: |
        echo "No tests configured yet"
        # python -m pytest tests/ || true
        
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.14
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "hackreality-main-bot"
        heroku_email: "your-email@example.com"
        appdir: "."
        usedocker: false
```

5. Replace `your-email@example.com` with your actual email
6. Click **Commit new file**

## 📁 Step 2: Create Admin Bot Workflow

1. Go to: `https://github.com/DmitryPavl/hackreality-admin-bot`
2. Click **Add file** → **Create new file**
3. Type: `.github/workflows/deploy.yml`
4. Copy this content:

```yaml
name: Deploy Admin Bot to Heroku

on:
  push:
    branches: [ main ]
  pull_request:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - name: Checkout code
      uses: actions/checkout@v3
      
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.9'
        
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        
    - name: Run tests (if any)
      run: |
        echo "No tests configured yet"
        # python -m pytest tests/ || true
        
    - name: Deploy to Heroku
      uses: akhileshns/heroku-deploy@v3.12.14
      with:
        heroku_api_key: ${{secrets.HEROKU_API_KEY}}
        heroku_app_name: "hackreality-admin-bot"
        heroku_email: "your-email@example.com"
        appdir: "."
        usedocker: false
```

5. Replace `your-email@example.com` with your actual email
6. Click **Commit new file**

## 🔑 Step 3: Add GitHub Secrets

### For Main Bot:
1. Go to `https://github.com/DmitryPavl/hackreality-main-bot/settings/secrets/actions`
2. Click **New repository secret**
3. Add:
   - Name: `HEROKU_API_KEY`
   - Value: `your-heroku-api-key-here`

### For Admin Bot:
1. Go to `https://github.com/DmitryPavl/hackreality-admin-bot/settings/secrets/actions`
2. Click **New repository secret**
3. Add:
   - Name: `HEROKU_API_KEY`
   - Value: `your-heroku-api-key-here`

## 🚀 Step 4: Enable Automatic Deployments

1. Go to your Heroku dashboard
2. Select each app
3. Go to **Deploy** tab
4. Connect to GitHub repository
5. ✅ **Enable Automatic Deploys**

## ✅ Step 5: Test

Make a small change and push to test automatic deployment!

---

**Note:** You can also get a new GitHub token with `workflow` scope from: https://github.com/settings/tokens
