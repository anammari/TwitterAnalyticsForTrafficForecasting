# -*- coding: utf-8 -*-
"""
Created on Mon May 23 15:23:45 2016

@author: Ahmad
"""
from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
import time
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn import svm
from sklearn.metrics import classification_report
import pymongo
import logging
import sys
import pandas as pd
from bson.son import SON
import json
from bson import json_util
from bson.json_util import dumps
import os
import math
import numpy as np

reload(sys)  
sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')


def establish_connection_optimum(db_name, collection_name):
    try:
        # establish a connection to the collection
        host = "XXX"
        port = XXX
        db = db_name
        user = ''
        password = ''
        collection = collection_name
        connection = pymongo.MongoClient(host, port)
#        connection[db].authenticate(user, password)
        return connection[db][collection]
    
    except Exception, e:
        print(e)
        sys.exit()
def save_classifier(classifier,rf_classifier_filename):
    f = open(rf_classifier_filename, 'wb')
    pickle.dump(classifier, f, -1)
    f.close()
    
def save_vectorizer(vectorizer,rf_vectorizer_filename):
    f = open(rf_vectorizer_filename, 'wb')
    pickle.dump(vectorizer, f, -1)
    f.close()

def load_classifier(rf_classifier_filename):
    f = open(rf_classifier_filename, 'rb')
    classifier = pickle.load(f)
    f.close()
    return classifier

def load_vectorizer(rf_vectorizer_filename):
    f = open(rf_vectorizer_filename, 'rb')
    vectorizer = pickle.load(f)
    f.close()
    return vectorizer

def train_RF_model(training_collection,rf_classifier_filename,rf_vectorizer_filename):
    if os.path.isfile(rf_classifier_filename):
        cl = load_classifier(rf_classifier_filename)
        vc = load_vectorizer(rf_vectorizer_filename)
        logging.info("classifier/vectorizer found and loaded from files")
    else:
        logging.info("classifier/vectorizer not found in files. Started training classifier")
        # Read the training data from mongo
        logging.info("Started reading training RF tweets")
        train_data = []
        train_labels = []
        query = {}
        try:
            project = {"_id": 0, "text": 1, "label": 1}
            cursor = training_collection.find(query,project)
            for doc in cursor:
                train_data.append(doc['text'])
                train_labels.append(doc['label'])
        except Exception, e:
            print(e)
            sys.exit()
        
        logging.info("Finished reading training RF tweets")
        
        # Create feature vectors
        try:
            vc = TfidfVectorizer(min_df=5,
                                     max_df = 0.99,
                                     sublinear_tf=True,
                                     use_idf=True,
                                     decode_error='ignore')
            train_vectors = vc.fit_transform(train_data)
        except Exception, e:
            print(e)
            sys.exit()
            
        # Perform training with SVM, kernel=LinearSVC
        try:
            logging.info("Started training RF tweets")
            cl = svm.LinearSVC()
#            cl = svm.SVC(kernel='linear',probability = True)
            t0 = time.time()
            cl.fit(train_vectors, train_labels)
            t1 = time.time()
            time_liblinear_train = t1-t0
            logging.info("Finished training. Time: {}".format(time_liblinear_train))
        except Exception, e:
            print(e)
            sys.exit()
        
        # Persist the classifier / vectorizer
        save_classifier(cl,rf_classifier_filename)
        save_vectorizer(vc,rf_vectorizer_filename)
        
    # Return the classifier / vectorizer
    return (cl,vc)
        
def classify_tweet(tweet1,tweet2,training_collection):
    rf_classifier_filename = 'rf_classifier.pickle'
    rf_vectorizer_filename = 'rf_vectorizer.pickle'
    if os.path.isfile(rf_classifier_filename) and os.path.isfile(rf_vectorizer_filename):
        cl = load_classifier(rf_classifier_filename)
        vc = load_vectorizer(rf_vectorizer_filename)
        logging.info("classifier/vectorizer found and loaded from files")
    else:
        (cl,vc) = train_RF_model(training_collection,rf_classifier_filename,rf_vectorizer_filename)
    
    test_vector = vc.transform([tweet1,tweet2])    
    arr = cl.decision_function(test_vector)
    classes = cl.predict(test_vector)
    return (arr,classes)
#    return str(1 / (1 + math.exp(-1 * cl.decision_function(test_vector))))
#    return (cl.predict(test_vector),cl.predict_proba(test_vector))

if __name__ == '__main__':
#    filename = "/home/optimum/social_entity_extraction/TwitterSentimentsTextBlob/df_tweets_for_classification.csv"
    training_collection = establish_connection_optimum("Twitter", "RFTrainingTweets")
    filename = "df_tweets_for_classification.csv"
    tweet1 = "M11 northbound within J14  Congestion  Thx 2 HW England"
    tweet2 = "A Rumpke employee stopped his garbage truck in middle of High St traffic to open his door and tell me I am the sexiest woman trashqueen"
    (arr,classes) = classify_tweet(tweet1,tweet2,training_collection)
    for i in range(0,len(arr)):
        arr2 = []
        for x in np.nditer(arr[i]):
            arr2.append(1 / (1 + math.exp(-1 * x)))
        print str(max(arr2))
    for i in range(0,len(classes)):
        print classes[i]
