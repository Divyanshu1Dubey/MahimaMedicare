# CI/CD Pipeline Setup Instructions

## 1. Push Workflow to GitHub

First, commit and push the workflow file:

```bash
git add .github/workflows/deploy.yml
git commit -m "Add CI/CD pipeline for automatic deployment"
git push origin main
```

## 2. Set up GitHub Secrets

Go to your GitHub repository settings and add these secrets:

1. **HOST**: `139.84.155.25`
2. **USERNAME**: `root`
3. **PASSWORD**: `D_o5{e2vYDL7fAR#`

### Steps:
1. Go to: https://github.com/Divyanshu1Dubey/MahimaMedicare/settings/secrets/actions
2. Click "New repository secret"
3. Add each secret:
   - Name: `HOST`, Value: `139.84.155.25`
   - Name: `USERNAME`, Value: `root`
   - Name: `PASSWORD`, Value: `D_o5{e2vYDL7fAR#`

## 3. Setup Git on Server

Run these commands on your server to enable git pull:

```bash
ssh root@139.84.155.25

cd /var/www/mahima-medicare

# Initialize git if not already done
git init
git remote add origin https://github.com/Divyanshu1Dubey/MahimaMedicare.git

# Configure git credentials (replace with your GitHub username)
git config user.name "Divyanshu1Dubey"
git config user.email "your-email@gmail.com"

# Set up authentication token (you'll need to create a Personal Access Token)
# Go to: https://github.com/settings/tokens
# Create token with repo permissions
# Then run: git config credential.helper store
```

## 4. How It Works

Once set up:

1. **Make changes** to your Django code locally
2. **Commit and push** to GitHub:
   ```bash
   git add .
   git commit -m "Your changes description"
   git push origin main
   ```
3. **GitHub automatically deploys** to your server
4. **Your website updates** at https://mahimamedicare.co.in

## 5. What Gets Deployed Automatically

- ✅ Code changes
- ✅ Database migrations
- ✅ Static files updates
- ✅ Dependencies installation
- ✅ Server restart
- ✅ Health check

## 6. Monitoring

You can see deployment status in:
- GitHub Actions tab in your repository
- Real-time logs of deployment process
- Success/failure notifications

This eliminates manual server updates - just push to GitHub and your website updates automatically! 🚀