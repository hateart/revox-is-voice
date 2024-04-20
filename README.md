# revox-is-voice

docker build --tag=google_revox_accent_image .
docker run -p 8000:8000 --name=google_revox_accent_container google_revox_accent_image
curl -X POST -d "@sample_input.json" -H "Content-Type: application/json" http://localhost:8000/predict

PROJECT_ID=vi-ai-405108
REGION=us-central1
REPOSITORY=revox
IMAGE=revox_is_voice_v2

docker login
docker build --tag=$REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE .
docker run -p 8000:8000 --name=$IMAGE $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE
gcloud auth login
gcloud config set project $PROJECT_ID
gcloud config get-value project
gcloud auth configure-docker $REGION-docker.pkg.dev
docker push $REGION-docker.pkg.dev/$PROJECT_ID/$REPOSITORY/$IMAGE

---
empty example audios/25/3578100_bfa63af9-f37c-1746-ccaa-21ec327fb6d4.mp3
normal exmale  audios/308265/3656735_9a054a46-05f1-bf0b-fc74-0da8c3a7e4b3.mp3