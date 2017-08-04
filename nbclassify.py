from __future__ import division
from collections import defaultdict
import ast
import json
import math
import re
import sys

class nbclassify:
    def __init__(self):
        self.reviewsF = []
        self.labelsF = []
        self.data = defaultdict(list)
        self.true = defaultdict(int)
        self.decp = defaultdict(int)
        self.pos = defaultdict(int)
        self.neg = defaultdict(int)
        self.prior_prob =tuple()

    def read_stops(self,fname1):
	fo = open(fname1,'rU')
	with fo as f:
            self.stops = [line.strip("\n\r") for line in f.readlines()]
	self.stops = set(self.stops)
        #print self.stops
        
    def read_input(self,fname1):
        self.read_stops("stopword.txt")
        fo = open(fname1,'rU')
        with fo as f:
            self.reviewsF = [line.strip("\n\r") for line in f.readlines()]

        self.create_data()
        self.read_model()
        self.predict()

    def create_data(self):
        for r in self.reviewsF:
            split = re.findall(r"[\w']+", r)
            #print split
            id = split.pop(0)
            #print id
            rev = self.process_d(split)
            self.data[id] = rev
        #print self.data

    def process_d(self,split):
        #stop word removal
        ret = []
        for word in split:
            if word.lower() not in self.stops:
               ret.append(word.lower())
        return ret

    def read_model(self):
        fo = open('nbmodel.txt', 'r')
        with fo as f:
            model = json.load(f)
        #model = eval(s)
        self.prior_prob = model["prior_prob"] 
        self.true = model["true"]
        self.decp = model["decp"]
        self.pos = model["pos"] 
        self.neg = model["neg"]
        print self.prior_prob

    def predict(self):
        outlist = []
        self.outdict = dict()
        for key in self.data.keys():
            #print self.data[key]
            probt = self.prior_prob[0]
            probd = self.prior_prob[1]
            probp = self.prior_prob[2]
            probn = self.prior_prob[3]
            #print probt, probd,probp,probn
            for word in self.data[key]:
                probt += self.true.get(word,0)
                probd += self.decp.get(word,0)
                probp += self.pos.get(word,0)
                probn += self.neg.get(word,0)
            print probt,probd,probp,probn
            t1 = ""
            t2 = ""
            if probt > probd :
                t1 = "truthful"
            else:
                t1 = "deceptive"
            if probp > probn:
                t2 = "positive"
            else:
                t2 = "negative"
            #print key, t1, t2
            self.outdict[key] = (t1,t2)
            outlist.append(key+" "+t1+" "+t2+"\n")

        fname = "nboutput.txt"
        fo = open(fname, 'w')
        fo.writelines(outlist)
        fo.close()

        self.evaluate()

    def evaluate(self):
        fo = open("test_label.txt",'rU')
        t_tp=0
        t_fn=0
        t_tn=0
        t_fp=0
        p_tp=0
        p_fn=0
        p_tn=0
        p_fp=0
        with fo as f:
            self.labelsF = [line.strip("\n\r") for line in f.readlines()]
        #print len(self.labelsF)
        for l in self.labelsF:
            labels = l.split()
            #self.outdict[labels[0]]+= [labels[1],labels[2]]
            if self.outdict[labels[0]][0]==labels[1]and labels[1]=='truthful':
                #print "hai"
                t_tp+=1
            elif self.outdict[labels[0]][0]==labels[1]and labels[1]=='deceptive':
                #print "hai"
                t_tn+=1
            elif self.outdict[labels[0]][0]!=labels[1]and labels[1]=='truthful':
                #print "hai"
                t_fn+=1
            elif self.outdict[labels[0]][0]!=labels[1]and labels[1]=='deceptive':
                #print "hai"
                t_fp+=1
                
            if self.outdict[labels[0]][1]==labels[2]and labels[2]=='positive':
                #print "hai"
                p_tp+=1
            elif self.outdict[labels[0]][1]==labels[2]and labels[2]=='negative':
                #print "hai"
                p_tn+=1
            elif self.outdict[labels[0]][1]!=labels[2]and labels[2]=='positive':
                #print "hai"
                p_fn+=1
            elif self.outdict[labels[0]][1]!=labels[2]and labels[2]=='negative':
                #print "hai"
                p_fp+=1

        print t_tp, t_tn, t_fn, t_fp ,p_tp, p_tn, p_fn, p_fp

        #print p_tp, p_fp, p_fn, p_tn
        pp = p_tp/(p_tp+p_fp)
        pr = p_tp/(p_tp+p_fn)

        np = p_tn/(p_tn+p_fn)
        nr = p_tn/(p_tn+p_fp)

        tp = t_tp/(t_tp+t_fp)
        tr = t_tp/(t_tp+t_fn)

        dp = t_tn/(t_tn+t_fn)
        dr = t_tn/(t_tn+t_fp)

        print pp,pr, np, nr, tp, tr, dp, dr

        f_p = (2*pp*pr)/(pp+pr)
        f_n = (2*np*nr)/(np+nr)
        f_t = (2*tp*tr)/(tp+tr)
        f_d = (2*dp*dr)/(dp+dr)

        print f_p, f_n, f_t, f_d
        print (f_t+f_d+f_p+f_n)/4

obj = nbclassify()
obj.read_input(sys.argv[1])
            
