import base64
import json
from datetime import date
from pathlib import Path

import streamlit as st
from PIL import ExifTags, Image

BASE = Path(__file__).parent
ASSETS = BASE / "assets"

st.set_page_config(page_title="LoanScope AX", page_icon="🛰️", layout="wide", initial_sidebar_state="collapsed")

def uri(name: str) -> str:
    path = ASSETS / name
    mime = "image/svg+xml" if path.suffix == ".svg" else "image/png"
    return f"data:{mime};base64," + base64.b64encode(path.read_bytes()).decode()

@st.cache_data
def load_cases():
    return json.loads((BASE / "sample_cases.json").read_text(encoding="utf-8"))

def extract_exif(uploaded):
    result = {"촬영일시": None, "GPS": False, "편집 프로그램": None}
    try:
        exif = Image.open(uploaded).getexif()
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
    for condition, label, points in rules:
        if condition:
            deductions.append((label, points))
    for doc, submitted in documents.items():
        if not submitted:
            deductions.append((f"핵심서류 누락: {doc}", 10))
    score = max(0, 100 - sum(points for _, points in deductions))
    if score >= 80:
        return score, "A", "낮음", "원격확인 가능", deductions
    if score >= 50:
        return score, "B", "중간", "추가 증빙 후 재검토", deductions
    return score, "C", "높음", "현장방문 권고", deductions

CHAR_BLUE = uri("im_character_blue.png")
CHAR_SKY = uri("im_character_sky.png")
THUMB_1 = uri("case2_after.png")
THUMB_2 = uri("case1_after.png")
THUMB_3 = uri("case3_submit.png")
ICON_NAMES = ["ai","data","clock","shield","doc","collect","preprocess","risk","result","lock","access","mask"]
ICONS = {name: uri(f"{name}.svg") for name in ICON_NAMES}

st.markdown(f"<style>{(BASE / 'styles.css').read_text(encoding='utf-8')}</style>", unsafe_allow_html=True)
st.markdown('<div class="topbar"><div class="brand"><div class="brandmark">iM</div><b>iM뱅크</b></div><div></div><div class="user">심사역 김IM⌄</div></div>', unsafe_allow_html=True)
menu = st.radio("메뉴", ["기능소개", "LoanScope AX", "QnA"], horizontal=True, label_visibility="collapsed")

