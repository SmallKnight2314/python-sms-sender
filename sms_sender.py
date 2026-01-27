import os
import tkinter as tk
from tkinter import messagebox
from tplinkrouterc6u import TplinkRouterProvider
from datetime import datetime

# Router config (edit these)
ROUTER_URL = 'http://192.168.1.1'  # Your router's IP
ROUTER_PASSWORD = 'Ev9[9_kQiuYF'  # Router admin password

# Folders for saving messages
OUTBOX_DIR = 'outbox'
DRAFTS_DIR = 'drafts'
os.makedirs(OUTBOX_DIR, exist_ok=True)
os.makedirs(DRAFTS_DIR, exist_ok=True)

def send_sms():
    phone = phone_entry.get().strip()
    message = message_entry.get("1.0", tk.END).rstrip()  # Remove trailing newline if any
    
    if not phone or not message:
        status_label.config(text="Error: Fill in phone and message.")
        return
    
    # Option 1: Replace newlines with chr(10) (LF) - most common fix for TP-Link
    #message_encoded = message.replace('\r\n', '\n').replace('\r', '\n')  # Normalize first
    #message_encoded = message_encoded.replace('\n', chr(10))  # TP-Link often wants plain LF
    
    # Option 2: If Option 1 fails, try this instead (some routers want chr(18) for newline)
    message_encoded = message.replace('\r\n', chr(18)).replace('\n', chr(18)).replace('\r', chr(18))
    
    # Option 3: Flatten to single line (fallback if nothing else works)
    # message_encoded = message.replace('\n', ' ').replace('\r', ' ')
    
    # Use this one for now (start with Option 1)
    message_to_send = message_encoded
    
    try:
        router = TplinkRouterProvider.get_client(ROUTER_URL, ROUTER_PASSWORD)
        router.authorize()
        
        # Extra debug
        print("DEBUG: Sending to:", phone)
        print("DEBUG: Original message repr:", repr(message))
        print("DEBUG: Encoded message repr:", repr(message_to_send))
        print("DEBUG: Encoded length:", len(message_to_send))
        
        router.send_sms(phone_number=phone, message=message_to_send)
        router.logout()
        
        # Save original (multi-line) version to outbox for your records
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{phone}.txt"
        with open(os.path.join(OUTBOX_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(f"Phone: {phone}\nMessage (original):\n{message}\n\nSent encoded as:\n{message_to_send}\nSent: {timestamp}")
        
        status_label.config(text="Success: SMS sent!")
        messagebox.showinfo("Success", "SMS sent and saved to outbox (with original formatting).")
    
    except Exception as e:
        # Save to drafts
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{timestamp}_{phone}.txt"
        with open(os.path.join(DRAFTS_DIR, filename), 'w', encoding='utf-8') as f:
            f.write(f"Phone: {phone}\nMessage (original):\n{message}\nFailed: {timestamp}\nError: {str(e)}")
        
        status_label.config(text=f"Fail: {str(e)}")
        messagebox.showerror("Error", f"Failed: {str(e)}. Saved to drafts.")

# GUI setup
root = tk.Tk()
root.title("Simple SMS Sender")
root.geometry("400x300")

tk.Label(root, text="Phone Number:").pack(pady=5)
phone_entry = tk.Entry(root, width=50)
phone_entry.pack()

tk.Label(root, text="Message:").pack(pady=5)
message_entry = tk.Text(root, height=5, width=50)
message_entry.pack()

send_button = tk.Button(root, text="Send SMS", command=send_sms)
send_button.pack(pady=10)

status_label = tk.Label(root, text="")
status_label.pack()

root.mainloop()