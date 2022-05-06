# This script processes MIMIC-III dataset and builds longitudinal diagnosis records for patients with at least two visits.
# The output data are cPickled, and suitable for training Doctor AI or RETAIN
# Written by Edward Choi (mp2893@gatech.edu)
# Usage: Put this script to the foler where MIMIC-III CSV files are located. Then execute the below command.
# python3 process_mimic.py ADMISSIONS.csv DIAGNOSES_ICD.csv PATIENTS.csv PRESCRIPTIONS.csv LABEVENTS.csv MIMICIIIPROCESSED

# Output files
# <output file>.pids: List of unique Patient IDs. Used for intermediate processing
# <output file>.morts: List of binary values indicating the mortality of each patient
# <output file>.dates: List of List of Python datetime objects. The outer List is for each patient. The inner List is for each visit made by each patient
# <output file>.seqs: List of List of List of integer diagnosis codes. The outer List is for each patient. The middle List contains visits made by each patient. The inner List contains the integer diagnosis codes that occurred in each visit
# <output file>.types: Python dictionary that maps string diagnosis codes to integer diagnosis codes.

import sys
import pickle
from datetime import datetime
import math
import time

def convert_to_icd9(dxStr):
	if dxStr.startswith('E'):
		if len(dxStr) > 4: return dxStr[:4] + '.' + dxStr[4:]
		else: return dxStr
	else:
		if len(dxStr) > 3: return dxStr[:3] + '.' + dxStr[3:]
		else: return dxStr
	
def convert_to_3digit_icd9(dxStr):
	if dxStr.startswith('E'):
		if len(dxStr) > 4: return dxStr[:4]
		else: return dxStr
	else:
		if len(dxStr) > 3: return dxStr[:3]
		else: return dxStr

if __name__ == '__main__':
	admissionFile =  sys.argv[1]
	diagnosisFile = sys.argv[2]
	patientsFile = sys.argv[3]
	medFile = sys.argv[4]
	labFile = sys.argv[5]
	outFile = sys.argv[6]

#	admAssessmap = pickle.load(open('../R-RNN/admToAssessmentDict.p', 'r'))

	print('Collecting mortality information')
	pidDodMap = {}
	infd = open(patientsFile, 'r')
	infd.readline()
	for line in infd:
		tokens = line.strip().split(',')
		pid = int(tokens[1])
		dod_hosp = tokens[5]
		if len(dod_hosp) > 0:
			pidDodMap[pid] = 1
		else:
			pidDodMap[pid] = 0
	infd.close()

	print('Collecting hospital mortality information')
	hosppidDodMap = {}
	infd = open(admissionFile, 'r')
	infd.readline()
	for line in infd:
		tokens = line.strip().split(',')
		pid = int(tokens[1])
		hosppidDodMap[pid] = int(tokens[-2])
	infd.close()

	print('Building pid-admission mapping, admission-date mapping')
	pidAdmMap = {}
	admDateMap = {}
	infd = open(admissionFile, 'r')
	infd.readline()
	for line in infd:
		tokens = line.strip().split(',')
		pid = int(tokens[1])
		admId = int(tokens[2])
		admTime = datetime.strptime(tokens[3], '%Y-%m-%d %H:%M:%S')
		admDateMap[admId] = admTime
		if pid in pidAdmMap: pidAdmMap[pid].append(admId)
		else: pidAdmMap[pid] = [admId]
	infd.close()

	print('Building admission-med mapping')
	admMedMap = {}
	infd = open(medFile, 'r')
	infd.readline()
	for line in infd:
		tokens = line.strip().split(',')
		admId = int(tokens[2])
		med = tokens[7]

		if admId in admMedMap:
			admMedMap[admId].append(med)
		else:
			admMedMap[admId] = [med]
	infd.close()

	print('Building admission-lab mapping') #3,8
	admAllLabMap = {}
	admAbnormalLabMap = {}
	infd = open(labFile, 'r')
	infd.readline()
	no_admission = 0
	total = 0
	for line in infd:
		tokens = line.strip().split(',')
		if tokens[2] == '':
			no_admission += 1
			total += 1
			continue
		total += 1
		admId = int(tokens[2])
		abnormal_flag = tokens[8]
		lab = tokens[3]

		if admId in admAllLabMap:
			admAllLabMap[admId].append(lab)
		else:
			admAllLabMap[admId] = [lab]

		if abnormal_flag:
			if admId in admAbnormalLabMap:
				admAbnormalLabMap[admId].append(lab)
			else:
				admAbnormalLabMap[admId] = [lab]

	infd.close()
	print("Labs without admissions =", no_admission, "out of", total)

	print('Building admission-dxList mapping')
	admDxMap = {}
	admDxMap_3digit = {}
	infd = open(diagnosisFile, 'r')
	infd.readline()
	for line in infd:
		tokens = line.strip().split(',')
		admId = int(tokens[2])
		dxStr = 'D_' + convert_to_icd9(tokens[4][1:-1]) ############## Uncomment this line and comment the line below, if you want to use the entire ICD9 digits.
		dxStr_3digit = 'D_' + convert_to_3digit_icd9(tokens[4][1:-1])

		if admId in admDxMap: 
			admDxMap[admId].append(dxStr)
		else: 
			admDxMap[admId] = [dxStr]

		if admId in admDxMap_3digit: 
			admDxMap_3digit[admId].append(dxStr_3digit)
		else: 
			admDxMap_3digit[admId] = [dxStr_3digit]
	infd.close()

	def getList(dictionary, key):
		if key in dictionary:
			return dictionary[key]
		else:
			return []

	print('Building pid-sortedVisits mapping')
	pidSeqMap = {}
	pidSeqMap_3digit = {}
	pidSeqMap_meds = {}
	pidSeqMap_allLabs = {}
	pidSeqMap_abnormalLabs = {}
	pidSeqMap_assessments = {}

	single_admission_count = 0

	for pid, admIdList in pidAdmMap.items():
		if len(admIdList) < 2: 
			single_admission_count += 1 
			continue

		sortedList = sorted([(admDateMap[admId], admDxMap[admId]) for admId in admIdList])
		pidSeqMap[pid] = sortedList

		sortedList_3digit = sorted([(admDateMap[admId], admDxMap_3digit[admId]) for admId in admIdList])
		pidSeqMap_3digit[pid] = sortedList_3digit

		sortedList_meds = sorted([(admDateMap[admId], getList(admMedMap, admId)) for admId in admIdList])
		pidSeqMap_meds[pid] = sortedList_meds

		sortedList_allLabs = sorted([(admDateMap[admId], getList(admAllLabMap, admId)) for admId in admIdList])
		pidSeqMap_allLabs[pid] = sortedList_allLabs

		sortedList_abnormalLabs = sorted([(admDateMap[admId], getList(admAbnormalLabMap, admId)) for admId in admIdList])
		pidSeqMap_abnormalLabs[pid] = sortedList_abnormalLabs

