# PonyCryptPublic -- PonyCrypt chat app public version

PonyCryptApp

CMPE 207 Term Project

PonyCrypt :)

Contents of PonyCryptApp Directory

#/aws_client_server_internet

This has the source code from which we build our project Shows test results with this working and running on the Internet with the server script running on an Amazon AWS EC2 instance The second version has issues because of: logging OAUTH 2.O in issues in authentication flow when runnign server on EC2 (this should be addressed in future work as well as using APP key versus credentials tokens). Server deployment and setup are shown with steps in README.md

#/local_client_server

LOCAL CLIENT-SERVER CODE WITH VIRTUAL DATASTORE (Google Photos) All source code here Testing/ folder has all automated and manual test scripts, packet captures on loopback Results/ folder has: video demo link on local testbed and automated testing results logs

Video demo shows: server and clients run & establish TLS

clients send messages to server (encrypted)

server encrypts and encodes messages into images & uploads to virtual data store (all transcripts kept here) -- cryptosteganography broadcast function

clients are notified whenever someone posted, any node can fetch the most recent message (server fetches, decrypts and sends it encrypted to client, client decrypts and views messages posted on the chatbox window) Automated logs: Verify the functionality of the main ponycrypt library functions

NOTES: anomalies where observed when trying to do iterated testing. Because the cryptosteganography library did not throw errors during the client-server testing, we believe there some image processing may be done by Google when we we upload and or download images and or there are some bugs in the cryptosteganography code. Manual testing: Allows you to verify the cryptosteganography part of Automated testing manually.

Generate your own public key pair: sudo openssl req -x509 -sha256 -nodes -newkey rsa:2048 -days 365 -keyout localhost.key -out localhost.crt

#/virtual_client_server

CLIENT-SIDE SCRIPT WITH VIRTUAL (SERVER(S) AND DATASTORE) == Google Photos servers and albums This runs similar to the first except that the client side script does all the work and the Google high speed servers replace our single server This was further developed by Urian dubbed it Photo Chat.
