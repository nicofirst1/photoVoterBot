import os
from urllib import parse
import telegram
from telegram.ext import Updater, MessageHandler, Filters, CallbackQueryHandler, CommandHandler
from telegram.inline.inlinekeyboardbutton import InlineKeyboardButton
from telegram.inline.inlinekeyboardmarkup import InlineKeyboardMarkup
import  logging


import psycopg2
import psycopg2.extras

logging.basicConfig()


token = "478975907:AAHmvk-XC4yw2kkhZZj3oS3aQLR63PDDfIc"
# token=str(bot_id)+""
updater = Updater(token)
disp=updater.dispatcher





channel_id="@fancaPhoto"
#channel_id="@provaaaaaaaaaaaaaaaaaaaa"

def photo_reciever(bot,update):

    photo_dict=get_votes()

    file_id=update.message.photo[0].file_id

    if not isinstance(photo_dict,list):photo_dict=[photo_dict]

    if file_id in [elem["file_id"] for elem in photo_dict]:
        update.message.reply_text("Questa foto è gia stata caricata")
        return



    print(f"Recieved photo with {file_id} id")

    inline = InlineKeyboardMarkup([
        [InlineKeyboardButton("👍", callback_data="/vote y "+file_id),
         InlineKeyboardButton("👎", callback_data="/vote n "+file_id)],

    ])



    insert_fileid(file_id,[],[])


    bot.sendPhoto( photo=file_id ,chat_id=channel_id, reply_markup=inline)

    update.message.reply_text("Vota la foto che hai mandato sul canale https://t.me/fancaPhoto")



def insert_fileid(file_id, yes, no):
    execute("INSERT INTO photos (file_id,yes,no) VALUES (%s,%s,%s)  ON CONFLICT(file_id) DO NOTHING; ",
            (file_id,yes,no,))


def dis_like(bot, update):


    photo_dict=get_votes()

    vote = update.callback_query.data.split()[1]
    file_id = update.callback_query.data.split()[2]

    print(f"got a {vote} vote fot the photo {file_id}")

    user_id=update.callback_query.from_user.id

    if file_id not in [elem['file_id'] for elem in photo_dict]:
        photo_dict.append({file_id:{'yes':set(),'no':set()}})



    specific_file=next((elem for elem in photo_dict if elem['file_id']==file_id))


    if user_id in specific_file['yes'] or user_id in specific_file['no']:
        print("User has already voted")
        bot.answer_callback_query(update.callback_query.id, text="Hai gia votato pirla", show_alert=True)
        return


    elif vote=="y" :
        specific_file['yes'].append(user_id)
        bot.answer_callback_query(update.callback_query.id,text="Hai votato si")

    elif vote=="n" :
        specific_file['no'].append(user_id)
        bot.answer_callback_query(update.callback_query.id,text="Hai votato no")

    else:
        print("User has already voted")
        bot.answer_callback_query(update.callback_query.id, text="Hai gia votato pirla", show_alert=True)
        return

    update_image_votes(bot,update,file_id,len(specific_file['yes']),len(specific_file['no']))

    new_photo_dict=[]
    for elem in photo_dict:
        if file_id in elem.keys():
            elem[file_id]=specific_file

        new_photo_dict.append(elem)

    save_votes(new_photo_dict)



def update_image_votes(bot, update,file_id,yes_num,no_num):




    inline_yes="👍 "+str(yes_num)

    inline_no="👎 "+str(no_num)

    inline = InlineKeyboardMarkup([
        [InlineKeyboardButton(inline_yes, callback_data="/vote y " + file_id),
         InlineKeyboardButton(inline_no, callback_data="/vote n " + file_id)],

    ])
    try:
        bot.editMessageReplyMarkup(channel_id,
                               message_id=update.callback_query.message.message_id,
                               reply_markup=inline)
    except telegram.error.BadRequest:
        pass



def get_votes():
    """get the photo dict"""
    res=execute("SELECT * FROM photos")
    if not isinstance(res,list):res=[res]

    return res

def save_votes(photo_dict):

    for photo in photo_dict:
        execute("UPDATE photos SET yes = %s, no = %s  WHERE file_id = %s",(photo['yes'],photo['no'],photo['file_id'],))


def connect_db():
    try:
        parse.uses_netloc.append("postgres")
        conn = psycopg2.connect(
            database="d286ke50intf6p",
            user="dsdpaxzpkggmos",
            password="ff1a7de37d1fe59bc61eaa8aa34b28b291a701c7869cdf7475d73da10506c60a",
            host="ec2-54-247-95-125.eu-west-1.compute.amazonaws.com",
            port="5432"
        )
        conn.autocommit = True
        return conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    except Exception:
        return None

def start_help(bot,update):
    update.message.reply_text("Inviami una foto per farla apparire sul canale "+channel_id)

def execute(query, param=None):
    cursor = connect_db()
    if cursor is not None:
        try:
            cursor.execute(query, param)
            if "SELECT" in query:
                if cursor.rowcount == 1:
                    return dict(cursor.fetchone())
                else:
                    return [dict(record) for record in cursor]
            elif "RETURNING" in query:
                if cursor.rowcount:
                    return [dict(record) for record in cursor]
                else:
                    return True
            else:
                return True
        except Exception as error:
            print("ERRORE {} \n{}\n{}".format(error, query, param))
            return False

            # connessione al db

def delete_all():
    execute("DELETE from photos")

if __name__ == '__main__':

    disp.add_handler(MessageHandler(Filters.photo, photo_reciever))
    disp.add_handler(CommandHandler("help",start_help))
    disp.add_handler(CommandHandler("start",start_help))
    disp.add_handler(CallbackQueryHandler(dis_like, pattern="/vote"))

    PORT = int(os.environ.get('PORT', '5000'))

    updater.start_webhook(listen="0.0.0.0",
                         port=PORT,
                        url_path="main.py")
    updater.bot.set_webhook("https://photovoterbot.herokuapp.com/main.py")

    updater.idle()

    print("polling")

    #updater.start_polling()

    photo_dict=get_votes()

    if photo_dict is False:
        execute("""
        CREATE TABLE photos (
        file_id        text PRIMARY KEY ,
        yes        integer[],
        no          integer[]
        );""")


