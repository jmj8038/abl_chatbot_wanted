import time
import json
import requests
import streamlit as st

import os
import io
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from googleapiclient.errors import HttpError
import fitz

#API_BASE_URL = "http://localhost:8002/chat"
API_BASE_URL = 'https://014e-34-135-181-190.ngrok-free.app/chat'
#st.title("ABL AI ChtBot")
    
# selected_contract = st.sidebar.selectbox("약관 종류를 선택하세요", contracts)
# print(selected_contract)


def request_chat_api(
    message: str,
    model: str,
    # max_tokens: int = 500,
    # temperature: float = 0.9,
    #terms: str
) -> str:
    
    print("@@@@@@@@@@@@@@@@", message)
    param = {'content': message, 'model': model}
    resp = requests.post(
        API_BASE_URL,
        json=param
    )
    resp = resp.json()
    print("----------------------", resp)
    
    return resp #["message"]['content'] #, resp["hyperlink"]

 #OAuth 2.0 인증 및 Google Drive API 클라이언트 설정
def get_drive_service():
    # 환경 변수에서 서비스 계정 키 정보 가져오기
    try:
        # 환경 변수에서 서비스 계정 키 정보 가져오기
        service_account_info = st.secrets["gcp_service_account"]
        credentials = service_account.Credentials.from_service_account_info(service_account_info)
        service = build('drive', 'v3', credentials=credentials)
        return service
    except KeyError as e:
        st.error(f"비밀 정보를 찾을 수 없습니다. {e}")
        return None


