# import warnings
# warnings.filterwarnings("ignore")
import os
import utils
import spacy
import pprint
from spacy.matcher import Matcher
import multiprocessing as mp
from spacy import displacy
from flask import Flask,jsonify,request
from resume_parser import ResumeParser
import pandas as pd
df=pd.DataFrame(columns=['commodity_name','MO_no','Email'])

def resumeParser():
    i=1
    # C:\Users\Saurabh\Desktop\CTGT_old\Git\input
    files_loc = "C:\\Users\\Saurabh\\Desktop\\CTGT_old\\Git\\input"
    arrayList = []
    for filename in os.listdir(files_loc):
        f = os.path.join(files_loc, filename)
        data = None
        parser = None
        parser = ResumeParser(f)
#         print("Original Filename:"+f)
        data = parser.get_extracted_data()
        print(data)
        if(data):
            name = data.get('name')
#             name = str(parser.get_tsf_name());
            if(name):
                nameArr = name.split()
            if(len(nameArr)>1):
                firstName = nameArr[0] if len(nameArr) >= 0 else None
                lastName = nameArr[1] if len(nameArr) > 0 else None
            obj = {}
#             print(name)
#             print(data.get('mobile_number'))
            print(data.get('email'))
            df.loc[i,'Name']=name
            df.loc[i,'MO_no']=(data.get('mobile_number'))
            df.loc[i,'Email']=(data.get('email'))
            i+=1
print(resumeParser())

