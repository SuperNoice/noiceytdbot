FROM python:3

WORKDIR /usr/src/app

COPY requirements.txt ./
COPY install.sh ./
RUN apt update && apt install -y nodejs npm && npm install deno && pip install --no-cache-dir -r requirements.txt && bash install.sh && apt clean

COPY ./bot ./bot
WORKDIR /usr/src/app/bot

CMD [ "python", "./bot.py" ]