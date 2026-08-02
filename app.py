import base64
import json
from datetime import date
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components
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

with st.container(key="app_header"):
    brand_col, menu_col, user_col = st.columns([1.15, 3.2, 1.25], vertical_alignment="center")
    with brand_col:
        st.markdown('<div class="brand"><div class="brandmark">iM</div><b>iM뱅크</b></div>', unsafe_allow_html=True)
    with menu_col:
        menu = st.radio(
            "메뉴",
            ["기능소개", "LoanScope AX", "QnA"],
            horizontal=True,
            label_visibility="collapsed",
            key="main_navigation",
        )
    with user_col:
        st.markdown('<div class="user">심사역 김IM⌄</div>', unsafe_allow_html=True)

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
    cases = load_cases()

    with st.container(key="loan_page"):
        st.markdown(
            '<div class="notice">본 서비스는 대출 승인·거절 또는 부정행위를 자동 판정하지 않습니다. '
            '공간정보와 제출자료의 불일치 신호를 제공하는 직원용 심사보조 도구입니다.</div>',
            unsafe_allow_html=True,
        )

        case_name = st.selectbox("연결 심사사례", list(cases.keys()), key="loan_case")
        case = cases[case_name]

        with st.container(key="loan_workspace"):
            nav_col, main_col = st.columns([0.19, 0.81], gap="large")
    
            with nav_col:
                with st.container(key="loan_nav"):
                    st.markdown(
                        f'''<nav class="loan-nav" aria-label="LoanScope AX 단계">
                          <div class="loan-nav-case">
                            <strong>{case["company_name"]}</strong>
                            <span>{case["loan_purpose"]}</span>
                            <div class="loan-nav-meta">
                              <div><small>고객번호</small><b>{case.get("customer_no", "0000000")}</b></div>
                              <div><small>관련담보번호</small><b>{case.get("collateral_no", "000000000001")}</b></div>
                            </div>
                          </div>
                          <a id="loan-nav-1" class="loan-link active" href="#loan-step-1"><span class="n">1</span><span><b>기본정보</b><small>기업·대출·시설</small></span></a>
                          <a id="loan-nav-2" class="loan-link" href="#loan-step-2"><span class="n">2</span><span><b>서류확인</b><small>필수 증빙 점검</small></span></a>
                          <a id="loan-nav-3" class="loan-link" href="#loan-step-3"><span class="n">3</span><span><b>이미지 비교</b><small>공간영상·현장사진</small></span></a>
                          <a id="loan-nav-4" class="loan-link" href="#loan-step-4"><span class="n">4</span><span><b>위험신호</b><small>메타데이터·일치성</small></span></a>
                          <a id="loan-nav-5" class="loan-link" href="#loan-step-5"><span class="n">5</span><span><b>심사결과</b><small>등급·방문 권고</small></span></a>
                        </nav>''',
                        unsafe_allow_html=True,
                    )
    
            with main_col:
                st.markdown('<div id="loan-step-1" class="loan-section-anchor"></div><div class="loan-section-head"><div class="eyebrow">Step 01</div><h3>대출·시설 기본정보</h3><p>연결된 신청심사 건의 기업, 대출 및 공사 정보를 확인합니다.</p></div>', unsafe_allow_html=True)
                l, r = st.columns(2)
                with l:
                    company_name = st.text_input("기업명", case["company_name"])
                    st.text_input("업종", case["industry"])
                    st.number_input("신청금액(원)", min_value=0, value=int(case["loan_amount"]), step=10_000_000)
                    loan_purpose = st.text_input("자금용도", case["loan_purpose"])
                with r:
                    st.text_input("사업장 주소", case["address"])
                    st.date_input("공사 시작일", value=date.fromisoformat(case["start_date"]))
                    st.date_input("공사 예정 완료일", value=date.fromisoformat(case["end_date"]))
                    st.slider("차주 신고 공정률", 0, 100, int(case["declared_progress"]))
    
                st.markdown('<div id="loan-step-2" class="loan-section-anchor"></div><div class="loan-section-head"><div class="eyebrow">Step 02</div><h3>제출서류 확인</h3><p>시설자금의 목적과 공정단계에 필요한 핵심 증빙을 점검합니다.</p></div>', unsafe_allow_html=True)
                cols = st.columns(2)
                documents = {}
                for idx, (doc, submitted) in enumerate(case["documents"].items()):
                    with cols[idx % 2]:
                        documents[doc] = st.checkbox(doc, value=submitted, key=f"{case_name}_{doc}")
    
                st.markdown('<div id="loan-step-3" class="loan-section-anchor"></div><div class="loan-section-head"><div class="eyebrow">Step 03</div><h3>공간영상·현장사진 비교</h3><p>신청 전후 공간영상과 차주가 제출한 현장사진을 비교합니다.</p></div>', unsafe_allow_html=True)
                cols = st.columns(3)
                for col, label, name in zip(cols, ["신청 전 공간영상", "최근 공간영상", "차주 제출 현장사진"], case["images"]):
                    with col:
                        st.caption(label)
                        st.image(str(ASSETS / name), use_container_width=True)
                uploaded = st.file_uploader("차주 제출 현장사진 교체", type=["jpg", "jpeg", "png"])
                if uploaded:
                    st.json(extract_exif(uploaded))
    
                st.markdown('<div id="loan-step-4" class="loan-section-anchor"></div><div class="loan-section-head"><div class="eyebrow">Step 04</div><h3>자동 분석·위험신호 확인</h3><p>영상 변화, 메타데이터, 공간구조와 중복 이미지 신호를 확인합니다.</p></div>', unsafe_allow_html=True)
                checks = dict(case["checks"])
                l, r = st.columns(2)
                with l:
                    checks["visible_change"] = st.toggle("신규 시설 변화 확인", value=checks["visible_change"])
                    checks["progress_mismatch"] = st.toggle("신고 공정률과 영상 변화 불일치", value=checks["progress_mismatch"])
                    checks["spatial_match"] = st.toggle("제출사진과 대상지 구조 일치", value=checks["spatial_match"])
                    checks["low_quality"] = st.toggle("영상 품질 부족", value=checks["low_quality"])
                with r:
                    checks["gps_exists"] = st.toggle("GPS 정보 확인", value=checks["gps_exists"])
                    checks["exif_exists"] = st.toggle("촬영일시 정보 확인", value=checks["exif_exists"])
                    checks["editing_suspected"] = st.toggle("편집·생성 의심 신호", value=checks["editing_suspected"])
                    checks["duplicate_suspected"] = st.toggle("유사 이미지 중복 의심", value=checks["duplicate_suspected"])
    
                if st.button("현장확인 분석 실행", use_container_width=True):
                    st.session_state["result"] = calculate_score(checks, documents)
    
                st.markdown('<div id="loan-step-5" class="loan-section-anchor"></div><div class="loan-section-head"><div class="eyebrow">Step 05</div><h3>심사결과</h3><p>확인 신뢰도와 위험신호를 종합하여 후속 조치를 제시합니다.</p></div>', unsafe_allow_html=True)
                if "result" in st.session_state:
                    score, grade, visit, recommendation, deductions = st.session_state["result"]
                    st.markdown(f'<div class="loan-result-card"><div class="metrics"><div class="metric"><small>확인 신뢰도</small><b>{score}점</b></div><div class="metric"><small>확인등급</small><b>{grade}</b></div><div class="metric"><small>현장방문 필요도</small><b>{visit}</b></div><div class="metric"><small>위험신호</small><b>{len(deductions)}건</b></div></div></div>', unsafe_allow_html=True)
                    st.markdown("#### 상세 위험신호")
                    if deductions:
                        for reason, points in deductions:
                            st.write(f"- {reason} (-{points}점)")
                    else:
                        st.success("특이 위험신호가 확인되지 않았습니다.")
                    st.text_area("심사보조 의견", f"{company_name}의 {loan_purpose} 관련 자료를 검토한 결과, 확인 신뢰도는 {score}점({grade}등급)이며 권고 조치는 {recommendation}입니다.", height=130)
                else:
                    st.info("상단 입력값을 확인한 뒤 ‘현장확인 분석 실행’을 눌러주세요.")
    components.html('''<script>(function(){const doc=window.parent.document;const ids=['loan-step-1','loan-step-2','loan-step-3','loan-step-4','loan-step-5'];function active(id){ids.forEach((sid,i)=>{const link=doc.getElementById('loan-nav-'+(i+1));if(link)link.classList.toggle('active',sid===id);});}function bind(){const sections=ids.map(id=>doc.getElementById(id)).filter(Boolean);if(!sections.length){setTimeout(bind,300);return;}ids.forEach((id,i)=>{const link=doc.getElementById('loan-nav-'+(i+1));if(link&&!link.dataset.bound){link.dataset.bound='1';link.addEventListener('click',e=>{e.preventDefault();const target=doc.getElementById(id);if(target){target.scrollIntoView({behavior:'smooth',block:'start'});active(id);}});}});const observer=new IntersectionObserver(entries=>{const visible=entries.filter(e=>e.isIntersecting).sort((a,b)=>a.boundingClientRect.top-b.boundingClientRect.top);if(visible.length)active(visible[0].target.id);},{root:null,rootMargin:'-92px 0px -58% 0px',threshold:[0,.1,.25]});sections.forEach(s=>observer.observe(s));}bind();})();</script>''', height=0, width=0)

