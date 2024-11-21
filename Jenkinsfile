def shellCMD(cmd) {
    steps.sh(script: '#!/bin/sh -e\n'+ cmd, returnStdout: true)
}

@groovy.transform.Field
def REPO_TAG = ''

@groovy.transform.Field
def PREV_REPO_TAG = ''


pipeline {
    agent any
    options {
        timeout(time: 10, unit: 'MINUTES') // timeout on whole pipeline job
    }
    environment {
        PROJECT_NAME = 'mac-audio-bot'
        BRANCH = 'development'
        MATTERMOST_CHANNEL = 'jenkins-deployment'
        DOCKER_CREDENTIALS_ID = 'macbot-docker-creds'
        JENKINS_SSH_KEY_ID = 'jenkins-ssh-key'
        SERVER_HOST = 'innvonix.in'
        SERVER_USER = 'apima2827'
        SERVER_UPLOAD_PATH = '/home/api.mac-audio-bot.innvonix.in'
    }
    stages {
        stage('Login to docker') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: DOCKER_CREDENTIALS_ID, usernameVariable: 'DOCKER_USERNAME', passwordVariable: 'DOCKER_PASSWORD')]) {
                        shellCMD("docker login -u $DOCKER_USERNAME -p $DOCKER_PASSWORD")
                    }
                }
            }
        }
        stage('Creating docker build') {
            steps {
                script {
                    shellCMD("touch .env")
                    shellCMD("docker-compose build")
                }
            }
        }
        stage('Generating git tag') {
            steps {
                script {
                    // Fetch previous repo tag
                    PREV_REPO_TAG = shellCMD("bump2version --dry-run --list patch | grep current_version | cut -d '=' -f 2").replaceAll("\\r", "").trim()

                    // Bump version to next patch
                    shellCMD("bump2version patch")
                    REPO_TAG = shellCMD("bump2version --dry-run --list patch | grep current_version | cut -d '=' -f 2").replaceAll("\\r", "").trim()

                    println("Current tag version: ${REPO_TAG} | Previous tag version: ${PREV_REPO_TAG}")
                    shellCMD("git push origin HEAD:$BRANCH")
                }
            }
        }
        stage('Regenerating docker build') {
            steps {
                script {
                    shellCMD("touch .env")
                    shellCMD("docker-compose build")
                }
            }
        }
        stage('Pushing docker build to repo') {
            steps {
                script {
                    shellCMD("docker-compose push")
                }
            }
        }
        stage('Deploying changes on dev server') {
            steps {
                script {
                    script {
                        sh """ssh -tt $SERVER_USER@$SERVER_HOST << EOF
                        cd $SERVER_UPLOAD_PATH
                        sed -i 's/$PREV_REPO_TAG/$REPO_TAG/g' docker-compose.yaml
                        docker-compose pull
                        docker-compose up -d
                        exit 0
                        EOF"""
                    }
                }
            }
        }
    }
    post {
        always {
            script {
                // Do clean up. 
                echo "Pipeline finished"
                echo "Cleaning workspace"
                dir("${env.WORKSPACE}@tmp") {
                    deleteDir()
                }
                dir("${env.WORKSPACE}@script") {
                    deleteDir()
                }
                dir("${env.WORKSPACE}@script@tmp") {
                    deleteDir()
                }
            }
        }
        success {
            script {
                echo "Build succeeded, finishing up"
                if(env.MATTERMOST_CHANNEL){
                    mattermostSend color: 'good', text: '@here', message: "Jenkins build pipeline succeeded for $PROJECT_NAME", channel: "$MATTERMOST_CHANNEL"
                }
            }
        }
        failure {
            script{
                echo "Build failed"
                if(env.MATTERMOST_CHANNEL){
                    mattermostSend color: 'bad', text: '@here', message: "Jenkins build pipeline failed for $PROJECT_NAME", channel: "$MATTERMOST_CHANNEL"
                }
            }
        }
    }
}