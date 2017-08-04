from __future__ import division
from collections import defaultdict
import json
import math
import re
import sys

class nb:
    def __init__(self):
        self.reviewsF = []
        self.labelsF = []
        self.data = defaultdict(list)
        self.true = defaultdict(int)
        self.decp = defaultdict(int)
        self.pos = defaultdict(int)
        self.neg = defaultdict(int)
        self.prior_prob =tuple()
        self.t_count = 0
        self.d_count = 0
        self.p_count = 0
        self.n_count = 0
        self.datat_count = 0
        self.datad_count = 0
        self.datap_count = 0
        self.datan_count = 0
        self.unique = set()

    def read_stops(self,fname1):
	fo = open(fname1,'rU')
	with fo as f:
            self.stops = [line.strip("\n\r") for line in f.readlines()]
	self.stops = set(self.stops)
        #print self.stops
    
    def read_input(self,fname1, fname2):
        self.read_stops("stopword.txt")
        fo = open(fname1,'rU')
        with fo as f:
            self.reviewsF = [line.strip("\n\r") for line in f.readlines()]
        #print self.reviewsF[0:2]

        fo = open(fname2,'rU')
        with fo as f:
            self.labelsF = [line.strip("\n\r") for line in f.readlines()]
        for l in self.labelsF:
            labels = l.split()
            self.data[labels[0]]+= [labels[1],labels[2]]
        #print self.data["0117CBUj98k8MKQp8svI"]

        if len(self.reviewsF)!= len(self.labelsF):
            print "Error, mismatch data"
            exit
        self.create_data()
        #print self.data["02kds25RFtpa6DJL21y6"]
        self.create_model()
        self.write_model()

    def create_data(self):
        for r in self.reviewsF:
            split = re.findall(r"[\w']+", r)
            #print split
            id = split.pop(0)
            #print id
            rev = self.process_d(split)
            self.data[id].append(rev)

        '''for key in self.data.keys()[0:5]:
            print self.data[key]'''
        for key in self.data.keys():
            t1 = self.data[key][0]
            t2 = self.data[key][1]
            if t1=="truthful":
                self.datat_count+= 1
                for word in self.data[key][2]:
                    self.true[word]+=1
                    self.unique.add(word)
                    self.t_count+=1
            else :
                self.datad_count+=1
                for word in self.data[key][2]:
                    self.decp[word]+=1
                    self.unique.add(word)
                    self.d_count+=1

            if t2=="positive":
                self.datap_count+=1
                for word in self.data[key][2]:
                    self.pos[word]+=1
                    self.unique.add(word)
                    self.p_count+=1
            else :
                self.datan_count+=1
                for word in self.data[key][2]:
                    self.neg[word]+=1
                    self.unique.add(word)
                    self.n_count+=1

            #print self.pos
        print self.p_count,self.n_count,self.d_count,self.t_count,len(self.unique)
        print self.datat_count,self.datad_count,self.datap_count,self.datan_count

    def create_model(self):
        norm = len(self.unique)
        p_deno = self.p_count+norm
        n_deno = self.n_count+norm
        t_deno = self.t_count+norm
        d_deno = self.d_count+norm
        
        '''for key in self.pos.keys():
            pr = self.pos[key]
            prob = math.log((pr+1)/p_deno)
            self.pos[key] = prob
            
        for key in self.neg.keys():
            pr = self.neg[key]
            prob = math.log((pr+1)/n_deno)
            self.neg[key] = prob
            
        for key in self.true.keys():
            pr = self.true[key]
            prob = math.log((pr+1)/t_deno)
            self.true[key] = prob
            
        for key in self.decp.keys():
            pr = self.decp[key]
            prob = math.log((pr+1)/d_deno)
            self.decp[key] = prob'''

        for key in self.unique:
            pr = self.pos.get(key,0)
            prob = math.log((pr+1)/p_deno)
            self.pos[key] = prob

            pr = self.neg.get(key,0)
            prob = math.log((pr+1)/n_deno)
            self.neg[key] = prob

            pr = self.true.get(key,0)
            prob = math.log((pr+1)/t_deno)
            self.true[key] = prob

            pr = self.decp.get(key,0)
            prob = math.log((pr+1)/d_deno)
            self.decp[key] = prob

        print len(self.pos.keys()),len(self.neg.keys()),len(self.true.keys()),len(self.decp.keys())
        #for key in self.pos.keys()[0:15]:
            #print self.pos[key]

        prior_true = math.log(self.datat_count/(self.datat_count+self.datad_count))
        prior_decp = math.log(self.datad_count/(self.datat_count+self.datad_count))
        prior_pos = math.log(self.datap_count/(self.datap_count+self.datan_count))
        prior_neg = math.log(self.datan_count/(self.datap_count+self.datan_count))

        self.prior_prob = (prior_true,prior_decp,prior_pos,prior_neg)
        print self.prior_prob
                    
    def process_d(self,split):
        #stop word removal
        ret = []
        for word in split:
            if word.lower() not in self.stops:
               ret.append(word.lower())
        return ret

    def write_model(self):
        #target = open('nbmodel.txt', 'a')
        model = dict()
        model["prior_prob"] = self.prior_prob
        model["true"] = self.true
        model["decp"] = self.decp
        model["pos"] = self.pos
        model["neg"] = self.neg
        with open('nbmodel.txt', 'w') as outfile:
            json.dump(model, outfile)
        #json.dump(model)

obj = nb()
#obj.read_input("hw2-data-corpus/train-text.txt","hw2-data-corpus/train-labels.txt")
#(hw2-data-corpus/train-text.txt hw2-data-corpus/train-labels.txt)
#print sys.argv
obj.read_input(sys.argv[1],sys.argv[2])
