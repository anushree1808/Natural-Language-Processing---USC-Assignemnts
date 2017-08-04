from __future__ import division
from collections import defaultdict
from operator import itemgetter
import json
import sys

class HMMDecode:
    def __init__(self):
        self.emissions = defaultdict(lambda : defaultdict(int))
        self.transitions = defaultdict(lambda : defaultdict(int))
        self.starts = defaultdict(int)
        self.tags = list()

    def read_model(self):
        fo = open('hmmmodel.txt', 'r')
        with fo as f:
            model = json.load(f)
        #model = eval(s)
        self.emissions = model['emissions']
        self.transitions = model['transitions']
        self.starts = model['starts']
        self.tags = model['tags']

    def read_input(self,filename):
        fo = open(filename,'rU')
        with fo as f:
            self.lines = [line.strip("\n\r") for line in f.readlines()]
        #print (self.lines[0])
        print (len(self.lines))
        self.viterbi_decode()

    def viterbi_decode(self):
        self.read_model()
        print (self.starts)
        self.output = []
        emission_keys = self.emissions.keys()
        for line in self.lines[0:]:
            
            words = line.split(" ")
            #print (len(words))
            num_words = len(words)
            bck_pointer = defaultdict(lambda:defaultdict(chr))
            prob = defaultdict(lambda:defaultdict(int))
            prev_tags = []
            if words[0] in emission_keys:
                prev_tags = self.emissions[words[0]].keys()
                for tag in self.emissions[words[0]].keys():#self.tags:#
                    #prob[tag][0] = self.starts[tag]+self.emissions[words[0]][tag]
                    #print (self.starts[tag])
                    #prob[tag][0] = self.starts[tag]+self.emissions.get(words[0]).get(tag,float("-inf"))
                    prob[tag][0] = self.starts[tag]+self.emissions[words[0]][tag]
                    bck_pointer[tag][0] = None

            else :
                prev_tags = self.tags
                for tag in self.tags:
                    #prob[tag][0] = self.starts[tag]+self.emissions[words[0]][tag]
                    #print (self.starts[tag])
                    prob[tag][0] = self.starts[tag]
                    bck_pointer[tag][0] = None
                    
            '''for i in range(1,num_words):
                for tag in self.tags:#self.emissions[word[i]].keys():
                    #computed = [prob[prev_tag][i-1]+self.transitions[prev_tag][tag]+self.emissions[words[i]][tag] for prev_tag in tags]
                    computed = [prob[prev_tag][i-1]+self.transitions[prev_tag][tag]+self.emissions.get(words[i],self.emissions[""]).get(tag,0) for prev_tag in self.tags]
                    index,element = max(enumerate(computed), key=itemgetter(1))
                    prob[tag][i] = element
                    bck_pointer[tag][i] = self.tags[index]'''
            #num_words = 5
            for i in range(1,num_words):
                prev_tags = list(prev_tags)
                #print (type(prev_tags))
                if words[i] in emission_keys:
                    for tag in self.emissions[words[i]].keys():#self.tags:#self.emissions[words[i]].keys():
                        computed = [prob[prev_tag][i-1]+self.transitions[prev_tag][tag]+self.emissions[words[i]][tag] for prev_tag in prev_tags]#self.tags]
                        index,element = max(enumerate(computed), key=itemgetter(1))
                        prob[tag][i] = element
                        bck_pointer[tag][i] = prev_tags[index]#self.tags[index]
                    prev_tags = list(self.emissions[words[i]].keys())

                else:
                    for tag in self.tags:
                        computed = [prob[prev_tag][i-1]+self.transitions[prev_tag][tag] for prev_tag in prev_tags]
                        index,element = max(enumerate(computed), key=itemgetter(1))
                        prob[tag][i] = element
                        bck_pointer[tag][i] = prev_tags[index]
                    prev_tags = list(self.tags)
                        
            prev_tags = list(prev_tags)
            max_computed = [prob[tag][num_words-1] for tag in prev_tags]
            index,element = max(enumerate(max_computed), key=itemgetter(1))
            most_prob_states = [''] * num_words
            #print (self.tags[index])
            most_prob_states = prev_tags[index] #self.tags[index]
            words[num_words-1]= words[num_words-1]+"/"+prev_tags[index]
            #print (most_prob_states)
            #print(bck_pointer)
            for i in range(num_words-1,0,-1):
                #print(bck_pointer[most_prob_states][i])
                words[i-1]= words[i-1]+"/"+bck_pointer[most_prob_states][i]
                most_prob_states = bck_pointer[most_prob_states][i]
                
            #print (most_prob_states)
            #temp = ""
            '''for i in range(num_words):
                words[i]= words[i]+"/"+most_prob_states[i]'''

            temp = (" ").join(words)
            temp += "\n"
            self.output.append(temp)
        #print (len(self.output))
        self.write_output()

    def write_output(self):
        fname = "hmmoutput.txt"
        fo = open(fname, 'w')
        fo.writelines(self.output)
        fo.close()
                
obj = HMMDecode()
obj.read_input(sys.argv[1])
