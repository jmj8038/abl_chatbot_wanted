import time
import json
import requests
import streamlit as st

#API_BASE_URL = "http://localhost:8002/chat"
API_BASE_URL = 'https://a25d-34-68-237-148.ngrok-free.app/chat'
#st.title("ABL AI ChtBot")

contracts = ['주계약', '무배당 경도이상치매진단특약T(해약환급금 미지급형)',
       '무배당 중등도이상치매진단특약T(해약환급금 미지급형)',
       '무배당 중등도이상치매종신간병생활자금특약T(해약환급금 미지급형)',
       '무배당 중증치매종신간병생활자금특약T(해약환급금 미지급형)',
       '무배당 중증알츠하이머치매진단특약T(해약환급금 미지급형)', '무배당 특정파킨슨ㆍ루게릭진단특약T(해약환급금 미지급형)',
       '무배당 장기요양(1~2등급)재가급여종신지원특약(해약환급금 미지급형)',
       '무배당 장기요양(1~5등급)재가급여지원특약(해약환급금 미지급형)',
       '무배당 장기요양(1~2등급)시설급여종신지원특약(해약환급금 미지급형)',
       '무배당 장기요양(1~5등급)시설급여지원특약(해약환급금 미지급형)',
       '무배당 급여치매ㆍ뇌혈관질환검사비보장특약(해약환급금 미지급형)',
       '무배당 급여치매약물치료보장특약(해약환급금 미지급형)', '무배당 중증치매산정특례대상보장특약(해약환급금 미지급형)',
       '무배당 간병인사용지원치매입원보장특약(갱신형)', '지정대리청구서비스특약', '특정신체부위ㆍ질병보장제한부인수특약',
       '단체취급특약', '장애인전용보험전환특약']
    
# selected_contract = st.sidebar.selectbox("약관 종류를 선택하세요", contracts)
# print(selected_contract)
    
def request_chat_api(
    message: str,
    # model: str = "gpt-3.5-turbo",
    # max_tokens: int = 500,
    # temperature: float = 0.9,
    #terms: str
) -> str:
    param = {'user_message': message}
    resp = requests.post(
        API_BASE_URL,
        json=param
        # {
        #     #"message": message,
        #     # "model": model,
        #     # "max_tokens": max_tokens,
        #     # "temperature": temperature,
        #     #'terms': terms
        # },
    )
    #resp = resp.json()
    resp = json.loads(resp.content)
    resp = resp['message']
    # print("@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@", resp['message']['content'])
    
    return resp #["message"]['content'] #, resp["hyperlink"]


def init_session_state():
    st.title("ABL AI ChatBot(OpenAI GPT-4)")
    init_message = "안녕하세요. ABL AI ChatBot입니다. 무엇을 도와드릴까요?"
    # Initialize chat history
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": init_message}]
        #st.session_state.messages = []

    #Display chat messages from history on app rerun
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


def chat_main():
    init_session_state()
    
    # contracts = ['주계약', '무배당 경도이상치매진단특약T(해약환급금 미지급형)',
    #    '무배당 중등도이상치매진단특약T(해약환급금 미지급형)',
    #    '무배당 중등도이상치매종신간병생활자금특약T(해약환급금 미지급형)',
    #    '무배당 중증치매종신간병생활자금특약T(해약환급금 미지급형)',
    #    '무배당 중증알츠하이머치매진단특약T(해약환급금 미지급형)', '무배당 특정파킨슨ㆍ루게릭진단특약T(해약환급금 미지급형)',
    #    '무배당 장기요양(1~2등급)재가급여종신지원특약(해약환급금 미지급형)',
    #    '무배당 장기요양(1~5등급)재가급여지원특약(해약환급금 미지급형)',
    #    '무배당 장기요양(1~2등급)시설급여종신지원특약(해약환급금 미지급형)',
    #    '무배당 장기요양(1~5등급)시설급여지원특약(해약환급금 미지급형)',
    #    '무배당 급여치매ㆍ뇌혈관질환검사비보장특약(해약환급금 미지급형)',
    #    '무배당 급여치매약물치료보장특약(해약환급금 미지급형)', '무배당 중증치매산정특례대상보장특약(해약환급금 미지급형)',
    #    '무배당 간병인사용지원치매입원보장특약(갱신형)', '지정대리청구서비스특약', '특정신체부위ㆍ질병보장제한부인수특약',
    #    '단체취급특약', '장애인전용보험전환특약']
    
    # selected_contract = st.selectbox("계약종류를 선택하세요", contracts)
    # print(selected_contract)
    # init_message = "안녕하세요. ABL AI ChatBot입니다. 무엇을 도와드릴까요?"
    
    # if "messages" not in st.session_state.keys():
    #     st.session_state.messages = [{"role": "assistant", "content": init_message}]
    #     print(st.session_state.messages)
        
    if message := st.chat_input(""):
        st.session_state.messages.append({"role": "user", "content": message})
        #st.session_state.messages.append({"role": "assistant", "content": init_message})
        
        with st.chat_message("user"):
            st.markdown(message)

        #assistant_response, hlink = request_chat_api(message=message) #, terms=selected_contract)
        assistant_response = request_chat_api(message=message) #, terms=selected_contract)

        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            full_response = ""
            for lines in assistant_response.split("\n"):
                for chunk in lines.split():
                    full_response += chunk + " "
                    time.sleep(0.05)
                    # Add a blinking cursor to simulate typing
                    message_placeholder.markdown(full_response)
                full_response += "\n"
            full_response = full_response #+ "\n ----------------------참고 약관---------------------- \n\n" + hlink + "\n" #full_response.replace('  ', ' ')
            message_placeholder.markdown(full_response)

        # Add assistant response to chat history
        st.session_state.messages.append(
            {"role": "assistant", "content": full_response}
        )
        print(st.session_state.messages)
        


if __name__ == "__main__":
    chat_main()


# python -m streamlit run app.py
# uvicorn api:app --reload --port 8002