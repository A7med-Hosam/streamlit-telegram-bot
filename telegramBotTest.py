from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import ast
from pathlib import Path


script_dir = Path(__file__).parent

TOKEN: Final = '8402834860:AAEscTZBvCGSC0G1s495m96DIlZDokW8Z9M'
BOT_USERNAME: Final = '@notion_trading_dashboard_bot'


# Commands /
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Hello! this is Notion Trading Dashboard')

async def update_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('Updating Dashboard ....')
    res = requests.get("https://ahmedhosam-sec01-sec09--example-lifecycle-web-update-5c94cb-dev.modal.run/")
    
    full_list = ast.literal_eval(res.text)
    text = f"""
------------------------------
    Balance = {full_list[0]}

    Today's Pnl 
        {full_list[1]}
  Live             Closed
  {full_list[2]}                  {full_list[3]}
------------------------------
"""



    print(f"update code {res.status_code}")
    print(res.text)
    await update.message.reply_text(f"Dashboard has been updated with code ✅{text}")


async def greet_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('greetings Ahmed I am your Notion Trading Dashboard')

async def message_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_url = "https://images.pexels.com/photos/36704/pexels-photo.jpg"
    photo_file = open(f"{script_dir}/pexels-photo.jpg","rb")
    await context.bot.send_photo(chat_id=update.effective_chat.id, photo=photo_url)

# Responses

def handle_response(text: str) -> str:
    processed: str = text.lower()

    if "hello" in processed:
        return "Hey there!"
    
    if "how are you" in processed:
        return "I am good!"
    
    return "I don't get that"

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text

    print(f'User ({update.message.chat.id}) in {message_type} : "{text}"')
    
    if message_type == "group":
        if BOT_USERNAME in text:
            new_text: str = text.replace(BOT_USERNAME, "").strip()
            response: str = handle_response(new_text)
        else:
            return
    else:
        response: str = handle_response(text)

    print('Bot:', response)
    await update.message.reply_text(response)

async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'Update {update} caused error {context.error}')

if __name__  == '__main__':
    print(" Starting bot...")
    app = Application.builder().token(TOKEN).build()

    # commands
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('greet', greet_command))
    app.add_handler(CommandHandler('update', update_command))
    app.add_handler(CommandHandler('photo', message_photo))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # errors
    app.add_error_handler(error)

    # check new messages
    print('polling messages...')
    app.run_polling(poll_interval=3)

    
