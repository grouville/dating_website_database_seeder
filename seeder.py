#!/usr/bin/env python3

from faker import Faker
from faker.providers import BaseProvider
import random
import os
import lorem
import shutil
import pymysql.cursors
import hashlib

# Debug print function
# print('login: {}\nfirst name: {}\nlast name: {}\nage: {}\ngender: {}\norientation: {}\nemail: {}\nbio: {}\nconfirmed_acc: {}\nlocalisation_acc: {}\npsswd: {}\n'.format(
#     login, first_name, last_name, age, gender, orientation, email, bio, CONFIRMED_ACC, LOCALISATION_ACC, password))

# Constants
PATH_MALE = '/Users/ldaveau/Desktop/portraits/hommes'
PATH_FEMALE = '/Users/ldaveau/Desktop/portraits/femmes'
DST_DIR = '/Users/ldaveau/Desktop/101-mamp4/data/www/matcha/uploads'
CONFIRMED_ACC = 1
LOCALISATION_ACC = 1
CONNECTED = 0
ADMIN = 0


# Prerequisites
orientations = ('Male', 'Female', 'Both')
tags = {'cinemas': ('cinemas','1'),'danses': ('danses','1'),'festivals': ('festivals','1'),'musiques': ('musiques','1'),'sports': ('sports','1'),'voyages': ('voyages','1')}
min_position = {'latitude': 45.099903, 'longitude': 3.589950}
max_position = {'latitude': 46.364163, 'longitude': 5.911202}
women = [name for r, d, f in os.walk(PATH_FEMALE) for name in f]
men = [name for r, d, f in os.walk(PATH_MALE) for name in f]
password = hashlib.sha256(b"coucou").hexdigest()


def copy_and_get_image_name(gender, index, login):
    """ Function that copies the image to the upload folder and saves it with the proper login, according to the corresponding gender of the fake profile """
    # Collect image name according to the sex and the index
    name = men[random.randint(1,len(men))] if gender is 'Male' else women[random.randint(1,len(women))]
    # Collect src path according to the sex
    src_path = "{}/{}".format(PATH_MALE if gender is 'Male' else PATH_FEMALE, name)
    # Construct new name for the image
    new_name = "{}_{}.png".format(login, index)
    # Copy and convert image
    shutil.copy(src_path, "{}/{}".format(DST_DIR, new_name))
    return new_name

def get_gender(sexe):
    """ Retrieves the gender and format it properly """
    return 'Female' if sexe is 'F' else 'Male'

def execute_push_to_db(sql, connection):
    """ Push the sql request to the db """
    with connection.cursor() as cursor:
        cursor.execute(sql)
    # Push to the db
    connection.commit()

def create_and_send_user_db(info, connection):
    """ Create and send user infos to the user table """
    # Create the fake data
    login = info['username']
    first_name = info['name'].split(' ')[0]
    last_name = info['name'].split(' ')[1]
    age = random.randint(18, 99)
    gender = get_gender(info['sex'])
    orientation = orientations[random.randint(0, 2)]
    email = info['mail']
    bio = lorem.paragraph()
    # Preprare SQL request
    sql = f"INSERT INTO user_db (picture, login, first_n, last_n, age, gender, sex_o, password, email, bio, connected, localisation, valid, admin) VALUES (0, '{login}', '{first_name}', '{last_name}', '{age}', '{gender}', '{orientation}', '{password}', '{email}', '{bio}', '{CONNECTED}', '{LOCALISATION_ACC}', '{CONFIRMED_ACC}', '{ADMIN}')"
    # Send data to the user table
    execute_push_to_db(sql, connection)
    return login, gender, age

def create_and_send_tag_db(connection, login, gender, age):
    """ Create and send tastes infos to the tags table """
    # Create the fake data
    cinemas = tags['cinemas'][random.randint(0,1)]
    danses = tags['danses'][random.randint(0,1)]
    festivals = tags['festivals'][random.randint(0,1)]
    musiques = tags['musiques'][random.randint(0,1)]
    sports = tags['sports'][random.randint(0,1)]
    voyages = tags['voyages'][random.randint(0,1)]
    popularity = random.randint(50, 200)
    latitude = random.uniform(min_position['latitude'], max_position['latitude'])
    longitude = random.uniform(min_position['longitude'], max_position['longitude'])
    # Preprare SQL request
    sql = f"INSERT INTO tag_db (login, cinemas, danses, festivals, musiques, sports, voyages, age, sex_o, popularite, latitudes, longitudes) VALUES ('{login}', '{cinemas}', '{danses}', '{festivals}', '{musiques}', '{sports}', '{voyages}', '{age}', '{gender}', '{popularity}', '{latitude}', '{longitude}')"
    # Send data to the user table
    execute_push_to_db(sql, connection)

def create_and_send_data_db(connection, gender, i, login):
    """ Create and send user infos to the user table """
    picture = 1
    # Create the fake data
    picture = copy_and_get_image_name(gender, i, login)
    # Preprare SQL request
    sql = f"INSERT INTO data (login, picture) VALUES ('{login}', '{picture}')"
    # Send data to the user table
    execute_push_to_db(sql, connection)

def construct_db(fake, nb_user, connection):
    """ Generates profiles one by one """
    # Range is faster than enumerates when we don't access the element at the index several times
    for i in range(nb_user):
        # Generate a fake profile
        info = fake.profile()
        # Create and upload to User_db
        login, gender, age = create_and_send_user_db(info, connection)
        # Create and upload to Tag_db
        create_and_send_tag_db(connection, login, gender, age)
        # Create and upload to Data_db
        create_and_send_data_db(connection, gender, i, login)

if __name__ == "__main__":
    """ Main of the program """
    # Initialize Faker
    fake = Faker()
    # Initialize module
    fake.add_provider(BaseProvider)
    # Request user input
    nb_user = input('How many user do you want to create? ')
    try:
        nb_user = int(nb_user)
    except ValueError:
        print('We want a number!!')
        exit()
    # Connect to db
    connection = pymysql.connect(host='localhost',
        port=3306,
        user=os.getenv('USER_BDD'),
        password=os.getenv('PSSWD_BDD'),
        db='Matcha')
    # Fake the data
    construct_db(fake, nb_user, connection)
    # Close connection
    connection.close()
