
import base64
import json
from pathlib import Path
from datetime import date

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

def image_uri(name: str) -> str:
    path = ASSETS / name
    return "data:image/png;base64," + base64.b64encode(path.read_bytes()).decode("ascii")

CHAR_BLUE = image_uri("im_character_blue.png")
CHAR_SKY = image_uri("im_character_sky.png")
CASE1 = image_uri("case2_after.png")
CASE2 = image_uri("case1_after.png")
CASE3 = image_uri("case3_submit.png")

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
    rules = [
        (not checks["visible_change"], "시설 변화 미확인", 30),
        (checks["progress_mismatch"], "신고 공정률과 영상 변화 불일치", 25),
        (not checks["gps_exists"], "현장사진 GPS 정보 없음", 10),
        (not checks["exif_exists"], "현장사진 촬영정보 없음", 5),
        (checks["editing_suspected"], "이미지 편집·생성 의심 신호", 20),
        (not checks["spatial_match"], "공간영상과 제출사진 구조 불일치", 30),
        (checks["duplicate_suspected"], "동일·유사 이미지 재사용 의심", 20),
        (checks["old_satellite"], "공간영상 촬영일 경과", 10),
        (checks["low_quality"], "영상 판독 품질 낮음", 5),
    ]
    for cond, label, pts in rules:
        if cond:
            deductions.append((label, pts))
    missing_docs = [k for k, v in documents.items() if not v]
    for doc in missing_docs:
        deductions.append((f"핵심서류 누락: {doc}", 10))

    score = max(0, 100 - sum(v for _, v in deductions))
    if score >= 80:
        return score, "A", "낮음", "원격확인 가능", deductions, missing_docs
    if score >= 50:
        return score, "B", "중간", "추가 증빙 후 재검토", deductions, missing_docs
    return score, "C", "높음", "현장방문 권고", deductions, missing_docs

