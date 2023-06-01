# Websocket

## Install

- install lib in requirements.txt
- cd SocketSV
- run local:  python server.py

## On server

### Run server 
Run in the background with nohup:

```
nohup python server.py &
```
### Check 

Check if the thread runs:

```
netstat -tulpn | grep LISTEN
```
### Kill thread


Kill server thread:
```
kill -9 <pid>
```
