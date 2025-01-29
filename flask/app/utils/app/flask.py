from flask import g, request
from contextlib import contextmanager

# -----------------------
# Logged user
# -----------------------
def set_logged_user(user):

    g.user = user


def get_logged_user():
    return getattr(g, "user", None)


def get_logged_user_id():
    u = get_logged_user()
    if u is None:
        return None
    return u.id


@contextmanager
def temporary_logged_user(user):
    prev = get_logged_user()
    try:
        set_logged_user(user)
        yield
    finally:
        set_logged_user(prev)


def get_locale():
    # if a user is logged in, use the locale from the user settings
    user = get_logged_user()
    from app.api.auth import token_auth, associate_action

    if user is not None:
        if user.locale is None:
            return "en"
        
        return user.locale.lower()
    
    # otherwise try to guess the language from the user accept
    # header the browser transmits.  We support de/fr/en in this
    # example.  The best match wins.
    return request.accept_languages.best_match(['de', 'fr', 'en', 'es', 'pt'])

def get_timezone():
    user = get_logged_user()
    if user is not None:
        return user.timezone
    

# -----------------------
# Event
# -----------------------
def set_current_event(event):
    g.event = event


def get_current_event():
    return getattr(g, "event", None)


@contextmanager
def temporary_event(event):
    from app import db

    prev = get_current_event()
    try:
        # I want to flush before setting the new event so that every change
        # made during the previous event is associated to it
        if prev is not None:
            db.session.flush()
        set_current_event(event)
        yield event
        # I want to flush before setting the previous event so that every change
        # made during the context manager is flushed to the database and associated to
        # the correct event
        db.session.flush()
    finally:
        set_current_event(prev)


# -----------------------
# Sudo
# -----------------------
def is_sudo():
    return getattr(g, "sudo", False)


@contextmanager
def sudo():
    # Did not create set_sudo() and unset_sudo()
    # on purpose, so that we always use the context manager
    try:
        g.sudo = True
        yield
    finally:
        g.sudo = False


# -----------------------
# In commit
# -----------------------
def is_in_commit():
    return getattr(g, "in_commit", False)


def start_commit():
    g.in_commit = True


def end_commit():
    g.in_commit = False
