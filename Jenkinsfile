pipeline {
    agent any

    options {
        timestamps()
        disableConcurrentBuilds()
    }

    environment {
        DOCKER_IMAGE = 'les190/ams_backend'
        DOCKERHUB_CREDENTIALS = credentials('dockerhub-credentials')
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

        stage('Trigger Production Deployment') {
            when {
                branch 'main'
            }

            steps {
                build job: 'AMS/ams-devops/main',
                    wait: false,
                    parameters: [
                        string(
                            name: 'BACKEND_VERSION',
                            value: "${env.IMAGE_TAG}"
                        )
                    ]
            }
        }
    }

    post {
        success {
            echo "AMS backend CI completed successfully."
        }

        failure {
            echo "AMS backend CI failed."
        }
    }
}