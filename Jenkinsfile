pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE = 'les190/ams-backend'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')

        // Jenkins credential containing the production environment file.
        DJANGO_ENV_FILE = credentials('ams-backend-env')

        DJANGO_SETTINGS_MODULE = 'umsproj.settings.production'

        // Jenkins SSH credential for the Ubuntu VPS.
        VPS_SSH_CREDENTIALS = 'ams-vps-ssh'

        // Remote deployment directory on the VPS.
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

                    echo "Backend version: ${env.IMAGE_TAG}"
                }
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    python3 -m venv .venv

                    . .venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Prepare Environment') {
            steps {
                sh '''
                    cp "$DJANGO_ENV_FILE" .env
                    chmod 600 .env
                '''
            }
        }

        stage('Django Checks') {
            steps {
                sh '''
                    . .venv/bin/activate

                    python manage.py check \
                        --settings="$DJANGO_SETTINGS_MODULE"
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
                sshagent(credentials: ["${VPS_SSH_CREDENTIALS}"]) {

                    sh '''
                        set -e

                        ssh -o StrictHostKeyChecking=no \
                            "$VPS_USER@$VPS_HOST" \
                            "cd '$VPS_DEPLOY_DIR' && \
                             docker compose pull web celery celery-beat && \
                             docker compose run --rm web \
                                python manage.py migrate \
                                --settings='$DJANGO_SETTINGS_MODULE' && \
                             docker compose run --rm web \
                                python manage.py collectstatic --noinput \
                                --settings='$DJANGO_SETTINGS_MODULE' && \
                             docker compose up -d \
                                web celery celery-beat"
                    '''
                }
            }
        }

        stage('Deployment Health Check') {
            when {
                branch 'main'
            }

            steps {
                sshagent(credentials: ["${VPS_SSH_CREDENTIALS}"]) {

                    sh '''
                        set -e

                        ssh -o StrictHostKeyChecking=no \
                            "$VPS_USER@$VPS_HOST" \
                            "cd '$VPS_DEPLOY_DIR' && \
                             docker compose ps web celery celery-beat"
                    '''
                }
            }
        }
    }

    post {

        always {
            sh 'rm -f .env || true'
            sh 'rm -rf .venv || true'
        }

        success {
            echo "AMS Backend CI/CD completed successfully."
            echo "Version deployed: ${env.IMAGE_TAG}"
        }

        failure {
            echo "AMS Backend CI/CD failed."
            echo "Check the Jenkins console output for details."
        }
    }
}