#		sortedList_assessments = sorted([(admDateMap[admId], (admAssessmap[admId] if admId in admAssessmap else [])) for admId in admIdList])
#		pidSeqMap_assessments[pid] = sortedList_assessments
	
	print('Single admission count: ', single_admission_count)

	print('Building pids, dates, mortality_labels, strSeqs')
	pids = []
	dates = []
	seqs = []
	morts = []
	hospmorts = []
	medseqs = []
	alllabseqs = []
	abnormallabseqs = []

	for pid, visits in pidSeqMap.items():
		pids.append(pid)
		morts.append(pidDodMap[pid])
		hospmorts.append(hosppidDodMap[pid])
		seq = []
		date = []
		for visit in visits:
			date.append(visit[0])
			seq.append(visit[1])
		dates.append(date)
		seqs.append(seq)
	
	print('Building pids, dates, strSeqs for 3digit ICD9 code')
	seqs_3digit = []
	for pid, visits in pidSeqMap_3digit.items():
		seq = []
		for visit in visits:
			seq.append(visit[1])
		seqs_3digit.append(seq)
	
	print('Building pids, dates, strSeqs for meds')
	seqs_meds = []
	for pid, visits in pidSeqMap_meds.items():
		seq = []
		for visit in visits:
			seq.append(visit[1])
		seqs_meds.append(seq)

	print('Converting strSeqs to intSeqs, and making types for meds')
	types_meds = {}
	newSeqs_meds = []
	for patient in seqs_meds:
		newPatient = []
		for visit in patient:
			newVisit = []
			for code in visit:
				if code in types_meds:
					newVisit.append('m'+str(types_meds[code]))
				else:
					types_meds[code] = len(types_meds)
					newVisit.append('m'+str(types_meds[code]))
			newPatient.append(newVisit)
		newSeqs_meds.append(newPatient)

	print("Med types size ", len(types_meds)) #3202 meds

	print('Building pids, dates, strSeqs for all labs')
	seqs_alllabs = []
	for pid, visits in pidSeqMap_allLabs.items():
		seq = []
		for visit in visits:
			seq.append(visit[1])
		seqs_alllabs.append(seq)

	print('Converting strSeqs to intSeqs, and making types for all labs')
	types_alllabs = {}
	newSeqs_alllabs = []
	for patient in seqs_alllabs:
		newPatient = []
		for visit in patient:
			newVisit = []
			for code in visit:
				if code in types_alllabs:
					newVisit.append(types_alllabs[code])
				else:
					types_alllabs[code] = len(types_alllabs)
					newVisit.append(types_alllabs[code])
			newPatient.append(newVisit)
		newSeqs_alllabs.append(newPatient)
	
	print("All lab types size ", len(types_alllabs))

	print ('Building pids, dates, strSeqs for abnormal labs')
	seqs_abnormallabs = []
	for pid, visits in pidSeqMap_abnormalLabs.items():
		seq = []
		for visit in visits:
			seq.append(visit[1])
		seqs_abnormallabs.append(seq)

