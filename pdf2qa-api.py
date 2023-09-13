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
from dotenv import load_dotenv
# Load the OpenAI API Key
# Create a .env file storing your key
load_dotenv('openai_key.env')

# Define the FastAPI instance
app = FastAPI()    

# Function to convert the pdf file to text
def get_text_data(pdf_path: str) -> str:
    with fitz.open(pdf_path) as doc:
        text = ""
        for page in doc:
            text += page.get_text()
        # Return the text data
        return text
  
# Function to tokenize the text and return the paragraphs
def get_paragraphs(text_data: str) -> list:

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

# Function to get the response from OpenAI's api
def get_qna_openai(text: str) -> str:
    try:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt="Generate 2 descriptive questions and answers per paragraph wise: " + text,
            temperature=0.9,
            max_tokens=200,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
        )
        return response.choices[0].text
    except Exception as err:
        return JSONResponse(content={'message': str(err)})
    
# Function to get the Q&A pairs from the qna generated
def parse_qa_pairs(lines: list) -> list:
    pairs = []
    current_q = ''
    current_a = ''
    for line in lines:
        line = line.strip()
        if line.startswith('Q'):
            if current_q:
                pairs.append((current_q, current_a))
            current_q = line
            current_a = ''
        elif line.startswith('A'):
            current_a += line[:] + '\n'
  
    if current_q:
        pairs.append((current_q, current_a))
    return pairs

# Function to split the Question and Answwer by removing prefixes before the actual Question and Answers
def remove_qa_prefix(text: str) -> str:
    # Initialise the index at end of text
    first_occurance_index = len(text)

    delimiters = ['.', '-', ':']

    # Finding the index of the first occurrence of any delimiter
    for delimiter in delimiters:
        index = text.find(delimiter)
        if index != -1 and index < first_occurance_index:
            first_occurance_index = index
        
    # Return the clean string
    return text[first_occurance_index+1:].strip()

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

            # Convert the pdf file to text
            text_data = get_text_data(pdf_path)
            
            # Extract the paragraphs
            paragraphs = get_paragraphs(text_data)

            # Define the api key
            openai.api_key = os.environ.get('OPENAI_API_KEY')

            # Create a temporary DataFrame to store the cleaned data
            columns = ['Paragraph', 'Question', 'Answer']      ## Adding 'paragraph' column 
            cleaned_data = pd.DataFrame(columns=columns)

            for para in paragraphs:
                # Variable to store the Q&A pairs
                qna = []

                # Get the Q&A from the OpenAI 
                response = get_qna_openai(para)

                if type(response) != str:
                    qna.append(response)
                else:
                    # move to next para
                    break
            
                # Create a temporary file to store the qna generated
                with tempfile.NamedTemporaryFile(mode='w', delete=False) as temp_file:
                    for qa in qna:
                        print(qa)
                        temp_file.write(qa)
                    temp_file.flush()
                    temp_file_path = temp_file.name

                with open(temp_file_path, 'r') as temp_file:
                    lines = temp_file.readlines()
                    pairs = parse_qa_pairs(lines)
                
                # The column values are appended accordingly to the new_rows list below
                new_rows = []
                for q, a in pairs:
                    new_rows.append({'Paragraph': para, 'Question': remove_qa_prefix(q), 'Answer': remove_qa_prefix(a)})
                
                cleaned_data = pd.concat([cleaned_data, pd.DataFrame(new_rows)], ignore_index=True)

            return JSONResponse(content={'message': 'PDF successfully uploaded, saved and extracted!', 'paragraphs': paragraphs})
    except Exception as err:
        return JSONResponse(content={'message': 'upload_pdf function error\n' + str(err)})
    
if __name__ == '__main__':
    uvicorn.run(app)