import os
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import  logging


logging.basicConfig()


token = "478975907:AAHmvk-XC4yw2kkhZZj3oS3aQLR63PDDfIc"
# token=str(bot_id)+""
updater = Updater(token)
disp=updater.dispatcher



photo_dict={}


channel_id="@fancaPhoto"


def photo_reciever(bot,update):



    file_id=update.message.photo[0].file_id

    print(f"Recieved photo with {file_id} id")

    inline = InlineKeyboardMarkup([
        [InlineKeyboardButton("👍", callback_data="/vote y "+file_id),
         InlineKeyboardButton("👎", callback_data="/vote n "+file_id)],

    ])


    photo_dict[file_id]={"yes":set(),"no":set()}


    bot.sendPhoto( photo=file_id ,chat_id=channel_id, reply_markup=inline)



def dis_like(bot, update):


    vote = update.callback_query.data.split()[1]
    file_id = update.callback_query.data.split()[2]

    print(f"got a {vote} vote fot the photo {file_id}")

    user_id=update.callback_query.from_user.id

    try:
        photo_dict[file_id]
    except KeyError:
        photo_dict[file_id]={"yes":set(),"no":set()}


    if vote=="y" and user_id not in photo_dict[file_id]['no']:
        photo_dict[file_id]['yes'].add(user_id)
        bot.answer_callback_query(update.callback_query.id,text="Hai votato si")

    elif vote=="n" and user_id not in photo_dict[file_id]['yes']:
        photo_dict[file_id]['no'].add(user_id)
        bot.answer_callback_query(update.callback_query.id,text="Hai votato no")

    else:
        print("User has already voted")
        bot.answer_callback_query(update.callback_query.id, text="Hai gia votato pirla", show_alert=True)
        return

    update_image_votes(bot,update,file_id)




def update_image_votes(bot, update,file_id):




    inline_yes="👍 "+str(len(photo_dict[file_id]['yes']))

    inline_no="👎 "+str(len(photo_dict[file_id]['no']))

    inline = InlineKeyboardMarkup([
        [InlineKeyboardButton(inline_yes, callback_data="/vote y " + file_id),
         InlineKeyboardButton(inline_no, callback_data="/vote n " + file_id)],

    ])

    bot.editMessageReplyMarkup(channel_id,
                               message_id=update.callback_query.message.message_id,
                               reply_markup=inline)



disp.add_handler(MessageHandler(Filters.photo, photo_reciever))
disp.add_handler(CallbackQueryHandler(dis_like, pattern="/vote"))



PORT = int(os.environ.get('PORT', '5000'))

# updater.start_webhook(listen="0.0.0.0",
#                               port=PORT,
#                               url_path="main")
# updater.bot.set_webhook("https://fancazzistibot.herokuapp.com/main")


print("polling")

updater.start_polling()