st.markdown("""
<style>
:root{
  --mint:#19b99c;
  --mint-dark:#078a76;
  --mint-soft:#eef9f6;
  --ink:#202426;
  --muted:#657276;
  --line:#e4ece9;
  --bg:#f7faf9;
}
html,body,[class*="css"]{
  font-family:Pretendard,"Noto Sans KR",-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;
}
.stApp{background:var(--bg);color:var(--ink);}
header[data-testid="stHeader"]{height:0;background:transparent;}
#MainMenu,footer{visibility:hidden;}
.block-container{max-width:none;padding:0 0 48px 0;}
.app-header{
  position:sticky;top:0;z-index:1000;height:66px;background:#fff;
  border-bottom:1px solid var(--line);display:grid;grid-template-columns:210px 1fr 260px;
  align-items:center;padding:0 30px;
}
.logo{display:flex;align-items:center;gap:10px;}
.logo-mark{
  width:34px;height:30px;border-radius:4px 12px 4px 12px;
  background:linear-gradient(135deg,#43d9bb,#1dba9c);color:#fff;
  display:grid;place-items:center;font-weight:900;font-size:13px;
}
.logo strong{font-size:20px;letter-spacing:-1px;color:#353b3d;}
.user-zone{justify-self:end;color:#303638;font-size:13px;}
.user-zone::before{content:"♧   ?   │";font-size:18px;letter-spacing:10px;margin-right:10px;}
div[data-baseweb="tab-list"]{
  position:sticky;top:0;z-index:1001;height:66px;margin-top:-66px;
  padding-left:250px;gap:46px;align-items:center;background:transparent;
}
button[data-baseweb="tab"]{
  height:66px;padding:0!important;border:none!important;border-radius:0!important;
  background:transparent!important;color:#171c1e!important;font-size:16px!important;font-weight:700!important;
}
button[data-baseweb="tab"][aria-selected="true"]{
  color:#078d78!important;border-bottom:4px solid #20bfa2!important;
}
.hero{
  min-height:175px;padding:38px 45px 31px;display:grid;
  grid-template-columns:430px minmax(420px,1fr) 310px;gap:28px;align-items:center;
  background:
    radial-gradient(circle at 66% 77%,rgba(36,195,165,.10) 0 12px,transparent 13px),
    radial-gradient(circle at 99% 56%,rgba(36,195,165,.12) 0 110px,transparent 111px),
    linear-gradient(90deg,#f0fbf8 0%,#f9fcfb 48%,#eaf8f4 100%);
  border-bottom:1px solid #dce9e5;
}
.hero h1{margin:0 0 9px;font-size:40px;letter-spacing:-2px;}
.hero-sub{color:#028d78;font-size:14px;font-weight:750;}
.hero-copy{font-size:14px;line-height:1.85;color:#202a2c;}
.hero-chars{display:flex;justify-content:flex-end;align-items:flex-end;padding-right:25px;}
.hero-chars img{max-height:132px;width:auto;filter:drop-shadow(0 10px 15px rgba(24,76,66,.10));}
.hero-chars img+img{margin-left:-21px;}
.page{padding:23px 28px 0;}
.card{
  background:#fff;border:1px solid #e3eae8;border-radius:16px;padding:14px;
  box-shadow:0 2px 9px rgba(18,67,58,.035);
}
.heading{display:flex;align-items:center;gap:10px;margin-bottom:12px;}
.badge{
  width:30px;height:30px;border-radius:7px;background:linear-gradient(135deg,#1bb297,#078875);
  color:#fff;display:grid;place-items:center;font-size:13px;font-weight:900;
}
.heading h2{margin:0;font-size:18px;letter-spacing:-.6px;}
.about{display:grid;grid-template-columns:1.05fr 2.35fr;gap:18px;}
.about-copy{padding:9px 3px;font-size:13px;line-height:1.72;color:#273336;}
.cap-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:8px;}
.cap{
  min-height:112px;padding:15px 9px;text-align:center;border:1px solid #e0ece8;border-radius:8px;
  background:linear-gradient(180deg,#f5fbf9,#edf7f4);
}
.cap .ico{height:35px;color:#088d77;font-size:29px;margin-bottom:9px;}
.cap strong{display:block;font-size:13px;margin-bottom:6px;color:#273033;}
.cap span{font-size:10px;line-height:1.47;color:#657477;}
.mid{display:grid;grid-template-columns:1.83fr 1fr;gap:14px;margin-top:14px;}
.flow{display:grid;grid-template-columns:1fr 29px 1fr 29px 1fr 29px 1fr 29px 1fr;gap:5px;align-items:center;}
.flow-step{
  min-height:204px;padding:18px 10px;text-align:center;border:1px solid #ddebe7;border-radius:8px;
  background:linear-gradient(180deg,#f3faf8,#edf7f4);
}
.flow-step strong{display:block;color:#087a69;font-size:13px;margin-bottom:20px;}
.flow-step .ico{height:51px;color:#0a8e79;font-size:40px;margin:6px 0 18px;}
.flow-step span{font-size:10px;line-height:1.58;color:#5b696c;}
.arrow{font-size:27px;color:#9aa9ac;text-align:center;}
.feedback{
  margin:8px 75px 0;padding:7px 0 4px;text-align:center;color:#087b6b;font-size:12px;font-weight:750;
  border-left:2px solid #356b78;border-right:2px solid #356b78;border-bottom:2px solid #356b78;border-radius:0 0 13px 13px;
}
.case{display:grid;grid-template-columns:112px 1fr;gap:11px;align-items:center;padding:7px;margin-bottom:8px;
  border:1px solid #e1ece8;border-radius:8px;background:linear-gradient(90deg,#f8fbfa,#eff7f4);}
.case img{width:112px;height:76px;object-fit:cover;border-radius:6px;}
.case strong{display:block;font-size:12px;line-height:1.35;margin-bottom:3px;}
.case p{margin:0 0 5px;font-size:9.8px;line-height:1.5;color:#5e6c6f;}
.case a{font-size:9.8px;font-weight:750;color:#078d78!important;text-decoration:none;}
.more{
  display:block;width:150px;margin:8px auto 0;padding:7px 10px;border:1px solid #cbddd7;border-radius:999px;
  color:#526568!important;text-align:center;font-size:10px;text-decoration:none;
}
.bottom{display:grid;grid-template-columns:1fr 1fr 1.05fr;gap:14px;margin-top:14px;}
.analysis{display:grid;grid-template-columns:1fr 1fr;gap:9px 14px;padding:5px 4px;}
.analysis div{font-size:10.5px;color:#405154;}
.analysis div::before{content:"●";color:#13a58b;font-size:8px;margin-right:8px;}
.effects{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.effect{min-height:78px;padding:11px 7px;text-align:center;border:1px solid #dfece8;border-radius:8px;background:#eff8f5;}
.effect span{display:block;font-size:10px;color:#4b5b5e;}
.effect b{display:block;font-size:22px;color:#078e78;margin:8px 0 4px;}
.security{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;}
.sec{text-align:center;font-size:9.8px;line-height:1.42;color:#48585b;}
.sec .ico{height:34px;font-size:28px;color:#078d78;margin-bottom:7px;}
.sec strong{display:block;font-size:11px;margin-bottom:2px;color:#2f3b3e;}
.workspace{padding:24px 28px;}
.workspace-card{background:#fff;border:1px solid var(--line);border-radius:16px;padding:22px;margin-bottom:16px;}
.notice{background:#eef9f6;border:1px solid #d7ebe5;border-radius:12px;padding:12px 14px;color:#49605d;font-size:12px;}
.metric-row{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;}
.metric{background:#f3faf8;border:1px solid #deece8;border-radius:12px;padding:16px;}
.metric label{font-size:11px;color:#69777a;}
.metric b{display:block;font-size:26px;color:#087b6b;margin-top:7px;}
@media(max-width:1150px){
  .hero{grid-template-columns:330px 1fr 250px}.cap-grid{grid-template-columns:repeat(3,1fr)}
  .mid,.bottom{grid-template-columns:1fr}
}
@media(max-width:800px){
  .app-header{grid-template-columns:160px 1fr 130px}
  div[data-baseweb="tab-list"]{padding-left:190px;gap:24px}
  .hero{grid-template-columns:1fr;padding:28px 18px}.hero-chars{justify-content:center;padding:0}
  .about{grid-template-columns:1fr}.cap-grid{grid-template-columns:1fr 1fr}.page{padding:16px 12px 0}
  .flow{grid-template-columns:1fr}.arrow{transform:rotate(90deg)}.feedback{margin:8px 10px 0}
}
</style>
""", unsafe_allow_html=True)

