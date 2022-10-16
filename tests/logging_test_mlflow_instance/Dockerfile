FROM python:latest
ARG MLFLOW_PORT_ARTIFACT
ARG MLFLOW_USERNAME
ARG MLFLOW_PASSWORD
RUN apt update && apt install -y openssh-server
RUN echo 'PasswordAuthentication yes' >> /etc/ssh/sshd_config
RUN echo "Port ${MLFLOW_PORT_ARTIFACT}" >> /etc/ssh/sshd_config
RUN useradd -d /home/mlflow -s /bin/bash -p "$(openssl passwd -1 ${MLFLOW_PASSWORD})" ${MLFLOW_USERNAME}
RUN pip install mlflow pysftp
RUN service ssh start
COPY start.sh /start.sh
ENTRYPOINT ["/start.sh"]