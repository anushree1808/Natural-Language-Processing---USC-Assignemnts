from __future__ import division
from collections import defaultdict
from functools import reduce
import os
import sys
import math
import operator

class Calculate_Bleu:
    def __init__(self):
        self.candidate = []
        self.references = []
        self.candidate_words = []
        self.references_words= []
        self.N = 0
        self.pns = []

    def read_input(self,filename1, directory1):
        fo = open(filename1,'rU')
        with fo as f:
            self.candidate = f.readlines()#[line.strip() for line in f.readlines()]
        #fo.close()

        if os.path.isfile(directory1):
            fo = open(directory1,'rU')
            with fo as f:
                reference = f.readlines()#[line.strip() for line in f.readlines()]
            self.references.append(reference)
            #fo.close()
            
        elif os.path.isdir(directory1):
            for filename in os.listdir(directory1):
                fo = open(directory1+"/"+filename,'rU')
                with fo as f:
                    reference = f.readlines()#[line.strip() for line in f.readlines()]
                self.references.append(reference)
                #fo.close()

        #print(len(self.candidate),len(self.references[0]),len(self.references[0]))

    def calculate_pn(self,n):
        pn_denominator = 0
        pn_numerator = 0
        
        for i in range(len(self.candidate)):
            
            #------------- Build Candidate Dictionary ------------
            words_c = self.candidate[i].strip().split()
            n_grams_c = defaultdict(int)
            count = 0
            for j in range(0,(len(words_c)-n+1)):
                n_gram_c = (" ").join(words_c[j:j+n]).lower()
                n_grams_c[n_gram_c] += 1
                count += 1
            pn_denominator += count


            #------------- Build References Dictionary ------------
            refs_dict = []
            for reference in self.references:
                words_r = reference[i].strip().split()
                n_grams_r =  defaultdict(int)
                for j in range(0,(len(words_r)-n+1)):
                    n_gram_r = (" ").join(words_r[j:j+n]).lower()
                    n_grams_r[n_gram_r] += 1

                refs_dict.append(n_grams_r)

            clipped_count = self.clipped_counts(n_grams_c, refs_dict)
            pn_numerator += clipped_count

        print (pn_numerator, pn_denominator)
        pn = pn_numerator/pn_denominator
        return pn

    def clipped_counts(self,n_grams_c, refs_dict):
        clip_count = 0
       
        for key in n_grams_c.keys():
            max_ref_count = 0
            cand_count = n_grams_c[key]
            for ref_dict in refs_dict:
                #if key in ref_dict:
                max_ref_count = max(max_ref_count,ref_dict.get(key,0))
            clip_count += min(cand_count,max_ref_count)
        return clip_count

    def best_length_match(self):
        cand_lengths = []
        refs_lengths = []
        r = 0
        c = 0
        
        for cand_sent in self.candidate:
            words = cand_sent.strip().split()
            self.candidate_words.append(words)
            cand_lengths.append(len(words))

        for reference in self.references:
            ref_lengths = []
            reference_words = []
            for ref_sent in reference:
                words = ref_sent.strip().split()
                reference_words.append(words)
                ref_lengths.append(len(words))
            refs_lengths.append(ref_lengths)
            self.references_words.append(reference_words)

        #print (cand_lengths,refs_lengths)

        for i in range(len(self.candidate)):
            #r += max(cand_lengths[i], max([x[i]for x in refs_lengths]))
            abs_min_diff = float("inf")
            ref_sent = 0
            for ref_lengths in refs_lengths:
                curr_diff = abs(cand_lengths[i]-ref_lengths[i])
                if curr_diff < abs_min_diff :
                    abs_min_diff = curr_diff
                    ref_sent = ref_lengths[i]
            r += ref_sent
            print (ref_sent)

        c = sum(cand_lengths)

        return (r,c)

    def geometric_mean(self):
        return (reduce(operator.mul, self.pns)) ** (1.0 / self.N)

    def bleu_score(self,N):
        sum_pn=0
        r,c = self.best_length_match()
        self.N = N
        
        for n in range(1,self.N+1):
            #print (n)
            pn = self.calculate_pn(n)
            #print (pn)
            self.pns.append(pn)
            sum_pn+=(1/n) * math.log(pn)
       
        #print (sum_pn)
        print (r,c)
        penalty = 1
        if c<=r:
            penalty = math.e**(1-r/c)

        print(penalty)

        bleu = penalty * self.geometric_mean()#(math.e ** sum_pn) #check for geometric mean computation!!
        return bleu


obj = Calculate_Bleu()
filename1 = sys.argv[1]
directory1 = sys.argv[2]
#print(filename1, directory1)
obj.read_input(filename1, directory1)
N = 4
bleu = obj.bleu_score(N)
print (str(bleu))
with open('bleu_out.txt','w') as outfile:
    outfile.write(str(bleu))
