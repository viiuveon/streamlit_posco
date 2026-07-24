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


def calendar_html(today: date) -> str:
    """오늘을 빨간 원으로 강조한 작은 월간 달력 HTML을 만든다."""
    weeks = calendar.Calendar(firstweekday=0).monthdayscalendar(today.year, today.month)
    rows = []
    for week in weeks:
        cells = []
        for day in week:
            content = "" if day == 0 else str(day)
            style = " today" if day == today.day else ""
            cells.append(f'<td><span class="calendar-day{style}">{content}</span></td>')
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return f"""
    <style>
      .mini-calendar {{ width: 100%; border-collapse: collapse; text-align: center; font-size: 0.78rem; }}
      .mini-calendar th {{ color: #6b7280; font-weight: 600; padding: 0.18rem 0; }}
      .mini-calendar td {{ height: 1.7rem; }}
      .calendar-day {{ display: inline-flex; width: 1.55rem; height: 1.55rem; align-items: center;
        justify-content: center; border-radius: 50%; }}
      .calendar-day.today {{ background: #e53935; color: white; font-weight: 700; }}
    </style>
    <div style="text-align:center; font-weight:600; margin:0.2rem 0 0.35rem;">{today:%Y년 %m월}</div>
    <table class="mini-calendar">
      <thead><tr><th>월</th><th>화</th><th>수</th><th>목</th><th>금</th><th>토</th><th>일</th></tr></thead>
      <tbody>{''.join(rows)}</tbody>
    </table>
    """


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
    st.divider()
    st.subheader("📅 달력")
    st.markdown(calendar_html(date.today()), unsafe_allow_html=True)

chat_tab, memo_tab = st.tabs(["💬 챗봇", "📝 메모"])

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
