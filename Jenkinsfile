pipeline {
    agent any

    environment {
        PYTHON = "python3"
        VENV_PATH = ".venv"
    }

    options {
        ansiColor('xterm')
        timestamps()
    }

    stages {
        stage('Checkout') {
            steps {
                deleteDir()
                git branch: 'main', url: 'https://github.com/BharathL2/Phishing-Detection-AI-Chat.git'
            }
        }

        stage('Set up Python') {
            steps {
                sh "${PYTHON} -m venv ${VENV_PATH}"
                sh ". ${VENV_PATH}/bin/activate && pip install --upgrade pip"
                sh ". ${VENV_PATH}/bin/activate && pip install -r requirements.txt pytest"
            }
        }

        stage('Static Analysis') {
            steps {
                sh ". ${VENV_PATH}/bin/activate && python -m compileall src"
            }
        }

        stage('Unit Tests') {
            steps {
                sh ". ${VENV_PATH}/bin/activate && pytest src/phishing_module --junitxml=reports/junit.xml"
            }
            post {
                always {
                    junit 'reports/junit.xml'
                }
            }
        }

        stage('Package Model Server') {
            when {
                expression { fileExists('Dockerfile') }
            }
            steps {
                sh 'docker build -t phishing-ai-chat:${BUILD_NUMBER} .'
            }
        }

        stage('Archive Artifacts') {
            steps {
                archiveArtifacts artifacts: 'models/**/*.pkl,models/**/*.json,docs/**/*.html', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully.'
        }
        failure {
            echo 'Pipeline failed. Check logs for details.'
        }
        always {
            cleanWs()
        }
    }
}
