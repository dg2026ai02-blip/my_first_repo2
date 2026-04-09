import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import re
from openai import OpenAI

# ─────────────────────────────────────────────
# 페이지 기본 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="YouTube 댓글 수집기",
    page_icon="🎬",
    layout="wide"
)

# ─────────────────────────────────────────────
# 💙 커스텀 CSS (파란색 테마)
# ─────────────────────────────────────────────
st.markdown("""
<style>
    /* 전체 배경 */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #0d1b4b 50%, #0a1628 100%);
        color: #e8f4fd;
    }

    /* 메인 타이틀 */
    .main-title {
        text-align: center;
        font-size: 3rem;
        font-weight: 900;
        background: linear-gradient(90deg, #4fc3f7, #1e88e5, #7c4dff);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0.3rem;
        text-shadow: none;
    }

    .sub-title {
        text-align: center;
        color: #90caf9;
        font-size: 1.1rem;
        margin-bottom: 2rem;
    }

    /* 카드 스타일 */
    .card {
        background: linear-gradient(145deg, #0d2137, #112244);
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 1.5rem;
        margin: 1rem 0;
        box-shadow: 0 4px 20px rgba(30, 136, 229, 0.15);
    }

    /* 요약 카드 */
    .summary-card {
        background: linear-gradient(145deg, #0d1f3c, #0a2d5a);
        border: 1px solid #1565c0;
        border-left: 4px solid #42a5f5;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        margin: 0.7rem 0;
        box-shadow: 0 2px 15px rgba(66, 165, 245, 0.1);
        transition: transform 0.2s;
    }

    .summary-card:hover {
        transform: translateX(5px);
        border-left-color: #1e88e5;
    }

    .summary-number {
        font-size: 1.5rem;
        font-weight: 800;
        color: #42a5f5;
        margin-right: 0.5rem;
    }

    .summary-topic {
        font-size: 1.1rem;
        font-weight: 700;
        color: #90caf9;
    }

    .summary-content {
        font-size: 0.95rem;
        color: #b3d9f7;
        margin-top: 0.5rem;
        line-height: 1.6;
    }

    /* TOP5 댓글 카드 */
    .top-comment-card {
        background: linear-gradient(145deg, #0a1f3c, #0c2a50);
        border: 1px solid #1e3f6e;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        margin: 0.5rem 0;
        box-shadow: 0 2px 10px rgba(30, 136, 229, 0.1);
    }

    /* 섹션 헤더 */
    .section-header {
        font-size: 1.4rem;
        font-weight: 800;
        color: #64b5f6;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1565c0;
    }

    /* 메트릭 카드 커스텀 */
    [data-testid="stMetric"] {
        background: linear-gradient(145deg, #0d2137, #112244);
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 10px rgba(30, 136, 229, 0.1);
    }

    [data-testid="stMetricValue"] {
        color: #42a5f5 !important;
        font-weight: 800;
    }

    [data-testid="stMetricLabel"] {
        color: #90caf9 !important;
    }

    /* 입력창 */
    .stTextInput > div > div > input {
        background-color: #0d1b3e !important;
        border: 1.5px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #e8f4fd !important;
        padding: 0.7rem 1rem !important;
    }

    .stTextInput > div > div > input:focus {
        border-color: #42a5f5 !important;
        box-shadow: 0 0 0 2px rgba(66, 165, 245, 0.2) !important;
    }

    /* 버튼 */
    .stButton > button {
        background: linear-gradient(90deg, #1565c0, #1e88e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
        font-size: 1rem !important;
        padding: 0.7rem 2rem !important;
        transition: all 0.3s !important;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.3) !important;
    }

    .stButton > button:hover {
        background: linear-gradient(90deg, #1976d2, #42a5f5) !important;
        box-shadow: 0 6px 20px rgba(66, 165, 245, 0.4) !important;
        transform: translateY(-2px) !important;
    }

    /* 다운로드 버튼 */
    .stDownloadButton > button {
        background: linear-gradient(90deg, #0d47a1, #1565c0) !important;
        color: white !important;
        border: 1px solid #1e88e5 !important;
        border-radius: 10px !important;
        font-weight: 700 !important;
    }

    /* 라디오 버튼 */
    .stRadio > div {
        background: transparent !important;
        color: #90caf9 !important;
    }

    /* 셀렉트박스 */
    .stSelectbox > div > div {
        background-color: #0d1b3e !important;
        border: 1.5px solid #1e3a5f !important;
        border-radius: 10px !important;
        color: #e8f4fd !important;
    }

    /* 넘버 인풋 */
    .stNumberInput > div > div > input {
        background-color: #0d1b3e !important;
        border: 1.5px solid #1e3a5f !important;
        color: #e8f4fd !important;
        border-radius: 10px !important;
    }

    /* 데이터프레임 */
    .stDataFrame {
        border: 1px solid #1e3a5f !important;
        border-radius: 12px !important;
        overflow: hidden !important;
    }

    /* divider */
    hr {
        border-color: #1e3a5f !important;
        margin: 1.5rem 0 !important;
    }

    /* 알림창 */
    .stAlert {
        border-radius: 10px !important;
    }

    /* 스피너 */
    .stSpinner > div {
        border-top-color: #42a5f5 !important;
    }

    /* 이미지 */
    .thumbnail-img {
        border-radius: 12px;
        border: 2px solid #1e3a5f;
        box-shadow: 0 4px 15px rgba(30, 136, 229, 0.2);
    }

    /* 푸터 */
    .footer {
        text-align: center;
        color: #546e7a;
        font-size: 0.85rem;
        padding: 1rem 0;
    }

    /* 뱃지 */
    .badge {
        display: inline-block;
        background: linear-gradient(90deg, #1565c0, #1e88e5);
        color: white;
        border-radius: 20px;
        padding: 0.2rem 0.8rem;
        font-size: 0.8rem;
        font-weight: 700;
        margin-right: 0.5rem;
    }

    /* 스크롤바 */
    ::-webkit-scrollbar {
        width: 6px;
    }
    ::-webkit-scrollbar-track {
        background: #0a0e27;
    }
    ::-webkit-scrollbar-thumb {
        background: #1565c0;
        border-radius: 3px;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# API 키 불러오기
# ─────────────────────────────────────────────
try:
    YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]
except Exception:
    st.error("⚠️ YouTube API 키가 설정되지 않았습니다. `.streamlit/secrets.toml`을 확인해주세요.")
    st.stop()

try:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
    openai_client = OpenAI(api_key=OPENAI_API_KEY)
    OPENAI_AVAILABLE = True
except Exception:
    OPENAI_AVAILABLE = False

# ─────────────────────────────────────────────
# 유튜브 영상 ID 추출 함수
# ─────────────────────────────────────────────
def extract_video_id(url: str):
    patterns = [
        r"(?:v=)([0-9A-Za-z_-]{11})",
        r"(?:youtu\.be/)([0-9A-Za-z_-]{11})",
        r"(?:shorts/)([0-9A-Za-z_-]{11})"
    ]
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    return None

# ─────────────────────────────────────────────
# 영상 정보 가져오기 함수
# ─────────────────────────────────────────────
def get_video_info(youtube, video_id: str) -> dict:
    request = youtube.videos().list(
        part="snippet,statistics",
        id=video_id
    )
    response = request.execute()

    if not response["items"]:
        return {}

    item = response["items"][0]
    snippet = item["snippet"]
    stats = item.get("statistics", {})

    return {
        "제목": snippet.get("title", "알 수 없음"),
        "채널명": snippet.get("channelTitle", "알 수 없음"),
        "조회수": int(stats.get("viewCount", 0)),
        "좋아요수": int(stats.get("likeCount", 0)),
        "댓글수": int(stats.get("commentCount", 0)),
        "썸네일": snippet["thumbnails"]["medium"]["url"]
    }

# ─────────────────────────────────────────────
# 댓글 수집 함수
# ─────────────────────────────────────────────
def get_comments(youtube, video_id: str, max_comments: int = 100, order: str = "relevance") -> list:
    comments = []
    next_page_token = None

    while len(comments) < max_comments:
        fetch_count = min(100, max_comments - len(comments))

        try:
            request = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=fetch_count,
                pageToken=next_page_token,
                textFormat="plainText",
                order=order
            )
            response = request.execute()
        except Exception as e:
            st.warning(f"댓글을 불러오는 중 오류 발생: {e}")
            break

        for item in response.get("items", []):
            top_comment = item["snippet"]["topLevelComment"]["snippet"]
            comments.append({
                "작성자": top_comment.get("authorDisplayName", "알 수 없음"),
                "댓글 내용": top_comment.get("textDisplay", ""),
                "좋아요수": top_comment.get("likeCount", 0),
                "작성일": top_comment.get("publishedAt", "")[:10],
                "답글수": item["snippet"].get("totalReplyCount", 0)
            })

        next_page_token = response.get("nextPageToken")
        if not next_page_token:
            break

    return comments

# ─────────────────────────────────────────────
# 댓글 주제 요약 함수 (OpenAI GPT)
# ─────────────────────────────────────────────
def summarize_comments_by_topic(comments: list) -> str:
    # 댓글 최대 200개만 사용 (토큰 절약)
    sample_comments = [c["댓글 내용"] for c in comments[:200]]
    comments_text = "\n".join([f"- {c}" for c in sample_comments])

    prompt = f"""
아래는 유튜브 영상에 달린 댓글들입니다.
이 댓글들을 분석하여 주요 반응을 정확히 5가지 큰 주제로 나누어 요약해주세요.

각 주제는 반드시 아래 형식으로 작성해주세요:
[주제 번호]. [주제 제목 (10자 이내)] | [해당 주제에 대한 댓글 반응 요약 2~3문장]

예시:
1. 영상 퀄리티 칭찬 | 많은 시청자들이 편집 퀄리티와 영상 구성에 감탄하고 있습니다. 특히 자막과 BGM 선택이 좋다는 반응이 많습니다.

댓글 목록:
{comments_text}

반드시 5가지 주제만 작성하고, 위 형식을 정확히 지켜주세요.
"""

    response = openai_client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "당신은 유튜브 댓글을 분석하는 전문가입니다. 한국어로 답변하세요."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=1000,
        temperature=0.5
    )

    return response.choices[0].message.content

# ─────────────────────────────────────────────
# 요약 결과 파싱 함수
# ─────────────────────────────────────────────
def parse_summary(summary_text: str) -> list:
    """
    GPT 결과를 파싱하여 리스트로 반환
    형식: [{"number": "1", "topic": "주제", "content": "내용"}, ...]
    """
    results = []
    lines = summary_text.strip().split("\n")

    for line in lines:
        line = line.strip()
        if not line:
            continue
        # "1. 주제 제목 | 내용" 형태 파싱
        match = re.match(r"^(\d+)\.\s*(.+?)\s*\|\s*(.+)$", line)
        if match:
            results.append({
                "number": match.group(1),
                "topic": match.group(2).strip(),
                "content": match.group(3).strip()
            })

    return results

# ─────────────────────────────────────────────
# 메인 UI
# ─────────────────────────────────────────────

# 타이틀
st.markdown('<h1 class="main-title">🎬 YouTube 댓글 수집기</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">유튜브 링크를 입력하면 댓글을 수집하고, AI가 반응을 분석해드립니다 ✨</p>', unsafe_allow_html=True)

st.divider()

# ── 입력 영역 ──
st.markdown('<div class="section-header">⚙️ 설정</div>', unsafe_allow_html=True)

col1, col2 = st.columns([3, 1])

with col1:
    url_input = st.text_input(
        "🔗 YouTube 영상 URL",
        placeholder="https://www.youtube.com/watch?v=...",
        label_visibility="visible"
    )

with col2:
    max_comments = st.number_input(
        "📊 수집할 댓글 수",
        min_value=10,
        max_value=500,
        value=100,
        step=10
    )

col3, col4 = st.columns([1, 2])

with col3:
    sort_option = st.radio(
        "🔃 정렬 기준",
        options=["인기순", "최신순"],
        horizontal=True
    )

with col4:
    search_keyword = st.text_input(
        "🔍 키워드 필터 (선택)",
        placeholder="특정 단어로 필터링"
    )

use_ai_summary = st.toggle(
    "🤖 AI 댓글 반응 요약 사용 (OpenAI GPT 필요)",
    value=True if OPENAI_AVAILABLE else False,
    disabled=not OPENAI_AVAILABLE,
    help="OpenAI API 키가 secrets에 등록되어 있어야 합니다."
)

if not OPENAI_AVAILABLE:
    st.info("💡 OpenAI API 키를 secrets에 추가하면 AI 댓글 요약 기능을 사용할 수 있습니다.")

st.divider()

# ── 수집 버튼 ──
start_btn = st.button("🚀 댓글 수집 시작", use_container_width=True, type="primary")

if start_btn:

    if not url_input:
        st.warning("⚠️ URL을 입력해주세요!")
        st.stop()

    video_id = extract_video_id(url_input)

    if not video_id:
        st.error("❌ 올바른 YouTube URL이 아닙니다. 다시 확인해주세요.")
        st.stop()

    youtube = build("youtube", "v3", developerKey=YOUTUBE_API_KEY)

    # ── 영상 정보 ──
    with st.spinner("🔍 영상 정보를 불러오는 중..."):
        video_info = get_video_info(youtube, video_id)

    if not video_info:
        st.error("❌ 영상 정보를 찾을 수 없습니다.")
        st.stop()

    st.markdown('<div class="section-header">📋 영상 정보</div>', unsafe_allow_html=True)

    info_col1, info_col2 = st.columns([1, 3])

    with info_col1:
        st.image(video_info["썸네일"], use_container_width=True)

    with info_col2:
        st.markdown(f"### 🎬 {video_info['제목']}")
        st.markdown(f"<span class='badge'>📺 채널</span> **{video_info['채널명']}**", unsafe_allow_html=True)
        st.markdown("")
        m1, m2, m3 = st.columns(3)
        m1.metric("👁️ 조회수", f"{video_info['조회수']:,}")
        m2.metric("👍 좋아요", f"{video_info['좋아요수']:,}")
        m3.metric("💬 전체 댓글", f"{video_info['댓글수']:,}")

    st.divider()

    # ── 댓글 수집 ──
    order = "relevance" if sort_option == "인기순" else "time"

    with st.spinner(f"💬 댓글 수집 중... (최대 {max_comments}개)"):
        comments = get_comments(youtube, video_id, max_comments=max_comments, order=order)

    if not comments:
        st.warning("⚠️ 댓글을 불러올 수 없습니다. (댓글이 비활성화된 영상일 수 있습니다.)")
        st.stop()

    df = pd.DataFrame(comments)

    # 키워드 필터링
    if search_keyword:
        df = df[df["댓글 내용"].str.contains(search_keyword, case=False, na=False)]
        st.info(f"🔍 **'{search_keyword}'** 키워드 포함 댓글: **{len(df)}개**")

    # ── AI 댓글 반응 요약 ──
    if use_ai_summary and OPENAI_AVAILABLE and len(df) > 0:
        st.markdown('<div class="section-header">🤖 AI 댓글 반응 요약</div>', unsafe_allow_html=True)

        with st.spinner("🧠 AI가 댓글을 분석하는 중... 잠시만 기다려주세요!"):
            try:
                summary_raw = summarize_comments_by_topic(df.to_dict("records"))
                parsed_summary = parse_summary(summary_raw)

                if parsed_summary:
                    st.markdown("**💡 수집된 댓글에서 발견한 5가지 주요 반응 주제:**")
                    st.markdown("")

                    for item in parsed_summary:
                        st.markdown(f"""
<div class="summary-card">
    <span class="summary-number">#{item['number']}</span>
    <span class="summary-topic">{item['topic']}</span>
    <div class="summary-content">{item['content']}</div>
</div>
""", unsafe_allow_html=True)

                else:
                    # 파싱 실패 시 원문 출력
                    st.markdown(f"""
<div class="card">
{summary_raw}
</div>
""", unsafe_allow_html=True)

            except Exception as e:
                st.error(f"❌ AI 요약 중 오류가 발생했습니다: {e}")

        st.divider()

    # ── 통계 요약 ──
    st.markdown('<div class="section-header">📊 댓글 통계</div>', unsafe_allow_html=True)

    s1, s2, s3, s4 = st.columns(4)
    s1.metric("📝 수집된 댓글", f"{len(df)}개")
    s2.metric("❤️ 평균 좋아요", f"{df['좋아요수'].mean():.1f}")
    s3.metric("🏆 최고 좋아요", f"{df['좋아요수'].max()}")
    s4.metric("💬 총 답글수", f"{df['답글수'].sum():,}")

    st.divider()

    # ── 좋아요 TOP 5 ──
    st.markdown('<div class="section-header">🏆 좋아요 TOP 5 댓글</div>', unsafe_allow_html=True)

    top5 = df.nlargest(5, "좋아요수").reset_index(drop=True)

    for i, row in top5.iterrows():
        st.markdown(f"""
<div class="top-comment-card">
    <span class="badge">#{i+1}</span>
    <span style="color:#42a5f5; font-weight:700;">👍 {row['좋아요수']:,}</span>
    <span style="color:#78909c; margin-left:1rem; font-size:0.85rem;">@{row['작성자']} · {row['작성일']}</span>
    <div style="margin-top:0.6rem; color:#e3f2fd; line-height:1.6;">{row['댓글 내용']}</div>
</div>
""", unsafe_allow_html=True)

    st.divider()

    # ── 전체 댓글 목록 ──
    st.markdown('<div class="section-header">📝 전체 댓글 목록</div>', unsafe_allow_html=True)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "댓글 내용": st.column_config.TextColumn("💬 댓글 내용", width="large"),
            "좋아요수": st.column_config.NumberColumn("👍 좋아요", format="%d"),
            "답글수": st.column_config.NumberColumn("💬 답글", format="%d"),
            "작성자": st.column_config.TextColumn("👤 작성자"),
            "작성일": st.column_config.TextColumn("📅 작성일"),
        }
    )

    st.divider()

    # ── CSV 다운로드 ──
    csv_data = df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="⬇️ CSV 파일로 다운로드",
        data=csv_data,
        file_name=f"youtube_comments_{video_id}.csv",
        mime="text/csv",
        use_container_width=True
    )

# ─────────────────────────────────────────────
# 푸터
# ─────────────────────────────────────────────
st.divider()
st.markdown("""
<div class="footer">
    ⚠️ YouTube Data API v3 일일 할당량(10,000 units) 초과 시 오류가 발생할 수 있습니다.<br>
    🔑 OpenAI API는 유료 서비스입니다. 사용량에 따라 요금이 부과될 수 있습니다.<br><br>
    🎬 YouTube 댓글 수집기 | Made with Streamlit 💙
</div>
""", unsafe_allow_html=True)