else:
    qna_items = [
        (
            "서비스 역할",
            "위성사진만으로 대출을 승인하거나 거절하나요?",
            "아닙니다. LoanScope AX는 자동 승인·거절 시스템이 아닙니다. 공간정보와 제출자료에서 확인된 위험신호를 직원에게 제공하고, 추가 서류 요청이나 현장방문 필요성을 판단하도록 지원합니다.",
        ),
        (
            "심사 업무",
            "탁상감정과 무엇이 다른가요?",
            "탁상감정은 담보 부동산의 예상가치를 검토하는 절차입니다. LoanScope AX는 사업장과 목적시설이 실제로 존재하는지, 신청 목적대로 변화하거나 공사가 진행되는지를 확인하는 사실검증 보조 도구입니다.",
        ),
        (
            "현장 확인",
            "현장점검을 완전히 대체할 수 있나요?",
            "전면 대체하지 않습니다. 규정상 현장방문이 필요한 건은 기존 절차를 유지합니다. LoanScope AX는 모든 건을 동일하게 방문하기보다 위험도가 높은 건을 우선 선별하는 데 목적이 있습니다.",
        ),
        (
            "이미지 검증",
            "AI로 생성하거나 편집한 이미지는 어떻게 확인하나요?",
            "EXIF 촬영정보, GPS, 편집 프로그램 기록, 유사 이미지 중복 여부, 공간영상과 주변 구조의 일치 여부를 함께 검토합니다. 하나의 탐지 결과만으로 조작을 확정하지 않습니다.",
        ),
        (
            "적용 대상",
            "어떤 대출에 가장 적합한가요?",
            "공장 신축·증축, 창고, 농업시설, 태양광, 토지조성처럼 외부 공간영상에서 시설이나 부지의 변화가 관찰되는 시설자금에 적합합니다. 실내 영업이나 무형 서비스업은 적용 적합도가 낮습니다.",
        ),
        (
            "데이터 품질",
            "공간영상이 오래되거나 흐리면 어떻게 하나요?",
            "촬영일 경과, 구름, 계절 차이, 해상도 부족 등으로 판독이 어려우면 신뢰도를 낮추고 최신 현장사진, 영상통화, 추가서류 또는 현장방문을 권고합니다.",
        ),
        (
            "개인정보",
            "개인정보는 어떻게 보호하나요?",
            "시설·토지 변화와 대출 목적 확인에 필요한 정보만 최소한으로 처리합니다. 사람 얼굴과 차량번호 분석은 제외하고, 역할 기반 접근통제, 암호화, 보관기간 관리와 처리 이력 기록을 전제로 합니다.",
        ),
    ]

    qna_cards = "".join(
        f"""
        <details class="qna-item">
          <summary>
            <span class="qna-category">{category}</span>
            <span class="qna-question">{question}</span>
            <span class="qna-plus" aria-hidden="true"></span>
          </summary>
          <div class="qna-answer">{answer}</div>
        </details>
        """
        for category, question, answer in qna_items
    )

    st.markdown(
        f"""
        <section class="qna-hero">
          <div class="qna-hero-copy">
            <span class="qna-kicker">LoanScope AX Guide</span>
            <h1>궁금한 점을<br>쉽고 명확하게 확인하세요.</h1>
            <p>
              서비스 역할부터 심사 적용 범위, 이미지 검증, 개인정보 보호까지<br>
              실제 은행 업무에서 자주 묻는 내용을 정리했습니다.
            </p>
          </div>
          <div class="qna-hero-visual">
            <div class="qna-orbit qna-orbit-one"></div>
            <div class="qna-orbit qna-orbit-two"></div>
            <img src="{CHAR_SKY}" alt="iM 캐릭터">
          </div>
        </section>

        <main class="qna-page">
          <section class="qna-intro">
            <div>
              <span class="qna-section-label">Frequently Asked Questions</span>
              <h2>자주 묻는 질문</h2>
              <p>질문을 선택하면 상세 답변을 확인할 수 있습니다.</p>
            </div>
            <div class="qna-count">
              <strong>{len(qna_items)}</strong>
              <span>개의 안내</span>
            </div>
          </section>

          <section class="qna-list">
            {qna_cards}
          </section>

          <section class="qna-support">
            <div class="qna-support-icon">?</div>
            <div>
              <strong>안내되지 않은 내용이 있나요?</strong>
              <p>베타 서비스에서는 담당 심사역의 검토와 기존 여신규정을 우선 적용합니다.</p>
            </div>
            <span class="qna-support-chip">Human-in-the-loop</span>
          </section>
        </main>
        """,
        unsafe_allow_html=True,
    )
