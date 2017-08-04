from __future__ import division
from collections import defaultdict
import math
import json
import sys

class HMMLearn:
    def __init__(self):
        self.emissions = defaultdict(lambda: defaultdict(int))
        self.transitions = defaultdict(lambda: defaultdict(int))
        self.first_tags = defaultdict(int)
        self.tag_counts = defaultdict(int)
        self.starts = defaultdict(int)
        self.lines = list()
        self.tags = set()

    def read_input(self, filename):
        fo = open(filename,'rU')
        with fo as f:
            self.lines = [line.strip("\n\r") for line in f.readlines()]
        #print (self.lines[0])
        self.create_matrix()

    def create_matrix(self):
        for line in self.lines[0:]:
            #print (line)
            terms = [x.rsplit("/",1) for x in line.split(" ")]
            for i in range(len(terms)-1):
                self.emissions[terms[i][0]][terms[i][1]] += 1
                self.transitions[terms[i][1]][terms[i+1][1]]+= 1
                self.tags.add(terms[i][1])
                self.first_tags[terms[i][1]] += 1
                self.tag_counts[terms[i][1]] += 1
            self.starts[terms[0][1]] += 1
            self.emissions[terms[-1][0]][terms[-1][1]] += 1
            self.tag_counts[terms[-1][1]] += 1
            self.tags.add(terms[-1][1])

        #print (self.transitions)
        #print (self.emissions)
        #print (self.starts)
        print (self.tags)
        #print (self.first_tags)
        #print (self.tag_counts)
        self.normalise_transitions()
        
    def normalise_transitions(self):
        num_tags = len(self.tags)
        print (num_tags)
        for tag_f in self.tags:
            for tag_s in self.tags:
                temp = self.transitions[tag_f][tag_s]+1
                temp /= (self.first_tags[tag_f]+num_tags)
                #self.transitions[tag_f][tag_s] += 1
                self.transitions[tag_f][tag_s] = math.log(temp)

        #print (self.transitions)
        self.emission_probs()

    def emission_probs(self):
        for word in self.emissions.keys():
            #print (self.emissions[word])
            for tag in (self.emissions[word]):
                #temp = self.emissions[word_tags][tag]/self.tag_counts[tag]
                self.emissions[word][tag] = math.log(self.emissions[word][tag]/self.tag_counts[tag])

        #print (self.emissions)
        self.emissions[""]={}
        self.start_probs()

    '''def start_probs(self):
        num_lines = len(self.lines)
        print (num_lines)
        #print (self.starts)
        sum = 0
        for key in self.starts.keys():
            sum += self.starts[key]
            self.starts[key] = math.log(self.starts[key]/num_lines)
        #print (self.starts)
        print (sum)
        self.write_model()'''

    def start_probs(self):
        num_lines = len(self.lines)
        print (num_lines)
        #print (self.starts)
        sum = 0
        denom = num_lines+len(self.tags)
        for tag in self.tags:
            sum += self.starts[tag]+1
            self.starts[tag] = math.log((self.starts[tag]+1)/denom)
        print (self.starts)
        print (sum,denom,len(self.starts.keys()))
        self.write_model()

    def write_model(self):
        model = dict()
        model['tags'] = list(self.tags)
        model['transitions'] = self.transitions
        model['emissions'] = self.emissions
        model['starts'] = self.starts
        with open('hmmmodel.txt','w') as outfile:
            json.dump(model,outfile)

obj = HMMLearn()
obj.read_input(sys.argv[1])
