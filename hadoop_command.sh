module load tensorflow/1.10-anaconda3

hadoop jar hadoop-streaming.jar \
-file mapper.py    -mapper mapper.py \
-file reducer.py   -reducer reducer.py \
-input People_Names_Final.txt -output final-output

hadoop fs -get final-output
rm final-output/_SUCCESS

hadoop jar hadoop-streaming.jar \
-file mapper2.py -mapper mapper2.py \
-input final-output/* -output final-layer-output

hadoop fs -cat final-layer-output/part-* > final_output.txt
shuf -n 100 final_output.txt > names_list.txt
cat names_list.txt | python fetchNames.py > peoples_names_list.txt
cat names_list.txt | python fetchSynset.py > synstring.txt

scp mapper2.py  darora2@dsba-hadoop.uncc.edu:/users/darora2/
