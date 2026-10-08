pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE = 'les190/ams_backend'

        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')

        VPS_SSH_CREDENTIALS = 'contabo-ssh'
        VPS_HOST = '169.58.142.4'
        VPS_DEPLOY_DIR = '/opt/ams-backend'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Set Version') {
            steps {
                script {
                    env.IMAGE_TAG = sh(
                        script: 'git rev-parse --short=7 HEAD',
                        returnStdout: true
                    ).trim()

                    echo "AMS backend version: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv

                    . .venv/bin/activate

                    pip install --upgrade pip

                    pip install -r ams-proj/requirements.txt
                '''
            }
        }

        stage('Django Checks') {
            steps {
                sh '''
                    . .venv/bin/activate

                    cd ams-proj

                    python manage.py check
                '''
            }
        }

        stage('Docker Build & Push') {
            when {
                branch 'main'
            }

            steps {
                sh '''
                    set -e

                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login \
                        -u "$DOCKERHUB_CREDENTIALS_USR" \
                        --password-stdin

                    docker build \
                        --target production \
                        -t "$DOCKER_IMAGE:$IMAGE_TAG" \
                        -t "$DOCKER_IMAGE:production" \
                        .

                    docker push "$DOCKER_IMAGE:$IMAGE_TAG"

                    docker push "$DOCKER_IMAGE:production"

                    docker logout
                '''
            }
        }

        stage('Deploy to VPS') {
            when {
                branch 'main'
            }

            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${VPS_SSH_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USERNAME'
                    )
                ]) {

                    sh '''
                        set -e

                        ssh \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            "$SSH_USERNAME@$VPS_HOST" \
                            bash -s -- \
                            "$IMAGE_TAG" \
                            "$DOCKER_IMAGE" \
                            "$VPS_DEPLOY_DIR" <<'REMOTE_SCRIPT'

IMAGE_TAG="$1"
DOCKER_IMAGE="$2"
VPS_DEPLOY_DIR="$3"

set -e

echo "=========================================="
echo "AMS PRODUCTION DEPLOYMENT"
echo "=========================================="

echo "Image tag: $IMAGE_TAG"
echo "Docker image: $DOCKER_IMAGE"
echo "Deployment directory: $VPS_DEPLOY_DIR"

cd "$VPS_DEPLOY_DIR"

echo ""
echo "Checking deployment environment..."

if [ ! -f .env ]; then
    echo "ERROR: .env file not found."
    exit 1
fi

if [ ! -f .env.prod ]; then
    echo "ERROR: .env.prod file not found."
    exit 1
fi

set -a
. ./.env
set +a

if [ -z "$DOCKER_HUB_USERNAME" ]; then
    echo "ERROR: DOCKER_HUB_USERNAME is not set in .env."
    exit 1
fi

echo "Docker Hub username: $DOCKER_HUB_USERNAME"

echo ""
echo "Checking Docker Compose configuration..."

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    config -q

echo "Compose configuration is valid."

echo ""
echo "Pulling AMS application image..."

docker pull "$DOCKER_IMAGE:production"

echo ""
echo "Starting PostgreSQL and Redis..."

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    up -d db redis

echo ""
echo "Waiting for PostgreSQL to become healthy..."

DB_READY=0

for i in $(seq 1 30); do

    DB_STATUS=$(docker inspect \
        --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \
        ams-backend-db-1 2>/dev/null || true)

    echo "PostgreSQL status: $DB_STATUS"

    if [ "$DB_STATUS" = "healthy" ]; then
        DB_READY=1
        break
    fi

    sleep 2

done

if [ "$DB_READY" -ne 1 ]; then

    echo ""
    echo "ERROR: PostgreSQL did not become healthy."

    echo ""
    echo "PostgreSQL container status:"

    docker ps -a --filter name=ams-backend-db-1

    echo ""
    echo "PostgreSQL logs:"

    docker logs --tail 100 ams-backend-db-1

    exit 1
fi

echo ""
echo "PostgreSQL is healthy."

echo ""
echo "Waiting for Redis to become healthy..."

REDIS_READY=0

for i in $(seq 1 30); do

    REDIS_STATUS=$(docker inspect \
        --format='{{if .State.Health}}{{.State.Health.Status}}{{else}}no-healthcheck{{end}}' \
        ams-backend-redis-1 2>/dev/null || true)

    echo "Redis status: $REDIS_STATUS"

    if [ "$REDIS_STATUS" = "healthy" ]; then
        REDIS_READY=1
        break
    fi

    sleep 2

done

if [ "$REDIS_READY" -ne 1 ]; then

    echo ""
    echo "ERROR: Redis did not become healthy."

    echo ""
    echo "Redis container status:"

    docker ps -a --filter name=ams-backend-redis-1

    echo ""
    echo "Redis logs:"

    docker logs --tail 100 ams-backend-redis-1

    exit 1
fi

echo ""
echo "Redis is healthy."

echo ""
echo "Running database migrations..."

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    run --rm web \
    python manage.py migrate --noinput

echo ""
echo "Collecting static files..."

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    run --rm web \
    python manage.py collectstatic --noinput

echo ""
echo "Starting AMS application services..."

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    up -d \
    web \
    celery \
    celery-beat

echo ""
echo "Cleaning unused Docker images..."

docker image prune -f

echo ""
echo "=========================================="
echo "AMS DEPLOYMENT COMPLETED"
echo "=========================================="

echo ""
echo "Running containers:"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    ps

REMOTE_SCRIPT
                    '''
                }
            }
        }

        stage('Verify Deployment') {
            when {
                branch 'main'
            }

            steps {
                withCredentials([
                    sshUserPrivateKey(
                        credentialsId: "${VPS_SSH_CREDENTIALS}",
                        keyFileVariable: 'SSH_KEY',
                        usernameVariable: 'SSH_USERNAME'
                    )
                ]) {

                    sh '''
                        set -e

                        echo "Checking AMS containers on VPS..."

                        ssh \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            "$SSH_USERNAME@$VPS_HOST" \
                            bash -s -- \
                            "$VPS_DEPLOY_DIR" <<'REMOTE_VERIFY'

VPS_DEPLOY_DIR="$1"

set -e

cd "$VPS_DEPLOY_DIR"

echo "Container status:"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env \
    ps

echo ""
echo "Checking running AMS web container..."

WEB_STATUS=$(docker inspect \
    --format='{{.State.Status}}' \
    ams-backend-web-1 2>/dev/null || true)

if [ "$WEB_STATUS" != "running" ]; then
    echo "ERROR: AMS web container is not running."
    exit 1
fi

echo "AMS web container is running."

echo ""
echo "AMS deployment verification completed."

REMOTE_VERIFY
                    '''
                }
            }
        }
    }

    post {

        success {
            echo "AMS backend CI/CD completed successfully."
        }

        failure {
            echo "AMS backend CI/CD failed."
        }

        cleanup {
            sh '''
                rm -rf .venv || true
            '''
        }
    }
}