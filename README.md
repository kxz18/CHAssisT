# python-wechaty 群聊助手机器人[![Python 3.7](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/release/python-370/)

<img src="./images/logo.png" alt="logo" style="zoom:100%;"/> 

## Usage

### Connecting Chatbots

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-brightgreen.svg)](https://github.com/Wechaty/wechaty)

Wechaty is a RPA SDK for Wechat **Individual** Account that can help you create a chatbot in 9 lines of Python.

### Requirements

1. python3.7+

### Quick Start

1. Clone this repository

   ```shell
   git clone https://github.com/kxz18/python-wechaty-groupchat-bot
   cd python-wechaty-groupchat-bot
   ```

2. Install Dependencies

   ```shell
   make install
   # or
   pip install -r requirements.txt
   ```

3. Set token for your bot

    ```sh
    # examples/ding-dong-bot.py : func-> main()
    # it must be donut token
    export WECHATY_PUPPET=wechaty-puppet-hostie
    export WECHATY_PUPPET_HOSTIE_TOKEN=your_token_at_here
    ```

4. Run the bot

   ```shell
   make bot
   # or
   python examples/ding-dong-bot.py
   ```

## Functions

To use the bot in a group chat, say something and @bot to let it know you are talking to it. To use the bot in private chat, just talk to it.

- help doc
  - Send `KEY_HELP` to the bot for help on usage.  Value of `KEY_HELP` depends on the language you chose, ”帮助“ for Chinese and "help" for English.
  - For all functions below, access to more specific expanation is available in the reply to `KEY_HELP` of the bot.

- Tagging
  - Quote some important message and reply with the tag you want to add on the message.
  - When asked with some questions, the bot will try to find a answer with the tag matching the question well. If it doesn't have enough confidence on the answer it found, it will list some of the possible keywords and ask for more specific question.
  - Browsing the saved message is possible. You can either browse all of them or some of them in a given time span.
  - Deleting the saved message is possible. Scheduled deleting function is also available with flexible period.
  - message can be saved with an expiry, after which the message will be automatically deleted. 
- timed task
  - The bot can help to to send time-scheduled message, either on a certain time point or periodically.
- member manager
  - The bot will welcome newly joined members
  - The bot will remove some unwelcome chatting members with a voting mechanism.

