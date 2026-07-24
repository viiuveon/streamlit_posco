"""OpenAI gpt-4o-mini 기반 Streamlit 챗봇과 개인 도구."""

import calendar
from datetime import date

import streamlit as st
from openai import APIError, AuthenticationError, OpenAI


MODEL = "gpt-4o-mini"
SYSTEM_PROMPT = "당신은 친절하고 정확한 AI 어시스턴트입니다. 기본적으로 한국어로 답변하세요."


def get_client() -> OpenAI:
    """Streamlit Community Cloud secrets에서 API 키를 읽어 클라이언트를 만든다."""
    try:
        return OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except (KeyError, FileNotFoundError):
        st.error("OPENAI_API_KEY가 설정되지 않았습니다. Streamlit secrets를 확인해 주세요.")
        st.stop()


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


def render_calendar(selected_date: date) -> None:
    """선택된 날짜의 월간 달력을 Markdown 표로 표시한다."""
    month = calendar.Calendar(firstweekday=0).monthdayscalendar(
        selected_date.year, selected_date.month
    )
    rows = ["| 월 | 화 | 수 | 목 | 금 | 토 | 일 |", "| --- | --- | --- | --- | --- | --- | --- |"]
    for week in month:
        cells = []
        for day in week:
            if day == 0:
                cells.append("")
            elif day == selected_date.day:
                cells.append(f"**{day}**")
            else:
                cells.append(str(day))
        rows.append("| " + " | ".join(cells) + " |")
    st.markdown("\n".join(rows))


st.set_page_config(page_title="OpenAI 챗봇", page_icon="💬")
st.title("💬 OpenAI 챗봇")
st.caption(f"모델: `{MODEL}`")

if "messages" not in st.session_state:
    st.session_state.messages = []
if "saved_memo" not in st.session_state:
    st.session_state.saved_memo = ""
if "memo_draft" not in st.session_state:
    st.session_state.memo_draft = ""

with st.sidebar:
    st.subheader("대화 관리")
    if st.button("새 대화", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

chat_tab, memo_tab, calendar_tab = st.tabs(["💬 챗봇", "📝 메모", "📅 달력"])

with chat_tab:
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

with memo_tab:
    st.subheader("메모")
    st.caption("메모는 현재 브라우저 세션에 저장됩니다. 영구 보관하려면 다운로드하세요.")
    st.text_area("내용", height=260, key="memo_draft", placeholder="메모를 작성하세요.")
    save_col, download_col = st.columns(2)
    with save_col:
        if st.button("메모 저장", use_container_width=True):
            st.session_state.saved_memo = st.session_state.memo_draft
            st.success("메모를 저장했습니다.")
    with download_col:
        st.download_button(
            "텍스트 파일로 다운로드",
            data=st.session_state.saved_memo,
            file_name="memo.txt",
            mime="text/plain",
            use_container_width=True,
            disabled=not st.session_state.saved_memo,
        )

with calendar_tab:
    st.subheader("달력")
    selected_date = st.date_input("날짜 선택", value=date.today())
    st.write(f"선택한 날짜: **{selected_date:%Y년 %m월 %d일}**")
    render_calendar(selected_date)
