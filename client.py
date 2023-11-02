from tkinter import *
from tkinter.messagebox import *
from PIL import Image, ImageTk
import socket
import json
from colorama import Fore
import time
import os

#Inisialisation

user = None

HOST = 'localhost'
PORT = 2985#int(input('port\n>> '))

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
client.send('con'.encode('utf-8'))
time.sleep(0.5)


#Fonction
def connexion_command() :
    option.pack_forget()
    connexion.pack(fill="x", padx=10, pady=10)

def inscription_command() :
    option.pack_forget()
    inscription.pack(fill="x", padx=10, pady=10)
    
def login() :
    
    username = username_conn.get()
    password = mdp_conn.get()
    print(username, password)
    
    connexion_info = {
        "type" : 'login',
        "username": username,
        "password": password
    }
    # Convertir le dictionnaire en JSON
    json_connexion_info = json.dumps(connexion_info)
    print('temoin')
    # Envoyer la chaîne JSON au serveur
    client.send(json_connexion_info.encode('utf-8'))
    
    connexion_info = client.recv(1024).decode('utf-8')
    connexion_info = json.loads(connexion_info)

    if connexion_info.get('type') == "connexion_succes" :
        print(Fore.YELLOW + connexion_info.get('message') + Fore.RESET)
        connexion.pack_forget()
        message.pack(padx=10, pady=10, fill="both", expand=True)
        user = connexion_info['user']
        os.environ['user'] = user
        admin = connexion_info['admin']
        os.environ['admin'] = admin
        client.setblocking(False)
        gui.geometry("800x600")

    if connexion_info.get('type') == "erreur" :
        print(Fore.RED + connexion_info.get('message') + Fore.RESET)
        showerror('Érreur', connexion_info.get('message'))
    
def signin() :
    
    username = username_insc.get()
    password = mdp_insc.get()
    password_conf = mdp_comfirm.get()
    
    if not 'admin' in username :
    
        if password != '' :
        
            if password == password_conf :
                
                connexion_info = {
                    "type" : 'signin',
                    "username": username,
                    "password": password
                }
                # Convertir le dictionnaire en JSON
                json_connexion_info = json.dumps(connexion_info)
                print('temoin')
                # Envoyer la chaîne JSON au serveur
                client.send(json_connexion_info.encode('utf-8'))
                
                connexion_info = client.recv(1024).decode('utf-8')
                connexion_info = json.loads(connexion_info)

                if connexion_info.get('type') == "inscription_succes" :
                    showinfo('Réusite', connexion_info.get('message'))
                    inscription.pack_forget()
                    connexion.pack(fill="x", padx=10, pady=10)

                if connexion_info.get('type') == "sign_in_erreur" :
                    print(Fore.RED + connexion_info.get('message') + Fore.RESET)
                    showerror('Érreur', connexion_info.get('message'))
            
            
            else :
                showerror('Érreur', 'Les mots de passe ne corespondent pas')
        else :
            showerror('Érreur', 'Les mots de passe ne peuvent être vide')
    else :
        showerror('Érreur', 'Le nom d\'utilisateur ne peut contenir le mot admin')
        
def send_msg(*args) :
    messagesend = send_entry.get()
    
    if messagesend != '' :
        user = os.environ['user']
        if os.environ['admin'] :
            user = f'[Admin] {user}'
        message_info = {
            "type" : 'message',
            "message": messagesend,
            "user": user
        }
        
        # Convertir le dictionnaire en JSON
        json_connexion_info = json.dumps(message_info)
        # Envoyer la chaîne JSON au serveur
        client.send(json_connexion_info.encode('utf-8'))
        send_entry.delete(0, END)


#Fenetre

gui = Tk()
gui.title('Messagerie')

#choix de l'option

option = Frame(gui)

Button(option, command=connexion_command, text='Connexion').pack(side=LEFT)
Button(option, command=inscription_command, text='Inscription').pack(side=RIGHT)

option.pack(padx=30, pady=30)

#Inscription
inscription = LabelFrame(gui, text="Inscription")
inscription.pack_forget()
#.pack(fill="x", padx=10, pady=10)

Label(inscription, text="Nom d'utilisateur :").pack()
username_insc = Entry(inscription)
username_insc.pack(fill="x", padx=5, pady=5)

Label(inscription, text="Mot de passe :").pack()
mdp_insc = Entry(inscription, show="•")
mdp_insc.pack(fill="x", padx=5, pady=5)

Label(inscription, text="Confirmer le mot de passe :").pack()

mdp_comfirm = Entry(inscription, show="•")
mdp_comfirm.pack(fill="x", padx=5, pady=5)

Button(inscription, command=signin, text='Inscription').pack()

#Connection
connexion = LabelFrame(gui, text="Connexion")
connexion.pack_forget()
#.pack(fill="x", padx=10, pady=10)

Label(connexion, text="Nom d'utilisateur :").pack()
username_conn = Entry(connexion)
username_conn.pack(fill="x", padx=5, pady=5)

Label(connexion, text="Mot de passe :").pack()
mdp_conn = Entry(connexion, show="•")
mdp_conn.pack(fill="x", padx=5, pady=5)

Button(connexion, command=login, text='Connexion').pack()

#Messagerie

message = Frame(gui)
message.pack_forget()
#.pack(padx=10, pady=10)

message_listbox = Listbox(message)
message_listbox.pack(fill="both", expand=True)

image_path = "send_logo.png"  # Remplacez par le nom de votre fichier PNG

send_image = Image.open(image_path)
send_image = ImageTk.PhotoImage(send_image)

send_message = Frame(message, borderwidth=2, relief=GROOVE, background='white')
send_message.pack(pady=5, fill="x")

send_entry = Entry(send_message, relief=FLAT, highlightthickness=0)
send_entry.pack(fill="x", expand=True, side=LEFT)
send_entry.bind("<Return>", send_msg)

def increment_label_forever():
    if message.winfo_viewable() :
        try :
            messagerecv = client.recv(1024).decode('utf-8')
            message_listbox.insert(END, messagerecv)
            if '[Admin]' in messagerecv.split(':')[0] :
                last_index = message_listbox.size() - 1
                message_listbox.itemconfig(last_index, {'bg': 'white', 'fg': 'red'})
        except :
            pass
    gui.after(100, increment_label_forever)

Button(send_message, command=send_msg, image=send_image, relief=FLAT, background='white', highlightthickness=0).pack(side=RIGHT)

gui.after_idle(increment_label_forever)
gui.mainloop()
