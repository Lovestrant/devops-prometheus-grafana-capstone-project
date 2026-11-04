pipeline {
    agent any

    options {
        disableConcurrentBuilds()
    }

    parameters {
        booleanParam(name: 'PUSH_IMAGE', defaultValue: false,
                     description: 'Push the image to Docker Hub (needs a "dockerhub" credential)')
        booleanParam(name: 'DEPLOY_TO_K8S', defaultValue: false,
                     description: 'Deploy to Kubernetes (needs PUSH_IMAGE plus a "kubeconfig" credential)')
    }

    environment {
        IMAGE_NAME = 'tasktracker'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
                sh 'git log -1 --oneline'
            }
        }

        stage('Test') {
            steps {
                dir('app') {
                    sh '''
                        python3 -m venv .venv
                        . .venv/bin/activate
                        pip install --quiet -r requirements-dev.txt
                        pytest -v
                    '''
                }
            }
        }

        stage('Build Image') {
            steps {
                sh 'docker build --build-arg APP_VERSION=1.0.${BUILD_NUMBER} -t ${IMAGE_NAME}:${BUILD_NUMBER} app'
            }
        }

        stage('Smoke Test') {
            steps {
                sh '''
                    docker rm -f tasktracker-smoke || true
                    docker run -d --name tasktracker-smoke ${IMAGE_NAME}:${BUILD_NUMBER}
                    for i in 1 2 3 4 5 6 7 8 9 10; do
                        if docker exec tasktracker-smoke python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://localhost:8000/health').status == 200 else 1)"; then
                            echo "Container is healthy"
                            exit 0
                        fi
                        echo "Waiting for the container..."
                        sleep 2
                    done
                    docker logs tasktracker-smoke
                    exit 1
                '''
            }
        }

        stage('Push Image') {
            when { expression { return params.PUSH_IMAGE } }
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub',
                                                  usernameVariable: 'DH_USER',
                                                  passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker tag ${IMAGE_NAME}:${BUILD_NUMBER} $DH_USER/${IMAGE_NAME}:${BUILD_NUMBER}
                        docker push $DH_USER/${IMAGE_NAME}:${BUILD_NUMBER}
                        docker logout
                    '''
                }
            }
        }

        stage('Deploy to Kubernetes') {
            when { expression { return params.DEPLOY_TO_K8S && params.PUSH_IMAGE } }
            steps {
                withCredentials([
                    usernamePassword(credentialsId: 'dockerhub',
                                     usernameVariable: 'DH_USER',
                                     passwordVariable: 'DH_PASS'),
                    file(credentialsId: 'kubeconfig', variable: 'KUBECONFIG')
                ]) {
                    sh '''
                        kubectl set image deployment/tasktracker tasktracker=$DH_USER/${IMAGE_NAME}:${BUILD_NUMBER} -n tasktracker
                        kubectl rollout status deployment/tasktracker -n tasktracker --timeout=120s
                    '''
                }
            }
        }
    }

    post {
        always {
            sh 'docker rm -f tasktracker-smoke || true'
        }
        success {
            echo "Pipeline finished: image ${IMAGE_NAME}:${BUILD_NUMBER} is ready."
        }
        failure {
            echo 'Pipeline failed - open "Console Output" to see which stage broke.'
        }
    }
}
