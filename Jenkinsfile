pipeline {
    agent { label 'windows' }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python & deps') {
            steps {
                bat 'py -3 -m venv .venv'
                bat 'call .venv\\Scripts\\activate && python -m pip install --upgrade pip'
                bat '''
                    rem Switch to requirements-ci.txt for a lean install if needed
                    call .venv\\Scripts\\activate && pip install -r requirements.txt
                '''
            }
        }

        stage('Static Check') {
            steps {
                bat 'call .venv\\Scripts\\activate && python -m compileall src'
            }
        }

        stage('Run Tests') {
            steps {
                bat 'call .venv\\Scripts\\activate && pytest --ignore=src/phishing_module/test_phishing_service.py'
            }
        }
    }

    post {
        always {
            bat 'if exist .venv rmdir /s /q .venv'
        }
    }
}
