# Automated Download & Upload - Setup Instructions

## पहली बार Setup (One-time setup)

### 1. Required Packages Install करें
```powershell
pip install -r requirements.txt
```

### 2. Credentials File बनाएं
एक `.env` नाम की file बनाएं और अपना userid/password डालें:

```powershell
# .env.example file को copy करें
copy .env.example .env

# अब .env file को open करें और अपनी credentials डालें:
# ECO_USERID=apki_actual_userid
# ECO_PASSWORD=apka_actual_password
```

**Important:** `.env` file git पर upload नहीं होगी (already .gitignore में है)

### 3. Microsoft Edge Browser
Script Edge browser use करती है (Windows में default होता है). अगर Edge नहीं है तो install करें या script में Chrome के लिए modify करें.

---

## कैसे इस्तेमाल करें (How to Use)

### एक Command में सब कुछ:
```powershell
python download_and_upload.py
```

यह script automatically:
1. ✅ Website पर login करेगी
2. ✅ `UTTAR PRADESH.xlsx` download करेगी
3. ✅ `All_Schools_with_Notifications_UTTAR PRADESH.xlsx` download करेगी
4. ✅ Files को workspace में move करेगी
5. ✅ Git पर push करेगी

---

## Troubleshooting

### अगर browser नहीं खुल रहा:
```powershell
# Edge WebDriver install करें
pip install msedge-selenium-tools
```

### अगर download नहीं हो रही:
- Check करें कि website का structure same है
- Script में XPath selectors को update करना पड़ सकता है
- Browser window को manually देखें (headless mode off है)

### अगर git push fail हो रहा:
```powershell
# Git credentials check करें
git config user.name
git config user.email

# या manually push करें
git add *.xlsx
git commit -m "Updated data"
git push
```

---

## Manual Process (अगर automation काम नहीं कर रहा)

1. **Download Files:**
   - https://ecoclubs.education.gov.in/Ekpedmaakenaam पर जाएं
   - Login करें
   - "Download State wise data excel" → UTTAR PRADESH.xlsx
   - "Total Notification Uploaded" → "Download all school excel"

2. **Move to Workspace:**
   - Downloaded files को `d:\Eco club\` में copy करें

3. **Push to Git:**
   ```powershell
   .\push_to_git.bat
   ```

---

## Script Customization

### Headless Mode (बिना browser window के)
[download_and_upload.py](download_and_upload.py#L60) में line 60 पर uncomment करें:
```python
edge_options.add_argument('--headless')
```

### Download Timeout बढ़ाएं
[download_and_upload.py](download_and_upload.py#L153) में timeout value बदलें:
```python
if wait_for_download("filename.xlsx", timeout=60):  # 60 seconds
```

### Chrome Browser Use करें
Edge की जगह Chrome use करने के लिए:
```python
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

driver = webdriver.Chrome(options=chrome_options)
```
