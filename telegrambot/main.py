from telegram import Update,  ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import random

STATE_START, STATE_QUIZ, STATE_ANSWERING = range(3)

FLASHCARDS = {
    "word1": {"question": "Meaning of word1?", "options": ["option1", "option2", "correct", "option4"], "answer": "correct"},
    "word2": {"question": "Meaning of word2?", "options": ["correct", "option2", "option3", "option4"], "answer": "correct"},
    "word3": {"question": "Meaning of word1?", "options": ["option1", "option2", "correct", "option4"], "answer": "correct"},
    "word4": {"question": "Meaning of word2?", "options": ["correct", "option2", "option3", "option4"], "answer": "correct"},
    "word5": {"question": "Meaning of word1?", "options": ["option1", "option2", "correct", "option4"], "answer": "correct"},
    "word6": {"question": "Meaning of word2?", "options": ["correct", "option2", "option3", "option4"], "answer": "correct"},
    "word7": {"question": "Meaning of word1?", "options": ["option1", "option2", "correct", "option4"], "answer": "correct"},
    "word8": {"question": "Meaning of word2?", "options": ["correct", "option2", "option3", "option4"], "answer": "correct"},
    "word9": {"question": "Meaning of word1?", "options": ["option1", "option2", "correct", "option4"], "answer": "correct"},
    "word10": {"question": "Meaning of word2?", "options": ["correct", "option2", "option3", "option4"], "answer": "correct"},
}

async def start(update: Update, context: CallbackContext) -> None:
    keyboard = [['Yes', 'No']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text('Welcome to the Flashcard Quiz Bot! Do you want to start the quiz?', reply_markup=reply_markup)
    context.user_data['state'] = STATE_START

async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    current_state = context.user_data.get('state', STATE_START)

    if current_state == STATE_START:
        if text == 'yes':
            # Prepare for the quiz
            keyboard = [['3 Questions', '5 Questions', '10 Questions']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Choose the number of questions:', reply_markup=reply_markup)
            context.user_data['state'] = STATE_QUIZ
        elif text == 'no':
            await update.message.reply_text('Good Bye!', reply_markup=ReplyKeyboardRemove())
            context.user_data.clear()
        else:
            await update.message.reply_text('Please click Yes or No.')

    elif current_state == STATE_QUIZ:
        # Handle quiz question number selection
        try:
            num_questions = int(text.split()[0])
            if num_questions > len(FLASHCARDS):
                await update.message.reply_text('Not enough flashcards available.')
                num_questions = len(FLASHCARDS)
            questions = random.sample(list(FLASHCARDS.items()), k=num_questions)
            context.user_data['questions'] = questions
            context.user_data['total'] = num_questions
            context.user_data['correct'] = 0
            context.user_data['index'] = 0
            context.user_data['state'] = STATE_ANSWERING
            await ask_question(update, context)
        except ValueError:
            await update.message.reply_text('Please select a valid number of questions.')

async def handle_answer(update: Update, context: CallbackContext):
    # Ensure we are in the answering state
    if context.user_data.get('state') == STATE_ANSWERING:
        text = update.message.text.lower()
        question_data = context.user_data['questions'][context.user_data['index']]
        correct_answer = question_data['answer']

        if text == correct_answer.lower():
            response = "Correct!"
            context.user_data['correct'] += 1
        else:
            response = f"Incorrect! The correct answer was {correct_answer}."

        await update.message.reply_text(response)
        context.user_data['index'] += 1
        if context.user_data['index'] < len(context.user_data['questions']):
            await ask_question(update, context)
        else:
            await update.message.reply_text(
                f'Quiz complete! You answered {context.user_data["correct"]} out of {context.user_data["total"]} correctly.',
                reply_markup=ReplyKeyboardRemove())
            context.user_data.clear()
    else:
        await update.message.reply_text("Please start a quiz by typing 'Yes' or select the number of questions.")


async def question(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    num_questions = int(query.data)
    if num_questions > len(FLASHCARDS):
        await query.message.reply_text('Not enough flashcards to fulfill the request. Lowering question count.')
        num_questions = len(FLASHCARDS)  # Lower the number of questions to the maximum available
    questions = random.sample(list(FLASHCARDS.items()), k=num_questions)
    context.user_data['questions'] = questions
    context.user_data['total'] = num_questions
    context.user_data['correct'] = 0
    context.user_data['index'] = 0
    await ask_question(update, context)

async def ask_question(update: Update, context: CallbackContext):
    questions = context.user_data['questions']
    index = context.user_data['index']
    if index < len(questions):
        word, data = questions[index]
        keyboard = [[ReplyKeyboardMarkup(option, callback_data=option) for option in data['options']]]
        reply_markup = ReplyKeyboardMarkup(keyboard)
        await update.callback_query.message.reply_text(data['question'], reply_markup=reply_markup)
    else:
        await update.callback_query.message.reply_text(
            f'Quiz complete! You answered {context.user_data["correct"]} out of {context.user_data["total"]} correctly.')
        context.user_data.clear()



async def handle_answer(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    await query.answer()
    selected_option = query.data
    question_data = context.user_data['questions'][context.user_data['index']]
    if selected_option == question_data[1]['answer']:
        context.user_data['correct'] += 1
        response = "Correct!"
    else:
        response = f"Incorrect! The correct answer was {question_data[1]['answer']}."
    await query.edit_message_text(text=f"{response}")
    context.user_data['index'] += 1
    await ask_question(update, context)

def main():
    TOKEN = '6731366092:AAHZNbxjzdtU0m8aC5iTKAEeocD0hdM4x1c'
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(MessageHandler(filters.TEXT & (filters.Regex('^(option1|option2|correct|option3|option4)$')), handle_answer))
    app.run_polling()

if __name__ == '__main__':
    main()