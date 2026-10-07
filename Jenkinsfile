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
        VPS_USER = 'leslie-cheghe'
        VPS_DEPLOY_DIR = '/opt/ams-backend'

        DJANGO_SETTINGS_MODULE = 'umsproj.settings.production'
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

                    echo "AMS version: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Verify Main Branch') {
            steps {
                script {
                    def commit = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Git commit: ${commit}"
                    echo "Jenkins BRANCH_NAME: ${env.BRANCH_NAME ?: '(not set)'}"
                    echo "Jenkins GIT_BRANCH: ${env.GIT_BRANCH ?: '(not set)'}"

                    if (
                        env.GIT_BRANCH != null &&
                        env.GIT_BRANCH != 'origin/main' &&
                        env.GIT_BRANCH != 'main'
                    ) {
                        error(
                            "Deployment pipeline must run from main. " +
                            "GIT_BRANCH=${env.GIT_BRANCH}"
                        )
                    }
                }
            }
        }

        stage('Django Checks') {
            steps {
                sh '''
                    set -e

                    echo "========================================"
                    echo "Running Django system checks"
                    echo "========================================"

                    cd ams-proj

                    echo "Working directory:"
                    pwd

                    echo "Settings: $DJANGO_SETTINGS_MODULE"

                    python3 -m venv .venv
                    . .venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt

                    DJANGO_SETTINGS_MODULE="$DJANGO_SETTINGS_MODULE" \
                    python manage.py check

                    deactivate
                '''
            }
        }

        stage('Docker Build & Push') {
            steps {
                sh '''
                    set -e

                    echo "========================================"
                    echo "Building AMS production image"
                    echo "Image: $DOCKER_IMAGE"
                    echo "Version: $IMAGE_TAG"
                    echo "========================================"

                    echo "$DOCKERHUB_CREDENTIALS_PSW" | docker login \
                        -u "$DOCKERHUB_CREDENTIALS_USR" \
                        --password-stdin

                    docker build \
                        --target production \
                        -t "$DOCKER_IMAGE:$IMAGE_TAG" \
                        -t "$DOCKER_IMAGE:production" \
                        .

                    echo "Pushing version tag..."
                    docker push "$DOCKER_IMAGE:$IMAGE_TAG"

                    echo "Pushing production tag..."
                    docker push "$DOCKER_IMAGE:production"

                    docker logout

                    echo "Docker image successfully pushed."
                '''
            }
        }

        stage('Deploy to VPS') {
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

                        echo "========================================"
                        echo "Deploying AMS to VPS"
                        echo "Host: $VPS_HOST"
                        echo "Directory: $VPS_DEPLOY_DIR"
                        echo "Version: $IMAGE_TAG"
                        echo "========================================"

                        chmod 600 "$SSH_KEY"

                        ssh \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            "$SSH_USERNAME@$VPS_HOST" \
                            "cd '$VPS_DEPLOY_DIR' && bash -s" <<REMOTE_SCRIPT

set -e

echo "----------------------------------------"
echo "Checking AMS deployment files"
echo "----------------------------------------"

cd "$VPS_DEPLOY_DIR"

if [ ! -f docker-compose.prod.yml ]; then
    echo "ERROR: docker-compose.prod.yml not found."
    exit 1
fi

if [ ! -f .env.prod ]; then
    echo "ERROR: .env.prod not found."
    exit 1
fi

if [ ! -f .env ]; then
    echo "ERROR: .env not found."
    echo "DOCKER_HUB_USERNAME must be defined in /opt/ams-backend/.env"
    exit 1
fi

echo "Deployment files found."

echo "----------------------------------------"
echo "Loading Docker Hub configuration"
echo "----------------------------------------"

set -a
. ./.env
set +a

if [ -z "\${DOCKER_HUB_USERNAME:-}" ]; then
    echo "ERROR: DOCKER_HUB_USERNAME is not defined."
    exit 1
fi

echo "Docker Hub username: \$DOCKER_HUB_USERNAME"

echo "----------------------------------------"
echo "Validating Docker Compose configuration"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    config > /dev/null

echo "Compose configuration is valid."

echo "----------------------------------------"
echo "Starting PostgreSQL and Redis"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    up -d db redis

echo "----------------------------------------"
echo "Pulling latest AMS application images"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    pull web celery celery-beat

echo "----------------------------------------"
echo "Running database migrations"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    run --rm web \
    python manage.py migrate --noinput

echo "----------------------------------------"
echo "Collecting static files"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    run --rm web \
    python manage.py collectstatic --noinput

echo "----------------------------------------"
echo "Starting AMS application"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    up -d web celery celery-beat

echo "----------------------------------------"
echo "Current AMS containers"
echo "----------------------------------------"

docker compose \
    -f docker-compose.prod.yml \
    --env-file .env.prod \
    ps

echo "----------------------------------------"
echo "Cleaning unused Docker images"
echo "----------------------------------------"

docker image prune -f

echo "----------------------------------------"
echo "AMS deployment completed"
echo "----------------------------------------"

REMOTE_SCRIPT
                    '''
                }
            }
        }

        stage('Verify Deployment') {
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

                        echo "========================================"
                        echo "Verifying AMS deployment"
                        echo "========================================"

                        chmod 600 "$SSH_KEY"

                        ssh \
                            -i "$SSH_KEY" \
                            -o StrictHostKeyChecking=no \
                            -o UserKnownHostsFile=/dev/null \
                            "$SSH_USERNAME@$VPS_HOST" \
                            "cd '$VPS_DEPLOY_DIR' && \
                             docker compose \
                             -f docker-compose.prod.yml \
                             --env-file .env.prod \
                             ps"

                        echo "Container verification completed."
                    '''
                }
            }
        }
    }

    post {

        always {
            sh 'rm -rf ams-proj/.venv || true'
        }

        success {
            echo "========================================"
            echo "AMS DEPLOYMENT SUCCESSFUL"
            echo "Version: ${env.IMAGE_TAG}"
            echo "Image: ${env.DOCKER_IMAGE}:${env.IMAGE_TAG}"
            echo "Production: ${env.DOCKER_IMAGE}:production"
            echo "========================================"
        }

        failure {
            echo "========================================"
            echo "AMS PIPELINE FAILED"
            echo "Check the failed stage above."
            echo "========================================"
        }
    }
}
