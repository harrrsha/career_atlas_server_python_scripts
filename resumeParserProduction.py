#!/usr/bin/env python
# coding: utf-8
import os
import utils
import spacy
import pprint
from spacy.matcher import Matcher
import multiprocessing as mp
from spacy import displacy
from docx2pdf import convert
import pathlib
from dotenv import load_dotenv
from flask import Flask, jsonify, request, send_file
from pdf_generation import pdf_gen
from resume_parser import ResumeParser 
ENVIRONMENT = 'prod'
if ENVIRONMENT == 'qa':
    load_dotenv('.env.qa')
elif ENVIRONMENT == 'prod':
    load_dotenv('.env.prod')
elif ENVIRONMENT == 'pre_prod':
    load_dotenv('.env.pre_prod')
app = Flask(__name__)
@app.route('/resume_parser/', methods=['POST'])
def resumeParser():
    files = request.json    
    arrayList = []
    for thing in files:   
        data = None
        parser = None
        #Function to return the file extension
        file_extension = pathlib.Path(thing['filename']).suffix       
        if file_extension == '.doc' or file_extension == '.docx':
            convert(thing['filename'])
            thing['filename'] =thing['filename'].replace(file_extension, '.pdf')              
        file_path = os.getenv('RESUME_PARSER_PATH')+thing['filename']
        parser = ResumeParser(file_path)
        data = parser.get_extracted_data() 
        if(data):
            name = data.get('name')
            #name = str(parser.get_tsf_name());            
            firstName = None
            lastName = None       
            if(name):
               nameArr = name.split()
               if(len(nameArr)>1):
                firstName = nameArr[0]
                lastName = nameArr[1]
               if(len(nameArr)>0):
                firstName = nameArr[0]
            obj = {}
            obj["firstName"] = firstName
            obj["lastName"] = lastName
            obj["mobileNo"] = data.get('mobile_number')
            obj["emailId"] = data.get('email')
            obj["fileName"] = thing['filename']
            obj["originalFileName"] = thing['originalname']                
            arrayList.append(obj)         
    return jsonify(arrayList)
    
@app.route('/interview_feedback_pdfexport/', methods=['POST'])
def interviewFeedbackPDFExport():
    req_data = request.json    
    path = pdf_gen(req_data,ENVIRONMENT)     
    return jsonify(filename=path);

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=105, debug=True)


