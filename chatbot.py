import streamlit as st
import pandas as pd
import io

# ✅ Streamlit UI 제목
st.title("💬 데이터 분석 챗봇")

# ✅ 세션 상태 초기화
if "messages" not in st.session_state:
    st.session_state.messages = []
if "task" not in st.session_state:
    st.session_state.task = None
if "string_column" not in st.session_state:
    st.session_state.string_column = None
if "target_column" not in st.session_state:
    st.session_state.target_column = None
if "file_uploaded" not in st.session_state:
    st.session_state.file_uploaded = False
if "df" not in st.session_state:
    st.session_state.df = None

def reset_session():
    """세션을 초기화하는 함수"""
    st.session_state.task = None
    st.session_state.string_column = None
    st.session_state.target_column = None
    st.session_state.file_uploaded = False
    st.session_state.df = None
    st.session_state.messages = []

# ✅ 사이드바 명령어 안내
st.sidebar.title("📜 사용 가능 명령어")
st.sidebar.write("- 중복 확인")

# ✅ 이전 대화 기록 표시 (채팅 UI)
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# ✅ 1. 사용자 작업 선택
# ✅ 1. 사용자 작업 선택
if st.session_state.task is None:
    user_task = st.chat_input("💬 어떤 작업을 도와드릴까요? (예: '중복 확인')")
    if user_task:
        if user_task.strip() == "중복 확인" or user_task.strip() == "중복확인":  # 수정된 조건
            st.session_state.task = user_task
            st.session_state.messages.append({"role": "user", "content": user_task})
            st.session_state.messages.append({"role": "assistant", "content": "🤖 중복 확인을 진행하겠습니다! 문자열로 읽을 열을 입력해주세요. (예: '이름' 또는 '주소')"})
        else:
            st.session_state.messages.append({"role": "assistant", "content": "🤖 죄송하지만 '중복 확인'만 지원됩니다. 다시 입력해주세요!"})
        st.rerun()

# ✅ 2. 문자열로 읽을 열 선택
if st.session_state.task == "중복 확인" and st.session_state.string_column is None:
    user_column = st.chat_input("🔤 문자열로 읽을 열을 입력하세요...")
    if user_column:
        st.session_state.string_column = user_column
        st.session_state.messages.append({"role": "user", "content": user_column})
        st.session_state.messages.append({"role": "assistant", "content": f"📂 '{user_column}' 열을 문자열로 변환합니다. 이제 파일을 업로드해주세요!"})
        st.rerun()

if st.session_state.task == "중복확인" and st.session_state.string_column is None:
    user_column = st.chat_input("🔤 문자열로 읽을 열을 입력하세요...")
    if user_column:
        st.session_state.string_column = user_column
        st.session_state.messages.append({"role": "user", "content": user_column})
        st.session_state.messages.append({"role": "assistant", "content": f"📂 '{user_column}' 열을 문자열로 변환합니다. 이제 파일을 업로드해주세요!"})
        st.rerun()


if st.session_state.string_column and not st.session_state.file_uploaded:
    upload_file = st.file_uploader("📂 CSV 또는 Excel 파일을 업로드하세요!", type=['csv', 'xlsx'])
    if upload_file is not None:
        if upload_file.name.endswith('.csv'):
            df = pd.read_csv(upload_file, dtype={st.session_state.string_column: str}, low_memory=False)
        elif upload_file.name.endswith('.xlsx'):
            df = pd.read_excel(upload_file, dtype={st.session_state.string_column: str})
        
        # ✅ 세션 상태 업데이트
        st.session_state.df = df
        st.session_state.file_uploaded = True
        st.session_state.messages.append({"role": "assistant", "content": "✅ 파일이 업로드되었습니다! 중복 확인할 열을 입력해주세요."})
        
        st.rerun()  # 🔄 리렌더링

# ✅ 4. 업로드된 파일 확인
if st.session_state.df is not None:
    with st.chat_message("assistant"):
        st.write("📊 업로드된 데이터 미리보기:")
        st.dataframe(st.session_state.df.head(5))  # 데이터프레임 상위 5개 행 출력
        

if st.session_state.df is not None and st.session_state.target_column is None:
    user_target_column = st.chat_input("🔍 중복 확인할 열을 입력하세요...")

    if user_target_column:
        # ✅ 입력한 열이 데이터프레임에 존재하는지 확인
        if user_target_column not in st.session_state.df.columns:
            st.warning(f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 다시 입력해주세요!")
            st.session_state.messages.append({
                "role": "assistant", 
                "content": f"⚠️ '{user_target_column}' 열이 데이터에 없습니다. 가능한 열: {', '.join(st.session_state.df.columns)}"
            })
        else:
            st.session_state.target_column = user_target_column
            st.session_state.messages.append({"role": "user", "content": user_target_column})
            st.session_state.messages.append({"role": "assistant", "content": f"⏳ '{user_target_column}' 열에서 중복을 확인 중입니다. 잠시만 기다려주세요!"})
            st.rerun()



# ✅ 5. 중복 확인 실행 및 결과 출력
if st.session_state.df is not None and st.session_state.target_column:
    df = st.session_state.df.copy()
    df['중복_횟수'] = df[st.session_state.target_column].map(df[st.session_state.target_column].value_counts())
    df['등장_순서'] = df.groupby(st.session_state.target_column).cumcount() + 1

    # ✅ 결과 메시지 추가
    st.session_state.messages.append({"role": "assistant", "content": "✅ 중복 확인이 완료되었습니다! 아래에서 결과를 확인하세요."})
    
    # ✅ 채팅 형식으로 출력
    with st.chat_message("assistant"):
        st.write(df)

    # ✅ CSV 다운로드 버튼 추가
    csv_file = io.BytesIO()
    df.to_csv(csv_file, index=False, encoding='utf-8-sig')
    csv_file.seek(0)

    st.download_button(
        label="📥 중복 확인 결과 다운로드",
        data=csv_file,
        file_name="중복_확인_결과.csv",
        mime="text/csv"
    )

    # ✅ 다시 시작 버튼 추가
    if st.button("🔄 다시 시작"):
        reset_session()
        st.rerun()
