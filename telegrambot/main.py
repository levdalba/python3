from telegram import ReplyKeyboardRemove, Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

async def start(update: Update, context):
    await update.message.reply_text("Hello man!")

async def info(update: Update, context):
    user = update.message.from_user
    user_info = f"""
    ID: {user.id}{context.user_data.get('is_useful')}
    Username: {user.username}
    Last Name: {user.last_name}
    Link: {user.link}
    Full Name: {user.full_name}
    Is Premium: {user.is_premium}
    Language Code: {user.language_code}
    """
    await update.message.reply_text(user_info)


async def infoForwarded(update: Update, context):
    user = update.message.forward_origin.sender_user
    frwd_info = f"""
    ID: {user.id}
    Username: {user.username or 'None'}
    Last Name: {user.last_name or 'None'}
    Link: {user.link or 'None'}
    Full Name: {user.full_name}
    Is Premium: {user.is_premium or 'None'}
    Language Code: {user.language_code or 'None'}
    """
    markup = ReplyKeyboardMarkup([['Nice', 'Good', 'Not so good']])
    await update.message.reply_text(frwd_info, reply_markup=markup)


async def default_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_choice = update.message.text
    context.user_data['is_useful'] = user_choice
    context.chat_data
    context.bot_data
    await update.message.reply_text('Ok', reply_markup=ReplyKeyboardRemove())

async def info_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    is_useful = context.user_data.get('is_useful', 'No data')
    await update.message.reply_text(f'You said the information was: {is_useful}')


def main():
    bot_token = '6731366092:AAHZNbxjzdtU0m8aC5iTKAEeocD0hdM4x1c'
    app = Application.builder().token(bot_token).build()
    app.add_handler(CommandHandler(command="start", callback=start))
    app.add_handler(CommandHandler(command="info", callback=info_handler))
    app.add_handler(MessageHandler(filters=filters.FORWARDED & ~filters.COMMAND, callback=infoForwarded))
    app.add_handler(MessageHandler(filters=filters.TEXT & ~filters.COMMAND, callback=default_handler))

    app.run_polling()

if __name__ == '__main__':
    main()
