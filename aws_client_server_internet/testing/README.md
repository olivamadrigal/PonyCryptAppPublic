Mohan

AWS deployment :

AWS account creation and define IAM user roles

In EC2 services, launch an EC2 service which can deploy python code containing server, we choose Amazon Linux AMI 2018.03.0 (HVM).

Choose default settings to launch the instance 

Public DNS (IPv4): ec2-<ip>.compute-1.amazonaws.com and the IP address of the instance is <YOUR_IP_ADDR>

Connect to the AWS EC2 server with our host computer running on Linux and deployed the server code (Server.py) and start the server. 

Change the client code (GUI.py) to “remote_ip = '<YOUR_TEST_REMOTE_IP>'”

Launch multiple instances of client and tested whether they can communicate or not. They are successfully communicating.

See Images inside same folder.
