
import json
from pathlib import Path
from datetime import date
from PIL import Image, ExifTags
import streamlit as st

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

st.set_page_config(
    page_title="LoanScope AX",
    page_icon="🛰️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Palette
MINT = "#29D3AA"
MINT_DARK = "#0B8F79"
MINT_DEEP = "#075F56"
MINT_SOFT = "#E8FBF6"
NAVY = "#16324F"
NAVY_SOFT = "#EAF0F6"
TEXT = "#18211F"
MUTED = "#67736F"
BG = "#F3F8F6"
WHITE = "#FFFFFF"
BORDER = "#DDEAE6"

st.markdown(f"""
<style>
html, body, [class*="css"] {{
  font-family: Pretendard, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}
.stApp {{
  background: linear-gradient(180deg, #F0FBF7 0%, {BG} 35%, #F7FAF9 100%);
  color: {TEXT};
}}
.block-container {{
  max-width: 1240px;
  padding-top: 1.2rem;
  padding-bottom: 5rem;
}}
header[data-testid="stHeader"] {{ background: transparent; }}
#MainMenu, footer {{ visibility: hidden; }}

.topnav {{
  position: sticky;
  top: 0.8rem;
  z-index: 100;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 16px;
  background: rgba(255,255,255,.92);
  backdrop-filter: blur(14px);
  border: 1px solid rgba(221,234,230,.9);
  border-radius: 22px;
  padding: 14px 18px;
  box-shadow: 0 14px 38px rgba(6,68,57,.10);
  margin-bottom: 18px;
}}
.brand-wrap {{
  display:flex; align-items:center; gap:12px;
}}
.brand-mark {{
  width:40px; height:40px; border-radius:13px;
  background: linear-gradient(145deg, {MINT} 0%, {MINT_DARK} 100%);
  color:white; display:grid; place-items:center; font-weight:900;
  box-shadow: 0 8px 20px rgba(41,211,170,.28);
}}
.brand-title {{ font-size:18px; font-weight:850; letter-spacing:-.5px; }}
.brand-sub {{ color:{MUTED}; font-size:12px; margin-top:1px; }}

.nav-hint {{
  display:flex; gap:8px; flex-wrap:wrap;
}}
.nav-pill {{
  background:#F7FAF9; border:1px solid {BORDER}; color:{NAVY};
  border-radius:999px; padding:7px 11px; font-size:12px; font-weight:750;
}}

.hero {{
  background:
    radial-gradient(circle at 85% 10%, rgba(41,211,170,.24), transparent 28%),
    linear-gradient(135deg, #FFFFFF 0%, #E6FAF5 55%, #D7F7EE 100%);
  border: 1px solid #D5EFE8;
  border-radius: 30px;
  padding: 34px;
  box-shadow: 0 18px 50px rgba(7,95,86,.12);
  overflow:hidden;
  position:relative;
}}
.hero-grid {{
  display:grid;
  grid-template-columns: 1.35fr .65fr;
  gap:26px;
  align-items:center;
}}
.hero-badge {{
  display:inline-flex; align-items:center; gap:7px;
  background:{MINT_DEEP}; color:white; padding:8px 13px;
  border-radius:999px; font-weight:800; font-size:12px;
}}
.hero h1 {{
  font-size:44px; line-height:1.08; letter-spacing:-2px;
  margin:18px 0 12px 0;
}}
.hero p {{
  color:{MUTED}; font-size:17px; line-height:1.65; margin:0;
}}
.hero img {{
  width:100%;
  max-width:260px;
  display:block;
  margin-left:auto;
  filter: drop-shadow(0 16px 20px rgba(22,50,79,.14));
}}
.hero-note {{
  margin-top:18px;
  display:flex; gap:10px; flex-wrap:wrap;
}}
.hero-chip {{
  background:white; color:{NAVY}; border:1px solid #D9ECE7;
  border-radius:14px; padding:9px 12px; font-size:13px; font-weight:750;
}}

.section {{
  background:{WHITE};
  border:1px solid {BORDER};
  border-radius:24px;
  padding:24px;
  margin:16px 0;
  box-shadow: 0 10px 28px rgba(6,68,57,.06);
}}
.section h3 {{
  margin:0 0 15px 0;
  letter-spacing:-.8px;
  font-size:21px;
}}
.section-kicker {{
  color:{MINT_DARK}; font-weight:850; font-size:12px; margin-bottom:6px;
}}
.info-card {{
  background:linear-gradient(145deg, #F8FCFB 0%, #EEF9F6 100%);
  border:1px solid #DDEFEA;
  border-radius:18px;
  padding:18px;
  height:100%;
}}
.info-card h4 {{ margin:0 0 8px 0; color:{NAVY}; }}
.info-card p {{ margin:0; color:{MUTED}; line-height:1.6; font-size:14px; }}

.id-banner {{
  display:grid; grid-template-columns:1fr 1fr; gap:12px;
  background:{NAVY}; color:white; border-radius:20px;
  padding:18px 20px; margin:14px 0 18px 0;
  box-shadow: 0 12px 30px rgba(22,50,79,.16);
}}
.id-label {{ color:#BFD3E5; font-size:12px; font-weight:750; }}
.id-value {{ font-size:18px; font-weight:850; margin-top:5px; letter-spacing:.3px; }}

.step-panel {{
  background:linear-gradient(180deg, {MINT_DEEP} 0%, {MINT_DARK} 100%);
  color:white; border-radius:22px; padding:18px;
  position:sticky; top:90px;
  box-shadow:0 14px 36px rgba(7,95,86,.20);
}}
.step-title {{ font-weight:850; font-size:15px; margin-bottom:12px; }}
.step-item {{
  display:flex; gap:10px; align-items:flex-start;
  padding:11px 0; border-bottom:1px solid rgba(255,255,255,.14);
}}
.step-item:last-child {{ border-bottom:none; }}
.step-num {{
  min-width:26px; height:26px; border-radius:9px;
  background:rgba(255,255,255,.16); display:grid; place-items:center;
  font-weight:850; font-size:12px;
}}
.step-copy b {{ display:block; font-size:13px; }}
.step-copy span {{ display:block; color:#CDEBE3; font-size:11px; margin-top:2px; }}

.metric-grid {{
  display:grid; grid-template-columns:repeat(4,1fr); gap:12px;
}}
.metric-card {{
  background:white; border:1px solid {BORDER}; border-radius:20px;
  padding:20px; box-shadow:0 9px 24px rgba(6,68,57,.06);
}}
.metric-label {{ color:{MUTED}; font-size:12px; font-weight:800; }}
.metric-value {{ color:{NAVY}; font-size:30px; font-weight:900; margin-top:8px; }}
.metric-value.mint {{ color:{MINT_DARK}; }}

.risk {{
  background:{NAVY_SOFT}; color:{NAVY};
  border-radius:15px; padding:13px 15px; margin:8px 0;
  border-left:5px solid {NAVY};
}}
.ok {{
  background:{MINT_SOFT}; color:{MINT_DEEP};
  border-radius:15px; padding:13px 15px; margin:8px 0;
  border-left:5px solid {MINT};
}}
.disclaimer {{
  background:#EAF3F1; color:#53625E; border-radius:16px;
  padding:14px 16px; line-height:1.55; font-size:13px;
  border:1px solid #DCE9E6;
}}
.qna {{
  background:white; border:1px solid {BORDER}; border-radius:18px;
  padding:18px 20px; margin:10px 0;
}}
.qna b {{ color:{NAVY}; }}
.qna p {{ color:{MUTED}; margin:8px 0 0 0; line-height:1.6; }}

.stButton>button {{
  background:linear-gradient(135deg, {MINT} 0%, {MINT_DARK} 100%);
  color:white; border:none; border-radius:16px; height:52px;
  font-size:16px; font-weight:850; width:100%;
  box-shadow:0 10px 22px rgba(41,211,170,.24);
}}
.stButton>button:hover {{ background:{MINT_DARK}; color:white; }}

div[data-testid="stMetric"] {{
  background:white; border:1px solid {BORDER}; border-radius:18px;
  padding:16px; box-shadow:0 8px 20px rgba(6,68,57,.05);
}}
div[data-baseweb="tab-list"] {{
  gap:8px;
}}
button[data-baseweb="tab"] {{
  background:white;
  border:1px solid {BORDER};
  border-radius:14px;
  padding:8px 16px;
  color:{NAVY};
  font-weight:800;
}}
button[data-baseweb="tab"][aria-selected="true"] {{
  background:{MINT_DEEP};
  color:white;
}}
@media (max-width: 900px) {{
  .hero-grid {{ grid-template-columns:1fr; }}
  .hero h1 {{ font-size:34px; }}
  .hero img {{ max-width:180px; margin:8px auto 0 auto; }}
  .id-banner {{ grid-template-columns:1fr; }}
  .metric-grid {{ grid-template-columns:repeat(2,1fr); }}
  .topnav {{ position:relative; top:0; }}
  .step-panel {{ position:relative; top:0; }}
}}
@media (max-width: 560px) {{
  .block-container {{ padding: .8rem .8rem 4rem .8rem; }}
  .hero {{ padding:24px 20px; border-radius:24px; }}
  .hero h1 {{ font-size:30px; }}
  .nav-hint {{ display:none; }}
  .metric-grid {{ grid-template-columns:1fr 1fr; }}
  .id-value {{ font-size:15px; }}
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

# Top navigation visual
st.markdown("""
<div class="topnav">
  <div class="brand-wrap">
    <div class="brand-mark">iM</div>
    <div>
      <div class="brand-title">LoanScope AX</div>
      <div class="brand-sub">기업여신 공간정보 심사보조</div>
    </div>
  </div>
  <div class="nav-hint">
    <span class="nav-pill">기능소개</span>
    <span class="nav-pill">LoanScope AX 실행</span>
    <span class="nav-pill">QnA</span>
  </div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["기능소개", "LoanScope AX 실행", "QnA"])

with tabs[0]:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <span class="hero-badge">AI·공간정보 기반 여신심사 지원</span>
          <h1>현장을 모두 방문하지 않고,<br>확인이 필요한 현장을 먼저 찾습니다.</h1>
          <p>
            위성·항공영상과 차주 제출자료를 교차검증해 시설의 존재, 시기별 변화,
            제출사진 신뢰성, 현장방문 필요도를 한 화면에서 확인합니다.
          </p>
          <div class="hero-note">
            <span class="hero-chip">시설자금 심사</span>
            <span class="hero-chip">비대면 현장확인</span>
            <span class="hero-chip">사후관리</span>
            <span class="hero-chip">이미지 진위 점검</span>
          </div>
        </div>
        <div>
          <img src="app/static/im_character_blue.png" alt="iM character">
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="section"><div class="section-kicker">WHY</div><h3>왜 필요한가요?</h3>', unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    cards = [
        ("비대면 심사의 한계", "시설자금 심사 시 차주 제출사진과 서류만으로는 실제 사업장 상태를 충분히 확인하기 어렵습니다."),
        ("현장방문의 비효율", "모든 건을 방문하기보다 공간정보로 위험건을 선별하면 출장시간과 비용을 줄일 수 있습니다."),
        ("AI 이미지 조작 위험", "AI 생성·편집 이미지를 제출할 수 있으므로 EXIF, 위치정보, 유사 이미지, 공간구조 교차검증이 필요합니다."),
    ]
    for col, (title, body) in zip((c1,c2,c3), cards):
        with col:
            st.markdown(f'<div class="info-card"><h4>{title}</h4><p>{body}</p></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section"><div class="section-kicker">FLOW</div><h3>동작 흐름</h3>', unsafe_allow_html=True)
    st.markdown("""
    1. 대출 신청정보와 연결된 품의·신청번호를 확인합니다.  
    2. 과거·현재 공간영상과 차주 제출사진을 비교합니다.  
    3. 시설 변화, 공정률 불일치, EXIF·GPS, 편집·중복 의심 신호를 분석합니다.  
    4. 필수서류 누락과 영상 신뢰도를 종합해 확인점수와 등급을 산출합니다.  
    5. `원격확인 가능 / 추가 증빙 / 현장방문 권고` 중 적정 조치를 제안합니다.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="section"><div class="section-kicker">EVIDENCE</div><h3>적용 가능성을 뒷받침하는 근거</h3>', unsafe_allow_html=True)
    st.markdown("""
    - 농림축산식품부는 위성·항공영상과 행정정보를 활용해 경작 여부와 이상 필지를 선별하고, 필요한 대상에 대해 추가 서류 및 현장점검을 수행하고 있습니다.
    - 본 서비스는 같은 구조를 기업여신에 적용하여 `공간정보 선별 → 서류 교차검증 → 필요한 건 현장방문` 프로세스를 제안합니다.
    - 탁상감정이 담보가치를 검토하는 절차라면, LoanScope AX는 사업장과 목적시설의 존재·변화를 확인하는 심사보조 절차입니다.
    """)
    st.markdown('</div>', unsafe_allow_html=True)

with tabs[1]:
    st.markdown(f"""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <span class="hero-badge">LIVE BETA</span>
          <h1>LoanScope AX 실행</h1>
          <p>연결된 신청심사 건의 대출정보, 공간영상, 제출서류를 기반으로 현장확인 필요도를 산출합니다.</p>
          <div class="hero-note">
            <span class="hero-chip">반응형 UI</span>
            <span class="hero-chip">심사번호 연계</span>
            <span class="hero-chip">위험신호 자동화</span>
          </div>
        </div>
        <div>
          <img src="app/static/im_character_sky.png" alt="iM character">
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer">
    본 서비스는 대출 승인·거절 또는 부정행위를 자동 판정하지 않습니다.
    공간정보와 제출자료의 불일치 신호를 제공하는 직원용 심사보조 도구입니다.
    </div>
    """, unsafe_allow_html=True)

    case_name = st.selectbox("연결 심사사례", list(cases.keys()))
    case = cases[case_name]

    st.markdown(f"""
    <div class="id-banner">
      <div>
        <div class="id-label">연결품의번호</div>
        <div class="id-value">{case.get("linked_approval_no", "XXXXXXXXXXXXXXXX")}</div>
      </div>
      <div>
        <div class="id-label">연결신청번호</div>
        <div class="id-value">{case.get("linked_application_no", "XXXXXXXXXXXXXXXX")}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    nav_col, main_col = st.columns([0.24, 0.76], gap="large")

    with nav_col:
        st.markdown("""
        <div class="step-panel">
          <div class="step-title">심사 진행단계</div>
          <div class="step-item"><div class="step-num">1</div><div class="step-copy"><b>기본정보</b><span>기업·대출·시설</span></div></div>
          <div class="step-item"><div class="step-num">2</div><div class="step-copy"><b>서류확인</b><span>필수 증빙 점검</span></div></div>
          <div class="step-item"><div class="step-num">3</div><div class="step-copy"><b>이미지 비교</b><span>과거·현재·제출사진</span></div></div>
          <div class="step-item"><div class="step-num">4</div><div class="step-copy"><b>위험신호</b><span>메타데이터·공간일치</span></div></div>
          <div class="step-item"><div class="step-num">5</div><div class="step-copy"><b>심사결과</b><span>등급·방문 권고</span></div></div>
        </div>
        """, unsafe_allow_html=True)

    with main_col:
        st.markdown('<div class="section"><div class="section-kicker">STEP 1</div><h3>대출·시설 정보</h3>', unsafe_allow_html=True)
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

        st.markdown('<div class="section"><div class="section-kicker">STEP 2</div><h3>제출서류 확인</h3>', unsafe_allow_html=True)
        doc_cols = st.columns(2)
        documents = {}
        for i, (doc, default) in enumerate(case["documents"].items()):
            with doc_cols[i % 2]:
                documents[doc] = st.checkbox(doc, value=default, key=f"{case_name}_{doc}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section"><div class="section-kicker">STEP 3</div><h3>공간영상·현장사진 비교</h3>', unsafe_allow_html=True)
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

        st.markdown('<div class="section"><div class="section-kicker">STEP 4</div><h3>자동 분석·담당자 확인</h3>', unsafe_allow_html=True)
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

            st.markdown('<div class="section"><div class="section-kicker">STEP 5</div><h3>심사결과</h3>', unsafe_allow_html=True)
            st.markdown(f"""
            <div class="metric-grid">
              <div class="metric-card"><div class="metric-label">확인 신뢰도</div><div class="metric-value mint">{score}점</div></div>
              <div class="metric-card"><div class="metric-label">확인등급</div><div class="metric-value">{grade}</div></div>
              <div class="metric-card"><div class="metric-label">현장방문 필요도</div><div class="metric-value">{visit}</div></div>
              <div class="metric-card"><div class="metric-label">위험신호</div><div class="metric-value">{len(deductions)}건</div></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 위험신호")
            if deductions:
                for reason, pts in deductions:
                    st.markdown(f'<div class="risk">◆ {reason} <b>(-{pts}점)</b></div>', unsafe_allow_html=True)
            else:
                st.markdown('<div class="ok">특이 위험신호가 확인되지 않았습니다.</div>', unsafe_allow_html=True)

            st.markdown("#### 추가 요청자료·조치")
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

            opinion = (
                f"{company_name}의 {loan_purpose} 관련 자료를 검토한 결과, "
                f"확인 신뢰도는 {score}점({grade}등급)입니다. "
                f"현재 권고 조치는 '{recommendation}'입니다. "
                "본 결과는 자동 승인·거절 판단이 아닌 추가 확인 절차 결정을 위한 참고자료입니다."
            )
            st.text_area("심사보조 의견", opinion, height=150)
            st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown("""
    <div class="hero">
      <div class="hero-grid">
        <div>
          <span class="hero-badge">QnA</span>
          <h1>자주 묻는 질문</h1>
          <p>서비스의 역할, 한계, 실제 은행업무 적용방식에 대한 주요 질문을 정리했습니다.</p>
        </div>
        <div>
          <img src="app/static/im_character_blue.png" alt="iM character">
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    qnas = [
        ("위성사진만으로 대출을 승인하거나 거절하나요?",
         "아닙니다. LoanScope AX는 자동 승인·거절 시스템이 아니라 추가 확인이 필요한 위험신호를 제공하는 심사보조 도구입니다."),
        ("탁상감정과 무엇이 다른가요?",
         "탁상감정은 담보가치를 추정하는 절차이고, LoanScope AX는 사업장·시설의 존재와 시기별 변화를 확인하는 사실검증 절차입니다."),
        ("현장점검을 완전히 대체할 수 있나요?",
         "전면 대체가 아니라 현장방문 대상을 선별하는 것이 1차 목적입니다. 규정상 방문이 필요한 건은 기존 절차를 유지합니다."),
        ("AI로 만든 제출사진은 어떻게 확인하나요?",
         "EXIF·GPS·편집정보, 유사 이미지 중복, 위성영상과 주변 구조의 일치 여부를 결합해 위·변조 의심 신호를 제공합니다."),
        ("어떤 대출에 가장 적합한가요?",
         "공장 신축·증축, 농업시설, 창고, 태양광, 토지조성 등 외부 공간영상에서 변화가 확인되는 시설자금에 적합합니다."),
        ("공간영상이 오래되거나 흐리면 어떻게 하나요?",
         "판독 신뢰도를 낮추고 최신 현장사진, 영상통화, 추가서류 또는 현장방문을 권고합니다."),
        ("실제 개인정보를 사용하나요?",
         "베타는 가상정보만 사용합니다. 실제 서비스에서는 주소·대출정보·현장사진의 접근권한과 보관기간, 동의 및 적법한 처리근거가 필요합니다."),
    ]
    for q, a in qnas:
        st.markdown(f'<div class="qna"><b>Q. {q}</b><p>A. {a}</p></div>', unsafe_allow_html=True)
