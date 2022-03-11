#!/bin/sh
gcloud auth login
gcloud auth list
gcloud config set project transcibe-343721
gcloud services enable speech.googleapis.com
gcloud services enable storage.googleapis.com
export PROJECT_ID=$(gcloud config get-value core/project)
gcloud iam service-accounts create my-stt-sa --display-name "my stt service account"
gcloud iam service-accounts keys create key.json \
  --iam-account my-stt-sa@${PROJECT_ID}.iam.gserviceaccount.com
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
      --member serviceAccount:my-stt-sa@${PROJECT_ID}.iam.gserviceaccount.com \
      --role roles/storage.objectAdmin
gcloud projects add-iam-policy-binding ${PROJECT_ID} \
      --member serviceAccount:my-stt-sa@${PROJECT_ID}.iam.gserviceaccount.com \
      --role roles/cloudtranslate.user
export GOOGLE_APPLICATION_CREDENTIALS=key.json
pip install -r requirements.txt