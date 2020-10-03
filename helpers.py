import hmac, os, csv
import logging
from werkzeug.security import safe_str_cmp
from datetime import datetime
from hashlib import sha512
from functools import wraps
from flask_session import Session
from flask import session, current_app, request, make_response
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, logout_user, login_required, login_fresh, current_user

from models import *


###########################
# Helpers for translation #
###########################

def get_page_title(page):
    """ 
    Input: language ("en", "fr"...), page ("about", ...)
    """
    if session.get('language') is None:
        language = "en"
    else:
        language = session.get('language')

    # Jinja2 uses UTF-8
    title_file = open(f"static/languages/{ language }/titles.csv", encoding="utf-8")
    
    if title_file is None:
        return ""

    title_reader = csv.reader(title_file)
    title = ""

    # If page doesn't have a specific title, use main title
    for text_id, text in title_reader:
        if text_id == "main":
            title = text
        if text_id == page:
            title = text

    return title


def get_page_static_content(page):
    """
    Input: language ("en", "fr"...), page ("about", ...)
    """
    if session.get('language') is None:
        language = "en"
    else:
        language = session['language']

    content_file = open(f"static/languages/{ language }/{ page }.csv", encoding="utf-8")

    if content_file is None:
        print(f"No { language } content found for page: { page }")
        return {}

    content_reader = csv.reader(content_file)
    content = {}

    for text_id, text in content_reader:
        content[text_id] = text

    return content


# def translate(route):
#     """
#     Decorator to translate pages
#     """
#     @wraps(route)
#     def translation_wrapper(*args, **kwargs):
#         response = make_response(route(*args, **kwargs))
        
#         if current_user.is_authenticated and current_user.remembered is True:
#             response = osga_set_remember_cookie(response)
        
#         elif current_user.is_authenticated and current_user.remembered is False:
#             response = osga_clear_remember_cookie(response)
#             session['user_id'] = None
#             logout_user()

#         return response

#     return translation_wrapper



#########################################################
# Based on: https://stackabuse.com/quicksort-in-python/ #
#########################################################
def partition_flowers(array, start, end):
    pivot_value = array[start].pos_y
    low = start + 1
    high = end

    while True:
        # If the current value we're looking at is larger than the pivot
        # it's in the right place (right side of pivot) and we can move left,
        # to the next element.
        # We also need to make sure we haven't surpassed the low pointer, since that
        # indicates we have already moved all the elements to their correct side of the pivot
        while low <= high and array[high].pos_y >= pivot_value:
            high = high - 1

        # Opposite process of the one above
        while low <= high and array[low].pos_y <= pivot_value:
            low = low + 1

        # We either found a value for both high and low that is out of order
        # or low is higher than high, in which case we exit the loop
        if low <= high:
            array[low], array[high] = array[high], array[low]
            # The loop continues
        else:
            # We exit out of the loop
            break

    array[start], array[high] = array[high], array[start]

    return high


def quick_sort_flowers(array, start, end):
    if start >= end:
        return

    p = partition_flowers(array, start, end)
    quick_sort_flowers(array, start, p-1)
    quick_sort_flowers(array, p+1, end)


#####################################
# Flask login fixes for Remember Me #
#####################################

def osga_encode_cookie(data, key):
    """
    Code from Flask login
    Takes data, encodes it, returns encoded data
    """
    key = key.encode('latin1')
    cookie_digest = hmac.new(key, data.encode('utf-8'), sha512).hexdigest()
    return u'{0}|{1}'.format(data, cookie_digest)


def osga_decode_cookie(cookie, key):
    try:
        data, digest = cookie.rsplit(u'|', 1)
        if hasattr(digest, 'decode'):
            digest = digest.decode('ascii')  # pragma: no cover
    except ValueError:
        return

    key = key.encode('latin1')
    cookie_digest = hmac.new(key, data.encode('utf-8'), sha512).hexdigest()
    if safe_str_cmp(cookie_digest, digest):
        return data


def osga_set_remember_cookie(response):
    """
    Code partially from Flask login
    Sets a Remember me cookie based on user_id, cookie lasts duration time
    """
    user_id = 0

    if 'user_id' in session:
        user_id = session['user_id']

    if user_id and user_id > 0:
        config = current_app.config
        data = osga_encode_cookie(str(user_id), current_app.secret_key)
        expires = datetime.utcnow() + config.get('REMEMBER_COOKIE_DURATION')

        response.set_cookie("remember_token",
                    value=data,
                    expires=expires)
    
    return response



def osga_clear_remember_cookie(response):
    response.delete_cookie("remember_token")
    return response



def cookie_check(route):
    """
    Decorator so each route does the "remember me" checks if remember_me cookie exists and if so, reloads user session.
    """
    @wraps(route)
    def cookie_check_wrapper(*args, **kwargs):
        remember_cookie = request.cookies.get("remember_token")
        
        if remember_cookie is not None:
            decoded_cookie = osga_decode_cookie(remember_cookie, os.getenv("SECRET_KEY"))
            user = Users.query.get(decoded_cookie)
            login_user(user)
            
        if current_user.is_authenticated:
            session['user_id'] = current_user.id
            
        response = make_response(route(*args, **kwargs))
        
        if current_user.is_authenticated and current_user.remembered is True:
            response = osga_set_remember_cookie(response)
        
        elif current_user.is_authenticated and current_user.remembered is False:
            response = osga_clear_remember_cookie(response)
            session['user_id'] = None
            logout_user()

        return response

    return cookie_check_wrapper
