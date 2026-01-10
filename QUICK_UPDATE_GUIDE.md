# 🚀 Eco Club - Quick Update Guide

## आपको क्या करना है (Simple 2-Step Process):

### Step 1: Files Replace करें
National website से 2 files download करके `D:\Eco club` folder में replace करें:
1. **All_Schools_with_Notifications_UTTAR PRADESH.xlsx**
2. **UTTAR PRADESH.xlsx**

### Step 2: Auto Update Button दबाएं
**`🚀 AUTO UPDATE.bat`** file पर double-click करें

बस! हो गया! ✅

---

## यह Automatic क्या करेगा:

✅ Notification data merge करेगा  
✅ Tree plantation data merge करेगा  
✅ Summary Excel report generate करेगा  
✅ GitHub पर automatically push करेगा  
✅ Streamlit Cloud dashboard 2-3 minutes में auto-update होगा  

---

## Files की Details:

### 📝 Main Script
- **AUTO_UPDATE_AND_PUSH.py** - यह main Python script है जो सब कुछ करती है

### 🔵 One-Click Button
- **🚀 AUTO UPDATE.bat** - इस पर बस double-click करें

### 📊 Generated Files (Auto-created)
- `Updated_School_Data.csv` - Merged data with notifications and trees
- `Eco-Club-Complete_Summary.xlsx` - Summary report with all districts
- `Tree_Data.csv` - Auto-converted from UTTAR PRADESH.xlsx
- `Notifications.csv` - Auto-converted from notification Excel

---

## Troubleshooting:

### ❌ अगर error आए तो:

1. **File not found error:**
   - Check करें कि 2 Excel files सही से replace हुई हैं
   - File names बिल्कुल same होनी चाहिए

2. **Git error:**
   - Internet connection check करें
   - GitHub credentials verify करें

3. **Python error:**
   - Virtual environment activate है या नहीं check करें
   - Required packages install हैं check करें: `pip install -r requirements.txt`

---

## Dashboard Links:

- **Live Dashboard:** https://ecoclubup.streamlit.app/
- **GitHub Repo:** https://github.com/alokkmohan/ECO-Club

---

## Notes:

- हर update के बाद Streamlit Cloud को redeploy होने में 2-3 minutes लगते हैं
- Local पर देखने के लिए: `streamlit run dashboard.py`
- Git status check करने के लिए: `git status`

---

**Developer:** Alok Mohan  
**Last Updated:** January 10, 2026
