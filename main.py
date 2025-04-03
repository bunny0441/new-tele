import telebot
import os
import time
import random
import threading
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

# Start Flask in a separate thread to keep the bot alive
threading.Thread(target=lambda: app.run(host='0.0.0.0', port=10000), daemon=True).start()

# Get bot token from environment variable (security best practice)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# Replace with your private channel IDs
CHANNELS = ["-1002408073109", "-1002568559251"]  

# Storage for all forwarded posts
collection_list = []
new_posts = []

bot = telebot.TeleBot(BOT_TOKEN)

# Function to send messages in batches of 10 every 3 hours
def send_scheduled_messages():
    while True:
        selected_posts = []

        if new_posts:
            selected_posts = new_posts[:10]
            del new_posts[:10]
        else:
            if len(collection_list) >= 10:
                selected_posts = random.sample(collection_list, 10)
            elif collection_list:
                selected_posts = collection_list[:10]

        for message in selected_posts:
            send_message_to_channels(message)

        print("✅ Sent 10 messages. Next batch in 3 hours...")
        time.sleep(3 * 60 * 60)  

threading.Thread(target=send_scheduled_messages, daemon=True).start()

def send_message_to_channels(message):
    for channel in CHANNELS:
        bot.send_message(channel, message)  

@bot.message_handler(content_types=['text'])
def handle_text(message):
    collection_list.append(message.text)
    new_posts.append(message.text)
    bot.reply_to(message, "📩 Added to collection & priority list!")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "Hello! Forward messages here. The bot will send 10 posts every 3 hours.")

print("Bot is running...")
bot.polling()
