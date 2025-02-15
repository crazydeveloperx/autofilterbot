FROM python:3.10

WORKDIR /AutoFilterBot

COPY . /AutoFilterBot

RUN pip install -r requirements.txt

CMD ["python", "bot.py"]
