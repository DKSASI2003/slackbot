import os
import time
from flask import Flask, request,jsonify
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

app = Flask(__name__)

# Load environment variables or set them directly
SLACK_TOKEN = os.getenv('SLACK_TOKEN') or "xoxb-5824702042788-7021940663892-jRIkZ85QHFtG3qveitfyGR1V"
CHANNEL_ID_OR_NAME = os.getenv('CHANNEL_ID_OR_NAME') or "C0708UKAY7N"

# Initialize WebClient
client = WebClient(token=SLACK_TOKEN)

# Define phrases indicating a request for resetting passwords
RESET_PHRASES = [
    "reset the password",
    "reset ipa password",
    "reset the ipa password",
    "cannot login jumpbox",
    "not able to login jumpbox"
]

# Message to send for a password reset request
RESET_MESSAGE = "Hi! Please reset your password using the following link: https://dummybawa.com"


@app.route('/slack/events', methods=['POST'])
def slack_events():
    """Handle Slack events."""
    data = request.json
    #print(data)
    # Check if it's a message event
    if data.get('type') == 'url_verification':
        challenge = data.get('challenge')
        if challenge:
            response_data = {
                "challenge": challenge
            }
            return jsonify(response_data)
    elif data.get('event')['type'] == 'message':
        #print(data)
        handle_message_event(data)
    return 'Received Slack event'


def handle_message_event(data):
    """Handle message events."""
    message = data['event']
    # Check if it's a bot message or doesn't have text
    if message.get('subtype') == 'bot_message' or 'text' not in message:
        return None
    text = message['text'].lower()
    if any(phrase in text for phrase in RESET_PHRASES):
        send_reset_message(message)


def send_reset_message(message):
    """Send a password reset message."""
    channel_id = message['channel']
    user_id = message['user']
    thread_ts = message.get("ts")
    message_to_send = f"<@{user_id}> {RESET_MESSAGE}"
    print(message)
    send_message(channel_id, message_to_send, thread_ts)


def send_message(channel_id, message, thread_ts):
    """Send a message to a Slack channel or thread."""
    try:
        response = client.chat_postMessage(
            channel=channel_id,
            text=message,
            thread_ts=thread_ts
        )
        print("Message sent successfully.")
        return response
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")
        return None


if __name__ == '__main__':
    app.run(debug=True)