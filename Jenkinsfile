pipeline {
    agent any

    environment {
        DOCKER_IMAGE_BACKEND = 'cheghe/ams-backend'
        DOCKER_IMAGE_NGINX   = 'cheghe/ams-nginx'

        DEPLOY_HOST = credentials('ams-deploy-host')
        DEPLOY_USER = credentials('ams-deploy-user')

        SSH_CREDENTIALS = 'ams-vps-ssh'
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Backend Tests') {
            steps {
                sh '''
                    python3 -m venv .venv
                    . .venv/bin/activate

                    pip install --upgrade pip
                    pip install -r requirements.txt

                    python manage.py check
                '''
            }
        }

        stage('Docker Build & Push') {
            steps {
                script {
                    def gitCommit = sh(
                        script: 'git rev-parse --short HEAD',
                        returnStdout: true
                    ).trim()

                    sh """
                        docker build \
                            -t ${DOCKER_IMAGE_BACKEND}:${gitCommit} \
                            -t ${DOCKER_IMAGE_BACKEND}:latest \
                            .

                        docker push ${DOCKER_IMAGE_BACKEND}:${gitCommit}
                        docker push ${DOCKER_IMAGE_BACKEND}:latest
                    """
                }
            }
        }

        stage('Deploy') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    script {
                        def gitCommit = sh(
                            script: 'git rev-parse --short HEAD',
                            returnStdout: true
                        ).trim()

                        sh """
                            ssh -o StrictHostKeyChecking=no \
                                ${DEPLOY_USER}@${DEPLOY_HOST} '
                                    cd ~/ams &&
                                    docker pull ${DOCKER_IMAGE_BACKEND}:${gitCommit} &&
                                    docker compose up -d &&
                                    docker image prune -f
                                '
                        """
                    }
                }
            }
        }

        stage('Verify Deployment') {
            steps {
                sshagent(credentials: [SSH_CREDENTIALS]) {
                    sh """
                        ssh -o StrictHostKeyChecking=no \
                            ${DEPLOY_USER}@${DEPLOY_HOST} '
                                cd ~/ams &&
                                docker compose ps &&
                                docker compose exec -T backend \
                                    python manage.py check
                            '
                    """
                }
            }
        }
    }

    post {
        always {
            cleanWs()
        }

        success {
            echo 'AMS CI/CD pipeline completed successfully.'
        }

        failure {
            echo 'AMS CI/CD pipeline failed.'
        }
    }
}
