# Hadoop_Project

This project is made with the help of Apache Pig on Hadoop Cluster and some Python Code.

The cartoon https://xkcd.com/1970/ shows an example of a name domino.
Used the Wikipedia to extract names of people and created the smallest possible name domino containing the maximum number of names extracted. 
Note - The name should be a title of the Wikipedia article about this person.

# Project Goal
Go to Wikipedia from Wikimedia dumps, https://dumps.wikimedia.org/enwiki/20181120/enwiki-20181120-pages-articles-multistream.xml.bz2 
Decide whether a given title represents a name of a person.
Run the script on Hadoop.
Make Domino from the names extracted using Python by making mapper and reducer classes.


# Steps followed are:

●	Downloaded the on Hadoop Cluster using wget command and shared the file with other teams through Google Drive because the link, https://dumps.wikimedia.org/enwiki/20181120/enwiki-20181120-pages-articles-multistream.xml.bz2  is no longer accessible and other teams did not have the file.

wget https://dumps.wikimedia.org/enwiki/20181120/enwiki-20181120-pages-articles-multistream.xml.bz2 &

●	Extracted the bz2 file using the bunzip2 command.

bzip2 -dk enwiki-20181120-pages-articles-multistream.xml.bz2

●	Pushed the file to Hadoop File System using put command.

hadoop fs -put enwiki-20181120-pages-articles-multistream.xml /user/darora2/Project


# How to decide whether a given title represents the name of a person.

I started with the analysis of the Wikipedia dump file and tried to identify the information that could help us shortlisting the titles with “Person names”. Initially, I looked up for famous personalities like Bill Gates and tried to understand the xml dump of a page. I noticed that the page contained “Birth”, “Death”, “was born on” tags and text in the dump file. 
The next step was to find look up for lesser known personalities and verify the same information. However, I noticed that this time pages were too generic with very little information and majorly missing these tags. Then I tried various other text grep on the XML dump like bibliography and few other filters, but I could find any uniformity of information across all the pages. Finally, I looked up the page category and Bingo!
I found the tag that I was looking for. All the pages with human titles had a generic tag “bio-stub” and other specific pages had “US-bio-stub”, “Sports-bio-stub” and many more. But the bio-stub tag was generic for all human titled pages. So I used it for extracting titles of pages with human names as discussed in the next section.

This helped us to get all the names of the persons along with some junk data which I removed with the help of the sed command in Hadoop local file system.
●	Removed empty lines having spaces.

●	Removed unnecessary data like:

	○	Removed lines having ‘Categorical’ data in it, non-related to people names.
	○	Removed lines having ‘Wikipedia’ data in it, non-related to people names.
	○	Removed lines having ‘Template’ data in it, non-related to people names.
	○	Removed lines having ‘Portal’ data in it, non-related to people names.
	○	Removed lines having ‘File’ data in it, non-related to people names.
	○	Removed special characters from the names.
	○	Removed Jr. and Sr. from the names.
	○	Removed numbers from the names.
	○	Removed the word “Draft:” from the names.	
●	Copied all the data from Filtered List to a final file containing all names.

# Algorithm to be run on Hadoop

Came up with several filters to filter out the names of the person using Apache Pig on Hadoop File System.

●	Logged into Apache Pig using pig command.

●	Loaded the file to variable A using XMLLoader and splitting the XML by pages.

Below is the command:
A = LOAD '/user/darora2/Project/enwiki-20181120-pages-articles-multistream.xml' using org.apache.pig.piggybank.storage.XMLLoader('page') as (x:chararray);

●	Applied filter on the data with the help of XPath if text tag contains bio-stub in it.
Below is the command:
B = FOREACH A GENERATE XPath(x,'page/revision/text[contains(text(),"bio-stub")]/../../title') ;

●	Stored the names into Hadoop Local File System
Below is the command:
	STORE B into '/user/darora2/Project/Names' using PigStorage(';');
●	Came out of Apache Pig using the quit command.

●	Merged the 520 files generated having names to one file.
Below is the command:
	hadoop fs -getmerge  /user/darora2/Project/Names /users/darora2/Project/Name.txt

●	Removed empty lines having spaces using the following command:
	awk 'NF' Name.txt > Names.txt

●	Checked the number of lines. Below is the command:
wc -l Names.txt

