# Jenkins with the tools our pipeline needs: Docker CLI, Python and kubectl
FROM jenkins/jenkins:lts-jdk17

USER root

RUN apt-get update \
 && apt-get install -y --no-install-recommends docker.io python3 python3-venv python3-pip curl ca-certificates \
 && rm -rf /var/lib/apt/lists/*

# kubectl (picks the right CPU architecture automatically)
RUN ARCH=$(dpkg --print-architecture) \
 && curl -fsSLo /usr/local/bin/kubectl "https://dl.k8s.io/release/v1.30.0/bin/linux/${ARCH}/kubectl" \
 && chmod +x /usr/local/bin/kubectl

# We stay root so Jenkins can talk to the Docker socket (OK for a learning lab only)
