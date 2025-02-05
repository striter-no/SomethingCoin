# Проект SomeThing Coin ($SMTH)

Проект создавался в качестве *POC* (proof of concept). Главная задумка - создание криптовалюты, понимание принципов её работы

## Как запустить

Первоначально, задумывалось, как `userbot` для телеграм, для запуска:

```sh
python -m venv venv
source ./venv/bin/activate

pip install -r requirements.txt

python main.py
```

После этого вы можете прописать в любой чат

```
>smth h
```

И выведется сообщение помощи. Сообщения можно изменять в `configs/messages.json`