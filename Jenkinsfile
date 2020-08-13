pipeline {
    agent any

    stages {
        dir('daemon') {
            stage('Build daemon') {
                steps {
                    sh 'make build'
                }
            }
            stage('Test daemon') {
                steps {
                    sh 'make build'
                }
            }
            stage('Setup daemon') {
                steps {
                    sh 'make setup'
                }
            }
            stage('Push daemon') {
                when {
                    branch 'master'
                }
                steps {
                    sh 'make push'
                }
            }
        }
    }
}
