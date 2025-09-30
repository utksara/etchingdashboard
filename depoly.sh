
export PROJECT_ID="river-data-470013-r4"
export REGION="europe-west1" 
export REPO_NAME="etching-dashboard"
export IMAGE_NAME="etching-dashboard"
export IMAGE_TAG="v1.0" 

# This is the full image path you'll use
export FULL_IMAGE_PATH="${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}/${IMAGE_NAME}:${IMAGE_TAG}"

# You can double-check the image exists with this command
gcloud artifacts docker images list ${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO_NAME}

# ------------------------------------------------------------------

git commit -m "docker changes"


docker build -t django-docker .
docker tag c7e8011046e7 us-central1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker:v1.0
docker push us-central1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker:v1.0
docker tag c7e8011046e7 europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker:v1.0
docker push europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker:v1.0

# docker remove images
docker rmi django-docker:us-central1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker
docker rmi etching-dashboard:v1
docker rmi gcr.io/europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker:v1

# docker tagging
docker tag etching-dashboard gcr.io/europe-west1/river-data-470013-r4/etching-dashboard:v1
docker push gcr.io/europe-west1/river-data-470013-r4/etching-dashboard:v1
docker logout gcr.io
docker push gcr.io/europe-west1/river-data-470013-r4/etching-dashboard:v1
docker images
docker rmi gcr.io/europe-west1/river-data-470013-r4/etching-dashboard:v1
docker tag etching-dashboard europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/etching-dashboard:v1.0
docker build -t etching-dashboard .
docker push gcr.io/europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/django-docker:v1
docker tag etching-dashboard:latest europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/etching-dashboard:v1.0
docker push europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/etching-dashboard:v1.0

gcloud auth configure-docker
gcloud auth configure-docker
gcloud run deploy etching-dashboard --image=europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/etching-dashboard:v1.0 --platform=managed --region=europe-west1 --allow-unauthenticated
gcloud auth configure-docker 
gcloud artifacts docker images push etching-dashboard europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/etching-dashboard:v1.0
gcloud auth configure-docker europe-west1-docker.pkg.dev
gcloud artifacts docker images list europe-west1-docker.pkg.dev/river-data-470013-r4/etching-dashboard/etching-dashboard:v1.0

rm ~/.docker/config.json
