# OpenAI Streamlit 챗봇

`gpt-4o-mini`와 OpenAI Responses API를 사용하는 간단한 Streamlit 챗봇입니다. 답변은 스트리밍으로 표시되며, 현재 대화는 브라우저 세션 동안 유지됩니다.

## 로컬 실행

1. 의존성을 설치합니다.

   ```bash
   pip install -r requirements.txt
   ```

2. `.streamlit/secrets.toml` 파일을 만들고 API 키를 넣습니다. 이 파일은 Git에 올리지 마세요.

   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

3. 실행합니다.

   ```bash
   streamlit run app.py
   ```

## Streamlit Community Cloud 배포

1. 이 프로젝트를 GitHub 저장소에 올립니다. `secrets.toml`과 API 키는 절대로 커밋하지 마세요.
2. Streamlit Community Cloud에서 해당 저장소를 선택하고 메인 파일로 `app.py`를 지정합니다.
3. 앱 설정의 **Secrets**에 아래 내용을 추가한 뒤 저장합니다.

   ```toml
   OPENAI_API_KEY = "sk-..."
   ```

`requirements.txt`는 Cloud 배포 시 자동으로 설치됩니다.
