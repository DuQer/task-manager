pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                checkout([$class: 'GitSCM', branches: [[name: 'master']], extensions: [], userRemoteConfigs: [[url: 'https://github.com/DuQer/task-manager.git']]])
            }
        }
        stage('Build') {
            steps {
                git branch: 'main', url: 'https://github.com/DuQer/task-manager.git'
                sh 'python3 main.py'
            }
        }
        stage('Test') {
            steps {
                sh 'python3 -m tests/pytest'
            }
        }
    }
}
