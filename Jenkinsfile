pipeline {
    agent any

    environment {
        GIT_CREDENTIALS = 'd0320e64-ef5a-47b3-b9be-a16d1c0d1967'
        SOURCE_REPO = 'https://github.com/chasesmith2468/LambdaScripts'
        TARGET_REPO = 'https://github.com/chasesmith2468/jenkinstest.git'
        SOURCE_BRANCH = 'main'
        TARGET_BRANCH = 'main'
        AWS_CREDENTIALS = '3da225a2-ff6d-46ab-b164-0358ce526b83'
        AWS_REGION = 'us-east-1'
    }

    stages {
        stage('Clone Source Repository') {
            steps {
                script {
                    if (!fileExists('source-repo')) {
                        dir('source-repo') {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: env.SOURCE_BRANCH]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        submoduleCfg: [],
                        userRemoteConfigs: [[
                            credentialsId: env.GIT_CREDENTIALS,
                            url: "https://x-access-token:${env.GIT_CREDENTIALS}@github.com/chasesmith2468/LambdaTest.git"
                        ]]
                    ])
                        }
                    } else {
                        dir('source-repo') {
                            sh 'git fetch --all'
                            sh "git checkout ${env.SOURCE_BRANCH}"
                            sh 'git pull origin ${SOURCE_BRANCH}'
                        }
                    }
                }
            }
        }

        stage('Clone Target Repository') {
            steps {
                script {
                    if (!fileExists('target-repo')) {
                        dir('target-repo') {
                    checkout([
                        $class: 'GitSCM',
                        branches: [[name: env.SOURCE_BRANCH]],
                        doGenerateSubmoduleConfigurations: false,
                        extensions: [],
                        submoduleCfg: [],
                        userRemoteConfigs: [[
                            credentialsId: env.GIT_CREDENTIALS,
                            url: "https://x-access-token:${env.GIT_CREDENTIALS}@github.com/chasesmith2468/jenkinstest.git"
                        ]]
                    ])
                                            }
                    } else {
                        dir('target-repo') {
                            sh 'git fetch --all'
                            sh "git checkout ${env.TARGET_BRANCH}"
                            sh 'git pull origin ${TARGET_BRANCH}'
                        }
                    }
                }
            }
        }

        stage('Copy Changes') {
            steps {
                sh '''
                rsync -auv --exclude='.git' --exclude='README.md' --exclude='.gitignore' --exclude='Jenkinsfile' source-repo/ target-repo/
                '''
            }
        }

        stage('Commit and Push Changes') {
            steps {
                dir('target-repo') {
                    withCredentials([string(credentialsId: env.GIT_CREDENTIALS, variable: 'GIT_TOKEN')]) {
                        sh('git config user.email chasesmith2468@gmail.com')
                        sh('git config user.name Chase Smith')
                        sh('git add -A')
                        sh('git diff-index --quiet HEAD || git commit -m "Updated Lambda functions by Jenkins"')
                        withCredentials([string(credentialsId: env.GIT_CREDENTIALS, variable: 'GIT_TOKEN')]) {
                            sh(script: 'git remote set-url origin https://${GIT_TOKEN}@github.com/chasesmith2468/jenkinstest.git', label: 'Set Git Remote URL')
                        }
                        sh('git push origin main')
                    }
                }
            }
        }

       stage('Update Lambda Functions') {
            steps {
                dir('target-repo') {
                    withAWS(credentials: env.AWS_CREDENTIALS, region: env.AWS_REGION) {
                        script {
                            def lambdaFolders = sh(script: "find . -mindepth 1 -maxdepth 1 -type d -not -path '*/.git*' -exec basename {} \\;", returnStdout: true).trim().split('\n')

                            for (folder in lambdaFolders) {
                                sh "cd ${folder} && zip -r ../${folder}.zip * && cd .."
                                sh "unzip -Z1 ${folder}.zip | grep -v -E 'README(.md)?\$' | while read filename; do aws lambda update-function-code --function-name \${filename%.py} --zip-file fileb://./${folder}.zip; done"
                                sh "rm -f ${folder}.zip"
                            }
                        }
                    }                    
                }
            }
        }
    }
}
