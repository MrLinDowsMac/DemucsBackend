#!/bin/bash
echo "models directory is... $1"
echo "File type is ... $2"
echo "writing to... $3"
echo "selected file... $4"
format=''
if [ $2 == 'mp3' ]; then format="--mp3" ; fi
conda run -n demucs bash -c "python3 -m demucs.separate -n demucs --models $1 $format --out $3 $4"
#Zip separated files, by default at /data/{file_folder}/demucs.zip
zip -r -j $3/result-demucs-separated.zip $3/demucs/ 