st.markdown("""
<div class="app-header">
  <div class="logo"><div class="logo-mark">iM</div><strong>iM뱅크</strong></div>
  <div></div>
  <div class="user-zone">심사역 김IM⌄</div>
</div>
""", unsafe_allow_html=True)

tabs = st.tabs(["기능소개", "LoanScope AX", "QnA"])

with tabs[0]:
    st.markdown(f"""
    <section class="hero">
      <div>
        <h1>기능소개</h1>
        <div class="hero-sub">AI와 데이터로 더 정확하고, 더 빠르고, 더 공정한 여신심사</div>
      </div>
      <div class="hero-copy">
        LoanScope AX는 위성·드론·현장사진·서류 데이터를 AI로 분석하여<br>
        담보의 실재성과 사업의 안정성을 입체적으로 검증하는<br>
        차세대 여신심사 지원 시스템입니다.
      </div>
      <div class="hero-chars">
        <img src="{CHAR_BLUE}" alt="iM 캐릭터">
        <img src="{CHAR_SKY}" alt="iM 캐릭터">
      </div>
    </section>

    <main class="page">
      <section class="card">
        <div class="heading"><div class="badge">01</div><h2>LoanScope AX란?</h2></div>
        <div class="about">
          <div class="about-copy">
            LoanScope AX는 위성·드론·현장사진·서류 데이터를 인공지능으로 분석하여
            담보의 실재성, 경작·운영의 지속성, 제출서류의 적정성을 종합적으로 검증하는
            AI 기반 여신심사 지원 솔루션입니다.
          </div>
          <div class="cap-grid">
            <div class="cap"><div class="ico">◉</div><strong>AI 기반 분석</strong><span>영상·이미지·텍스트 데이터를<br>AI가 정밀 분석하여<br>위험 신호를 도출합니다.</span></div>
            <div class="cap"><div class="ico">◫</div><strong>다중 데이터 융합</strong><span>위성·드론·현장사진·서류·<br>공공데이터를 융합하여<br>입체적으로 검증합니다.</span></div>
            <div class="cap"><div class="ico">◴</div><strong>심사 효율 향상</strong><span>자동화 분석으로<br>심사 시간을 단축하고<br>업무 생산성을 높입니다.</span></div>
            <div class="cap"><div class="ico">♢</div><strong>리스크 예방</strong><span>사전 위험 신호 탐지로<br>부실 여신 가능성을 낮추고<br>건전성을 강화합니다.</span></div>
            <div class="cap"><div class="ico">▤</div><strong>근거 기반 심사</strong><span>정량화된 근거와 시각화된<br>분석 결과로 심사 신뢰도와<br>일관성을 높입니다.</span></div>
          </div>
        </div>
      </section>

      <div class="mid">
        <section class="card">
          <div class="heading"><div class="badge">02</div><h2>LoanScope AX 흐름</h2></div>
          <div class="flow">
            <div class="flow-step"><strong>1. 데이터 수집</strong><div class="ico">⌁</div><span>위성영상, 드론영상, 현장사진,<br>제출서류, 공공데이터 수집</span></div>
            <div class="arrow">→</div>
            <div class="flow-step"><strong>2. 데이터 전처리</strong><div class="ico">◫</div><span>데이터 정제 및 표준화,<br>위치·시간 정보 정합</span></div>
            <div class="arrow">→</div>
            <div class="flow-step"><strong>3. AI 분석</strong><div class="ico">AI</div><span>이미지 변화 탐지, 객체 인식,<br>텍스트 분석으로 위험 신호 도출</span></div>
            <div class="arrow">→</div>
            <div class="flow-step"><strong>4. 위험도 평가</strong><div class="ico">◔</div><span>위험 요소별 점수화 및<br>종합 위험도 산출</span></div>
            <div class="arrow">→</div>
            <div class="flow-step"><strong>5. 심사 결과 제공</strong><div class="ico">▣</div><span>심사 등급, 현장방문 권고,<br>추가자료 요청, 심사보조의견 제공</span></div>
          </div>
          <div class="feedback">피드백 학습을 통한 모델 고도화</div>
        </section>

        <section class="card">
          <div class="heading"><div class="badge">03</div><h2>근거 및 활용 사례</h2></div>
          <div class="case">
            <img src="{CASE1}" alt="농지 공간영상">
            <div><strong>농림축산식품부: 위성영상으로 실제 경작 여부 점검</strong><p>위성·드론 영상을 활용하여 농업경영체 등록 여부와 실제 경작 여부를 점검합니다.</p><a href="https://www.mafra.go.kr/bbs/home/792/596131/download.do" target="_blank">농림축산식품부 공식자료 ↗</a></div>
          </div>
          <div class="case">
            <img src="{CASE2}" alt="건축물 공간영상">
            <div><strong>국토교통부: 공간정보·건축물대장 기반 검증</strong><p>영상지도, 건축물대장, 토지이용계획 정보를 결합해 대상지와 시설정보를 교차검증할 수 있습니다.</p><a href="https://www.vworld.kr/dev/v4dv_wmtsguide_s001.do" target="_blank">VWorld 공식 가이드 ↗</a></div>
          </div>
          <div class="case">
            <img src="{CASE3}" alt="위성 데이터 분석">
            <div><strong>Copernicus: Sentinel-2 기반 토지 변화 모니터링</strong><p>무료 위성 데이터를 활용해 농지와 대규모 시설의 시계열 변화를 분석할 수 있습니다.</p><a href="https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2" target="_blank">Copernicus 공식 페이지 ↗</a></div>
          </div>
          <a class="more" href="https://www.data.go.kr/" target="_blank">더 많은 공공데이터 보기 〉</a>
        </section>
      </div>

      <div class="bottom">
        <section class="card">
          <div class="heading"><div class="badge">04</div><h2>주요 분석 항목</h2></div>
          <div class="analysis">
            <div>이미지 변화 분석</div><div>서류 진위·일관성 검증</div>
            <div>객체 탐지</div><div>위치·면적 정확도 검증</div>
            <div>경작지·시설 적합성 분석</div><div>위험 신호 종합 평가</div>
          </div>
        </section>

        <section class="card">
          <div class="heading"><div class="badge">05</div><h2>기대 효과</h2></div>
          <div class="effects">
            <div class="effect"><span>심사 시간</span><b>단축</b><span>PoC 검증 목표</span></div>
            <div class="effect"><span>위험 탐지 정확도</span><b>향상</b><span>PoC 검증 목표</span></div>
            <div class="effect"><span>부실 여신 예방</span><b>개선</b><span>PoC 검증 목표</span></div>
          </div>
        </section>

        <section class="card">
          <div class="heading"><div class="badge">06</div><h2>보안 및 개인정보 보호</h2></div>
          <div class="security">
            <div class="sec"><div class="ico">▣</div><strong>데이터 암호화</strong>전송 및 저장 데이터<br>암호화 적용</div>
            <div class="sec"><div class="ico">♢</div><strong>접근 통제</strong>역할 기반 접근 통제 및<br>권한 관리</div>
            <div class="sec"><div class="ico">◯</div><strong>개인정보 비식별화</strong>개인정보 최소화 처리 및<br>안전한 관리</div>
          </div>
        </section>
      </div>
    </main>
    """, unsafe_allow_html=True)

