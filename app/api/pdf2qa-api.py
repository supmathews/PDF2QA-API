from fastapi import FastAPI, UploadFile
from fastapi.responses import JSONResponse
import uvicorn
import tempfile
import os
import logging
from pdf2qaconverter import PDF2QAConverter  # PDF2QA class

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
    
    logging.info('Extracting text contents from the PDF file. . .')
    text_data = PDF2QAConverter.get_text_data(pdf_path)

    logging.info('Extracting the paragraphs from the text content. . .')
    paragraphs = PDF2QAConverter.get_paragraphs(text_data)

    logging.info('Extracting the QNA from the paragraphs. . .')
    responses = PDF2QAConverter.get_qna_openai(paragraphs)

    return responses

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
            
            # Extracting the QNA from the PDF file
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