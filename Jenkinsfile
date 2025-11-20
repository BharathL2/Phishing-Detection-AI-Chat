pipeline {
    agent any

    environment {
        VENV_PATH = '.venv'
        UNIX_PY = 'python3'
        REQUIREMENTS_FILE = 'requirements.txt'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Setup Python & deps') {
            steps {
                script {
                    def reqFile = env.REQUIREMENTS_FILE ?: 'requirements.txt'
                    if (isUnix()) {
                        sh "${env.UNIX_PY} -m venv ${env.VENV_PATH}"
                        sh ". ${env.VENV_PATH}/bin/activate && python -m pip install --upgrade pip"
                        sh ". ${env.VENV_PATH}/bin/activate && pip install -r ${reqFile}"
                    } else {
                        bat "py -3 -m venv ${env.VENV_PATH}"
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && python -m pip install --upgrade pip"
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && pip install -r ${reqFile}"
                    }
                }
            }
        }

        stage('Static Check') {
            steps {
                script {
                    if (isUnix()) {
                        sh ". ${env.VENV_PATH}/bin/activate && python -m compileall src"
                    } else {
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && python -m compileall src"
                    }
                }
            }
        }

        stage('Run Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh ". ${env.VENV_PATH}/bin/activate && pytest --ignore=src/phishing_module/test_phishing_service.py"
                    } else {
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && pytest --ignore=src/phishing_module/test_phishing_service.py"
                    }
                }
            }
        }
    }

    post {
        always {
            script {
                if (isUnix()) {
                    sh "rm -rf ${env.VENV_PATH}"
                } else {
                    bat "if exist ${env.VENV_PATH} rmdir /s /q ${env.VENV_PATH}"
                }
            }
        }
    }
}