if menu == "기능소개":
    st.markdown(f'''<section class="hero"><div><h1>기능소개</h1><div class="hero-sub">AI와 데이터로 더 정확하고, 더 빠르고, 더 공정한 여신심사</div></div><div class="hero-copy">LoanScope AX는 위성·드론·현장사진·서류 데이터를 AI로 분석하여<br>담보의 실재성과 사업의 안정성을 입체적으로 검증하는<br>차세대 여신심사 지원 시스템입니다.</div><div class="chars"><img src="{CHAR_BLUE}" alt="iM 캐릭터"><img src="{CHAR_SKY}" alt="iM 캐릭터"></div></section>''', unsafe_allow_html=True)

    caps = [
        ("ai","AI 기반 분석","영상·이미지·텍스트 데이터를<br>AI가 정밀 분석하여<br>위험 신호를 도출합니다."),
        ("data","다중 데이터 융합","위성·드론·현장사진·서류·<br>공공데이터를 융합하여<br>입체적으로 검증합니다."),
        ("clock","심사 효율 향상","자동화 분석으로<br>심사 시간을 단축하고<br>업무 생산성을 높입니다."),
        ("shield","리스크 예방","사전 위험 신호 탐지로<br>부실 여신 가능성을 낮추고<br>건전성을 강화합니다."),
        ("doc","근거 기반 심사","정량화된 근거와 시각화된<br>분석 결과로 신뢰도와<br>일관성을 높입니다."),
    ]
    caps_html = ''.join(f'<div class="cap"><img src="{ICONS[i]}" alt=""><strong>{t}</strong><span>{b}</span></div>' for i,t,b in caps)
    steps = [
        ("1. 데이터 수집","collect","위성영상, 드론영상, 현장사진,<br>제출서류, 공공데이터 수집"),
        ("2. 데이터 전처리","preprocess","데이터 정제 및 표준화,<br>위치·시간 정보 정합"),
        ("3. AI 분석","ai","이미지 변화 탐지, 객체 인식,<br>텍스트 분석으로 위험 신호 도출"),
        ("4. 위험도 평가","risk","위험 요소별 점수화 및<br>종합 위험도 산출"),
        ("5. 심사 결과 제공","result","심사 등급, 현장방문 권고,<br>추가자료 요청, 심사보조의견 제공"),
    ]
    parts=[]
    for idx,(t,i,b) in enumerate(steps):
        parts.append(f'<div class="step"><strong>{t}</strong><img src="{ICONS[i]}" alt=""><span>{b}</span></div>')
        if idx < len(steps)-1: parts.append('<div class="arrow">→</div>')
    flow_html=''.join(parts)

    st.markdown(f'''<main class="page"><section class="card"><div class="heading"><div class="badge">01</div><h2>LoanScope AX란?</h2></div><div class="about"><div class="aboutcopy">LoanScope AX는 위성·드론·현장사진·서류 데이터를 인공지능으로 분석하여 담보의 실재성, 경작·운영의 지속성, 제출서류의 적정성을 종합적으로 검증하는 AI 기반 여신심사 지원 솔루션입니다.</div><div class="capgrid">{caps_html}</div></div></section><div class="mid"><section class="card"><div class="heading"><div class="badge">02</div><h2>LoanScope AX 흐름</h2></div><div class="flow">{flow_html}</div><div class="feedback">피드백 학습을 통한 모델 고도화</div></section><section class="card"><div class="heading"><div class="badge">03</div><h2>근거 및 활용 사례</h2></div><div class="case"><img src="{THUMB_1}" alt="농지 공간영상"><div><strong>농림축산식품부: 위성영상으로 실제 경작 여부 점검</strong><p>위성·드론 영상을 활용하여 농업경영체 등록 여부와 실제 경작 여부를 점검합니다.</p><a href="https://www.mafra.go.kr/bbs/home/792/596131/download.do" target="_blank">농림축산식품부 공식자료 ↗</a></div></div><div class="case"><img src="{THUMB_2}" alt="건축물 공간영상"><div><strong>국토교통부: 공간정보·건축물대장 기반 검증</strong><p>영상지도, 건축물대장, 토지이용계획 정보를 결합해 대상지와 시설정보를 교차검증할 수 있습니다.</p><a href="https://www.vworld.kr/dev/v4dv_wmtsguide_s001.do" target="_blank">VWorld 공식 가이드 ↗</a></div></div><div class="case"><img src="{THUMB_3}" alt="위성 데이터 분석"><div><strong>Copernicus: Sentinel-2 기반 토지 변화 모니터링</strong><p>무료 위성 데이터를 활용해 농지와 대규모 시설의 시계열 변화를 분석할 수 있습니다.</p><a href="https://dataspace.copernicus.eu/data-collections/copernicus-sentinel-missions/sentinel-2" target="_blank">Copernicus 공식 페이지 ↗</a></div></div><a class="more" href="https://www.data.go.kr/" target="_blank">더 많은 공공데이터 보기 〉</a></section></div><div class="bottom"><section class="card"><div class="heading"><div class="badge">04</div><h2>주요 분석 항목</h2></div><div class="analysis"><div>이미지 변화 분석</div><div>서류 진위·일관성 검증</div><div>객체 탐지</div><div>위치·면적 정확도 검증</div><div>경작지·시설 적합성 분석</div><div>위험 신호 종합 평가</div></div></section><section class="card"><div class="heading"><div class="badge">05</div><h2>기대 효과</h2></div><div class="effects"><div class="effect"><span>심사 시간</span><b>단축</b><span>PoC 검증 목표</span></div><div class="effect"><span>위험 탐지 정확도</span><b>향상</b><span>PoC 검증 목표</span></div><div class="effect"><span>부실 여신 예방</span><b>개선</b><span>PoC 검증 목표</span></div></div></section><section class="card"><div class="heading"><div class="badge">06</div><h2>보안 및 개인정보 보호</h2></div><div class="security"><div class="sec"><img src="{ICONS['lock']}" alt=""><strong>데이터 암호화</strong>전송 및 저장 데이터<br>암호화 적용</div><div class="sec"><img src="{ICONS['access']}" alt=""><strong>접근 통제</strong>역할 기반 접근 통제 및<br>권한 관리</div><div class="sec"><img src="{ICONS['mask']}" alt=""><strong>개인정보 비식별화</strong>개인정보 최소화 처리 및<br>안전한 관리</div></div></section></div></main>''', unsafe_allow_html=True)

