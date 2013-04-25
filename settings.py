import os
# configuration
DATABASE = 'Flashyapp'
DEBUG = True
SECRET_KEY = 'devkey333'
USERNAME = 'flashyuser'
PASSWORD = 'abjnty333'
APP_ROOT = os.path.dirname(os.path.abspath(__file__))
# Image directory
IMAGE_DIRECTORY = "/var/www/user_images/"
ALLOWED_IMAGE_EXTENSIONS = set(['jpeg', 'jpg', 'gif', 'png', 'bmp'])
# Logging TODO:add logging code

