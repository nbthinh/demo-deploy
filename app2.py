# Python libraries that we need to import for our bot
import random
from flask import Flask, request
from pymessenger.bot import Bot
import os
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
        output = request.get_json()
        for event in output['entry']:
            messaging = event['messaging']
            for message in messaging:
                if message.get('message'):
                    # Facebook Messenger ID for user so we know where to send response back to
                    recipient_id = message['sender']['id']
                    if message['message'].get('text'):
                        response_sent_text = get_message()
                        """
                        Tạm thời giải thuật recommendation system sẽ viết trong này
                        """
                        send_message(recipient_id, response_sent_text)
                    # if user sends us a GIF, photo,video, or any other non-text item
                    if message['message'].get('attachments'):
                        response_sent_nontext = get_message()
                        send_message(recipient_id, response_sent_nontext)
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
