import sqlite3
import bcrypt

# Connexion à la base de données
connection = sqlite3.connect('base.db')
cursor = connection.cursor()

# Création de la table "user"
create_table_query = '''
CREATE TABLE IF NOT EXISTS user (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL,
    is_admin BOOLEAN,
    is_staff BOOLEAN
);
'''
cursor.execute(create_table_query)

# Informations de l'utilisateur à ajouter
new_username = input("Nom d'utilisateur : ")
new_password = input("Mot de passe : ")
new_is_admin = input('Admin : ')
new_is_staff = input('staff : ') 

# Générer un sel pour le hachage
salt = bcrypt.gensalt()

# Hacher le mot de passe
hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), salt)

# Ajouter l'utilisateur à la table
insert_query = '''
INSERT INTO user (username, password, is_admin, is_staff)
VALUES (?, ?, ?, ?);
'''
cursor.execute(insert_query, (new_username, hashed_password, new_is_admin, new_is_staff))

# Commit les changements et fermer la connexion
connection.commit()
connection.close()
