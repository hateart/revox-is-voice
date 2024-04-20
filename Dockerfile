FROM --platform=linux/amd64 python:3.10

WORKDIR /app

COPY requirements.txt ./

RUN apt-get update && apt-get install -y libsndfile1 libasound-dev portaudio19-dev libportaudio2 libportaudiocpp0 ffmpeg

RUN pip install --no-cache-dir -r requirements.txt

ENV GUNICORN_CMD_ARGS="--bind=0.0.0.0:8000 --chdir=/app --workers 8  --timeout 120"

COPY . .

EXPOSE 8000

CMD [ "gunicorn", "app:app" ]