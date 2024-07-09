from flask import Flask, request, jsonify
import requests
import yaml

app = Flask(__name__)

# Load configuration
with open("config.yaml", 'r') as file:
    yamlfile = yaml.safe_load(file)

chatgpt_key = yamlfile["chatgpt_key"]
slack_token = yamlfile["slack_token"]
app_token = yamlfile["app_token"]
slack_id = yamlfile["slack_id"]

SLACK_BOT_TOKEN =  yamlfile["slack_token"]
OPENAI_API_KEY =  yamlfile["chatgpt_key"]

file_path = "yahoo_news.csv"
with open(file_path, 'r', encoding='utf-8') as file:
    text_yahoo = file.read()

file_path = "goo_news.csv"
with open(file_path, 'r', encoding='utf-8') as file:
    text_goo = file.read()

text = text_yahoo + text_goo

from openai import OpenAI
def send_message_to_chatgpt(message):
    client = OpenAI(api_key=chatgpt_key)

    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": f"Please answer queries from users. Answers must be made in Japanese and based on the following contents: {text}"},
            {"role": "user", "content": message}
        ]
    )
    return completion

@app.route('/slack/events', methods=['POST'])
def slack_events():
    data = request.json
    if 'challenge' in data:
        return jsonify({'challenge': data['challenge']})
    
    if 'event' in data:
        event = data['event']
        if event.get('type') == 'message':
            message = event.get('text')
            if message is not None:
                if f"<@{slack_id}>" in message:
                    chatgpt_response_completion = send_message_to_chatgpt(message)
                    return_message = chatgpt_response_completion.choices[0].message.content
                    send_message_to_slack(event['channel'], return_message)
        
    return jsonify({'status': 'ok'})

def send_message_to_slack(channel, text):
    requests.post(
        'https://slack.com/api/chat.postMessage',
        headers={
            'Authorization': f'Bearer ' + SLACK_BOT_TOKEN,
            'Content-Type': 'application/json'
        },
        json={
            'channel': channel,
            'text': text
        }
    )

if __name__ == '__main__':
    app.run(port=3000)
