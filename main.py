import streamlit as st
from googleapiclient.discovery import build
from urllib.parse import urlparse, parse_qs
import re
import pandas as pd

st.set_page_config(
    page_title="YouTube 댓글 수집기",
    page_icon="🎬",
    layout="wide"
)

@st.cache_resource
def get_youtube_client():
    api_key = st.secrets["YOUTUBE_API_KEY"]
    return build("youtube", "v3", developerKey=api_key)

def extract_video_id(url: str):
    url = url.strip()
    short = re.match(r"(?:https?://)?youtu\.be/([A-Za-z0-9_-]{11})", url)
    if short:
        return short.group(1)
    parsed = urlparse(url)
    if "youtube.com" in parsed.netloc:
        qs = parse_qs(parsed.query)
        if "v" in qs:
            return qs["v"][0]
        shorts = re.match(r"/shorts/([A-Za-z0-9_-]{11})", parsed.path)
        if shorts:
            return shorts.group(1)
    if re.match(r"^[A-Za-z0-9_-]{11}$", url):
        return url
    return None

def get_video_info(youtube, video_id: str):
    try:
        response = youtube.videos().list(
            part="snippet,statistics",
            id=video_id
        ).execute()
        if not response["items"]:
            return None
        item = response["items"][0]
        snippet = item["snippet"]
        stats = item.get("statistics", {})
        return {
            "title": snippet.get("title", "제목 없음"),
            "channel": snippet.get("channelTitle", "채널 없음"),
            "published_at": snippet.get("publishedAt", "")[:10],
            "thumbnail": snippet["thumbnails"]["medium"]["url"],
            "view_count": int(stats.get("viewCount", 0)),
            "like_count": int(stats.get("likeCount", 0)),
            "comment_count": int(stats.get("commentCount", 0)),
        }
    except Exception as e:
        st.error(f"영상 정보를 가져오는 중 오류 발생: {e}")
        return None

def get_comments(youtube, video_id: str, max_comments: int = 100):
    comments = []
    next_page_token = None
    try:
        while len(comments) < max_comments:
            fetch_count = min(100, max_comments - len(comments))
            response = youtube.commentThreads().list(
                part="snippet",
                videoId=video_id,
                maxResults=fetch_count,
                pageToken=next_page_token,
                textFormat="plainText",
                order="relevance"
            ).execute()
            for item in response.get("items", []):
                top = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "작성자": top.get("authorDisplayName", "익명"),
                    "댓글 내용": top.get("textDisplay", ""),
                    "좋아요 수": top.get("likeCount", 0),
                    "답글 수": item["snippet"].get("totalReplyCount", 0),
                    "작성일": top.get("publishedAt", "")[:10],
                })
            next_page_token = response.get("nextPageToken")
            if not next_page_token:
                break
    except Exception as e:
        error_msg = str(e)
        if "commentsDisabled" in error_msg:
            st.warning("⚠️ 이 영상은 댓글이 비활성화되어 있습니다.")
        else:
            st.error(f"댓글을 가져오는 중 오류 발생: {e}")
    return comments

def main():
    st.title("🎬 YouTube 댓글 수집기")
    st.caption("YouTube 영상 링크를 입력하면 댓글을 불러옵니다.")
    st.divider()

    col1, col2 = st.columns([3, 1])
    with col1:
        url_input = st.text_input(
            "🔗 YouTube URL 또는 Video ID 입력",
            placeholder="https://www.youtube.com/watch?v=xxxxx",
        )
    with col2:
        max_comments = st.number_input(
            "📊 가져올 댓글 수",
            min_value=10,
            max_value=500,
            value=100,
            step=10
        )

    search_btn = st.button("🔍 댓글 불러오기", type="primary", use_container_width=True)

    if search_btn:
        if not url_input:
            st.warning("URL을 입력해주세요.")
            st.stop()

        video_id = extract_video_id(url_input)
        if not video_id:
            st.error("❌ 올바른 YouTube URL 또는 Video ID를 입력해주세요.")
            st.stop()

        youtube = get_youtube_client()

        with st.spinner("영상 정보를 불러오는 중..."):
            info = get_video_info(youtube, video_id)

        if info:
            st.subheader("📌 영상 정보")
            info_col1, info_col2 = st.columns([1, 2])
            with info_col1:
                st.image(info["thumbnail"], use_container_width=True)
            with info_col2:
                st.markdown(f"### {info['title']}")
                st.markdown(f"**채널:** {info['channel']}")
                st.markdown(f"**업로드 날짜:** {info['published_at']}")
                m1, m2, m3 = st.columns(3)
                m1.metric("👁️ 조회수", f"{info['view_count']:,}")
                m2.metric("👍 좋아요", f"{info['like_count']:,}")
                m3.metric("💬 댓글 수", f"{info['comment_count']:,}")
            st.divider()

        with st.spinner(f"댓글 최대 {max_comments}개를 불러오는 중..."):
            comments = get_comments(youtube, video_id, max_comments)

        if comments:
            st.subheader(f"💬 댓글 목록 (총 {len(comments)}개)")

            search_keyword = st.text_input(
                "🔎 댓글 내용 검색 (선택사항)",
                placeholder="검색할 키워드를 입력하세요"
            )
            sort_option = st.selectbox(
                "정렬 기준",
                options=["좋아요 수 (높은순)", "답글 수 (높은순)", "작성일 (최신순)", "기본 순서"]
            )

            df = pd.DataFrame(comments)

            if search_keyword:
                df = df[df["댓글 내용"].str.contains(search_keyword, case=False, na=False)]
                st.info(f"'{search_keyword}' 검색 결과: {len(df)}개")

            if sort_option == "좋아요 수 (높은순)":
                df = df.sort_values("좋아요 수", ascending=False)
            elif sort_option == "답글 수 (높은순)":
                df = df.sort_values("답글 수", ascending=False)
            elif sort_option == "작성일 (최신순)":
                df = df.sort_values("작성일", ascending=False)

            df = df.reset_index(drop=True)
            df.index += 1

            st.dataframe(
                df,
                use_container_width=True,
                height=500,
                column_config={
                    "댓글 내용": st.column_config.TextColumn(width="large"),
                    "좋아요 수": st.column_config.NumberColumn(format="%d 👍"),
                    "답글 수": st.column_config.NumberColumn(format="%d 💬"),
                }
            )

            csv = df.to_csv(index=False, encoding="utf-8-sig")
            st.download_button(
                label="📥 CSV로 다운로드",
                data=csv,
                file_name=f"youtube_comments_{video_id}.csv",
                mime="text/csv",
                use_container_width=True
            )
        else:
            st.info("불러온 댓글이 없습니다.")

    with st.expander("📖 사용 방법 안내"):
        st.markdown("""
        ### 지원하는 URL 형식
        | 형식 | 예시 |
        |------|------|
        | 일반 URL | `https://www.youtube.com/watch?v=dQw4w9WgXcQ` |
        | 단축 URL | `https://youtu.be/dQw4w9WgXcQ` |
        | Shorts | `https://www.youtube.com/shorts/VIDEO_ID` |
        | Video ID | `dQw4w9WgXcQ` |

        ### 주의사항
        - YouTube API는 하루 **10,000 유닛** 무료 할당량이 있습니다.
        - 댓글이 비활성화된 영상은 수집이 불가능합니다.
        """)

if __name__ == "__main__":
    main()
