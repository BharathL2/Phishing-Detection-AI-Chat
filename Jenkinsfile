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
                        def resolveCmd = { String candidate ->
                            if (!candidate) {
                                return null
                            }
                            def trimmed = candidate.trim()
                            if (trimmed.isEmpty()) {
                                return null
                            }
                            def prepared = trimmed
                            if (prepared.contains(' ') && !prepared.startsWith('"')) {
                                prepared = "\"${prepared}\""
                            }
                            def status = bat(script: "${prepared} --version", returnStatus: true)
                            return status == 0 ? prepared : null
                        }

                        def candidates = []
                        if (env.WINDOWS_PY?.trim()) {
                            candidates << env.WINDOWS_PY.trim()
                        }
                        candidates.addAll(['py -3', 'py', 'python', 'python3',
                            'C:/Program Files/Python313/python.exe',
                            'C:/Program Files/Python312/python.exe',
                            'C:/Program Files/Python311/python.exe',
                            'C:/Python313/python.exe',
                            'C:/Python312/python.exe',
                            'C:/Python311/python.exe'])

                        def winPython = null
                        for (candidate in candidates) {
                            winPython = resolveCmd(candidate)
                            if (winPython) {
                                echo "Using Windows Python command: ${candidate}"
                                break
                            }
                        }

                        if (!winPython) {
                            error('Unable to locate a usable Python interpreter on this Windows agent. Set WINDOWS_PY to a valid path.')
                        }

                        env.RESOLVED_WINDOWS_PY = winPython
                        bat "${winPython} -m venv ${env.VENV_PATH}"
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && ${winPython} -m pip install --upgrade pip"
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && ${winPython} -m pip install -r ${reqFile}"
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
