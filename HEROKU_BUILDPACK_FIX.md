# 🔧 Heroku Buildpack Fix Guide

## 🚨 Problem: "Ruby app detected" instead of Python

The issue is that Heroku found Ruby files in your repository (from `node_modules`) and is trying to build it as a Ruby app instead of Python.

## ✅ Solution 1: Fix .gitignore (Recommended)

### Step 1: Update .gitignore
Add these lines to your `.gitignore` file:

```gitignore
# Node.js
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React Native
ios/
android/
.expo/
.expo-shared/

# Other
*.log
.DS_Store
```

### Step 2: Remove node_modules from Git
```bash
# Remove from git tracking
git rm -r --cached node_modules/
git rm -r --cached ios/
git rm -r --cached android/

# Add to .gitignore
echo "node_modules/" >> .gitignore
echo "ios/" >> .gitignore
echo "android/" >> .gitignore

# Commit changes
git add .gitignore
git commit -m "Remove node_modules and fix .gitignore"
git push origin main
```

### Step 3: Redeploy on Heroku
1. Go to Heroku dashboard
2. Click "Deploy" tab
3. Click "Deploy branch"

## ✅ Solution 2: Force Python Buildpack

### Step 1: Set Buildpack in Heroku Dashboard
1. Go to your app dashboard
2. Click "Settings" tab
3. Click "Add buildpack"
4. Select "Python"
5. Click "Save changes"

### Step 2: Redeploy
1. Go to "Deploy" tab
2. Click "Deploy branch"

## ✅ Solution 3: Clean Repository

### Step 1: Remove Unnecessary Files
```bash
# Remove node_modules
rm -rf node_modules/

# Remove other unnecessary directories
rm -rf ios/
rm -rf android/
rm -rf .expo/

# Remove log files
rm -f *.log
```

### Step 2: Update .gitignore
```bash
# Create comprehensive .gitignore
cat > .gitignore << 'EOF'
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
pip-wheel-metadata/
share/python-wheels/
*.egg-info/
.installed.cfg
*.egg
MANIFEST

# Virtual Environment
venv/
venv_new/
env/
ENV/
env.bak/
venv.bak/

# Environment Variables
.env
.env.local
.env.development
.env.test
.env.production

# Database
*.db
*.sqlite
*.sqlite3

# Logs
logs/
*.log
log/

# IDE
.vscode/
.idea/
*.swp
*.swo
*~

# OS
.DS_Store
.DS_Store?
._*
.Spotlight-V100
.Trashes
ehthumbs.db
Thumbs.db

# Temporary files
temp/
tmp/
*.tmp
*.temp

# Coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
.hypothesis/
.pytest_cache/

# Jupyter Notebook
.ipynb_checkpoints

# pyenv
.python-version

# Heroku
.heroku/

# Backup files
*.bak
*.backup
*_backup_*

# SSH keys
*.pem
*.key
id_rsa*
id_ed25519*

# Node.js (if any)
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# React Native
ios/
android/
.expo/
.expo-shared/

# Local configuration
config.local.py
settings.local.py
EOF
```

### Step 3: Commit and Push
```bash
# Add all changes
git add .

# Commit
git commit -m "Clean repository and fix buildpack detection"

# Push to GitHub
git push origin main
```

### Step 4: Redeploy on Heroku
1. Go to Heroku dashboard
2. Click "Deploy" tab
3. Click "Deploy branch"

## ✅ Solution 4: Manual Buildpack Selection

### Step 1: Use Heroku CLI (if available)
```bash
# Set Python buildpack
heroku buildpacks:set heroku/python --app your-app-name

# Deploy
git push heroku main
```

### Step 2: Alternative - Dashboard Method
1. Go to app dashboard
2. Settings tab
3. Buildpacks section
4. Click "Add buildpack"
5. Select "Python"
6. Save changes
7. Deploy again

## 🔍 Troubleshooting

### Problem 1: Still Detecting Ruby
**Solution:** Make sure all Ruby files are removed from repository

### Problem 2: Buildpack Not Saving
**Solution:** Try refreshing page and setting buildpack again

### Problem 3: Deployment Still Fails
**Solution:** Check logs for specific error messages

## 📋 Quick Fix Steps

1. **Remove node_modules from git:**
   ```bash
   git rm -r --cached node_modules/
   git commit -m "Remove node_modules"
   git push origin main
   ```

2. **Set Python buildpack in Heroku:**
   - Go to Settings tab
   - Add buildpack: Python
   - Save changes

3. **Redeploy:**
   - Go to Deploy tab
   - Click "Deploy branch"

4. **Check Resources tab:**
   - Should now show worker dyno
   - Scale to 1 Eco

## 🎯 Expected Result

After fixing, you should see:
```
-----> Python app detected
-----> Installing python-3.9.18
-----> Installing pip
-----> Installing dependencies from requirements.txt
-----> Detected Procfile
```

## 🆘 Still Having Issues?

### Alternative: Create Clean Repository
1. Create new GitHub repository
2. Copy only bot files (no node_modules)
3. Deploy fresh repository to Heroku

### Contact Support
If nothing works, contact Heroku support with the buildpack detection issue.

## 🎉 Success!

Once fixed, your bot will deploy as a Python app and you'll be able to set worker dynos! 🚀
