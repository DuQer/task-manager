pipeline {
    agent any

    stages {
        // stage('Checkout') {
        //     steps {
        //         checkout([$class: 'GitSCM', branches: [[name: 'master']], doGenerateSubmoduleConfigurations: false,  extensions: [], submoduleCfg: [], userRemoteConfigs: [[credentialsId: 'Jenkins', url: 'https://github.com/DuQer/task-manager.git']]])
        //     }
        // }
        stage('Build') {
            steps {
                sh 'pip install -r requirements.txt'
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
