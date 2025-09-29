@echo off
echo Setting up server for CI/CD pipeline...

ssh root@139.84.155.25 "
cd /var/www/mahima-medicare

echo 'Configuring Git on server...'

# Configure git for the project
git config user.name 'Divyanshu1Dubey'
git config user.email 'divyanshu@mahimamedicare.co.in'

# Set up the remote origin if not exists
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/Divyanshu1Dubey/MahimaMedicare.git

# Verify git configuration
echo 'Git configuration:'
git config --list | grep user
git remote -v

echo 'Testing git pull...'
git pull origin main || echo 'Note: You may need to set up GitHub Personal Access Token for authentication'

echo 'Server is ready for CI/CD pipeline!'
echo ''
echo 'Next steps:'
echo '1. Push the workflow file to GitHub'
echo '2. Add secrets in GitHub repository settings'
echo '3. Create GitHub Personal Access Token if needed'
"

echo ''
echo 'Now you can push your workflow to GitHub:'
echo 'git add .github/'
echo 'git commit -m \"Add CI/CD pipeline\"'
echo 'git push origin main'

pause