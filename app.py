
import json
from pathlib import Path
from datetime import date
from io import BytesIO

import streamlit as st
from PIL import Image, ExifTags

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

st.set_page_config(
    page_title="LoanScope AX",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MINT = "#2CC9A3"
DARK = "#18211F"
GRAY = "#6B7673"
BG = "#F5F8F7"

st.markdown(f"""
<style>
html, body, [class*="css"] {{
    font-family: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.stApp {{ background: {BG}; color: {DARK}; }}
.block-container {{ max-width: 1180px; padding-top: 2rem; padding-bottom: 5rem; }}
.hero {{
    background: linear-gradient(135deg, #FFFFFF 0%, #E9FBF6 100%);
    border-radius: 28px;
    padding: 34px 34px 28px 34px;
    box-shadow: 0 10px 30px rgba(20, 70, 58, 0.08);
    margin-bottom: 22px;
}}
.hero h1 {{ margin:0; font-size: 42px; letter-spacing:-1.8px; }}
.hero p {{ margin:12px 0 0 0; color:{GRAY}; font-size:17px; line-height:1.6; }}
.badge {{
    display:inline-block; background:#DFF8F1; color:#137C65; padding:7px 12px;
    border-radius:999px; font-weight:700; margin-bottom:15px;
}}
.section {{
    background:white; border-radius:24px; padding:26px; margin:16px 0;
    box-shadow: 0 8px 24px rgba(20, 70, 58, 0.06);
}}
.section h3 {{ margin-top:0; letter-spacing:-0.8px; }}
.metric-card {{
    background:white; border-radius:22px; padding:22px;
    box-shadow:0 8px 22px rgba(20,70,58,.07);
    min-height:120px;
}}
.metric-label {{ color:{GRAY}; font-size:14px; font-weight:700; }}
.metric-value {{ color:{DARK}; font-size:32px; font-weight:800; margin-top:8px; }}
.mint {{ color:{MINT}; }}
.risk {{
    background:#FFF7F0; border-radius:16px; padding:14px 16px; margin:8px 0;
    border-left:5px solid #FF9C55;
}}
.ok {{
    background:#EAFBF6; border-radius:16px; padding:14px 16px; margin:8px 0;
    border-left:5px solid {MINT};
}}
.disclaimer {{
    background:#EEF3F2; color:#5E6966; border-radius:16px; padding:14px 16px;
    font-size:13px; line-height:1.55;
}}
.stButton>button {{
    background:{MINT}; color:white; border:none; border-radius:16px;
    height:52px; font-size:17px; font-weight:800; width:100%;
}}
.stButton>button:hover {{ background:#1EB18E; color:white; }}
div[data-testid="stMetric"] {{
    background:white; border-radius:20px; padding:18px;
    box-shadow:0 8px 22px rgba(20,70,58,.06);
}}
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_cases():
    return json.loads((BASE / "sample_cases.json").read_text(encoding="utf-8"))

def extract_exif(uploaded):
    result = {"촬영일시": None, "GPS": False, "편집 프로그램": None}
    try:
        image = Image.open(uploaded)
        exif = image.getexif()
        if not exif:
            return result
        for tag_id, value in exif.items():
            tag = ExifTags.TAGS.get(tag_id, tag_id)
            if tag in ("DateTimeOriginal", "DateTime"):
                result["촬영일시"] = str(value)
            elif tag == "GPSInfo":
                result["GPS"] = True
            elif tag == "Software":
                result["편집 프로그램"] = str(value)
    except Exception:
        pass
    return result

def calculate_score(checks, documents):
    deductions = []
    if not checks["visible_change"]:
        deductions.append(("시설 변화 미확인", 30))
    if checks["progress_mismatch"]:
        deductions.append(("신고 공정률과 영상 변화 불일치", 25))
    if not checks["gps_exists"]:
        deductions.append(("현장사진 GPS 정보 없음", 10))
    if not checks["exif_exists"]:
        deductions.append(("현장사진 촬영정보 없음", 5))
    if checks["editing_suspected"]:
        deductions.append(("이미지 편집·생성 의심 신호", 20))
    if not checks["spatial_match"]:
        deductions.append(("공간영상과 제출사진 구조 불일치", 30))
    if checks["duplicate_suspected"]:
        deductions.append(("동일·유사 이미지 재사용 의심", 20))
    if checks["old_satellite"]:
        deductions.append(("공간영상 촬영일 경과", 10))
    if checks["low_quality"]:
        deductions.append(("영상 판독 품질 낮음", 5))

    missing_docs = [name for name, ok in documents.items() if not ok]
    for doc in missing_docs:
        deductions.append((f"핵심서류 누락: {doc}", 10))

    score = max(0, 100 - sum(v for _, v in deductions))
    if score >= 80:
        grade, recommendation, visit = "A", "원격확인 가능", "낮음"
    elif score >= 50:
        grade, recommendation, visit = "B", "추가 증빙 후 재검토", "중간"
    else:
        grade, recommendation, visit = "C", "현장방문 권고", "높음"
    return score, grade, recommendation, visit, deductions, missing_docs

cases = load_cases()

st.markdown("""
<div class="hero">
  <div class="badge">기업여신 AX Beta</div>
  <h1>LoanScope AX</h1>
  <p>공간영상과 차주 제출자료를 교차검증해 시설자금의 목적사업 진행 여부와 현장방문 필요도를 판단합니다.</p>
</div>
""", unsafe_allow_html=True)

st.markdown("""
<div class="disclaimer">
본 서비스는 대출 승인·거절 또는 부정행위를 자동 판정하지 않습니다.
공간정보와 제출자료의 불일치 신호를 제공하는 직원용 심사보조 도구입니다.
</div>
""", unsafe_allow_html=True)

st.markdown('<div class="section"><h3>1. 심사 사례 선택</h3>', unsafe_allow_html=True)
case_name = st.selectbox("샘플 사례", list(cases.keys()), label_visibility="collapsed")
case = cases[case_name]
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"><h3>2. 대출·시설 정보</h3>', unsafe_allow_html=True)
c1, c2 = st.columns(2)
with c1:
    company_name = st.text_input("기업명", case["company_name"])
    industry = st.text_input("업종", case["industry"])
    loan_type = st.selectbox("대출 종류", ["시설자금대출", "운전자금대출"], index=0)
    loan_amount = st.number_input("신청금액(원)", min_value=0, value=int(case["loan_amount"]), step=10000000)
    loan_purpose = st.text_input("자금용도", case["loan_purpose"])
with c2:
    address = st.text_input("사업장 주소", case["address"])
    start_date = st.date_input("공사 시작일", value=date.fromisoformat(case["start_date"]))
    end_date = st.date_input("공사 예정 완료일", value=date.fromisoformat(case["end_date"]))
    facility_area = st.number_input("신청 시설면적(㎡)", min_value=0, value=int(case["facility_area"]), step=100)
    declared_progress = st.slider("차주 신고 공정률", 0, 100, int(case["declared_progress"]))
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"><h3>3. 제출서류 확인</h3>', unsafe_allow_html=True)
doc_cols = st.columns(2)
documents = {}
for i, (doc, default) in enumerate(case["documents"].items()):
    with doc_cols[i % 2]:
        documents[doc] = st.checkbox(doc, value=default, key=f"{case_name}_{doc}")
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"><h3>4. 공간영상·현장사진 비교</h3>', unsafe_allow_html=True)
img_cols = st.columns(3)
labels = ["신청 전 공간영상", "최근 공간영상", "차주 제출 현장사진"]
for col, label, img_name in zip(img_cols, labels, case["images"]):
    with col:
        st.caption(label)
        st.image(str(ASSETS / img_name), use_container_width=True)
uploaded = st.file_uploader("차주 제출 현장사진 교체", type=["jpg","jpeg","png"])
if uploaded is not None:
    st.image(uploaded, caption="업로드한 현장사진", use_container_width=True)
    exif = extract_exif(uploaded)
    st.write({
        "촬영일시": exif["촬영일시"] or "확인 불가",
        "GPS": "확인" if exif["GPS"] else "없음",
        "편집 프로그램": exif["편집 프로그램"] or "기록 없음"
    })
st.markdown('</div>', unsafe_allow_html=True)

st.markdown('<div class="section"><h3>5. 자동 분석·담당자 확인</h3>', unsafe_allow_html=True)
checks = dict(case["checks"])
a, b = st.columns(2)
with a:
    checks["visible_change"] = st.toggle("신규 시설 변화 확인", value=checks["visible_change"])
    checks["progress_mismatch"] = st.toggle("신고 공정률과 영상 변화 불일치", value=checks["progress_mismatch"])
    checks["spatial_match"] = st.toggle("제출사진과 대상지 구조 일치", value=checks["spatial_match"])
    checks["low_quality"] = st.toggle("영상 품질 부족", value=checks["low_quality"])
with b:
    checks["gps_exists"] = st.toggle("GPS 정보 확인", value=checks["gps_exists"])
    checks["exif_exists"] = st.toggle("촬영일시 정보 확인", value=checks["exif_exists"])
    checks["editing_suspected"] = st.toggle("편집·생성 의심 신호", value=checks["editing_suspected"])
    checks["duplicate_suspected"] = st.toggle("유사 이미지 중복 의심", value=checks["duplicate_suspected"])
st.markdown('</div>', unsafe_allow_html=True)

if st.button("현장확인 분석 실행"):
    score, grade, recommendation, visit, deductions, missing_docs = calculate_score(checks, documents)
    st.session_state["result"] = (score, grade, recommendation, visit, deductions, missing_docs)

if "result" in st.session_state:
    score, grade, recommendation, visit, deductions, missing_docs = st.session_state["result"]

    st.markdown("## 분석 결과")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("확인 신뢰도", f"{score}점")
    m2.metric("확인등급", grade)
    m3.metric("현장방문 필요도", visit)
    m4.metric("위험신호", f"{len(deductions)}건")

    st.markdown('<div class="section"><h3>위험신호</h3>', unsafe_allow_html=True)
    if deductions:
        for reason, pts in deductions:
            st.markdown(f'<div class="risk">⚠ {reason} <b>(-{pts}점)</b></div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="ok">특이 위험신호가 확인되지 않았습니다.</div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section"><h3>추가 요청자료·조치</h3>', unsafe_allow_html=True)
    requests = []
    if not checks["gps_exists"]:
        requests.append("위치정보가 포함된 신규 현장사진")
    if checks["editing_suspected"] or checks["duplicate_suspected"]:
        requests.append("앱 내 실시간 재촬영 또는 영상통화")
    if not checks["spatial_match"]:
        requests.append("시설배치도 및 현장 진입경로 확인자료")
    requests += missing_docs
    if not requests:
        requests.append("담당자 검토 후 원격확인 가능")
    for item in dict.fromkeys(requests):
        st.markdown(f"- {item}")
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section"><h3>심사보조 의견</h3>', unsafe_allow_html=True)
    opinion = (
        f"{company_name}의 {loan_purpose} 관련 자료를 검토한 결과, "
        f"확인 신뢰도는 {score}점({grade}등급)입니다. "
        f"현재 권고 조치는 '{recommendation}'입니다. "
        "본 결과는 자동 승인·거절 판단이 아닌 추가 확인 절차 결정을 위한 참고자료입니다."
    )
    st.text_area("검토의견", opinion, height=150)
    st.markdown('</div>', unsafe_allow_html=True)
