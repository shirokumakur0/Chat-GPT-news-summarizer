# ChatGPT-news-summarizer

Code for an automatic news summarizer with ChatGPT. This is a class assignment for the "Introduction Course for AI Practitioners" during the 2024 spring semester.

- main_push.py: collects today's latest news from various media sources, creates local databases, and sends a summary to an integrated Slack workspace
- main_interact.py: receives messages on a Slack channel and responds based on the databases.

### Preparations

1. Create a 'config.yaml' file and store the following information:
-- chatgpt_key: [chat-gpt-api-key](https://platform.openai.com/docs/api-reference/introduction)
-- slack_token: [slack-bot-token](https://api.slack.com/concepts/token-types#bot)
-- slack_id: [bot's-member-ID](https://api.slack.com/methods/users.identity)
-- app_token: [slack-event-api-key](https://api.slack.com/apis/events-api)
-- slack_channel: slack channel name to send message

1. Expose the local PC's web server to the outside by using [ngrok](https://ngrok.com/).