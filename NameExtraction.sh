pig
register piggybank-0.17.0.jar
DEFINE XPath org.apache.pig.piggybank.evaluation.xml.XPath();
A = LOAD '/user/darora2/Project/enwiki-20181120-pages-articles-multistream.xml' using org.apache.pig.piggybank.storage.XMLLoader('page') as (x:chararray);
B = FOREACH A GENERATE XPath(x, 'page/revision/text[contains(text(),"bio-stub")]/../../title') ;
STORE B into '/user/darora2/Project/Names' using PigStorage(';');
quit
hadoop fs -getmerge  /user/darora2/Project/Names /users/darora2/Project/Name.txt
awk 'NF' Name.txt > Names.txt
wc -l Names.txt
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
cp FilteredName11.txt People_Names_Final.txt
wc -l People_Names_Final.txt