●	Removed unnecessary data using the below commands:
	sed "/Category/d" Names.txt > FilteredName1.txt
sed "/Wikipedia/d" FilteredName1.txt > FilteredName2.txt
sed "/Template/d" FilteredName2.txt > FilteredName3.txt
sed "/Portal/d" FilteredName3.txt > FilteredName4.txt
sed "/File/d" FilteredName4.txt > FilteredName5.txt
sed -e "s/([^()]*)//g" FilteredName5.txt > FilteredName6.txt
sed -e "s/Jr.//g" FilteredName6.txt > FilteredName7.txt
sed -e "s/Sr.//g" FilteredName7.txt > FilteredName8.txt
sed -e "s/,.*$//" FilteredName8.txt > FilteredName9.txt
sed -e "s/Draft://g" FilteredName9.txt > FilteredName10.txt
sed "/[0-9]/d" FilteredName10.txt > FilteredName11.txt

●	Copied all the data from Filtered List to a final file. Below is the command:
cp FilteredName11.txt People_Names_Final.txt

●	Checked the name count of names using word count command. Below is the command:
	wc -l People_Names_Final.txt

●	Extracted the list of names using WinSCP.

●	Now, domino creation starts after sampling the data, ensuring cohesion of the name cluster.


# Figure out how to create a domino. Under what conditions you need/don't need to do this task on the cluster?

Creating a word domino in python. First, one must create a board and dominoes. Then we read all the names from the text file and only use 2500 randomly sampled names out of the whole list. Then we need to find synonyms of each name to match them with similar names. The result is the visualization of the board with dominoes placed according to other slightly matching first names or last names.  We divided the names between the first name and last name and evaluated using a key-value pair. Doing this as a local script takes a heavy amount of load and time and its unfeasible to do it on all data. So, we used Hadoop MapReduce to find the names which are similar and then we generated the visualization using python.

# Run it on the extracted data and visualize.

Run the code on Hadoop local file system providing the file containing all persons’ names to 
Once we get the file containing all names, we run Hadoop MapReduce task to get similar names.
Below are the commands:

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

In the first map reduce we fetch similar words in the name. In the next mapper we just keep names which are highly common. We write the output of the map reduce to final_output.txt file
As we have too many names for visualization, it is not feasible and sensible to use all the names for visualization. Hence, we use random 100 lines from final output and then filter the files accordingly.

shuf -n 100 final_output.txt > names_list.txt
module unload tensorflow/1.10-anaconda3

cat names_list.txt | python fetchNames.py > peoples_names_list.txt
cat names_list.txt | python fetchSynset.py > synstring.txt

At the end of it we run the visualization code and the output is saved in visualization.png

module load tensorflow/1.10-anaconda3
python Domino.py 

Output figure is being achieved in the form of an image “visualization.png”.
Note: Code for Domino.py, fetchNames.py, fetchSynset.py, mapper.py, mapper2.py and reducer.py has been attached separately.

# What is the precision, recall, and F-measure of your extractor, and how you established it.

Precision
Precision is the number of items correctly identified as positive out of total items identified as positive.

Recall or Sensitivity or TPR (True Positive Rate)
The recall is the number of items correctly identified as positive out of total true positives.

F-measure
It is the harmonic mean of precision and score and given by:

Checked the names that were in the final domino. The count of names is 91. Apart from this, we sampled 200 names randomly to check for the accuracy of our model. Checked them on Wikipedia to verify if they were human names and we were able to achieve 100% accuracy. All the names that we had were human titled Wikipedia pages.

Here are the Precision, Recall and F-measure:

TP = 291, FP = 0 , FN = 0, TN = 0
Precision = 291/ (291+0) = 1
Recall = 291/ (291+0) = 1
F-measure = 2 * (1*1) / (1+1) = 2/2 = 1


●	Count of the people names extracted from the “enwiki-20181120-pages-articles-multistream.xml.bz2” file provided is 275,000.

●	F measure is 1 i.e. 100 %. (as calculated in previous question)

# Density of Domino

I divided the domino into parts of 100px to 100px and measured the words in that diameter. 

By taking random samples of 10 such diameters we got the density as:
- The number of letters per square of the domino diameter is 8.44 letters per 100pixels diameter.
- The density of letters goes as high as 14 -18 words per diameter and as low as 4 to 5 words.
