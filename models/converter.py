#This file is used to unravel the three documents used by CAE and AE into just visits, and codes.

import pickle
import numpy as np
import time

digitICD9 = []
meds = []
abnlabs = []

#Might need to reformat these three to just store in a text file or something line by line as np.arrays 
#Or be prepared to convert to numpy arrays in subsequent files?
def unravelicd(input):
    for patient in input:
        for visit in patient:
            digitICD9.append(np.array(visit))
    print "Finished unraveling ICDs"

def unravelmed(input):
    for patient in input:
        for visit in patient:
            meds.append(np.array(visit))
    print "Finished unraveling meds"

def unravellab(input):
    for patient in input:
        for visit in patient:
            abnlabs.append(np.array(visit))
    print "Finished unraveling labs"


#import data
ICD_data = pickle.load(open('./MIMICIIIPROCESSED.3digitICD9.seqs','r'))
Med_data = pickle.load(open('./MIMICIIIPROCESSED.meds.seqs','r'))
Lab_data = pickle.load(open('./MIMICIIIPROCESSED.abnlabs.seqs','r'))

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


print "complete"