import firebase_admin
from firebase_admin import credentials, firestore
import pyrebase

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

db = firestore.client()


firebaseConfig = {
    "apiKey": "AIzaSyDBUIc83FIGrfJYvc2yTQLroYoYrG0IBfI",
  "authDomain": "nana-777a9.firebaseapp.com",
  "databaseURL": "https://nana-777a9-default-rtdb.asia-southeast1.firebasedatabase.app",
  "projectId": "nana-777a9",
  "storageBucket": "nana-777a9.appspot.com",
  "messagingSenderId": "597052531820",
  "appId": "1:597052531820:web:b90a57695fe1aeaa852449"
}
firebase = pyrebase.initialize_app(firebaseConfig)
storage = firebase.storage()

def get_all_collection(collection, orderBy=None, direction=None):
    if orderBy:
        collects_ref = db.collection(collection).order_by(
            orderBy, direction=direction)
    else:
        collects_ref = db.collection(collection)
    collects = collects_ref.stream()
    RETURN = []
    for collect in collects:
        ret = collect.to_dict()
        ret['id'] = collect.id
        RETURN.append(ret)
    return RETURN



