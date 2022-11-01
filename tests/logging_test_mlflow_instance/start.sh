#!/bin/bash
chown -R mlflow /home/mlflow

if [ ! -d "$HOME/.ssh" ]; then
  mkdir ~/.ssh
fi

/usr/sbin/sshd -D &
sleep 1
ssh-keyscan -p ${MLFLOW_PORT_ARTIFACT} localhost | sed -e 's/\[//g' -e 's/\]:[0-9]\+//g' > ~/.ssh/known_hosts

mlflow server --host 0.0.0.0 --default-artifact-root sftp://${MLFLOW_USERNAME}:${MLFLOW_PASSWORD}@${MLFLOW_HOST}:${MLFLOW_PORT_ARTIFACT}/home/mlflow/artifacts --serve-artifacts