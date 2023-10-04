from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import tempfile
import os
import logging
from json import loads, dumps
import openai
import pandas as pd
from pdf2qaconverter import PDF2QAConverter  # PDF2QA class
from dotenv import load_dotenv
import time

# Load the OpenAI API Key
# Create a .env file storing your key
load_dotenv('openai_key.env')

# Log configuration
logging.basicConfig(filename='pdf2qa.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Define the FastAPI instance
app = FastAPI()    

def extract_qna_pairs(pdf_path: str) -> list:
    """
    This function extracts the QnA from the pdf file.
    
    Args:
        pdf_path (string): Path of the PDF file saved in the temporary directory
    
    Returns:
        list: contains the QnA pair
    """
    text_data = PDF2QAConverter.get_text_data(pdf_path)
    paragraphs = PDF2QAConverter.get_paragraphs(text_data)

    qna_pairs = []
    
    # Define the api key
    openai.api_key = os.environ.get('OPENAI_API_KEY')
    for index, para in enumerate(paragraphs):
        logging.info(f'Processing Paragraph {index + 1}')
       
        para = para.replace('\n', '')
        qna = []
        
        logging.info(f'Extracting QNA for Paragraph: {para}')
        response = PDF2QAConverter.get_qna_openai(para)
        logging.info(f'Extracted QNA for Paragraph: {response}')

        qna.append(response)

        with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
            logging.info('Opened the temporary file')
            for qa in qna:
                try:
                    temp_file.write(qa)
                except Exception as err:
                    logging.info(f'{err} in Paragraph {index + 1}')
                    #break

            temp_file.flush()
            temp_file_path = temp_file.name

        try:
            with open(temp_file_path, 'r') as temp_file:
                lines = temp_file.readlines()
                pairs = PDF2QAConverter.parse_qa_pairs(lines)
                logging.info('Extracted QNA pairs')
        except Exception as err:
            logging.info(err)
            #break

        for q, a in pairs:
            try:
                qna_pairs.append({'Paragraph': para.strip(), 'Question': PDF2QAConverter.remove_qa_prefix(q), 'Answer': PDF2QAConverter.remove_qa_prefix(a)})
            except Exception as err:
                logging.info('QnA was an empty sequence, moving to the next set')
                logging.info(err)
                #break

    return qna_pairs

# API endpoint to upload the PDF file
@app.post('/upload-pdf')
async def upload_pdf(file: UploadFile):
    """
        API endpoint to upload the PDF file. 
        The function will store the PDF file in a temporary directory which
        will be active until the PDF is successfully uploaded, saved, and
        QNA pairs are extracted.

        Args:
            file (UploadFile): form-data object uploaded by the user
        Returns:
            JSONResponse: key-value of message and data
    """
    try:
        logging.info('Starting PDF2QA Converter...')
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, file.filename)
            logging.info(f'Created temporary directory: {temp_dir}')

            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(file.file.read())
                logging.info(f'Saved the PDF file in the directory {pdf_path}')
                #time.sleep(0.5)

            qna_pairs = extract_qna_pairs(pdf_path)

            if not qna_pairs:
                logging.info('No QNA pairs found in the PDF')
                return JSONResponse(content={'message': 'No QNA pairs found in the PDF.'})
            
            logging.info(f'PDF successfully uploaded, saved and extracted!')
            return JSONResponse(content={'message': 'PDF successfully uploaded, saved, and QNA pairs extracted!', 'data': qna_pairs})
    except Exception as err:
        return JSONResponse(content={'message': str(err)})
    
if __name__ == '__main__':
    uvicorn.run(app)