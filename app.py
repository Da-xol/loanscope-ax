
import json
from pathlib import Path
from datetime import date
import base64

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

def image_data_uri(path: Path) -> str:
    encoded = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:image/png;base64,{encoded}"

IM_CHARACTER_BLUE = image_data_uri(ASSETS / "im_character_blue.png")
IM_CHARACTER_SKY = image_data_uri(ASSETS / "im_character_sky.png")

# iM-inspired professional palette
MINT = "#36D6B2"
MINT_ACTIVE = "#20B99A"
MINT_DARK = "#087A69"
MINT_DEEP = "#07564C"
MINT_PALE = "#EAFBF6"
MINT_WASH = "#F4FCF9"
INK = "#102A2E"
INK_2 = "#244247"
MUTED = "#708185"
LINE = "#DCEAE6"
CANVAS = "#F3F7F6"
WHITE = "#FFFFFF"
NAVY = "#163A4A"
NAVY_2 = "#0D2D3A"
AMBER = "#A66A1F"

st.markdown(f"""
<style>
:root {{
  --mint:{MINT};
  --mint-active:{MINT_ACTIVE};
  --mint-dark:{MINT_DARK};
  --mint-deep:{MINT_DEEP};
  --mint-pale:{MINT_PALE};
  --ink:{INK};
  --muted:{MUTED};
  --line:{LINE};
  --canvas:{CANVAS};
  --navy:{NAVY};
}}

html {{
  scroll-behavior: smooth;
}}

html, body, [class*="css"] {{
  font-family: Pretendard, Inter, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}}

.stApp {{
  background:
    radial-gradient(circle at 78% -10%, rgba(54,214,178,.10), transparent 30%),
    linear-gradient(180deg, #F7FAF9 0%, {CANVAS} 100%);
  color: {INK};
}}

header[data-testid="stHeader"] {{
  background: transparent;
  height: 0;
}}

#MainMenu, footer {{
  visibility: hidden;
}}

.block-container {{
  max-width: 1540px;
  padding: 0 2.2rem 5rem 2.2rem;
}}

.app-shell {{
  position: sticky;
  top: 0;
  z-index: 999;
  margin: 0 -2.2rem 26px -2.2rem;
  padding: 0 2.2rem;
  background: rgba(248,251,250,.94);
  backdrop-filter: blur(18px);
  border-bottom: 1px solid rgba(220,234,230,.95);
  box-shadow: 0 6px 24px rgba(7,86,76,.045);
}}

.appbar {{
  max-width: 1540px;
  margin: 0 auto;
  min-height: 76px;
  display: grid;
  grid-template-columns: 300px 1fr auto;
  align-items: center;
  gap: 24px;
}}

.logo-block {{
  display:flex;
  align-items:center;
  gap:12px;
}}

.logo-mark {{
  width:42px;
  height:42px;
  border-radius:12px;
  display:grid;
  place-items:center;
  color:white;
  font-size:18px;
  font-weight:900;
  letter-spacing:-1px;
  background: linear-gradient(145deg, {MINT} 0%, {MINT_DARK} 100%);
  box-shadow: 0 10px 26px rgba(32,185,154,.24);
}}

.logo-copy strong {{
  display:block;
  color:{INK};
  font-size:17px;
  font-weight:900;
  letter-spacing:-.55px;
}}

.logo-copy span {{
  color:{MUTED};
  font-size:11px;
  font-weight:650;
}}

.system-status {{
  display:flex;
  align-items:center;
  gap:8px;
  justify-self:end;
  color:{MINT_DARK};
  font-size:12px;
  font-weight:800;
  background:{MINT_PALE};
  padding:8px 11px;
  border-radius:999px;
  border:1px solid #CDEFE5;
}}

.status-dot {{
  width:7px;
  height:7px;
  border-radius:50%;
  background:{MINT_ACTIVE};
  box-shadow:0 0 0 4px rgba(32,185,154,.11);
}}

div[data-baseweb="tab-list"] {{
  justify-content:center;
  gap:30px;
  background:transparent;
  border:none;
}}

button[data-baseweb="tab"] {{
  background:transparent !important;
  border:none !important;
  border-radius:0 !important;
  color:{MUTED} !important;
  font-size:14px !important;
  font-weight:800 !important;
  padding:25px 0 21px 0 !important;
  box-shadow:none !important;
}}

button[data-baseweb="tab"][aria-selected="true"] {{
  color:{MINT_DEEP} !important;
  border-bottom:3px solid {MINT_ACTIVE} !important;
}}

.executive-hero {{
  position:relative;
  overflow:hidden;
  min-height:270px;
  padding:38px 42px;
  border-radius:28px;
  border:1px solid #D7EBE5;
  background:
    linear-gradient(115deg, rgba(255,255,255,.98) 0%, rgba(240,252,248,.98) 58%, rgba(220,247,239,.95) 100%);
  box-shadow: 0 22px 58px rgba(7,86,76,.10);
}}

.executive-hero:after {{
  content:"";
  position:absolute;
  width:420px;
  height:420px;
  border-radius:50%;
  top:-225px;
  right:-70px;
  background:rgba(54,214,178,.14);
}}

.hero-layout {{
  position:relative;
  z-index:2;
  display:grid;
  grid-template-columns:minmax(0, 1fr) 260px;
  gap:42px;
  align-items:center;
}}

.eyebrow {{
  display:inline-flex;
  align-items:center;
  gap:8px;
  color:{MINT_DARK};
  font-size:12px;
  font-weight:900;
  letter-spacing:.7px;
  text-transform:uppercase;
}}

.eyebrow-line {{
  width:24px;
  height:2px;
  background:{MINT_ACTIVE};
}}

.executive-hero h1 {{
  margin:14px 0 12px 0;
  color:{INK};
  font-size:43px;
  line-height:1.12;
  letter-spacing:-2.1px;
  font-weight:900;
}}

.executive-hero p {{
  max-width:760px;
  margin:0;
  color:{MUTED};
  font-size:16px;
  line-height:1.75;
}}

.hero-meta {{
  display:flex;
  gap:10px;
  flex-wrap:wrap;
  margin-top:22px;
}}

.meta-chip {{
  background:white;
  border:1px solid #D5E8E2;
  border-radius:999px;
  padding:8px 12px;
  color:{INK_2};
  font-size:12px;
  font-weight:800;
  box-shadow:0 5px 12px rgba(7,86,76,.035);
}}

.hero-character {{
  width:205px;
  display:block;
  margin:0 auto;
  filter:drop-shadow(0 20px 24px rgba(13,45,58,.12));
}}

.content-grid {{
  display:grid;
  grid-template-columns:250px minmax(0, 1fr);
  gap:24px;
  align-items:start;
  margin-top:22px;
}}

.left-rail {{
  position:sticky;
  top:98px;
  align-self:start;
}}

.rail-card {{
  background:{NAVY_2};
  border-radius:22px;
  padding:18px;
  box-shadow:0 18px 42px rgba(13,45,58,.17);
  color:white;
}}

.rail-title {{
  font-size:12px;
  color:#A8C8D1;
  font-weight:850;
  letter-spacing:.55px;
  text-transform:uppercase;
  margin-bottom:10px;
}}

.rail-case {{
  padding:14px;
  background:rgba(255,255,255,.07);
  border:1px solid rgba(255,255,255,.08);
  border-radius:15px;
  margin-bottom:14px;
}}

.rail-case strong {{
  display:block;
  font-size:14px;
  margin-bottom:4px;
}}

.rail-case span {{
  color:#AFCCD3;
  font-size:11px;
}}

.step-link {{
  display:flex;
  gap:10px;
  align-items:flex-start;
  padding:12px 10px;
  color:#D2E4E8 !important;
  text-decoration:none !important;
  border-radius:13px;
  transition:.18s ease;
  margin:3px 0;
}}

.step-link:hover {{
  background:rgba(54,214,178,.14);
  color:white !important;
  transform:translateX(2px);
}}

.step-link .num {{
  min-width:26px;
  height:26px;
  border-radius:9px;
  display:grid;
  place-items:center;
  color:{NAVY_2};
  background:{MINT};
  font-size:11px;
  font-weight:900;
}}

.step-link b {{
  display:block;
  font-size:13px;
  line-height:1.25;
}}

.step-link small {{
  display:block;
  color:#91B9C2;
  margin-top:2px;
  font-size:10px;
}}

.panel {{
  background:{WHITE};
  border:1px solid {LINE};
  border-radius:22px;
  padding:24px;
  margin-bottom:18px;
  box-shadow:0 12px 34px rgba(7,86,76,.055);
}}

.anchor-offset {{
  scroll-margin-top:110px;
}}

.panel-head {{
  display:flex;
  align-items:flex-end;
  justify-content:space-between;
  gap:20px;
  margin-bottom:18px;
}}

.panel-index {{
  color:{MINT_DARK};
  font-size:11px;
  font-weight:900;
  letter-spacing:.75px;
  text-transform:uppercase;
}}

.panel h3 {{
  margin:5px 0 0 0;
  color:{INK};
  font-size:21px;
  font-weight:900;
  letter-spacing:-.75px;
}}

.panel-desc {{
  color:{MUTED};
  font-size:12px;
  max-width:480px;
  text-align:right;
  line-height:1.5;
}}

.case-header {{
  display:grid;
  grid-template-columns:1.2fr 1fr 1fr;
  gap:12px;
  margin:18px 0;
}}

.case-box {{
  background:linear-gradient(145deg, #F8FCFB 0%, {MINT_WASH} 100%);
  border:1px solid #DDEDE8;
  border-radius:16px;
  padding:15px 17px;
}}

.case-label {{
  color:{MUTED};
  font-size:10px;
  font-weight:850;
  text-transform:uppercase;
  letter-spacing:.5px;
}}

.case-value {{
  color:{INK};
  font-size:15px;
  font-weight:900;
  margin-top:6px;
  overflow-wrap:anywhere;
}}

.notice {{
  background:#EFF8F5;
  border:1px solid #D8EBE5;
  color:#46615E;
  border-radius:14px;
  padding:12px 14px;
  font-size:12px;
  line-height:1.55;
}}

.analysis-strip {{
  display:grid;
  grid-template-columns:repeat(4,1fr);
  gap:12px;
}}

.analysis-card {{
  min-height:122px;
  background:linear-gradient(160deg, #FFFFFF 0%, #F5FBF9 100%);
  border:1px solid {LINE};
  border-radius:18px;
  padding:18px;
  box-shadow:0 8px 22px rgba(7,86,76,.045);
}}

.analysis-label {{
  color:{MUTED};
  font-size:11px;
  font-weight:850;
}}

.analysis-value {{
  color:{INK};
  font-size:30px;
  line-height:1;
  font-weight:950;
  margin-top:13px;
  letter-spacing:-1.2px;
}}

.analysis-value.mint {{
  color:{MINT_DARK};
}}

.risk-item {{
  display:grid;
  grid-template-columns:30px 1fr auto;
  align-items:center;
  gap:10px;
  background:#F1F6F7;
  border:1px solid #DDE8EB;
  border-radius:14px;
  padding:12px 14px;
  margin:8px 0;
  color:{NAVY_2};
}}

.risk-icon {{
  width:26px;
  height:26px;
  border-radius:9px;
  display:grid;
  place-items:center;
  color:white;
  background:{NAVY};
  font-size:11px;
  font-weight:900;
}}

.risk-score {{
  color:{NAVY};
  font-weight:900;
  font-size:12px;
}}

.success-item {{
  background:{MINT_PALE};
  border:1px solid #CDEFE5;
  color:{MINT_DEEP};
  border-radius:14px;
  padding:13px 15px;
  font-weight:750;
}}

.info-grid {{
  display:grid;
  grid-template-columns:repeat(3,1fr);
  gap:14px;
}}

.info-tile {{
  background:white;
  border:1px solid {LINE};
  border-radius:18px;
  padding:20px;
  box-shadow:0 10px 26px rgba(7,86,76,.04);
}}

.info-tile .icon {{
  width:38px;
  height:38px;
  display:grid;
  place-items:center;
  border-radius:12px;
  background:{MINT_PALE};
  color:{MINT_DARK};
  font-weight:900;
  margin-bottom:14px;
}}

.info-tile h4 {{
  margin:0 0 8px 0;
  font-size:15px;
  color:{INK};
}}

.info-tile p {{
  margin:0;
  color:{MUTED};
  font-size:12px;
  line-height:1.65;
}}

.qna-card {{
  background:white;
  border:1px solid {LINE};
  border-radius:16px;
  padding:17px 18px;
  margin:9px 0;
  box-shadow:0 6px 16px rgba(7,86,76,.025);
}}

.qna-card strong {{
  color:{INK};
  font-size:14px;
}}

.qna-card p {{
  margin:7px 0 0 0;
  color:{MUTED};
  line-height:1.62;
  font-size:13px;
}}

.stButton>button {{
  min-height:52px;
  border:none;
  border-radius:14px;
  color:white;
  font-size:15px;
  font-weight:900;
  background:linear-gradient(135deg, {MINT_ACTIVE} 0%, {MINT_DARK} 100%);
  box-shadow:0 11px 24px rgba(32,185,154,.20);
}}

.stButton>button:hover {{
  color:white;
  background:linear-gradient(135deg, {MINT} 0%, {MINT_DARK} 100%);
  transform:translateY(-1px);
}}

[data-testid="stFileUploader"] {{
  background:#F8FBFA;
  border:1px dashed #BFDCD4;
  border-radius:16px;
  padding:6px;
}}

@media (max-width: 1180px) {{
  .appbar {{
    grid-template-columns:250px 1fr auto;
  }}
  .content-grid {{
    grid-template-columns:215px minmax(0, 1fr);
  }}
  .analysis-strip {{
    grid-template-columns:repeat(2,1fr);
  }}
}}

@media (max-width: 960px) {{
  .block-container {{
    padding:0 1rem 4rem 1rem;
  }}
  .app-shell {{
    margin:0 -1rem 20px -1rem;
    padding:0 1rem;
  }}
  .appbar {{
    grid-template-columns:1fr auto;
  }}
  .appbar > div:nth-child(2) {{
    grid-column:1 / -1;
    grid-row:2;
  }}
  .system-status {{
    grid-column:2;
    grid-row:1;
  }}
  .content-grid {{
    grid-template-columns:1fr;
  }}
  .left-rail {{
    position:relative;
    top:auto;
  }}
  .rail-card {{
    display:grid;
    grid-template-columns:repeat(5,1fr);
    gap:6px;
  }}
  .rail-title, .rail-case {{
    display:none;
  }}
  .step-link {{
    display:block;
    text-align:center;
    padding:10px 5px;
  }}
  .step-link .num {{
    margin:0 auto 6px auto;
  }}
  .step-link small {{
    display:none;
  }}
  .hero-layout {{
    grid-template-columns:1fr;
  }}
  .hero-character {{
    display:none;
  }}
  .case-header {{
    grid-template-columns:1fr;
  }}
}}

@media (max-width: 650px) {{
  .executive-hero {{
    padding:28px 22px;
  }}
  .executive-hero h1 {{
    font-size:32px;
  }}
  .info-grid {{
    grid-template-columns:1fr;
  }}
  .analysis-strip {{
    grid-template-columns:1fr 1fr;
  }}
  .panel-head {{
    display:block;
  }}
  .panel-desc {{
    text-align:left;
    margin-top:8px;
  }}
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

# Independent enterprise application header
st.markdown("""
<div class="app-shell">
  <div class="appbar">
    <div class="logo-block">
      <div class="logo-mark">iM</div>
      <div class="logo-copy">
        <strong>LoanScope AX</strong>
        <span>기업여신 공간정보 심사 플랫폼</span>
      </div>
    </div>
    <div></div>
    <div class="system-status"><span class="status-dot"></span>Beta System Online</div>
  </div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["기능소개", "LoanScope AX", "QnA"])