elif menu == "LoanScope AX":
    cases=load_cases()
    st.markdown('<div class="workspace"><div class="notice">본 서비스는 대출 승인·거절 또는 부정행위를 자동 판정하지 않습니다. 공간정보와 제출자료의 불일치 신호를 제공하는 직원용 심사보조 도구입니다.</div></div>',unsafe_allow_html=True)
    case_name=st.selectbox("연결 심사사례",list(cases.keys())); case=cases[case_name]
    st.markdown('<div class="workspace">',unsafe_allow_html=True)
    st.markdown(f'<div class="workcard"><b>심사 대상</b> {case["company_name"]}<br><b>연결품의번호</b> {case.get("linked_approval_no","XXXXXXXXXXXXXXXX")} &nbsp;&nbsp; <b>연결신청번호</b> {case.get("linked_application_no","XXXXXXXXXXXXXXXX")}</div>',unsafe_allow_html=True)
    l,r=st.columns(2)
    with l:
        company_name=st.text_input("기업명",case["company_name"]);st.text_input("업종",case["industry"]);st.number_input("신청금액(원)",min_value=0,value=int(case["loan_amount"]),step=10_000_000);loan_purpose=st.text_input("자금용도",case["loan_purpose"])
    with r:
        st.text_input("사업장 주소",case["address"]);st.date_input("공사 시작일",value=date.fromisoformat(case["start_date"]));st.date_input("공사 예정 완료일",value=date.fromisoformat(case["end_date"]));st.slider("차주 신고 공정률",0,100,int(case["declared_progress"]))
    st.markdown("### 제출서류 확인"); cols=st.columns(2); documents={}
    for idx,(doc,submitted) in enumerate(case["documents"].items()):
        with cols[idx%2]: documents[doc]=st.checkbox(doc,value=submitted,key=f"{case_name}_{doc}")
    st.markdown("### 공간영상·현장사진 비교"); cols=st.columns(3)
    for col,label,name in zip(cols,["신청 전 공간영상","최근 공간영상","차주 제출 현장사진"],case["images"]):
        with col: st.caption(label);st.image(str(ASSETS/name),use_container_width=True)
    uploaded=st.file_uploader("차주 제출 현장사진 교체",type=["jpg","jpeg","png"])
    if uploaded: st.json(extract_exif(uploaded))
    st.markdown("### 자동 분석·담당자 확인"); checks=dict(case["checks"]);l,r=st.columns(2)
    with l:
        checks["visible_change"]=st.toggle("신규 시설 변화 확인",value=checks["visible_change"]);checks["progress_mismatch"]=st.toggle("신고 공정률과 영상 변화 불일치",value=checks["progress_mismatch"]);checks["spatial_match"]=st.toggle("제출사진과 대상지 구조 일치",value=checks["spatial_match"]);checks["low_quality"]=st.toggle("영상 품질 부족",value=checks["low_quality"])
    with r:
        checks["gps_exists"]=st.toggle("GPS 정보 확인",value=checks["gps_exists"]);checks["exif_exists"]=st.toggle("촬영일시 정보 확인",value=checks["exif_exists"]);checks["editing_suspected"]=st.toggle("편집·생성 의심 신호",value=checks["editing_suspected"]);checks["duplicate_suspected"]=st.toggle("유사 이미지 중복 의심",value=checks["duplicate_suspected"])
    if st.button("현장확인 분석 실행",use_container_width=True): st.session_state["result"]=calculate_score(checks,documents)
    if "result" in st.session_state:
        score,grade,visit,recommendation,deductions=st.session_state["result"]
        st.markdown(f'<div class="metrics"><div class="metric"><small>확인 신뢰도</small><b>{score}점</b></div><div class="metric"><small>확인등급</small><b>{grade}</b></div><div class="metric"><small>현장방문 필요도</small><b>{visit}</b></div><div class="metric"><small>위험신호</small><b>{len(deductions)}건</b></div></div>',unsafe_allow_html=True)
        st.markdown("#### 상세 위험신호")
        for reason,points in deductions: st.write(f"- {reason} (-{points}점)")
        st.text_area("심사보조 의견",f"{company_name}의 {loan_purpose} 관련 자료를 검토한 결과, 확인 신뢰도는 {score}점({grade}등급)이며 권고 조치는 {recommendation}입니다.",height=130)
    st.markdown('</div>',unsafe_allow_html=True)
else:
    st.markdown('<div class="workspace"><h2>자주 묻는 질문</h2>',unsafe_allow_html=True)
    for q,a in [("위성사진만으로 대출을 승인하거나 거절하나요?","아닙니다. 추가 확인이 필요한 위험신호를 제공하는 심사보조 도구입니다."),("탁상감정과 무엇이 다른가요?","탁상감정은 담보가치 검토, LoanScope AX는 사업장과 시설의 존재·변화 확인이 목적입니다."),("현장점검을 완전히 대체할 수 있나요?","전면 대체가 아니라 현장방문 대상을 선별하는 것이 1차 목적입니다."),("AI 생성 이미지는 어떻게 확인하나요?","EXIF·GPS·편집정보·중복 이미지·공간구조 일치 여부를 종합 검토합니다.")]:
        with st.expander(q): st.write(a)
    st.markdown('</div>',unsafe_allow_html=True)
