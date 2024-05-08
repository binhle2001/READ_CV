import logging
from fastapi import FastAPI, File, UploadFile, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import io
import google.generativeai as genai
from PyPDF2 import PdfReader
import os 
import json
from google.generativeai.types import HarmCategory, HarmBlockThreshold
from ai_core.source.getting_email import get_attachment
from api.helpers.common import get_env_var
from api.helpers.database import get_db
from api.schema import ProcessStatus

genai.configure(api_key = get_env_var("gemini", "API_KEY"))
model_gemini = genai.GenerativeModel('gemini-pro')
app = FastAPI()


class PDFInfo(BaseModel):
    title: str
    text: str

def extract_info_from_pdf(file: bytes) -> PDFInfo:
    pdf_reader = PdfReader(io.BytesIO(file))
    metadata = pdf_reader.metadata
    try:
        title = metadata.get('/Title', '')
    except:
        title = ""
        pass
    text = ""
    for page in pdf_reader.pages:
        text += page.extract_text()
    return PDFInfo(title=title, text=text)

info_format = """{
    "Name": "",
    "Applied_position": "",
    "Phone_number":"",
    "Email":"",
    "Work_experience": [{"Company", "Position", "Duration"}],
    "Projects": [{"Name", "Duration","Description", }]
    "Education": [{"Major", "School", "Degree", "Duration", "GPA"}],
    "Technical_skills": []
}"""

''' 
def extract_pdf_info(tenant_id):
    ProcessStatus.list_tenant[tenant_id] = True
    data_cv = get_attachment(tenant_id)
    
    if data_cv is None:
        return None
    candidate_informations = []
    for cv in data_cv:
        file_path = cv["attachment"]
        if file_path is None:
            continue
        with open(file_path, "rb") as file:
            contents = file.read()
        pdf_info = extract_info_from_pdf(contents)
        if pdf_info.text == "":
            logging.error("Định dạng file không hỗ trợ")
            candidate_informations.append({
                "snippet": cv["snippet"],
                "isFalse": True,
                "link_cv": cv['link_cv']
            })
            continue
        prompt = f"""
            <|im_start|> DOCUMENT
            {pdf_info.text}
            <|im_end|>
            <|im_start|> system
            Tokyo Tech Lab Bot is a bot designed to extract information from the content of PDF files. Tokyo Tech Lab Bot is capable of:
            - Please rewrite this with correct spelling. For example: "Đ ạ i h ọ c Qu ố c Gia Hà N ộ i" is changed to "Đại học Quốc Gia Hà Nội".
            - Extracting information such as name, position applied for, phone number, email, work experience/projects undertaken, education, skills.
            - Providing responses in the form of a dictionary as follows:
            {info_format}
            - Do not use external knowledge beyond the information provided in the DOCUMENT. If information is not provided, write "null". If a field has no information, return the entire field as null.
            <|im_end|>
            <|im_start|> assistant
            """.strip()
        output = model_gemini.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                                        candidate_count = 1,
                                        stop_sequences = ['<|im_end|>'],
                                        max_output_tokens = 2000,
                                        top_p = 0.9,
                                        top_k = 7,
                                        temperature = 0.1),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
            },

    )
        try:
            parse_data = json.loads(output.text.replace("\n", ""))
            candidate_informations.append({
                "snippet": cv["snippet"],
                "candidate_info": parse_data,
                "link_cv": cv["link_cv"]
            })
            
        except Exception as e:
            print("Error at read_cv:", e)
            candidate_informations.append({
                "snippet": cv["snippet"],
                "isFalse": True,
                "link_cv": cv["link_cv"]
            })
    ProcessStatus.list_tenant[tenant_id] = False
    return candidate_informations

'''

def extract_candidate_info(contents):
    pdf_info = extract_info_from_pdf(contents)
    if pdf_info.text == "":
        logging.error("Định dạng file không hỗ trợ")
        return {
            "http_code": status.HTTP_400_BAD_REQUEST,
            "message": "Định dạng file không hỗ trợ"
        }
    prompt = f"""
            <|im_start|> DOCUMENT
            {pdf_info.text}
            <|im_end|>
            <|im_start|> system
            Tokyo Tech Lab Bot is a bot designed to extract information from the content of PDF files. Tokyo Tech Lab Bot is capable of:
            - Please rewrite this with correct spelling. For example: "Đ ạ i h ọ c Qu ố c Gia Hà N ộ i" is changed to "Đại học Quốc Gia Hà Nội".
            - Extracting information such as name, position applied for, phone number, email, work experience/projects undertaken, education, skills.
            - Providing responses in the form of a dictionary as follows:
            {info_format}
            - Do not use external knowledge beyond the information provided in the DOCUMENT. If information is not provided, write "null". If a field has no information, return the entire field as null.
            <|im_end|>
            <|im_start|> assistant
            """.strip()
    output = model_gemini.generate_content(
        prompt,
        generation_config=genai.types.GenerationConfig(
                                    candidate_count = 1,
                                    stop_sequences = ['<|im_end|>'],
                                    max_output_tokens = 2000,
                                    top_p = 0.9,
                                    top_k = 7,
                                    temperature = 0.1),
        safety_settings={
            HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
            HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
        },

    )
    try:
        parse_data = json.loads(output.text.replace("\n", ""))
        return parse_data
            
    except Exception as e:
            
        return {
            "http_code": status.HTTP_400_BAD_REQUEST,
            "message": str(e),
        }

'''

def push_data_to_DB(tenant_id): #Khi nào đổi flow sang lưu vào db thì dùng cái này
    conn = get_db(tenant_id)
    if conn is None:
        logging.error("Can't connect database")
    else:
        
        candidates = extract_pdf_info(tenant_id)

        if candidates is None: 
            logging.error("Tenant not found")
        else:

            cursor = conn.cursor()
            for candidate  in candidates:
                if "isFalse" not in candidate:
                    snippet = candidate["snippet"]
                    candidate_info = candidate["candidate_info"]
                    name = str(candidate_info["Name"])
                    phone_number = str(candidate_info["Phone_number"])
                    applied_position = str(candidate_info["Applied_position"])
                    email = str(candidate_info["Email"])
                    work_experience = str(candidate_info["Work_experience"])
                    projects = str(candidate_info["Projects"])
                    education = str(candidate_info["Education"])
                    technical_skills = str(candidate_info["Technical_skills"])
                    link_cv = candidate["link_cv"]
                    sql_query = "INSERT INTO candidate_info (name, email, phone_number, applied_position, work_experience, projects, educations, technical_skills, link_CV, reading_successfully, snippet) VALUES (%s, %s,  %s,%s, %s,%s, %s,%s, %s, %s, %s)"
                    cursor.execute(sql_query,(name, email, phone_number, applied_position, work_experience, projects, education, technical_skills, link_cv, True, snippet))
                    conn.commit()
                else: 
                    link_cv = candidate["link_cv"]
                    snippet = candidate["snippet"]
                    sql_query = "INSERT INTO candidate_info (link_cv, reading_successfully, snippet) VALUES (%s, %s, %s)"
                    cursor.execute(sql_query, (link_cv, False, snippet))
                    conn.commit()


'''