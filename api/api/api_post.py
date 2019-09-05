from api_config import *
import time
import cryptolib
from rq.decorators import job
import requests
import random, string, shutil
from bson.json_util import dumps
import hashlib

#######################################################
############ functions related to endpoints ###########
#######################################################

# calculate md5 checksum of given file
def checksum(filepath):
    return hashlib.md5(open(filepath,'rb').read()).hexdigest()


def generate_filename(payload):
    try:
        extension = "." + payload.split(".")[-1] if len(payload.split(".")[-1]) <= 4 else ".file"
    except:
        extension = ".file"
    filename = ''.join(random.choice(string.ascii_uppercase) for i in range(8)) + extension
    return filename


@job('encrypt', connection=Redis(host='connectivity-redis'))
def download_encrypt_queue(is_remote, data, filename, record):
    enc_file    = ENCRYPTED_FOLDER + filename + ENC_FILE_EXTENSION
    COPY_FOLDER = STATIC_FOLDER if is_remote else LOCAL_FOLDER

    if is_remote:
        # download file
        FILES.update_one({ '_id': record }, {"$set": { "status": "downloading" }})
        r = requests.get(data["url"], stream=True)
        with open(STATIC_FOLDER + filename, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

    # open and encrypt file
    FILES.update_one({ 'id': record }, {"$set": { "status": "encrypting" }})
    try:
        start_time = time.time()
        cipher = cryptolib.Crypto(key=data["key"], payload=open(COPY_FOLDER + filename, "rb").read())
        cipher.encrypt(enc_file)
        end_time = time.time()

        FILES.update_one({ 'id': record }, {"$set": { "status": "encrypted", "checksum": checksum(enc_file), "time": end_time - start_time }})

        # remove raw file
        if is_remote:
            os.remove(STATIC_FOLDER + filename)

    except MemoryError as e:
        FILES.update_one({ 'id': record }, {"$set": { "status": "memory_error" }})
    except:
        FILES.update_one({ 'id': record }, {"$set": { "status": "error" }})



@job('decrypt', connection=Redis(host='connectivity-redis'))
def decrypt_queue(name, id, filepath, key):
    cipher = cryptolib.Crypto() # empty cipher

    FILES.update_one({ 'id': id }, {"$set": { "status": "decrypting" }})
    result = cipher.decrypt(filepath=filepath, key=key)
    with open(STATIC_FOLDER + name, 'wb') as f:
        f.write(result)
        FILES.update_one({ 'id': id }, {"$set": { "checksum": checksum(STATIC_FOLDER + name) }})
    FILES.update_one({ 'id': id }, {"$set": { "status": "decrypted", "url": API_URL + id, "location": STATIC_FOLDER + name }})

    # remove encrypted file
    #os.remove(filepath)




class Encryption(object):
    def on_post(self, req, resp):
        data     = req.json

        # scenario1 : when user enters a URL in payload
        if "url" in data:
            filename  = generate_filename(data["url"])
            raw_file  = STATIC_FOLDER + filename
            is_remote = True
        # scenario2 : when user wants to encrypt a local file
        elif "filename" in data:
            filename  = data["filename"]
            raw_file  = LOCAL_FOLDER + filename
            is_remote = False

        enc_file  = ENCRYPTED_FOLDER + filename + ENC_FILE_EXTENSION
        file_id   = ''.join(random.choices(string.ascii_lowercase + string.digits, k=16))

        result    = { "filename": filename,
                      "location": enc_file,
                      "url": API_URL + file_id,
                      "status": "queued",
                      "id": file_id }

        record    = FILES.insert_one(result)
        job       = download_encrypt_queue.delay(is_remote=is_remote,
                                                 data=data,
                                                 filename=filename,
                                                 record=file_id).id

        resp.json = { "id": file_id }



class Decryption(object):
    def on_post(self, req, resp):
        data     = req.json # expecting id and key

        # get the corresponding record
        record = FILES.find_one({"id": data["id"]})
        filepath = record["location"]

        job      = decrypt_queue.delay(name=record["filename"],
                                       id=data["id"],
                                       filepath=record["location"],
                                       key=data["key"]).id
        resp.json = { "id": data["id"] }



class CheckRequest(object):
    def on_post(self, req, resp):
        data     = req.json

        record = FILES.find_one({"id": data["id"]})

        result = { "id": record["id"],
                   "url": record["url"],
                   "status": record["status"]}

        if "checksum" in record:
            result["checksum"] = record["checksum"]
        if "time" in record:
            result["time"]     = record["time"]

        resp.json = result


class DownloadFile(object):
    def on_get(self, req, resp, id):

        try:
            record = FILES.find_one({"id": id})

            # check if file is ready
            if record["status"] == "encrypted" or record["status"] == "decrypted":
                resp.status = falcon.HTTP_200
                resp.content_type = "application/octet-stream"
                record = FILES.find_one({"id": id})
                with open(record["location"], 'r') as f:
                    resp.body = f.read()
            else: # means that file is either not ready or no such file
                resp.status = falcon.HTTP_100
                resp.json = { "message": "denied" }
        except:
            resp.status = falcon.HTTP_404
            resp.json = { "message": "denied" }

################


class MCL_Onboard(object):
    def on_post(self, req, resp):
        resp.json = {'message': 'OK', 'status': 'success'}

class MCL_KeyRotation(object):
    def on_post(self, req, resp, agent_id):
        data      = req.json
        resp.json = {'message': 'OK', 'status': 'success', 'id': agent_id}

class MCL_AccessToken(object):
    def on_post(self, req, resp):
        job       = stacked_function.delay(value=1 ).id
        resp.json = {'message': 'OK', 'status': 'success'}

class MCL_Exchange(object):
    def on_post(self, req, resp):
        job       = stacked_function.delay(value=1 ).id
        resp.json = {'message': 'OK', 'status': 'success'}


api.add_route(ENDPOINT.format('encrypt'), Encryption())
api.add_route(ENDPOINT.format('decrypt'), Decryption())
api.add_route(ENDPOINT.format('check'), CheckRequest())
api.add_route('/download/{id}', DownloadFile())
api.add_route(ENDPOINT.format('register'), MCL_Onboard())
api.add_route(ENDPOINT.format('register/{agent_id}'), MCL_KeyRotation())
api.add_route(ENDPOINT.format('oauth/token'), MCL_AccessToken())
api.add_route(ENDPOINT.format('exchange'), MCL_Exchange())









#EOF
