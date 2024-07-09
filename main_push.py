import requests
from bs4 import BeautifulSoup
import pandas as pd
import yaml
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

try:
    from rich import print
except ImportError:
    pass

url = "https://news.yahoo.co.jp/topics/top-picks"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

response = requests.get(url, headers=headers)
if response.status_code == 200:
    page_content = response.content
    soup = BeautifulSoup(page_content, "html.parser")
    articles = []
    for article in soup.find_all('a'):
        if article.get('href') is not None:
            link = article.get('href')
            title = article.find('div', class_='newsFeed_item_title')
            if link is not None and title is not None:
                articles.append({'Title': title.get_text(), 'Link': link})
    df = pd.DataFrame(articles)
    df.to_csv('yahoo_news.csv', index=False, encoding='utf-8-sig')
else:
    print(f"Failed to retrieve the page. Status code: {response.status_code}")

response = requests.get("https://news.goo.ne.jp/topstories/backnumber/all/")
response.encoding = response.apparent_encoding
soup = BeautifulSoup(response.text, 'html.parser')
news_list = []
articles = soup.find_all('li')
for article in articles:
    p_tag = article.find('p')
    if p_tag and p_tag.get('class') == ['list-title-topics', 'margin-bottom5']:
        title = article.get_text().strip()
        link = article.find('a')['href']
        news_list.append({'Title': title, 'Link': link})
df = pd.DataFrame(news_list)
df.to_csv('goo_news.csv', index=False, encoding='utf-8-sig')

with open("config.yaml", 'r') as file:
    yamlfile = yaml.safe_load(file)

chatgpt_key = yamlfile["chatgpt_key"]
endpoint = "https://api.openai.com/v1/completions"
api_key = chatgpt_key
file_path = "yahoo_news.csv"
slack_channel = yamlfile["slack_channel"]

with open(file_path, "r", encoding="utf-8") as file:
    text = file.read()

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}

data = {
    "model": "gpt-3.5-turbo",
    "prompt": text,
    "max_tokens": 100
}

response = requests.post(endpoint, json=data, headers=headers)

token = yamlfile["slack_token"]
slack_id = yamlfile["slack_id"]
slack_client = WebClient(token=token)

def send_notification(channel, message, slack_client=slack_client):
    try:
        slack_client.chat_postMessage(channel=channel, text=message)
    except SlackApiError as e:
        print(f"Error sending message: {e.response['error']}")

file_path = "yahoo_news.csv"
with open(file_path, 'r', encoding='utf-8') as file:
    text_yahoo = file.read()

file_path = "goo_news.csv"
with open(file_path, 'r', encoding='utf-8') as file:
    text_goo = file.read()

text = text_yahoo + text_goo

from openai import OpenAI
client = OpenAI(api_key=chatgpt_key)

completion = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "This is a file summarizing the news of the day. Please select the most important ones and tell me what you have gathered and summarized the details from the links.The answer should be made in Japanese and in the following manner: ・駅ホームで友人が転落 9歳が救う 概要: 駅のホームで友人が転落した際、9歳の子供が救助しました。 リンク: Yahooニュース"},
        {"role": "user", "content": text}
    ]
)

message = completion.choices[0].message.content
send_notification(slack_channel, message)