def download_pdf_from_gdrive(file_id):
    try:
        service = get_drive_service()
        if service is None:
            return None
        request = service.files().get_media(fileId=file_id)
        file_handle = io.BytesIO()
        downloader = MediaIoBaseDownload(file_handle, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print("Download status: ", status)
        file_handle.seek(0)
        return file_handle
    except HttpError as error:
        st.error(f"An error occurred: {error}")
        return None


# PDF를 페이지별로 이미지를 생성하여 보여주는 함수
# def display_pdf(file_handle, page_num):
#     try:
#         print("========================\n\n")
#         print(page_num)
#         print("========================\n\n")
#         page_num = int(page_num)-1
#         pdf_document = fitz.open(stream=file_handle, filetype="pdf")
#         if 0 <= page_num < len(pdf_document):
#             page = pdf_document.load_page(page_num)
#             pix = page.get_pixmap()
#             img = pix.tobytes("png")
#             st.image(img)
#         else:
#             st.warning(f"페이지 번호 {page_num}가 유효하지 않습니다.")
#     except Exception as e:
#         st.error(f"PDF를 표시할 수 없습니다: {e}")

def display_pdf(file_handle, page_nums):
    try:
        print("==========", page_nums)
        page_nums.sort()
        pdf_document = fitz.open(stream=file_handle, filetype="pdf")
        
        # page_nums는 1 기반이므로 이를 0 기반으로 변경
        page_nums = [int(pn) - 1 for pn in page_nums]

        for page_num in page_nums:
            print("========================\n\n")
            print(page_num + 1)  # 1 기반으로 표시
            print("========================\n\n")
            
            if 0 <= page_num < len(pdf_document):
                page = pdf_document.load_page(page_num)
                pix = page.get_pixmap()
                img = pix.tobytes("png")
                st.image(img)
            else:
                st.warning(f"페이지 번호 {page_num + 1}가 유효하지 않습니다.")
    except Exception as e:
        st.error(f"PDF를 표시할 수 없습니다: {e}")

# 대화 상태 초기화 함수
def init_session_state():
    init_message = """안녕하세요. 저는 ABL 생명 인사팀에 근무하는 복리후생 챗봇입니다. 
    현재 개발 중이라서 답변이 정확하지 않을 수도 있습니다. 아래 채팅창에 궁금한 내용을 입력해주세요. 
    그리고 오른쪽에 있는 PDF 뷰어에서 참고 문서를 확인할 수 있습니다.
    좀 더 정확한 답변을 드리기 위해 노력하겠습니다. 감사합니다. 

    가급적 자세히 질문해주시면 더 정확한 답변을 드릴 수 있습니다.
    """
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": init_message}]
    if "page_num" not in st.session_state:
        st.session_state.page_num = [1]


def chat_main():
    
    # 메인 레이아웃 설정
    st.set_page_config(layout="wide")
    init_session_state()

    # 스타일 추가
    st.markdown(
        """
        <style>
        .chat-container {
            height: 500px;
            overflow-y: auto;
            border: 1px solid #ccc;
            padding: 10px;
            background-color: white;
            margin-bottom: 10px;
        }
        .chat-input {
            position: fixed;
            bottom: 10px;
            left: 20px;
            right: 20px;
            margin: 0 auto;
            z-index: 1;
            background-color: white;
            padding: 10px;
            border-top: 1px solid #ccc;
        }
        </style>
        """, 
        unsafe_allow_html=True
    )

    #select_col, 
    left_col, right_col = st.columns(2)
    # with select_col:
    #     option = st.selectbox(
    #     "How would you like to be contacted?",
    #     ("Email", "Home phone", "Mobile phone"),
    #     label_visibility=st.session_state.visibility,
    #     #disabled=st.session_state.disabled,
    # )
    # 왼쪽 컬럼: 채팅 인터페이스
    with left_col:
        st.title("ABL AI ChatBot")
        models = ["GPT-4", 'HCX-1']
    
        selected_model = st.sidebar.selectbox("모델을 선택하세요", models)

        # st.markdown('<div class="left-col-container">', unsafe_allow_html=True)
        # st.markdown('<div class="chat-container-wrapper">', unsafe_allow_html=True)
        chat_container = st.empty()
        with chat_container.container():
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        # st.markdown('</div>', unsafe_allow_html=True)

        #if message := st.chat_input("메시지를 입력하세요..."):
        
        # 메시지 입력창
        #st.markdown('<div class="chat-input-wrapper">', unsafe_allow_html=True)
        #user_input = st.chat_input("메시지를 입력하세요...", key="chat_input")#, placeholder="Type a message", label_visibility="collapsed")
        #st.markdown('</div>', unsafe_allow_html=True)
        
        if message := st.chat_input(""): #user_input:
            st.session_state.messages.append({"role": "user", "content": message})
            
            with st.chat_message("user"):
                st.markdown(message)

            #assistant_response, hlink = request_chat_api(message=message) #, terms=selected_contract)
            assistant_response = request_chat_api(message=message, model=selected_model) 
            #, terms=selected_contract)
            
            page_num = assistant_response['pages']
            st.session_state.page_num = page_num  # 페이지 번호를 세션 상태에 저장


            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                full_response = ""
                for lines in assistant_response['content'].split("\n"):
                    for chunk in lines.split():
                        full_response += chunk + " "
                        time.sleep(0.05)
                        # Add a blinking cursor to simulate typing
                        message_placeholder.markdown(full_response)
                    full_response += "\n"
                #full_response = full_response #+ "\n ----------------------참고 약관---------------------- \n\n" + hlink + "\n" #full_response.replace('  ', ' ')
                message_placeholder.markdown(full_response)

            # Add assistant response to chat history
            st.session_state.messages.append(
                {"role": "assistant", "content": full_response}
            )
            # print(st.session_state.messages)
        # st.markdown('</div>', unsafe_allow_html=True)  # close chat-input-wrapper
        # st.markdown('</div>', unsafe_allow_html=True)  # close left-col-container

    # 오른쪽 컬럼: PDF 뷰어
    with right_col:
        st.header("Reference Document")
        file_id = "1Gkd7NYYju-Mqy2wNbR1A5OaQAQHTSBsH"  # Google Drive 파일 ID
        
        if file_id:
            file_handle = download_pdf_from_gdrive(file_id)
            if file_handle:
                display_pdf(file_handle, st.session_state.page_num)
        else:
            st.warning("No file ID provided")   


if __name__ == "__main__":
    chat_main()


# python -m streamlit run app.py
# uvicorn api:app --reload --port 8002
