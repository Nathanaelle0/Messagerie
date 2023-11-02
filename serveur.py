import socket
import threading
import sqlite3
import form
import os
import bcrypt
import json
import colorama
from colorama import Fore
import psutil          
import sqlite3
import bcrypt

colorama.init(autoreset=True)
#"""
#def kill_process_using_port(port):
    #for conn in psutil.net_connections(kind='inet'):
        #if conn.laddr.port == port:
            #process = psutil.Process(conn.pid)
            #process.terminate()
            #print(f"Process with PID {conn.pid} using port {port} terminated.")
    #print(f"No process using port {port} found.")

## Remplacez <port> par le numéro de port que vous souhaitez libérer
#port_to_free = 2985
#kill_process_using_port(port_to_free)
#"""

# Configuration du serveur
HOST = '0.0.0.0'
PORT = 2985

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen()
#print(server)
clients = []
users = {}

# Fonction pour gérer les connexions clients
def handle_client(client_socket):
    while True:
        #print('boucle')
        try:
            message = client_socket.recv(1024).decode('utf-8')
            if message:
                print(f"Message reçu : {message}")
                    
                try :
                    connexion_info = json.loads(message)
                    print(connexion_info['type'])
                    # Utiliser les informations de connexion
                    if connexion_info['type'] == 'login' :
                        
                        username = connexion_info["username"]
                        password = connexion_info["password"] #conn('username', 'pasword')
                        connexion_info = (username, password)
                        
                        print(f'tentative de connexion : {connexion_info}')
                        
                        user_find = True
                        
                        for user in form.users :
                            print(user.username, username)
                            if user.username == username :
                                user_find = False
                                if bcrypt.checkpw(connexion_info[1].encode('utf-8'), user.password):
                                    print(f'Connextion de l\'utilisateur {user.username}')
                                    
                                    connexion_message = {
                                        "type": "connexion_succes",
                                        "message": f"Connextion de l\'utilisateur {user.username}",
                                        "user": user.username,
                                        "admin": user.is_admin,
                                        "staff": user.is_staff
                                    }
                                    print(connexion_message)
                                    # Convertir le dictionnaire en JSON
                                    json_connexion_message = json.dumps(connexion_message)
                                    
                                    client_socket.send(json_connexion_message.encode('utf-8'))
                                    users[client_socket] = user.username
                                    #print('temoin2')
                                    
                                    
                                else :
                                    print(f'{Fore.RED}Érreur : Echec de la connexion de l\'utilisateur {user.username} : Mauvais mot de passe')
                                    connexion_message = {
                                        "type": "erreur",
                                        "message": f"Érreur : Echec de la connexion de l\'utilisateur {user.username} : Mauvais mot de passe"
                                    }
                                    # Convertir le dictionnaire en JSON
                                    json_connexion_message = json.dumps(connexion_message)
                                    client_socket.send(json_connexion_message.encode('utf-8'))
                            
                        if user_find :
                            
                            print(f'{Fore.RED}Érreur : Echec de la connexion de l\'utilisateur {username} : Aucun compte trouvé')
                            connexion_message = {
                                "type": "erreur",
                                "message": f"Érreur : Echec de la connexion de l\'utilisateur {username} : Aucun compte trouvé"
                            }
                            # Convertir le dictionnaire en JSON
                            json_connexion_message = json.dumps(connexion_message)
                            client_socket.send(json_connexion_message.encode('utf-8'))
                                    
                    
                    elif connexion_info['type'] == 'signin' :
                        username = connexion_info["username"]
                        password = connexion_info["password"]
                        user_find = True
                        for user in form.users :
        
                            if user.username.lower() == connexion_info["username"].lower() :
                                print(f'Érreur : Echec de la connexion de l\'utilisateur {connexion_info["username"]}, {user.username} exsiste déja, veullier choisir un autre nom d\'utilisateur')
                                user_find = False
                                connexion_message = {
                                    "type": "sign_in_erreur",
                                    "message": f'Érreur : Echec de la connexion de l\'utilisateur {connexion_info["username"]}, {user.username} exsiste déja, veullier choisir un autre nom d\'utilisateur'
                                }
                                # Convertir le dictionnaire en JSON
                                json_connexion_message = json.dumps(connexion_message)
                                client_socket.send(json_connexion_message.encode('utf-8'))

                        if user_find :

                            # Connexion à la base de données
                            connection = sqlite3.connect('base.db')
                            cursor = connection.cursor()
                            
                            salt = bcrypt.gensalt()

                            # Hacher le mot de passe
                            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)

                            # Ajouter l'utilisateur à la table
                            insert_query = '''
                                INSERT INTO user (username, password, is_admin)
                                VALUES (?, ?, ?);
                                '''
                            cursor.execute(insert_query, (username, hashed_password, False))

                            # Commit les changements et fermer la connexion
                            connection.commit()
                            connection.close()
                            #Envoyer une confirmation a l'utilisateur
                            print('nouveau compte créer')
                            
                            connexion_message = {
                                "type": "inscription_succes",
                                "message": f'Nouveu compte créer ! Veullier vous connecter !'
                            }
                            # Convertir le dictionnaire en JSON
                            json_connexion_message = json.dumps(connexion_message)
                            client_socket.send(json_connexion_message.encode('utf-8'))
                    
                    elif connexion_info['type'] == 'message' :
                        message = form.message(connexion_info['message'], connexion_info['user'])
                        print(message)
                        # Diffuser le message à tous les clients connectés
                        for client in clients:
                            print(client)
                            try:
                                client.send(message.format.encode('utf-8'))
                            except Exception as e :
                                print(Fore.RED + str(e) + Fore.RESET)                            
                                clients.remove(client)
                
                
                except Exception as e :
                    print(Fore.RED + e + Foer.RESET)
                    
                            
        except Exception as e :
            print(e)
            clients.remove(client_socket)
            

# Accepter les connexions des clients
while True:
    #print('temoin')
    client_socket, client_address = server.accept()
    message = client_socket.recv(1024).decode('utf-8')
    clients.append(client_socket)
    client_thread = threading.Thread(target=handle_client, args=(client_socket,))
    client_thread.start()
 
