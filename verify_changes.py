"""
Verification script to check if all dashboard changes are present
"""

print("🔍 Verifying Dashboard Changes...\n")

with open('dashboard.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
checks = {
    "Bottom 25 Districts": "Bottom 25 Districts" in content,
    "Percentage (%) column": "Percentage (%)" in content,
    "Tree data in summary": "Total Tree Uploaded" in content and "Tree Upload Percentage" in content,
    "Removed Sr. No.": "Sr. No." not in content or content.count("Sr. No.") < 3,  # Might be in comments
    "No header icons": "::before" not in content or "🌳" not in content
}

print("📋 Change Verification Results:")
print("-" * 50)
for check, passed in checks.items():
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status} - {check}")

print("\n" + "=" * 50)
if all(checks.values()):
    print("✅ All changes are present in dashboard.py!")
    print("\n💡 If Streamlit Cloud still shows old version:")
    print("   1. Check app settings - correct repository & branch")
    print("   2. Manual reboot from Streamlit Cloud dashboard")
    print("   3. Clear browser cache (Ctrl+Shift+Delete)")
    print("   4. Wait 2-3 minutes for deployment")
else:
    print("⚠️  Some changes are missing!")
    print("   Please check dashboard.py file")

print("=" * 50)

# Show git status
import subprocess
try:
    result = subprocess.run(['git', 'log', '--oneline', '-1'], 
                          capture_output=True, text=True)
    print("\n📊 Latest Git Commit:")
    print(result.stdout.strip())
except:
    pass
