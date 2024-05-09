from telegram import Update,  ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackContext, MessageHandler, filters
import random

STATE_START, STATE_QUIZ, STATE_ANSWERING, STATE_DECIDING,STATE_ADD_QUESTION = range(5)

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
            keyboard = [['3 Questions', '5 Questions', '10 Questions']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Choose the number of questions:', reply_markup=reply_markup)
            context.user_data['state'] = STATE_QUIZ
        elif text == 'no':
            keyboard = [['Add a Question', 'Good Bye']]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
            await update.message.reply_text('Would you like to add a question or say goodbye?', reply_markup=reply_markup)
            context.user_data['state'] = STATE_DECIDING
        else:
            await update.message.reply_text('Please click Yes or No.')

    elif current_state == STATE_QUIZ:
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
    
    elif current_state == STATE_ADD_QUESTION:
        if 'temp_question' not in context.user_data:
            context.user_data['temp_question'] = {'question': text}
            await update.message.reply_text('Please enter the options separated by commas (e.g., option1, option2, correct, option4):')
        elif 'options' not in context.user_data['temp_question']:
            options = text.split(',')
            context.user_data['temp_question']['options'] = options
            await update.message.reply_text('Which one is the correct answer? Please type exactly as you listed in options.')
        else:
            correct_answer = text
            if correct_answer in context.user_data['temp_question']['options']:
                context.user_data['temp_question']['answer'] = correct_answer
                FLASHCARDS[f"word{len(FLASHCARDS) + 1}"] = context.user_data['temp_question']
                await update.message.reply_text('Your question has been added!')
                context.user_data.pop('temp_question', None)
                context.user_data['state'] = STATE_START  # Reset to start
            else:
                await update.message.reply_text('The correct answer must match one of the options. Please re-enter the correct answer.')


    elif current_state == STATE_DECIDING:
        if text == 'add a question':
            await update.message.reply_text('Please enter your question:')
            context.user_data['state'] = STATE_ADD_QUESTION
        elif text == 'good bye':
            await update.message.reply_text('Good Bye!', reply_markup=ReplyKeyboardRemove())
            context.user_data.clear()
        else:
            await update.message.reply_text('Please choose "Add a Question" or "Good Bye".')

    elif current_state == STATE_ANSWERING:
        await handle_answer(update, context)
       

async def ask_question(update: Update, context: CallbackContext):
    questions = context.user_data['questions']
    index = context.user_data['index']
    if index < len(questions):
        word, data = questions[index]
        options = data['options']
        keyboard = [options[i:i + 2] for i in range(0, len(options), 2)]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
        await update.message.reply_text(data['question'], reply_markup=reply_markup)
    else:
        await update.message.reply_text(
            f'Quiz complete! You answered {context.user_data["correct"]} out of {context.user_data["total"]} correctly.',
            reply_markup=ReplyKeyboardRemove())
        context.user_data.clear()

async def handle_answer(update: Update, context: CallbackContext):
    text = update.message.text.lower()
    question_data = context.user_data['questions'][context.user_data['index']]
    correct_answer = question_data[1]['answer']

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
        await end_quiz(update, context)

async def end_quiz(update: Update, context: CallbackContext):
    await update.message.reply_text(
        f'Quiz complete! You answered {context.user_data["correct"]} out of {context.user_data["total"]} correctly.',
        reply_markup=ReplyKeyboardRemove())
    context.user_data.clear()

def main():
    TOKEN = '6731366092:AAHZNbxjzdtU0m8aC5iTKAEeocD0hdM4x1c'
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    app.run_polling()

if __name__ == '__main__':
    main()