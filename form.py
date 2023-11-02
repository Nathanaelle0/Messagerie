import datetime
import sqlite3

class message() :
    def __init__(self, content, user) :
        self.content = content
        self.user = user
        self.time = datetime.datetime.now().strftime("%H:%M")
        self.format = f'{self.user} à {self.time} : {self.content}'
        

# Connexion à la base de données
connection = sqlite3.connect('base.db')
cursor = connection.cursor()

# Récupérer les enregistrements de la table "user"
cursor.execute("SELECT * FROM user;")
user_records = cursor.fetchall()

# Créer une classe User
class User:
    def __init__(self, id, username, password, admin, staff):
        self.id = id
        self.username = username
        self.password = password
        self.is_admin = admin
        self.is_staff = staff

# Créer des objets User à partir des enregistrements
users = [User(id=row[0], username=row[1], password=row[2], admin=row[3], staff=row[4]) for row in user_records]


# Fermer la connexion
connection.close()
