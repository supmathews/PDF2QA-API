from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import tempfile
import os
import pandas as pd
import openai
import fitz
import nltk
nltk.download('punkt')
from nltk import tokenize

# Define the FastAPI instance
app = FastAPI()    

# Function to convert the pdf file to text
def get_text_data(pdf_path: str) -> str:
  with fitz.open(pdf_path) as doc:
      text = ""
      for page in doc:
          text += page.get_text()

      return text
  
# Function to tokenize the text and return the paragraphs
def get_paragraphs(pdf_path: str) -> list:
    # Extract the text data from the pdf
    text_data = get_text_data(pdf_path)

    # Tokenize the text by sentences
    result = tokenize. sent_tokenize(text_data)

    # Variables to store the tokenized strings and paragraphs
    str_paragraph = ''
    paragraphs = []

    # Iterate through the tokenized sentences
    for i in range(len(result)):
        sentence = result[i]
        len_para = len(tokenize.word_tokenize(str_paragraph))

        if len_para < 200:
            str_paragraph += ' ' +  sentence
        elif len_para >= 200:
            paragraphs.append(str_paragraph)
            str_paragraph = ''
            str_paragraph += ' ' + sentence
        elif i == len(result) - 1:
            paragraphs.append(str_paragraph)
    
    # Return the paragraphs
    return paragraphs

# API Endpoint to upload file
@app.post('/upload-pdf')
async def upload_pdf(file: UploadFile):
    try:
        # Create a temporary directory to save the uploaded file
        with tempfile.TemporaryDirectory() as temp_dir:
            pdf_path = os.path.join(temp_dir, file.filename)

            # Save the uploaded PDF file to the temporary directory
            with open(pdf_path, "wb") as pdf_file:
                pdf_file.write(file.file.read())
            
            # Extract the paragraphs
            paragraphs = get_paragraphs(pdf_path)

            return JSONResponse(content={'message': 'PDF successfully uploaded, saved and extracted!', 'paragraphs': paragraphs})
    except Exception as err:
        return JSONResponse(content={'message': 'upload_pdf function error\n' + str(err)})
if __name__ == '__main__':
    uvicorn.run(app)