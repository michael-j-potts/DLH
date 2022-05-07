#This file is used to unravel the three documents used by CAE and AE into just visits, and codes.
#This creates the embeddings used by CAE and AE to ultimately create embedding weights used
#For the latent space models.

import pickle
import numpy as np
import time

vocabsize_icd = 942
vocabsize_meds = 3202
vocabsize_labs = 284 #all 681 284
digitICD9 = []
meds = []
abnlabs = []


#We want to unravel each of icd med and lab to reduce to to an array of arrays
#And we want to get rid of the "i", "m", and "l" descriptors for each code to 
#prevent problems when feeding them into the models
def unravelicd(input):
    for patient in input:
        for visit in patient:
            tempcodes = np.zeros(vocabsize_icd)
            for codes in visit:
                codes = int(codes.replace("i",""))
                tempcodes[codes] = 1
            digitICD9.append(np.array(tempcodes))
    print("Finished unraveling and altering ICDs")
    

def unravelmed(input):
    for patient in input:
        for visit in patient:
            tempcodes = np.zeros(vocabsize_meds)
            for codes in visit:
                codes = int(codes.replace("m",""))
                tempcodes[codes] = 1
            meds.append(np.array(tempcodes))
    print("Finished unraveling and altering meds")

def unravellab(input):
    for patient in input:
        for visit in patient:
            tempcodes = np.zeros(vocabsize_labs)
            for codes in visit:
                codes = int(codes.replace("l",""))
                tempcodes[codes] = 1
            abnlabs.append(np.array(tempcodes))
    print("Finished unraveling and altering labs")


#import data
ICD_data = pickle.load(open('./MIMICIIIPROCESSED.3digitICD9.seqs','rb'))
Med_data = pickle.load(open('./MIMICIIIPROCESSED.meds.seqs','rb'))
Lab_data = pickle.load(open('./MIMICIIIPROCESSED.abnlabs.seqs','rb'))

#Call methods
unravelicd(ICD_data)
unravelmed(Med_data)
unravellab(Lab_data)

#store data in conveniently named files
pickle.dump(np.array(digitICD9), open('CAEEntries.3digitICD9', 'wb'), -1)
pickle.dump(np.array(meds), open('CAEEntries.meds', 'wb'), -1)
pickle.dump(np.array(abnlabs), open('CAEEntries.abnlabs', 'wb'), -1)

#Test to look at values quickly
#testicds = pickle.load(open('CAEEntries.3digitICD9', 'r'))
#testmeds = pickle.load(open('CAEEntries.meds', 'r'))
#testlabs = pickle.load(open('CAEEntries.abnlabs', 'r'))

#print testicds[0]
#print testmeds[0]
#print testlabs[0]

print("complete")
