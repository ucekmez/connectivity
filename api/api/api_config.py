#!/usr/bin/python
# -*- coding: utf-8 -*-

import falcon, falcon_jsonify, json, os, requests, shutil
import random, string
from falcon_cors import CORS
from redis import Redis
import glob
import pymongo
import uuid

cors = CORS(allow_all_origins=True,
            allow_all_headers=True,
            allow_all_methods=True,
            allow_credentials_all_origins=True,
            expose_headers_list=["X-Total-Count", "Cache-Control", "Content-Language",
                                 "Content-Type", "Expires", "Last-Modified", "Pragma"]
            )

api = application = falcon.API(middleware=[
    falcon_jsonify.Middleware(help_messages=True),
    cors.middleware])

api.req_options.auto_parse_form_urlencoded=True

DEV                = True
ADDRESS            = os.environ["DEV_ADDRESS"] if DEV else os.environ["PROD_ADDRESS"]
ENDPOINT           = '/api/agentmanagement/v3/{}'
API_URL            = "{}:{}/download/".format(ADDRESS, os.environ["APIPORT"])
STATIC_FOLDER      = "/api/static/"
LOCAL_FOLDER       = STATIC_FOLDER + "local/"
ENCRYPTED_FOLDER   = STATIC_FOLDER + "encrypted/"
ENC_FILE_EXTENSION = '_enc'
MONGOCLIENT        = pymongo.MongoClient("mongodb://root:conn!Mongo123@connectivity-db:27017/")
MONGODB            = MONGOCLIENT["connectivitydb"]
FILES              = MONGODB["files"]
