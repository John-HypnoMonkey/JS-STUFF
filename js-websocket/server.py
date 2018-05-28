import socket
import threading
import time
import base64
import hashlib

bind_ip = "127.0.0.1"
bind_port = 9999

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

server.bind((bind_ip, bind_port))

server.listen(5)

print("Listening on {0}, {1}".format(bind_ip, str(bind_port)))


# this is our client-handling thread
def handle_client(client_socket):
    key = ""
    request = client_socket.recv(1024).strip()
    headers = str(request).split("\\r\\n")
    print(headers)
    if "Connection: Upgrade" in str(request) and "Upgrade: websocket" in str(request):
        for line in headers:
            if "Sec-WebSocket-Key" in line:
                print(line)
                key = line.split(" ")[1]
    key = key + "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
    key = key.encode("ascii")
    resp_key = base64.standard_b64encode(hashlib.sha1(key).digest())
    resp_key = resp_key.decode("utf-8")
    hand_shake = "HTTP/1.1 101 Switching Protocols\r\n" + \
                 "Upgrade: websocket\r\n" + \
                 "Connection: Upgrade\r\n" + \
                 "Sec-WebSocket-Accept: %s\r\n\r\n"%(resp_key)
    print(hand_shake)
    client_socket.send(hand_shake.encode("ascii"))
    message = "Well hello there"
    # first byte is a code
    frame = [129]
    # second is a length of the message
    frame += [len(message)]
    frame_to_send = bytearray(frame) + message.encode("ascii")
    time.sleep(1)
    client_socket.send(frame_to_send)
    client_socket.close()


while True:
    client, addr = server.accept()
    print("Accepted connection")
    client_handler = threading.Thread(target=handle_client,
                                      args=(client,))
    client_handler.start()
