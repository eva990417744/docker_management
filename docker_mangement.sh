#!/bin/bash
sudo apt-get update
sudo apt-get install -y docker
sudo docker pull sumeragibi/docker_mangement
sudo docker run -p 5001:5001 -v /var/run/docker.sock:/var/run/docker.sock --name "docker_mangement" -d -t sumeragibi/docker_mangement /bin/bash start.sh