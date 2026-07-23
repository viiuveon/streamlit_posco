"""OpenAI gpt-4o-mini 기반 Streamlit 챗봇."""

import streamlit as st
from openai import OpenAI, APIError, AuthenticationError


MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "당신은 친절하고 정확한 AI 어시스턴트입니다. 기본적으로 한국어로 답변하세요."


def get_client() -> OpenAI:
    """Streamlit Community Cloud secrets에서 API 키를 읽어 클라이언트를 만든다."""
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except (KeyError, FileNotFoundError) as error:
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. Streamlit secrets를 확인해 주세요.")
        st.stop()
        raise error  # st.stop() 이후의 타입 검사기를 위한 코드

    return OpenAI(api_key=api_key)


def response_stream(client: OpenAI, messages: list[dict[str, str]]):
    """Responses API의 텍스트 델타를 Streamlit에 전달한다."""
    stream = client.responses.create(
        model=MODEL,
        instructions=SYSTEM_PROMPT,
        input=messages,
        stream=True,
    )
    for event in stream:
        if event.type == "response.output_text.delta":
            yield event.delta


st.set_page_config(page_title="OpenAI 챗봇", page_icon="💬")
st.title("💬 OpenAI 챗봇")
st.caption(f"모델: `{MODEL}`")

if "messages" not in st.session_state:
    st.session_state.messages = []

with st.sidebar:
    st.subheader("대화 관리")
    if st.button("새 대화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

if prompt := st.chat_input("메시지를 입력하세요"):
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            answer = st.write_stream(response_stream(get_client(), st.session_state.messages))
        except AuthenticationError:
            st.error("API 키를 확인해 주세요.")
            answer = None
        except APIError as error:
            st.error(f"OpenAI API 요청 중 오류가 발생했습니다: {error}")
            answer = None

    if answer:
        st.session_state.messages.append({"role": "assistant", "content": answer})
