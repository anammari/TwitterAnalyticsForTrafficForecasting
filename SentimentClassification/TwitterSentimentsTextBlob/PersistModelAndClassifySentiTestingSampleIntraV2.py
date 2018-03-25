# -*- coding: utf-8 -*-
"""
Created on Mon May 23 15:23:45 2016

Use a 50% random sample of the training data to train the model 

@author: Ahmad
"""
from __future__ import division
try:
   import cPickle as pickle
except:
   import pickle
from textblob import TextBlob
from textblob.classifiers import NaiveBayesClassifier
import pymongo
import logging
from pytz import timezone
import datetime
import sys
import pandas as pd
from bson.son import SON
import json
from bson import json_util
from bson.json_util import dumps
import os
import random
from collections import Counter

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

def get_column_data(filename, cols):
    filtered_column_data = []
    csv_file = filename
    df = pd.read_csv(csv_file, header=None, dtype=object)
    saved_col = df.ix[:,cols]
    column_data = saved_col.tolist()
    for c in column_data:
        if str(c) != 'nan':
            filtered_column_data.append(str(c))
    return filtered_column_data

def save_classifier(classifier,sentiment_classifier_filename):
    f = open(sentiment_classifier_filename, 'wb')
    pickle.dump(classifier, f, -1)
    f.close()

def load_classifier(sentiment_classifier_filename):
    f = open(sentiment_classifier_filename, 'rb')
    classifier = pickle.load(f)
    f.close()
    return classifier

def train_senti_model(training_collection,sentiment_classifier_filename):
    if os.path.isfile(sentiment_classifier_filename):
        cl = load_classifier(sentiment_classifier_filename)
        logging.info("classifier found and loaded from file")
    else:
        logging.info("classifier not found in file. Started training classifier")
        
        #get random integers 
        try:
            query = {}
            project = {"_id": 0, "text": 1, "label": 1}
            numOfDocs = training_collection.find(query,project).count()
            randomInts = random.sample(range(0, numOfDocs), int(0.5*numOfDocs))
#            print str(numOfDocs)
#            print str(len(randomInts))
        except Exception, e:
            print(e)
            sys.exit()
        tweetsForTraining = []
        texts = []
        labels = []
        labelsForTr = []
        try:
            project = {"_id": 0, "text": 1, "label": 1}
            cursor = training_collection.find(query,project)
            for doc in cursor:
                texts.append(doc['text'])
                labels.append(doc['label'])
            
            for num in randomInts:
                tweetsForTraining.append((texts[num],labels[num]))
                labelsForTr.append(labels[num])
#            print str(len(tweetsForTraining))
            logging.info("training using {} tweets".format(len(tweetsForTraining)))
            logging.info("Distribution of classes in the training sample: {}".format(Counter(labelsForTr))) 
            cl = NaiveBayesClassifier(tweetsForTraining)
            save_classifier(cl,sentiment_classifier_filename)
            logging.info("classifier trained and saved in file")
        except Exception, e:
            print(e)
            sys.exit()
            
    return cl
      
def classify_testing_sample(cl,filename):
    logging.info("Started reading senti tweets from text file")
    tweetsForTesting = []
    try:
        tweetTexts = get_column_data(filename,0)
        tweetClasses = get_column_data(filename,1)
                
        if len(tweetTexts) == len(tweetClasses) and len(tweetTexts) > 2:
            for i in range(1,len(tweetTexts)):
                tweetsForTesting.append((tweetTexts[i],tweetClasses[i]))
    except Exception, e:
    		print(e)
    		sys.exit()
     
    logging.info("Finished reading {} senti tweets and {} classes from text file".format(len(tweetTexts),len(tweetClasses)))

    if len(tweetsForTesting) > 1:
        failed = 0
        true_tags = []
        classified_tags = []
        for i in range(0,len(tweetsForTesting)):
            try:
                classified_tags.append(cl.classify(tweetsForTesting[i][0]))
                true_tags.append(tweetsForTesting[i][1])
            except UnicodeDecodeError, e:
        		failed += 1
        		continue
            except Exception, e:
        		print(e)
        		sys.exit()
        logging.info("no of true tags: {}".format(len(true_tags)))
        logging.info("no of classified tags: {}".format(len(classified_tags)))
        logging.info("failed to classify {} tweets".format(failed))
        
        #classification evaluation
        true_pos = 0
        false_pos = 0
        true_neg = 0
        false_neg = 0
        true_neut = 0
        false_neut = 0
        overall_acc = 0
        for i in range(0,len(true_tags)):
            if true_tags[i] == 'Positive' and classified_tags[i] == 'Positive':
                true_pos += 1
            elif true_tags[i] != 'Positive' and classified_tags[i] == 'Positive':
                false_pos += 1
            elif true_tags[i] == 'Negative' and classified_tags[i] == 'Negative':
                true_neg += 1
            elif true_tags[i] != 'Negative' and classified_tags[i] == 'Negative':
                false_neg += 1
            elif true_tags[i] == 'Neutral' and classified_tags[i] == 'Neutral':
                true_neut += 1
            elif true_tags[i] != 'Neutral' and classified_tags[i] == 'Neutral':
                false_neut += 1
        overall_acc = round((true_pos + true_neg + true_neut) / len(true_tags),2)
        
        logging.info("no of true positives: {}".format(true_pos))
        logging.info("no of false positives: {}".format(false_pos))
        logging.info("no of true negatives: {}".format(true_neg))
        logging.info("no of false negatives: {}".format(false_neg))
        logging.info("no of true neutrals: {}".format(true_neut))
        logging.info("no of false neutrals: {}".format(false_neut))
        logging.info("overall accuracy: {}".format(overall_acc))
          
    
#    acc = cl.accuracy(tweetsForTesting)
#    logging.info("Classifier accuracy: {}".format(acc))
        

if __name__ == '__main__':
    training_collection = establish_connection_optimum("Twitter", "SentiTrainingTweets")
    filename = "/home/optimum/social_entity_extraction/TwitterSentimentsTextBlob/df_tweets_for_classification.csv"
    sentiment_classifier_filename = "/home/optimum/social_entity_extraction/TwitterSentimentsTextBlob/semtiment_classifier.pickle"
#    sentiment_classifier_filename = "semtiment_classifier.pickle"    
    cl = train_senti_model(training_collection,sentiment_classifier_filename)
#    train_senti_model(training_collection,sentiment_classifier_filename)
    classify_testing_sample(cl,filename)
