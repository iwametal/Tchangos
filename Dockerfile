FROM python:3.11-slim

WORKDIR /app

RUN pip install poetry
RUN poetry config virtualenvs.create false

COPY . ./
RUN poetry install

CMD ["python", "./tchangos/src/bot.py"]