with tabs[0]:
    st.markdown(f"""
    <div class="executive-hero">
      <div class="hero-layout">
        <div>
          <div class="eyebrow"><span class="eyebrow-line"></span>Enterprise Credit Intelligence</div>
          <h1>공간정보로 심사 깊이를 높이고,<br>현장점검의 정확도를 높입니다.</h1>
          <p>
            LoanScope AX는 위성·항공영상, 차주 제출자료, 공정정보를 교차검증하여
            시설자금의 목적사업 진행 여부와 현장방문 필요도를 판단하는 기업여신 심사보조 시스템입니다.
          </p>
          <div class="hero-meta">
            <span class="meta-chip">시설자금 심사</span>
            <span class="meta-chip">비대면 현장확인</span>
            <span class="meta-chip">사후관리</span>
            <span class="meta-chip">이미지 진위 점검</span>
          </div>
        </div>
        <div><img class="hero-character" src="{IM_CHARACTER_BLUE}" alt="iM 캐릭터"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div class="panel-head">
        <div>
          <div class="panel-index">Core Value</div>
          <h3>서비스가 해결하는 세 가지 문제</h3>
        </div>
      </div>
      <div class="info-grid">
        <div class="info-tile">
          <div class="icon">01</div>
          <h4>비대면 심사의 정보 한계</h4>
          <p>차주 제출사진과 서류만으로는 사업장·시설의 실제 존재와 공사 진행상태를 충분히 확인하기 어렵습니다.</p>
        </div>
        <div class="info-tile">
          <div class="icon">02</div>
          <h4>현장점검 자원의 비효율</h4>
          <p>모든 건을 일괄 방문하기보다 공간정보 기반 위험선별로 점검 우선순위를 정교화합니다.</p>
        </div>
        <div class="info-tile">
          <div class="icon">03</div>
          <h4>AI 이미지 조작 위험</h4>
          <p>EXIF·GPS·편집정보·유사 이미지·공간구조 일치 여부를 결합해 제출 이미지의 진위 위험을 점검합니다.</p>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="panel">
      <div class="panel-head">
        <div>
          <div class="panel-index">Process</div>
          <h3>업무 동작 흐름</h3>
        </div>
        <div class="panel-desc">공간정보 선별 → 서류 교차검증 → 현장방문 필요도 산출</div>
      </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("""
    1. 대출 신청정보와 연결된 품의·신청번호를 확인합니다.  
    2. 과거·현재 공간영상과 차주 제출사진을 비교합니다.  
    3. 시설 변화, 공정률 불일치, EXIF·GPS, 편집·중복 의심 신호를 분석합니다.  
    4. 필수서류 누락과 영상 신뢰도를 종합해 확인점수와 등급을 산출합니다.  
    5. `원격확인 가능 / 추가 증빙 / 현장방문 권고` 중 적정 조치를 제안합니다.
    """)

with tabs[1]:
    st.markdown(f"""
    <div class="executive-hero">
      <div class="hero-layout">
        <div>
          <div class="eyebrow"><span class="eyebrow-line"></span>Loan Review Workspace</div>
          <h1>연결 신청심사 건을<br>공간정보로 심층 검토합니다.</h1>
          <p>
            대출·시설정보, 제출서류, 공간영상, 이미지 진위 위험을 단계별로 분석하고
            최종 현장확인 필요도를 산출합니다.
          </p>
          <div class="hero-meta">
            <span class="meta-chip">연결심사건 조회</span>
            <span class="meta-chip">위험신호 산출</span>
            <span class="meta-chip">현장방문 권고</span>
          </div>
        </div>
        <div><img class="hero-character" src="{IM_CHARACTER_SKY}" alt="iM 캐릭터"></div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("""
    <div class="notice">
      본 서비스는 대출 승인·거절 또는 부정행위를 자동 판정하지 않습니다.
      공간정보와 제출자료의 불일치 신호를 제공하는 직원용 심사보조 도구입니다.
    </div>
    """, unsafe_allow_html=True)

    case_name = st.selectbox("연결 심사사례", list(cases.keys()))
    case = cases[case_name]

    st.markdown(f"""
    <div class="case-header">
      <div class="case-box">
        <div class="case-label">심사 대상</div>
        <div class="case-value">{case["company_name"]}</div>
      </div>
      <div class="case-box">
        <div class="case-label">연결품의번호</div>
        <div class="case-value">{case.get("linked_approval_no", "XXXXXXXXXXXXXXXX")}</div>
      </div>
      <div class="case-box">
        <div class="case-label">연결신청번호</div>
        <div class="case-value">{case.get("linked_application_no", "XXXXXXXXXXXXXXXX")}</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown('<div class="content-grid">', unsafe_allow_html=True)

    rail_col, main_col = st.columns([0.22, 0.78], gap="large")

    with rail_col:
        st.markdown(f"""
        <div class="left-rail">
          <div class="rail-card">
            <div class="rail-title">Review Navigator</div>
            <div class="rail-case">
              <strong>{case["company_name"]}</strong>
              <span>{case["loan_purpose"]}</span>
            </div>
            <a class="step-link" href="#step-1"><span class="num">1</span><span><b>기본정보</b><small>기업·대출·시설</small></span></a>
            <a class="step-link" href="#step-2"><span class="num">2</span><span><b>서류확인</b><small>필수 증빙 점검</small></span></a>
            <a class="step-link" href="#step-3"><span class="num">3</span><span><b>이미지 비교</b><small>과거·현재·제출사진</small></span></a>
            <a class="step-link" href="#step-4"><span class="num">4</span><span><b>위험신호</b><small>메타데이터·공간일치</small></span></a>
            <a class="step-link" href="#step-5"><span class="num">5</span><span><b>심사결과</b><small>등급·방문 권고</small></span></a>
          </div>
        </div>
        """, unsafe_allow_html=True)

    with main_col:
        st.markdown("""
        <div id="step-1" class="panel anchor-offset">
          <div class="panel-head">
            <div><div class="panel-index">Step 01</div><h3>대출·시설 정보</h3></div>
            <div class="panel-desc">신청심사 건의 기본정보와 공사·시설 조건을 확인합니다.</div>
          </div>
        """, unsafe_allow_html=True)
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

        st.markdown("""
        <div id="step-2" class="panel anchor-offset">
          <div class="panel-head">
            <div><div class="panel-index">Step 02</div><h3>제출서류 확인</h3></div>
            <div class="panel-desc">자금용도와 공정단계에 필요한 핵심 증빙의 제출 여부를 점검합니다.</div>
          </div>
        """, unsafe_allow_html=True)
        doc_cols = st.columns(2)
        documents = {}
        for i, (doc, default) in enumerate(case["documents"].items()):
            with doc_cols[i % 2]:
                documents[doc] = st.checkbox(doc, value=default, key=f"{case_name}_{doc}")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown("""
        <div id="step-3" class="panel anchor-offset">
          <div class="panel-head">
            <div><div class="panel-index">Step 03</div><h3>공간영상·현장사진 비교</h3></div>
            <div class="panel-desc">신청 전·최근 공간영상과 차주 제출사진을 나란히 비교합니다.</div>
          </div>
        """, unsafe_allow_html=True)
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

        st.markdown("""
        <div id="step-4" class="panel anchor-offset">
          <div class="panel-head">
            <div><div class="panel-index">Step 04</div><h3>자동 분석·담당자 확인</h3></div>
            <div class="panel-desc">자동 탐지값과 담당자 확인값을 결합해 위험신호를 구성합니다.</div>
          </div>
        """, unsafe_allow_html=True)
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

        if st.button("현장확인 분석 실행", use_container_width=True):
            score, grade, recommendation, visit, deductions, missing_docs = calculate_score(checks, documents)
            st.session_state["result"] = (score, grade, recommendation, visit, deductions, missing_docs)

        st.markdown('<div id="step-5" class="anchor-offset"></div>', unsafe_allow_html=True)
        if "result" in st.session_state:
            score, grade, recommendation, visit, deductions, missing_docs = st.session_state["result"]

            st.markdown("""
            <div class="panel">
              <div class="panel-head">
                <div><div class="panel-index">Step 05</div><h3>심사결과</h3></div>
                <div class="panel-desc">확인 신뢰도, 등급, 방문 필요도와 상세 위험신호를 제공합니다.</div>
              </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="analysis-strip">
              <div class="analysis-card"><div class="analysis-label">확인 신뢰도</div><div class="analysis-value mint">{score}점</div></div>
              <div class="analysis-card"><div class="analysis-label">확인등급</div><div class="analysis-value">{grade}</div></div>
              <div class="analysis-card"><div class="analysis-label">현장방문 필요도</div><div class="analysis-value">{visit}</div></div>
              <div class="analysis-card"><div class="analysis-label">위험신호</div><div class="analysis-value">{len(deductions)}건</div></div>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("#### 상세 위험신호")
            if deductions:
                for idx, (reason, pts) in enumerate(deductions, start=1):
                    st.markdown(
                        f'<div class="risk-item"><div class="risk-icon">{idx}</div>'
                        f'<div>{reason}</div><div class="risk-score">-{pts}점</div></div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<div class="success-item">특이 위험신호가 확인되지 않았습니다.</div>', unsafe_allow_html=True)

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

    st.markdown('</div>', unsafe_allow_html=True)

with tabs[2]:
    st.markdown(f"""
    <div class="executive-hero">
      <div class="hero-layout">
        <div>
          <div class="eyebrow"><span class="eyebrow-line"></span>Service Guide</div>
          <h1>자주 묻는 질문</h1>
          <p>서비스 역할, 적용 범위, 한계 및 실제 은행업무 도입방식을 정리했습니다.</p>
        </div>
        <div><img class="hero-character" src="{IM_CHARACTER_BLUE}" alt="iM 캐릭터"></div>
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
        st.markdown(f'<div class="qna-card"><strong>Q. {q}</strong><p>A. {a}</p></div>', unsafe_allow_html=True)
