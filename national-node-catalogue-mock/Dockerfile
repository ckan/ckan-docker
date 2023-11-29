FROM python:3.11

COPY ./ /code

WORKDIR /code

RUN pip install --no-cache-dir --upgrade -r requirements.txt

CMD ["python", "main.py"]
