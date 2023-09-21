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

class PDF2QAConverter:
    def __init__(self):
        self.app = FastAPI()

    # Function to convert the pdf file to text
    @staticmethod
    def get_text_data(pdf_path: str) -> str:
        with fitz.open(pdf_path) as doc:
            text = "".join(page.get_text() for page in doc)
            return text

    # Function to tokenize the text and return the paragraphs
    @staticmethod
    def get_paragraphs(text_data: str) -> list:
        result = tokenize.sent_tokenize(text_data)
        paragraphs = []
        current_paragraph = ""

        for sentence in result:
            if len(current_paragraph) + len(sentence) < 200:
                current_paragraph += " " + sentence
            else:
                paragraphs.append(current_paragraph)
                current_paragraph = sentence

        if current_paragraph:
            paragraphs.append(current_paragraph)

        return paragraphs

    # Function to get the response from OpenAI's api
    @staticmethod
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
            return str(err)

    # Function to split the Question and Answer by removing prefixes before the actual Question and Answers
    @staticmethod
    def remove_qa_prefix(text: str) -> str:
        delimiters = ['.', '-', ':']
        first_occurrence_index = min(text.find(delimiter) for delimiter in delimiters if text.find(delimiter) != -1)
        return text[first_occurrence_index + 1:].strip()

    # Function to parse Q&A pairs from lines
    @staticmethod
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