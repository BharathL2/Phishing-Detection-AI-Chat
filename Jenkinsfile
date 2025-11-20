pipeline {
    agent any

    environment {
        VENV_PATH = '.venv'
        UNIX_PY = 'python3'
        WINDOWS_PY_INSTALL_URL = 'https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe'
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
                        def quoteIfNeeded = { String value ->
                            if (value.contains(' ')) {
                                return "\"${value}\""
                            }
                            value
                        }

                        def tryCandidate = { String exe, List args ->
                            def commandParts = []
                            commandParts << quoteIfNeeded(exe)
                            if (args) {
                                commandParts.addAll(args)
                            }
                            commandParts << '--version'
                            def status = bat(script: commandParts.join(' '), returnStatus: true)
                            return status == 0
                        }

                        def candidateList = []
                        if (env.WINDOWS_PY?.trim()) {
                            candidateList << [exe: env.WINDOWS_PY.trim(), args: []]
                        }
                        candidateList.addAll([
                            [exe: 'py', args: ['-3']],
                            [exe: 'py', args: []],
                            [exe: 'python', args: []],
                            [exe: 'python3', args: []],
                            [exe: 'C:/Program Files/Python313/python.exe', args: []],
                            [exe: 'C:/Program Files/Python312/python.exe', args: []],
                            [exe: 'C:/Program Files/Python311/python.exe', args: []],
                            [exe: 'C:/Python313/python.exe', args: []],
                            [exe: 'C:/Python312/python.exe', args: []],
                            [exe: 'C:/Python311/python.exe', args: []]
                        ])

                        def detected = null
                        for (candidate in candidateList) {
                            if (tryCandidate(candidate.exe, candidate.args)) {
                                echo "Using Windows Python command: ${([candidate.exe] + candidate.args).join(' ')}"
                                detected = candidate
                                break
                            }
                        }

                        def installWorkspacePython = {
                            def installerUrl = env.WINDOWS_PY_INSTALL_URL ?: 'https://www.python.org/ftp/python/3.13.1/python-3.13.1-amd64.exe'
                            def pythonExeRel = "python-home\\python.exe"
                            if (!fileExists(pythonExeRel)) {
                                def workspacePosix = env.WORKSPACE.replace('\\', '/')
                                def installerPathPosix = "${workspacePosix}/python-installer.exe"
                                def targetDirPosix = "${workspacePosix}/python-home"
                                def installerPathWin = installerPathPosix.replace('/', '\\')
                                def targetDirWin = targetDirPosix.replace('/', '\\')
                                echo "Downloading Python installer ${installerUrl}"
                                bat "powershell -NoProfile -Command \"\\$ErrorActionPreference='Stop'; Invoke-WebRequest -Uri '${installerUrl}' -OutFile '${installerPathPosix}'\""
                                def targetDirArg = targetDirWin.contains(' ') ? "\"${targetDirWin}\"" : targetDirWin
                                bat "\"${installerPathWin}\" /quiet InstallAllUsers=0 Include_launcher=0 SimpleInstall=1 Shortcuts=0 PrependPath=0 TargetDir=${targetDirArg}"
                            }
                            return "${env.WORKSPACE}\\python-home\\python.exe"
                        }

                        if (!detected) {
                            def localPython = installWorkspacePython()
                            detected = [exe: localPython, args: []]
                            echo "Installed standalone Python at ${localPython}"
                        }

                        def pythonCommandParts = []
                        pythonCommandParts << quoteIfNeeded(detected.exe)
                        if (detected.args) {
                            pythonCommandParts.addAll(detected.args)
                        }

                        def pythonCommand = pythonCommandParts.join(' ')
                        bat "${pythonCommand} -m venv ${env.VENV_PATH}"
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && python -m pip install --upgrade pip"
                        bat "call ${env.VENV_PATH}\\Scripts\\activate && python -m pip install -r ${reqFile}"
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
