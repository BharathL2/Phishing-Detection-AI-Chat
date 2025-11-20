pipeline {
    agent any

    environment {
        VENV_PATH = ".venv"
        UNIX_PY = "python3"
        WINDOWS_PY = "C:\\Users\\l670b\\AppData\\Local\\Programs\\Python\\Python313\\python.exe"
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
                script {
                    if (isUnix()) {
                        sh "${UNIX_PY} -m venv ${VENV_PATH}"
                        sh ". ${VENV_PATH}/bin/activate && pip install --upgrade pip"
                        sh ". ${VENV_PATH}/bin/activate && pip install -r requirements.txt pytest"
                    } else {
                        def pyCmd = env.WINDOWS_PY?.trim()
                        if (pyCmd) {
                            bat "\"${pyCmd}\" -m venv ${VENV_PATH}"
                        } else {
                            bat "py -3 -m venv ${VENV_PATH}"
                        }
                        bat "call ${VENV_PATH}\\Scripts\\activate && python -m pip install --upgrade pip"
                        bat "call ${VENV_PATH}\\Scripts\\activate && python -m pip install -r requirements.txt pytest"
                    }
                }
            }
        }

        stage('Static Analysis') {
            steps {
                script {
                    if (isUnix()) {
                        sh ". ${VENV_PATH}/bin/activate && python -m compileall src"
                    } else {
                        bat "call ${VENV_PATH}\\Scripts\\activate && python -m compileall src"
                    }
                }
            }
        }

        stage('Unit Tests') {
            steps {
                script {
                    if (isUnix()) {
                        sh "mkdir -p reports"
                        sh ". ${VENV_PATH}/bin/activate && pytest src/phishing_module --junitxml=reports/junit.xml"
                    } else {
                        bat "if not exist reports mkdir reports"
                        bat "call ${VENV_PATH}\\Scripts\\activate && pytest src\\phishing_module --junitxml=reports\\junit.xml"
                    }
                }
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
                script {
                    if (isUnix()) {
                        sh 'docker build -t phishing-ai-chat:${BUILD_NUMBER} .'
                    } else {
                        bat 'docker build -t phishing-ai-chat:%BUILD_NUMBER% .'
                    }
                }
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
