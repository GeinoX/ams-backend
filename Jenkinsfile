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

        stage('Verify Branch') {
            steps {
                script {
                    def branch = sh(
                        script: 'git branch --show-current',
                        returnStdout: true
                    ).trim()

                    def commit = sh(
                        script: 'git rev-parse HEAD',
                        returnStdout: true
                    ).trim()

                    echo "Git branch: ${branch}"
                    echo "Git commit: ${commit}"
                    echo "Jenkins BRANCH_NAME: ${env.BRANCH_NAME ?: '(not set)'}"
                    echo "Jenkins GIT_BRANCH: ${env.GIT_BRANCH ?: '(not set)'}"

                    if (env.GIT_BRANCH != null && env.GIT_BRANCH != 'origin/main' && env.GIT_BRANCH != 'main') {
                        error("This pipeline is not running from main. GIT_BRANCH=${env.GIT_BRANCH}")
                    }
                }
            }
        }

        stage('Docker Build & Push') {
            steps {
                sh '''
                    set -e

                    echo "Building AMS production image..."
                    echo "Image: $DOCKER_IMAGE"
                    echo "Version: $IMAGE_TAG"

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
            steps {
                script {
                    /*
                     * Deployment will be handled by the AMS DevOps Jenkins job.
                     *
                     * We are not creating the DevOps job yet.
                     * For this run, this stage only confirms that the
                     * Docker image was successfully built and pushed.
                     */

                    echo "Docker image pushed successfully."
                    echo "Deployment stage will be connected after AMS DevOps is configured."
                    echo "Version ready for deployment: ${env.IMAGE_TAG}"
                }
            }
        }
    }

    post {
        success {
            echo "AMS backend CI completed successfully."
            echo "Built version: ${env.IMAGE_TAG}"
        }

        failure {
            echo "AMS backend CI failed."
        }
    }
}

