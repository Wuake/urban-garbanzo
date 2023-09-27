import socket
import os

def server_program():
    # get the hostname
    host = '127.0.0.1'
    port = 5000  # initiate port no above 1024

    server_socket = socket.socket()  # get instance
    # look closely. The bind() function takes tuple as argument
    server_socket.bind(('', port))  # bind host address and port together
    
    # configure how many client the server can listen simultaneously
    server_socket.listen(2)
    print("server running :: \n")
    while True:
        conn, address = server_socket.accept()  # accept new connection
        print("Connection from: " + str(address))
        while True:
            # receive data stream. it won't accept data packet greater than 1024 bytes
            data = conn.recv(1024).decode()
            if not data:
                break
            print("from connected user: " + str(data))
            smsg = str(data)  # initiate port no above 1024
            print(smsg.split("@")[0])
            if smsg.split("@")[0] == "open_ppt": 
                msg = "server ok "
                ppt = smsg.split("@")[1] # "C:\\wamp64\\www\\test.pptx"
                conn.send(msg.encode())  # send data to the client
                print("Votre adresse IP locale est :", ppt)
                os.system('start /max "" "POWERPNT.EXE" /S '+"./"+ppt)  # /s slide show C:\\Program Files (x86)\\Microsoft Office\\root\\Office16\\
                # os.system('start /max "" "chrome.EXE" /s '+ppt)
        conn.close()  # close the connection
        print("client disconnected")                      
        # Créer un socket pour récupérer l'adresse IP locale
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        local_ip_address = s.getsockname()[0]
        s.close()

        # Récupérer l'adresse IP distante
        remote_ip_address = socket.gethostbyname(socket.gethostname())

        print("Votre adresse IP locale est :", local_ip_address)
        print("Votre adresse IP distante est :", remote_ip_address)
if __name__ == '__main__':
    server_program()
