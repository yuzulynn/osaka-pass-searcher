import streamlit as st # Streamlit 라이브러리 임포트
import sqlite3
import pandas as pd # 데이터를 보기 좋게 표시하기 위해 pandas 임포트

# 데이터베이스 파일 경로 설정 (Streamlit 앱 파일과 같은 폴더에 있어야 합니다!)
DB_FILE = 'osaka_pass.db'
TABLE_NAME = 'facilities'

# 데이터베이스 연결 함수 (기존 Flask 앱에서 가져옴)
def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

# 데이터베이스에서 모든 시설 정보를 불러오는 함수
def get_all_facilities():
    conn = get_db_connection()
    facilities = conn.execute(f'SELECT * FROM {TABLE_NAME} ORDER BY name_ko;').fetchall()
    conn.close()
    return [dict(row) for row in facilities]

# 데이터베이스에서 검색 쿼리에 맞는 시설 정보를 불러오는 함수
def search_facilities_db(query):
    conn = get_db_connection()
    facilities = []

    if query:
        search_query_sql = """
        SELECT * FROM facilities
        WHERE name_ko LIKE ? OR
              name_en LIKE ? OR
              category LIKE ? OR
              address LIKE ?
        ORDER BY name_ko;
        """
        search_term = f"%{query}%"
        
        facilities = conn.execute(search_query_sql, 
                                  (search_term, search_term, search_term, search_term)).fetchall()
    
    else: # 검색어가 없으면 모든 시설 반환
        facilities = conn.execute(f'SELECT * FROM {TABLE_NAME} ORDER BY name_ko;').fetchall()
    
    conn.close()
    return [dict(row) for row in facilities]


# --- Streamlit 앱의 UI 구성 시작 ---

st.set_page_config(page_title="오사카 주유패스 검색기", layout="centered") # 페이지 설정

st.title("🏯 오사카 주유패스 포함 시설 검색기")
st.markdown("궁금한 시설의 이름, 카테고리, 주소 등으로 검색해보세요!")

# 검색 입력 필드
search_query = st.text_input("검색어 입력", placeholder="예: 오사카성, 박물관, 우메다", help="시설명, 카테고리, 주소 등으로 검색 가능")

# 검색 버튼 (텍스트 입력 시 자동으로 검색되므로, 버튼은 선택 사항)
# if st.button("검색"):
#     st.write("검색 시작!")

# 검색 실행 및 결과 표시
if search_query:
    st.write(f"'{search_query}'(으)로 검색 중...")
    results = search_facilities_db(search_query)
else:
    st.write("모든 시설 목록:")
    results = get_all_facilities() # 검색어가 없으면 모든 시설 표시

if not results:
    st.warning("검색 결과가 없습니다.")
else:
    # 데이터를 보기 좋게 DataFrame으로 표시
    st.subheader(f"총 {len(results)}개의 검색 결과")
    
    # 각 시설 정보를 개별적으로 표시
    for facility in results:
        st.markdown("---") # 구분선
        st.write(f"### {facility.get('name_ko', '이름 없음')}") # name_en 부분을 삭제!
        
        # 주유패스 포함 여부 표시
        is_included = facility.get('included', '').lower() == 'yes' or facility.get('included', '') == '예'
        if is_included:
            st.success("✅ 주유패스 포함")
        else:
            st.error("❌ 주유패스 미포함")
        
        st.write(f"**카테고리:** {facility.get('category', '정보 없음')}")
        st.write(f"**지역:** {facility.get('region', '정보 없음')}")
        st.write(f"**주소:** {facility.get('address', '정보 없음')}")
        st.write(f"**운영 요일:** {facility.get('open_days', '정보 없음')}")
        open_hours_raw = facility.get('open_hours', '정보 없음') # <-- 새로운 줄 추가 (원래 값 가져오기)
        open_hours_display = open_hours_raw.replace('~', '\\~') 
        st.write(f"**운영 시간:** {open_hours_display}")
        st.write(f"**마지막 입장:** {facility.get('last_entry', '정보 없음')}")
        st.write(f"**예약 필요:** {facility.get('reservation', '정보 없음')}")
        st.write(f"**QR패스 필요:** {facility.get('qr_pass', '정보 없음')}")
        st.write(f"**원래 가격:** {facility.get('cost_original', '정보 없음')}")
        st.write(f"**참고:** {facility.get('notes', '없음')}")
        st.write(f"**주의:** {facility.get('caution', '없음')}")