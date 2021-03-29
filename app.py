# Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import os
import psycopg2
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

# Tham khảo tại đây: https://www.twilio.com/blog/2017/12/facebook-messenger-bot-python.html
app = Flask(__name__)
# ACCESS_TOKEN của trang `Demo RS`
# ACCESS_TOKEN = 'EAAGNZAZCsaZBD0BAOb6ngiZCJC3tUmhcEBniGFRmllSkoZBBHvnqRqufd8eWhS26ezwClMhIW133YSdCNfOGIAjU2kVpcjadS27IbMAIRZANtijl6a7BZAniU4ZCegS1a5sSv63YZBpIU0ZA4CRqZAaCLh6mVJ2KzmqbQxMJZAcYAK1aDQZDZD'

# ACCESS TOKEN của trang `Page for Recommendation System`
ACCESS_TOKEN = 'EAAGNZAZCsaZBD0BAGPGrZBxJoud24MFT7Btw60qpZC2EyBDFEWo4hJZBOdiE9CYoNNVeQNTKVcr62KgNVgjzlP8XKNkLLeF1PicirxnKN9dzZAtBgAa1Nuc2oVKkVv9PeEgDgIrEvzndlbmj1wz8WiJZAjPP0beDIvrZA9vrSF3LzEQZDZD'
VERIFY_TOKEN = 'secret'

# ACCESS_TOKEN = os.environ['ACCESS_TOKEN']
# VERIFY_TOKEN = os.environ['VERIFY_TOKEN']
bot = Bot(ACCESS_TOKEN)

# We will receive messages that Facebook sends our bot at this endpoint
@app.route("/demo")
def demo():
    DB_HOST = 'ec2-23-21-229-200.compute-1.amazonaws.com'
    DB_NAME = 'd4k5c62e1ofteh'
    DB_USER = 'gljdcsupgxcqkl'
    DB_PASS = '0f13baa951eff711d3645bca70aeea92a8e471d9c7ea66bc2410d512046f9cfa'
    conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
    sql ='''SELECT * FROM san_pham'''
    cur = conn.cursor()
    cur.execute(sql)
    ourdata = cur.fetchall()
    # print(ourdata)
    # ourdata = ourdata[0][2]
    col_name = ["id_sanpham", "Loai_sp", "Ten_sp", "Mo_ta_sp", "Gia_tien", "Cau_hinh"]
    df = pd.DataFrame(ourdata, columns=col_name)
    # print(df)
    return "Thay phun dep trai"

@app.route("/", methods=['GET', 'POST'])
def receive_message():
    if request.method == 'GET':
        """Before allowing people to message your bot, Facebook has implemented a verify token
        that confirms all requests that your bot receives came from Facebook."""
        token_sent = request.args.get("hub.verify_token")
        print(token_sent)
        return verify_fb_token(token_sent)
    # if the request was not get, it must be POST and we can just proceed with sending a message back to user
    else:
        # get whatever message a user sent the bot
        DB_HOST = 'ec2-23-21-229-200.compute-1.amazonaws.com'
        DB_NAME = 'd4k5c62e1ofteh'
        DB_USER = 'gljdcsupgxcqkl'
        DB_PASS = '0f13baa951eff711d3645bca70aeea92a8e471d9c7ea66bc2410d512046f9cfa'
        conn = psycopg2.connect(database=DB_NAME, user=DB_USER, password=DB_PASS, host=DB_HOST)
        sql ='''SELECT * FROM san_pham'''
        cur = conn.cursor()
        cur.execute(sql)
        ourdata = cur.fetchall()
        col_name = ["id_sanpham", "Loai_sp", "Ten_sp", "Mo_ta_sp", "Gia_tien", "Cau_hinh"]
        df = pd.DataFrame(ourdata, columns=col_name)
        replace_by_space = ["/", ",", "-", ". ", "\n"]
        replace_by_ignore = ["(", ")", "."]
        added_col = []

        for each_index in df.index:
            val1 = df["Ten_sp"][each_index]
            # val2 = df["Mo_ta_sp"][each_index]
            # val3 = df["Gia_tien"][each_index]
            # combine = val1 + " " + val2 + " " + str(val3)
            combine = val1
            for each_replace in replace_by_space:
                combine = combine.replace(each_replace, " ")
            for each_replace in replace_by_ignore:
                combine = combine.replace(each_replace, "")
            combine = combine.lower()
            added_col.append(combine)
        df["Process_data"] = added_col

        vectorizer = TfidfVectorizer()
        vectorizer.fit(df["Process_data"])
        tfidf = vectorizer.transform(df["Process_data"])
        feature_vector = tfidf.todense()

        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    text = message['message'].get('text')
                    if text:
                        # response_sent_text = get_message()
                        
                        returntext = "anh phong"
                        """
                        Tạm thời giải thuật recommendation system sẽ viết trong này
                        """
                        _2tfidf = vectorizer.transform([text])
                        sim_scores = linear_kernel(_2tfidf, tfidf)
                        sim_scores_idx = list(enumerate(sim_scores))
                        sim_scores = sorted(sim_scores_idx, key=lambda x: x[1], reverse=True)
                        idx_choose = sim_scores[0]
                        returntext = df['Ten_sp'].iloc(idx_choose)
                        """
                        Tạm thời giải thuật recommendation system sẽ viết trong này
                        """
                        send_message(recipient_id, returntext)
                    # if user sends us a GIF, photo,video, or any other non-text item

                    # if message['message'].get('attachments'):
                    #     response_sent_nontext = get_message()
                    #     send_message(recipient_id, response_sent_nontext)
    return "Message Processed"


def verify_fb_token(token_sent):
    # take token sent by facebook and verify it matches the verify token you sent
    # if they match, allow the request, else return an error
    if token_sent == VERIFY_TOKEN:
        return request.args.get("hub.challenge")
    return 'Invalid verification token'


# chooses a random message to send to the user
def get_message():
    sample_responses = ["You are stunning!", "We're proud of you.",
                        "Keep on being you!", "We're greatful to know you :)"]
    # return selected item to the user
    return random.choice(sample_responses)

# uses PyMessenger to send response to user


def send_message(recipient_id, response):
    # sends user the text message provided via input response parameter
    bot.send_text_message(recipient_id, response)
    return "success"


if __name__ == "__main__":
    app.run()
