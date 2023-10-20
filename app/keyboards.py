from telebot.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton, \
    ReplyKeyboardRemove

keyboard_main = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard_main.row(
    KeyboardButton("/create"),
    KeyboardButton("/update"),
    KeyboardButton("/get_all"),
)

close_keyboard = ReplyKeyboardRemove()