with tabs[1]:
    cases = load_cases()
    st.markdown("""
    <div class="workspace">
      <div class="notice">
        본 서비스는 대출 승인·거절 또는 부정행위를 자동 판정하지 않습니다.
        공간정보와 제출자료의 불일치 신호를 제공하는 직원용 심사보조 도구입니다.
      </div>
    </div>
    """, unsafe_allow_html=True)

    case_name = st.selectbox("연결 심사사례", list(cases.keys()))
    case = cases[case_name]

    st.markdown('<div class="workspace">', unsafe_allow_html=True)
    st.markdown(
        f"""<div class="workspace-card">
        <b>심사 대상</b> {case["company_name"]}<br>
        <b>연결품의번호</b> {case.get("linked_approval_no","XXXXXXXXXXXXXXXX")} &nbsp;&nbsp;
        <b>연결신청번호</b> {case.get("linked_application_no","XXXXXXXXXXXXXXXX")}
        </div>""",
        unsafe_allow_html=True,
    )

    with st.container():
        c1, c2 = st.columns(2)
        with c1:
            company_name = st.text_input("기업명", case["company_name"])
            industry = st.text_input("업종", case["industry"])
            loan_amount = st.number_input("신청금액(원)", min_value=0, value=int(case["loan_amount"]), step=10000000)
            loan_purpose = st.text_input("자금용도", case["loan_purpose"])
        with c2:
            address = st.text_input("사업장 주소", case["address"])
            start_date = st.date_input("공사 시작일", value=date.fromisoformat(case["start_date"]))
            end_date = st.date_input("공사 예정 완료일", value=date.fromisoformat(case["end_date"]))
            declared_progress = st.slider("차주 신고 공정률", 0, 100, int(case["declared_progress"]))

    st.markdown("### 제출서류 확인")
    doc_cols = st.columns(2)
    documents = {}
    for i, (doc, default) in enumerate(case["documents"].items()):
        with doc_cols[i % 2]:
            documents[doc] = st.checkbox(doc, value=default, key=f"{case_name}_{doc}")

    st.markdown("### 공간영상·현장사진 비교")
    cols = st.columns(3)
    labels = ["신청 전 공간영상", "최근 공간영상", "차주 제출 현장사진"]
    for col, label, name in zip(cols, labels, case["images"]):
        with col:
            st.caption(label)
            st.image(str(ASSETS / name), use_container_width=True)

    uploaded = st.file_uploader("차주 제출 현장사진 교체", type=["jpg","jpeg","png"])
    if uploaded:
        exif = extract_exif(uploaded)
        st.json({
            "촬영일시": exif["촬영일시"] or "확인 불가",
            "GPS": "확인" if exif["GPS"] else "없음",
            "편집 프로그램": exif["편집 프로그램"] or "기록 없음",
        })

    st.markdown("### 자동 분석·담당자 확인")
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

    if st.button("현장확인 분석 실행", use_container_width=True):
        st.session_state.result = calculate_score(checks, documents)

    if "result" in st.session_state:
        score, grade, visit, recommendation, deductions, missing_docs = st.session_state.result
        st.markdown(
            f"""<div class="metric-row">
            <div class="metric"><label>확인 신뢰도</label><b>{score}점</b></div>
            <div class="metric"><label>확인등급</label><b>{grade}</b></div>
            <div class="metric"><label>현장방문 필요도</label><b>{visit}</b></div>
            <div class="metric"><label>위험신호</label><b>{len(deductions)}건</b></div>
            </div>""",
            unsafe_allow_html=True,
        )
        st.markdown("#### 상세 위험신호")
        if deductions:
            for reason, pts in deductions:
                st.write(f"- {reason} (-{pts}점)")
        else:
            st.success("특이 위험신호가 확인되지 않았습니다.")
        opinion = (
            f"{company_name}의 {loan_purpose} 관련 자료를 검토한 결과, "
            f"확인 신뢰도는 {score}점({grade}등급)이며, 권고 조치는 '{recommendation}'입니다."
        )
        st.text_area("심사보조 의견", opinion, height=130)
    st.markdown("</div>", unsafe_allow_html=True)

with tabs[2]:
    st.markdown('<div class="workspace">', unsafe_allow_html=True)
    st.markdown("## 자주 묻는 질문")
    qnas = [
        ("위성사진만으로 대출을 승인하거나 거절하나요?", "아닙니다. 추가 확인이 필요한 위험신호를 제공하는 심사보조 도구입니다."),
        ("탁상감정과 무엇이 다른가요?", "탁상감정은 담보가치 검토, LoanScope AX는 사업장과 시설의 존재·변화 확인이 목적입니다."),
        ("현장점검을 완전히 대체할 수 있나요?", "전면 대체가 아니라 현장방문 대상을 선별하는 것이 1차 목적입니다."),
        ("AI 생성 이미지는 어떻게 확인하나요?", "EXIF·GPS·편집정보·중복 이미지·공간구조 일치 여부를 종합 검토합니다."),
    ]
    for q, a in qnas:
        with st.expander(q):
            st.write(a)
    st.markdown("</div>", unsafe_allow_html=True)
