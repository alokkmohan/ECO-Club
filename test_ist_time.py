"""
Test IST timezone in PDF
"""
from datetime import datetime
import pytz

# Test IST time
ist_timezone = pytz.timezone('Asia/Kolkata')
current_time = datetime.now(ist_timezone)

print("=" * 50)
print("TIME TEST")
print("=" * 50)
print(f"IST Time: {current_time.strftime('%B %d, %Y at %I:%M %p IST')}")
print(f"24-hour format: {current_time.strftime('%Y-%m-%d %H:%M:%S IST')}")
print(f"Current hour: {current_time.hour}")
print(f"Current minute: {current_time.minute}")
print("=" * 50)
