# -*- coding: utf-8 -*-
"""
Created on Wed Jul 15 14:45:09 2015

@author: shubham
"""

#import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
import json
import string
import os.path

#import nltk
from nltk import word_tokenize
from nltk.stem import SnowballStemmer
from nltk.corpus import stopwords
from collections import Counter
from fuzzywuzzy import process
from collections import defaultdict
import re
from textblob import TextBlob


class Tagger(object):
    def __init__(self, filename):
        self.data = []
        with open('data/' + filename) as f:
            for line in f:
                self.data.append(json.loads(line))
            f.close()    
        
        self.positive = defaultdict(lambda:False)
        self.negative = defaultdict(lambda:False)
        with open('positive.txt') as f:
            for line in f:
                self.positive[line.split('\n')[0]] = True
            f.close()
        
        with open('negative.txt') as f:
            for line in f:
                self.negative[line.split('\n')[0]] = True
        self.positive['pros'] = True
        self.negative['cons'] = True
        self.negative['expensive'] = True
        self.positive['mammoth'] = True	
        self.positive['value'] = True
        self.positive['sound'] = False
        self.positive['gud'] = True
        self.positive['timely'] = True
        self.positive['thanks'] = True
        self.positive['before time'] = True
        self.stopwords = stopwords.words('english')
        self.stopwords.remove('not')
        self.product_tag = {'camera':['photo', 'camera','megapixel', 'ppi', 'resolution' ],
                            'battery': ['backup', 'battery','charging','charge','charger', 'longlasting', 'backup', 'internal'],
                            'sound': ['sound','audio','music', 'loud', 'voice', 'volume', 'headphone', 'head phone', 'microphone', 'mic'],
                            'display': ['display', 'touch','screen', 'bright', 'large', 'touchscreen', 'clear'],
                            'specs': ['specs', 'memory','heat', 'ram','bluetooth','android','performance','app', 'cdma', 'repair', 'software'],
                            'build': [ 'build', 'built', 'durabl', 'durabil','color', 'weight','heavy','light', 'lightweight','metal','matte','plastic', 'solid', 'build', 'button']
                            }
        self.price_tag = ['rate', 'budget','price','expensive','cheap', 'cost', 'value', 'money']
        self.delivery_tag = ['delivery','delivered','deliver','quick', 'on time', 'service']
        self.warranty_tag = ['warranty', 'guarantee', 'guaranty',]
        self.seller_tag = ['seller', 'vendor', 'courier', 'amazon', 'flipkart', 'snapdeal', 'paytm']
        
        self.tags = {'product': self.product_tag, 'price': self.price_tag,
                     'seller': self.seller_tag, 'warranty': self.warranty_tag,
                     'delivery': self.delivery_tag}
        self.tagged_data = {}
        self.overall_dict = {"overall_sentiment": 0,
        'product':{'camera':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
                   'battery':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
                   'sound':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
                   'display':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
                   'build':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
                   'specs':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
                   'whole':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10}},
       'delivery':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
       'warranty':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
       'seller':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10},
       'price':{'pos':0, 'neg':0, 'pos_contribute': [['',0]]*10, 'neg_contribute': [['',0]]*10}}
                    
        #self.overall_aggregate()
    
    def add_reviews(self, filename, sort_new = True):
        '''Add reviews from other json files
        INPUT: String: Filename like flipkart.json         
        '''
        with open('data/' + filename) as f:
            for line in f:
                self.data.append(json.loads(line))
            f.close()  
        if sort_new:
            self.sort_data()
        self.store_mobile_list()
           
    def sort_data(self):
        self.data = sorted(self.data, key = lambda k: k['title'])

    def compute_avg_rating(self):
        '''Stores the average rating value in data'''
        for phone in self.data:
            avg = sum(float(review[0]) for review in phone['reviews'])
            if len(phone['reviews'])!=0:
                avg = avg/len(phone['reviews'])
            phone['avg_rating'] = float(avg)
        
    def remove_punc(self, text):
        '''Returns the input text without any punctuations'''
        text = text.replace('.', ' ')
        text = text.replace("isn't", "is not")
        return ''.join([t for t in text if t not in string.punctuation and t not in '1234567890' and ord(t)<128])
                
    def clean_data(self, joint=False):
        '''Strips the data of all stopwords, punctuations and tokenizes reviews
        INPUT: joint: Boolean value: True if output is wanted as a string
                                     False if output wanted as list of words
        '''
        for phone in self.data:
            for i, review in enumerate(phone['reviews']):
                review = str(self.remove_punc(review[-1].lower().encode('utf-8')))
                tokens = [word for word in word_tokenize(review) if word not in self.stopwords]
                if joint == True:
                    tokens = ' '.join(tokens)
                phone['reviews'][i].append(tokens)
                
    def get_tag_list(self):
        '''Returns all the tags in a list format. Just a helper function'''
        tag_list = []
        for tag_type, tags in self.tags.items():
            if tag_type!='product':
                tag_list.extend(tags)
            else:
                for attr, attr_tags in self.tags[tag_type].items():
                    tag_list.append(attr)
                    tag_list.extend(attr_tags)
        return tag_list
            
    def filter_bad_reviews(self):
    	'''Remove reviews from the data which do not contain any of attributes.'''
        self.tag_list = self.get_tag_list()
        for phone in self.data:
            phone['noise'] = []
            for i, review in enumerate(phone['reviews']):
                found = False
                for word in self.tag_list:
                    if word in review[-1] or word in review[1]:
                        found = True
                        break
                if found == False:
                    phone['noise'].append(review) 
                    phone['reviews'].pop(i)
                    
    def noise_filter(self) :
    	'''Returns a counter of the most occuring words aggregated over all reviews.
    	   Helper function to aid the filtering of bad reviews
    	'''
        list_review_word = []
        ls = SnowballStemmer('english')
        for  phone in self.data:
            phone_reviews = []
            for i , content in enumerate(phone['noise']):
                review = content[-1]
                list_words = word_tokenize(review)
                list_stem_words = [ ls.stem(word) for word in list_words]
                phone_reviews.extend(list_stem_words)
            list_review_word.extend(phone_reviews)
        self.noise_count = Counter(list_review_word)
    
    def store_mobile_list(self):
        '''Stores a list of all mobile titles in the class'''
        self.phone_list = []
        for i in range(len(self.data)):
            self.phone_list.append(self.data[i]['title'])
        
    def get_phone_name(self, phone_name):
        return process.extract(phone_name,self.phone_list, limit=1)[0]
        
    def get_index_of_phone(self, phone_name):
        name = self.get_phone_name(phone_name)[0]
        return self.phone_list.index(name)
    
    def aggregate_review(self, index):
        (delivery, product, price, seller, warranty) = (0,0,0,0,0)
        (battery, build, camera, display, sound, specs) = (0,0,0,0,0,0)
        total = float(len(self.data[index]['reviews']))
        for review in self.data[index]['reviews']:
            score = self.review_category(review[-1])
            if score['delivery'] != False:
                delivery +=1
            if score['price'] != False:
                price +=1
            if score['warranty'] != False:
                warranty +=1
            if score['seller'] != False:
                seller +=1
            if score['product']['camera'] != False or score['product']['battery'] != False or score['product']['sound'] != False or score['product']['display'] != False or score['product']['build'] != False or score['product']['specs'] != False:
                product +=1
            if score['product']['battery'] != False:
                battery += 1
            if score['product']['build'] != False:
                build += 1
            if score['product']['camera'] != False:
                camera += 1
            if score['product']['display'] != False:
                display += 1
            if score['product']['sound'] != False:
                sound += 1
            if score['product']['specs'] != False:
                specs += 1
        product_total = product
        delivery= round(delivery*100/total,1)
        product = round(product*100/total,1)
        price = round(price*100/total,1)
        seller = round(seller*100/total,1)
        warranty = round(warranty*100/total,1)
        return {'title':self.data[index]['title'].title(),'delivery': delivery, 'price':price,
                 'product':product, 'seller':seller, 'warranty':warranty, 
                 'product_total':product_total, 'total': total,
                 'attributes': {'camera':camera,'battery':battery, 'build':build, 
                                'display':display, 'sound':sound, 'specs':specs}}

    def aggregate_sentiment(self, index):
        rev_dict = {"overall_sentiment": 0,
        'product':{'camera':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
                   'battery':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
                   'sound':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
                   'display':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
                   'build':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
                   'specs':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
                   'whole':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []}
                   },
       'delivery':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
       'warranty':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
      'seller':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
      'price':{'pos':0, 'neg':0, 'pos_rev':[], 'neg_rev': []},
      'title':self.data[index]['title'].title()}
        total = float(len(self.data[index]['reviews']))
        for review in self.data[index]['reviews']:
            score = self.review_category(review[-1])
            rev_dict['overall_sentiment'] += score['overall_sentiment']            
            for key in score.keys():
                if key != 'overall_sentiment' or key !='product':
                    if score[key]=='positive':
                        rev_dict[key]['pos'] +=1
                        rev_dict[key]['pos_rev'].append(review[-1])
                    elif score[key]=='negative':
                        rev_dict[key]['neg'] +=1
                        rev_dict[key]['neg_rev'].append(review[-1])
                #For the attributes of product
                if key=='product':
                    for attr in score[key].keys():
                        if score[key][attr] =='positive':
                            rev_dict[key][attr]['pos'] +=1
                            rev_dict[key][attr]['pos_rev'].append(review[-1])
                            rev_dict[key]['whole']['pos'] +=1
                            rev_dict[key]['whole']['pos_rev'].append(review[-1])
                        elif score[key][attr] == 'negative':
                            rev_dict[key][attr]['neg'] +=1
                            rev_dict[key][attr]['neg_rev'].append(review[-1])
                            rev_dict[key]['whole']['neg'] +=1
                            rev_dict[key]['whole']['neg_rev'].append(review[-1])
                   
        if total !=0:
            rev_dict['overall_sentiment'] /= total    
        return rev_dict
        
    def aggregate_sentiment_without_reviews(self, index):
        rev_dict = {"overall_sentiment": 0,
        'product':{'camera':{'pos':0, 'neg':0},
                   'battery':{'pos':0, 'neg':0},
                   'sound':{'pos':0, 'neg':0},
                   'display':{'pos':0, 'neg':0},
                   'build':{'pos':0, 'neg':0},
                   'specs':{'pos':0, 'neg':0},
                   'whole':{'pos':0, 'neg':0}
                   },
       'delivery':{'pos':0, 'neg':0},
       'warranty':{'pos':0, 'neg':0},
      'seller':{'pos':0, 'neg':0},
      'price':{'pos':0, 'neg':0},
      'title':self.data[index]['title'].title()}
        total = float(len(self.data[index]['reviews']))
        for review in self.data[index]['reviews']:
            score = self.review_category(review[-1])
            rev_dict['overall_sentiment'] += score['overall_sentiment']            
            for key in score.keys():
                if key != 'overall_sentiment' or key !='product':
                    if score[key]=='positive':
                        rev_dict[key]['pos'] +=1                        
                    elif score[key]=='negative':
                        rev_dict[key]['neg'] +=1
                #For the attributes of product
                if key=='product':
                    for attr in score[key].keys():
                        if score[key][attr] =='positive':
                            rev_dict[key][attr]['pos'] +=1
                            rev_dict[key]['whole']['pos'] +=1
                        elif score[key][attr] == 'negative':
                            rev_dict[key][attr]['neg'] +=1
                            rev_dict[key]['whole']['neg'] +=1
                            
        if total !=0:
            rev_dict['overall_sentiment'] /= total    
        return rev_dict
        
    def overall_aggregate(self, filename = 'overall_dict.json'):
        for i in range(len(self.data)):
            if i%50==0:
                print "Step no.",i
            score = self.aggregate_sentiment_without_reviews(i)
            for key in score.keys():
                if key =='overall_sentiment':
                    self.overall_dict[key] += score[key]
                elif key=='product':
                    for attr in score[key]:
                        self.overall_dict[key][attr]['pos'] += score[key][attr]['pos']
                        self.overall_dict[key][attr]['neg'] += score[key][attr]['neg']
                        if score[key][attr]['pos']>self.overall_dict[key][attr]['pos_contribute'][-1][-1]:
                            self.overall_dict[key][attr]['pos_contribute'][-1] = [self.data[i]['title'],score[key][attr]['pos']] 
                            self.overall_dict[key][attr]['pos_contribute'] = sorted(self.overall_dict[key][attr]['pos_contribute'], key = lambda k:k[1], reverse=True)
                        if score[key][attr]['neg']>self.overall_dict[key][attr]['neg_contribute'][-1][-1]:
                            self.overall_dict[key][attr]['neg_contribute'][-1] = [self.data[i]['title'],score[key][attr]['neg']] 
                            self.overall_dict[key][attr]['neg_contribute'] = sorted(self.overall_dict[key][attr]['neg_contribute'], key = lambda k:k[1], reverse=True)
                        
                elif key != 'title':
                    self.overall_dict[key]['pos'] += score[key]['pos']
                    self.overall_dict[key]['neg'] += score[key]['neg']
                    if score[key]['pos']>self.overall_dict[key]['pos_contribute'][-1][-1]:
                        self.overall_dict[key]['pos_contribute'][-1] = [self.data[i]['title'],score[key]['pos']] 
                        self.overall_dict[key]['pos_contribute'] = sorted(self.overall_dict[key]['pos_contribute'], key = lambda k:k[1], reverse=True)
                    if score[key]['neg']>self.overall_dict[key]['neg_contribute'][-1][-1]:
                        self.overall_dict[key]['neg_contribute'][-1] = [self.data[i]['title'],score[key]['neg']] 
                        self.overall_dict[key]['neg_contribute'] = sorted(self.overall_dict[key]['neg_contribute'], key = lambda k:k[1], reverse=True)
        
        
        with open(filename, 'w') as f:
            json.dump(self.overall_dict, f)
    
    def load_overall_aggregate(self, filename='overall_dict.json'):
        if os.path.isfile(filename):
            with open(filename) as f:
                self.overall_dict = json.load(f)
        else:
            self.overall_aggregate(filename)
    
    
    def phone_name_aggregate(self, phone_name):
        index = self.get_index_of_phone(phone_name)
        return self.aggregate_review(index)

    def phone_name_sentiment(self, phone_name):
        index = self.get_index_of_phone(phone_name)
        return self.aggregate_sentiment(index)

    def get_mobile_reviews(self, mobile_name, tag = None, attr = None, limit=10):
        '''Returns reviews with specific tags for the input mobile title.'''
        #Uses the fuzzywuzzy library to compute the closest matched phone
        #in terms of edit distance. 
        similar_phones = process.extract(mobile_name, self.phone_list, limit = limit)
        #print similar_phones
        matched_phone = similar_phones[0][0]
        if tag != None:
            if tag in self.tags.keys():
                if attr==None:
                    return self.tagged_data[matched_phone][tag]
                if attr in self.product_tag.keys() and tag=='product':
                    return self.tagged_data[matched_phone][tag][attr]
                else:
                    return "Attribute not found"
            else:
                return "Tag not found"
        return self.tagged_data[matched_phone]
        
    def review_category(self, review):
        '''Returns the tags of the input review with their sentiment
        '''
        review = str(self.remove_punc(review.lower().encode('utf-8')))
        tokens = [word for word in word_tokenize(review) if word not in self.stopwords]
        tokens = ' '.join(tokens)
        rev_dict = {"overall_sentiment": 0,
        'product':{'camera':False,'battery':False,
                               'sound':False, 'display':False,
                               'build':False,'specs':False},
                    'delivery':False,
                    'warranty':False,
                    'seller':False,
                    'price':False}
        
        for category in self.tags:
            if category != 'product':
                count = 0
                countChanged = False
                for tag in eval('self.' + category + '_tag'):
                    nearby_words = []
                    if tag in tokens:
                        #print 'entering tag in token'
                        #print tag
                        rev_dict[category] = True
                        tag_pos = [pos.start() for pos in re.finditer(tag, tokens)]
                        for position in tag_pos:
                            before = tokens[:position].split()
                            after = tokens[position:].split()
                            #print before, after
                            if len(before) > 0:
                                nearby_words.extend([before[-1]])
                                if len(before) > 1:
                                    nearby_words.extend([before[-2]])
                            if len(after) > 1:
                                nearby_words.extend([after[1]])
                                if len(after) > 2:
                                    nearby_words.extend([after[2]])
                    for word in nearby_words:
                        if self.positive[word] == True:
                            #print nearby_words
                            if 'not' in nearby_words or 'no' in nearby_words:
                                #print 'not is there'
                                count -=2
                            else:
                                count +=2
                            countChanged= True
                        if self.negative[word] == True:
                            if 'not' in nearby_words or 'no' in nearby_words:
                                count -=1
                            else:
                                count -=2
                            countChanged = True
                #Assigning a sentiment to the specific category            
                if count>0:
                    rev_dict[category] = 'positive'
                elif count<0:
                    rev_dict[category] = 'negative'
                elif count==0 and countChanged==True:
                    rev_dict[category] = 'neutral'
                    
            else:
                for attrs in self.product_tag:
                    count = 0
                    countChanged = False
                    nearby_words = []
                    for tag in self.product_tag[attrs]:
                        if tag in tokens:
                            rev_dict['product'][attrs] = True
                            tag_pos = [pos.start() for pos in re.finditer(tag, tokens)]
                            for position in tag_pos:
                                before = tokens[:position].split()
                                after = tokens[position:].split()
                                if len(before) > 0:
                                    nearby_words.extend([before[-1]])
                                    if len(before) > 1:
                                        nearby_words.extend([before[-2]])
                                if len(after) > 1:
                                    nearby_words.extend([after[1]])
                                    if len(after) > 2:
                                        nearby_words.extend([after[2]])
                    for word in nearby_words:
                        if self.positive[word] == True:
                            if 'not' in nearby_words or 'no' in nearby_words:
                                count -=2
                            else:
                                count +=2
                            countChanged = True
                        if self.negative[word] == True:
                            if 'not' in nearby_words or 'no' in nearby_words:
                                count -=1
                            else:
                                count -=2
                            countChanged = True
                            
                    if count>0:
                        rev_dict['product'][attrs] = 'positive'
                    elif count<0:
                        rev_dict['product'][attrs] = 'negative'
                    elif count ==0 and countChanged == True:
                        rev_dict['product'][attrs] = 'neutral'
        blob = TextBlob(review)
        rev_dict['overall_sentiment'] = round(blob.sentiment.polarity,2)
               
        return rev_dict

if __name__=='__main__':
    amazon = Tagger('amazon_review.json')
    amazon.add_reviews('flipkart_review.json')
    amazon.filter_bad_reviews()
    #print amazon.data[50]['reviews'][0][-1]
    #print json.dumps(amazon.review_category(amazon.data[50]['reviews'][0][-1]))
    #print amazon.data[51]['reviews'][0][-1]
    #print json.dumps(amazon.review_category(amazon.data[51]['reviews'][0][-1]))



                  
                    
                
                    
            
        
        
        
        
        
        
        
        
        
        
        
        
        