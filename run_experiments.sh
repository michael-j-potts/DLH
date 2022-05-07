#!/bin/bash
echo Preparing data and embedding files
python3 process_mimic.py ADMISSIONS.csv DIAGNOSES_ICD.csv PATIENTS.csv PRESCRIPTIONS.csv LABEVENTS.csv MIMICIIIPROCESSED
python3 converter.py
printf "\n"

echo Running the latent space models
python3 CAE.py
python3 AE.py
printf "\n"

echo Logistic Regression
python3 logistic_regression.py
printf "\n"

echo LSTM with only ICD
python3 rnn_icd.py
printf "\n"

echo LSTM - simple concatenation
python3 rnn_concat.py
printf "\n"

echo LSTM - only latent CAE
python3 rnn_latent.py --emb_weights './CAE_embedding_weights.npy'
printf "\n"

echo LSTM - only latent AE
python3 rnn_latent.py --emb_weights './AE_embedding_weights.npy'
printf "\n"

echo LSTM - concat latent AE
python3 rnn_concat_latent.py --emb_weights './AE_embedding_weights.npy'
printf "\n"

echo LSTM - concat latent CAE
python3 rnn_concat_latent.py --emb_weights './CAE_embedding_weights.npy'
printf "\n"

echo Mortality prediction based on in hospital death
echo Logistic Regression
python3 logistic_regression.py --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

echo LSTM with only ICD
python3 rnn_icd.py --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

echo LSTM - simple concatenation
python3 rnn_concat.py --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

echo LSTM - only latent CAE
python3 rnn_latent.py --emb_weights './CAE_embedding_weights.npy' --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

echo LSTM - only latent AE
python3 rnn_latent.py --emb_weights './AE_embedding_weights.npy' --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

echo LSTM - concat latent AE
python3 rnn_concat_latent.py --emb_weights './AE_embedding_weights.npy' --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

echo LSTM - concat latent CAE
python3 rnn_concat_latent.py --emb_weights './CAE_embedding_weights.npy' --hosp './MIMICIIIPROCESSED.hospmorts'
printf "\n"

