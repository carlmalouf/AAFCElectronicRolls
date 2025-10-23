import streamlit as st
import sys
import platform
from datetime import datetime
import os

# Page configuration
st.set_page_config(
    page_title="Azure Smoke Test",
    page_icon="🔥",
    layout="wide"
)

# Title
st.title("🔥 Azure Deployment Smoke Test")
st.markdown("---")

# Success message
st.success("✅ Streamlit application is running successfully!")

# Display system information
st.subheader("📊 System Information")
col1, col2 = st.columns(2)

with col1:
    st.metric("Python Version", f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")
    st.metric("Platform", platform.system())
    st.metric("Platform Release", platform.release())

with col2:
    st.metric("Streamlit Version", st.__version__)
    st.metric("Current Time", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    st.metric("Machine", platform.machine())

# Environment check
st.markdown("---")
st.subheader("🔍 Environment Check")

env_vars_to_check = [
    "PYTHONPATH",
    "PATH",
    "HOME",
    "USER",
    "WEBSITE_SITE_NAME",
    "WEBSITE_INSTANCE_ID"
]

env_data = []
for var in env_vars_to_check:
    value = os.environ.get(var, "Not Set")
    if len(str(value)) > 100:
        value = str(value)[:100] + "..."
    env_data.append({"Variable": var, "Value": value})

st.table(env_data)

# Test basic functionality
st.markdown("---")
st.subheader("🧪 Basic Functionality Tests")

# Test input
test_input = st.text_input("Test Input Field", "Hello Azure!")
st.write(f"You entered: **{test_input}**")

# Test button
if st.button("Test Button"):
    st.balloons()
    st.success("Button works! 🎉")

# Test file operations
st.markdown("---")
st.subheader("📁 File System Test")
try:
    test_file = "test_write.txt"
    with open(test_file, "w") as f:
        f.write("Test write operation")
    with open(test_file, "r") as f:
        content = f.read()
    os.remove(test_file)
    st.success("✅ File system write/read/delete operations successful")
except Exception as e:
    st.error(f"❌ File system operations failed: {str(e)}")

# Test imports
st.markdown("---")
st.subheader("📦 Package Import Tests")

packages_to_test = [
    ("pandas", "pd"),
    ("numpy", "np"),
    ("io", None),
    ("typing", None),
    ("re", None)
]

for package, alias in packages_to_test:
    try:
        if alias:
            exec(f"import {package} as {alias}")
            exec(f"version = {alias}.__version__ if hasattr({alias}, '__version__') else 'N/A'")
        else:
            exec(f"import {package}")
            version = "N/A"
        st.success(f"✅ {package} - Version: {version}")
    except Exception as e:
        st.error(f"❌ {package} - Failed: {str(e)}")

# Footer
st.markdown("---")
st.info("""
### 📝 Next Steps
If you see this page without errors:
1. ✅ Azure deployment is working
2. ✅ Streamlit is running correctly
3. ✅ Basic Python operations are functional

You can now restore the original app.py from app.py.backup
""")
