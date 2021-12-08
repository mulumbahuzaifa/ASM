# Afripaas Readme
# You will need to enable docker API access. Follow these steps for your operating system.
# On Ubuntu Linux.
# Open the docker.service file with a text editor.
sudo vi /lib/systemd/system/docker.service
# Change the line that begins with ExecStart and add the text -H tcp://0.0.0.0:2375 so that it looks like below:
ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock -H tcp://0.0.0.0:2375
# Save the file and reload
systemctl daemon-reload
# Restart docker
sudo service docker restart
# Then use docker run command as below to start the container
docker run -d --rm --name afripaas --net=host afripaas:1.0
# To access the container, use your host Ip or hostname.
http://your-hostname:8013
# Example
http://192.168.8.120:8013
#Login with user admin and pasword admin

