#!/usr/bin/python
#-*- coding: utf-8 -*-
""".. module:: blueprints """
import json

from flask import request, abort, current_app

def auth_required(func):
    def check_auth(*args, **kwargs):
        try:
            token = request.cookies.get('token'),
            if token != current_app.config['token']:
                abort(401)
        except Exception as err:
            abort(401)
        return func(*args, **kwargs)
    return check_auth