#	print 'Building pids, dates, strSeqs for assessments'
#	seqs_assessments = []
#	for pid, visits in pidSeqMap_assessments.items():
#		seq = []
#		for visit in visits:
#			seq.append(visit[1])
#		seqs_assessments.append(seq)

	print('Converting strSeqs to intSeqs, and making types for abnormal labs')
	types_abnormallabs = {}
	newSeqs_abnormallabs = []
	for patient in seqs_abnormallabs:
		newPatient = []
		for visit in patient:
			newVisit = []
			for code in visit:
				if code in types_abnormallabs:
					newVisit.append('l'+str(types_abnormallabs[code]))
				else:
					types_abnormallabs[code] = len(types_abnormallabs)
					newVisit.append('l'+str(types_abnormallabs[code]))
			newPatient.append(newVisit)
		newSeqs_abnormallabs.append(newPatient)

	print("Abnormal lab types size ", len(types_abnormallabs))

	print('Converting strSeqs to intSeqs, and making types')
	types = {}
	newSeqs = []
	for patient in seqs:
		newPatient = []
		for visit in patient:
			newVisit = []
			for code in visit:
				if code in types:
					newVisit.append(types[code])
				else:
					types[code] = len(types)
					newVisit.append(types[code])
			newPatient.append(newVisit)
		newSeqs.append(newPatient)
	
	print('Converting strSeqs to intSeqs, and making types for 3digit ICD9 code')
	types_3digit = {}
	newSeqs_3digit = []
	for patient in seqs_3digit:
		newPatient = []
		for visit in patient:
			newVisit = []
			for code in set(visit):
				if code in types_3digit:
					newVisit.append('i'+str(types_3digit[code]))
				else:
					types_3digit[code] = len(types_3digit)
					newVisit.append('i'+str(types_3digit[code]))
			newPatient.append(newVisit)
		newSeqs_3digit.append(newPatient)
	
	print("ICD types size ", len(types_3digit))

	newSeqs_all = [[(newSeqs_abnormallabs[i][j] + newSeqs_meds[i][j] + newSeqs_3digit[i][j]) for j in range(len(newSeqs_abnormallabs[i]))] for i in range(len(newSeqs_abnormallabs))]

	types_all = {}
	newSeqs_all_int = []
	for patient in newSeqs_all:
		newPatient = []
		for visit in patient:
			newVisit = []
			for code in set(visit):
				if code in types_all:
					newVisit.append(types_all[code])
				else:
					types_all[code] = len(types_all)
					newVisit.append(types_all[code])
			newPatient.append(newVisit)
		newSeqs_all_int.append(newPatient)

	print("All types size ", len(types_all))

	pickle.dump(pids, open(outFile+'.pids', 'wb'), -1)
	pickle.dump(dates, open(outFile+'.dates', 'wb'), -1)
	pickle.dump(morts, open(outFile+'.morts', 'wb'), -1)
	pickle.dump(hospmorts, open(outFile+".hospmorts", "wb"), -1)
	pickle.dump(newSeqs, open(outFile+'.seqs', 'wb'), -1)
	pickle.dump(types, open(outFile+'.types', 'wb'), -1)
	pickle.dump(newSeqs_3digit, open(outFile+'.3digitICD9.seqs', 'wb'), -1)
	pickle.dump(types_3digit, open(outFile+'.3digitICD9.types', 'wb'), -1)
	pickle.dump(newSeqs_meds, open(outFile+'.meds.seqs', 'wb'), -1)
	pickle.dump(types_meds, open(outFile+'.meds.types', 'wb'), -1)
	pickle.dump(newSeqs_alllabs, open(outFile+'.alllabs.seqs', 'wb'), -1)
	pickle.dump(types_alllabs, open(outFile+'.alllabs.types', 'wb'), -1)
	pickle.dump(newSeqs_abnormallabs, open(outFile+'.abnlabs.seqs', 'wb'), -1)
	pickle.dump(types_abnormallabs, open(outFile+'.abnlabs.types', 'wb'), -1)
	# pickle.dump(seqs_assessments, open(outFile+'.assessments.seqs', 'wb'), -1)
	pickle.dump(types_all, open(outFile+'.all.types', 'wb'), -1)
	pickle.dump(newSeqs_all_int, open(outFile+'.all.seqs', 'wb'), -1)
	print("complete")
