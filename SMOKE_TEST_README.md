# Azure Smoke Test Branch

This branch contains a minimal Streamlit application designed to troubleshoot Azure deployment issues.

## What This Does

The `app.py` file in this branch is a simple diagnostic tool that:

1. ✅ **Confirms Streamlit is Running** - Displays a success message if the app loads
2. 📊 **Shows System Information** - Python version, platform, machine type, Streamlit version
3. 🔍 **Checks Environment Variables** - Displays Azure-specific env vars like `WEBSITE_SITE_NAME`
4. 🧪 **Tests Basic Functionality** - Interactive buttons and inputs
5. 📁 **Tests File System** - Verifies read/write permissions
6. 📦 **Tests Package Imports** - Checks if pandas, numpy, and other required packages load correctly

## How to Use

1. Deploy this branch to Azure
2. Visit your Azure app URL
3. If you see the smoke test page, your deployment is working!
4. Check the displayed information for any errors or issues

## Files in This Branch

- `app.py` - The smoke test application (currently active)
- `app_original.py` - The original AAFC Electronic Rolls application (backed up)
- `app.py.backup` - Additional backup of the original application

## Restoring the Original App

Once you've verified the deployment works:

1. Switch back to the `main` branch
2. Or restore the original app by running:
   ```powershell
   Move-Item app_original.py app.py -Force
   ```

## Common Azure Issues to Check

- **Application Error**: Check if Python packages are installed (see Package Import Tests section)
- **Startup Command**: Ensure Azure startup command is: `python -m streamlit run app.py --server.port 8000 --server.address 0.0.0.0`
- **Requirements**: Verify all packages in `requirements.txt` are compatible
- **File Permissions**: Check the File System Test section for write access issues
