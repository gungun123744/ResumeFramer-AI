import csv
import html
import io
import json
import re

import fitz
import streamlit as st

from modules.analyzer import (
    DEFAULT_MODEL,
    analyze_documents,
    tailor_resume,
    build_learning_plan,
)
from modules.resources import get_resources_for_skills


# ============================================================
# PAGE CONFIG + PROFESSIONAL WHITE/BLUE THEME
# ============================================================

st.set_page_config(
    page_title="ResumeFramer AI",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed",
)

MODEL = DEFAULT_MODEL

st.markdown(
    """
    <style>
    :root { --rf-blue: #2563eb; --rf-ink: #172033; --rf-muted: #64748b; }
    .stApp { background: #f6f8fc; color: var(--rf-ink); }
    h1, h2, h3, h4 { color: var(--rf-ink); letter-spacing: -.35px; }
    hr { border-color: #e7edf6; }

    [data-testid="stHeader"] {
        background: rgba(248,250,252,.95);
    }

    [data-testid="stSidebar"] { display: none; }
    [data-testid="stSidebarCollapsedControl"] { display: none; }
    [data-testid="stToolbar"] { right: 1rem; }

    section[data-testid="stMain"] > div {
        padding-top: 1.4rem;
    }

    .block-container {
        max-width: 1320px;
        padding-left: 2.25rem;
        padding-right: 2.25rem;
        padding-top: 1.2rem;
        padding-bottom: 4rem;
    }

    div[role="radiogroup"] {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
    }

    div[role="radiogroup"] label {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 10px 15px;
        transition: all .18s ease;
        font-weight: 650;
    }

    div[role="radiogroup"] label:hover {
        border-color: #2563eb;
        background: #eff6ff;
    }

    div[role="radiogroup"] label:has(input:checked) {
        background: #eff6ff;
        border-color: #2563eb;
        box-shadow: 0 2px 8px rgba(37,99,235,.08);
    }

    .rf-brand {
        display: flex; align-items: center; gap: 13px;
        padding: 8px 4px 18px; margin-bottom: 16px;
        border-bottom: 1px solid #e8edf5;
    }

    .rf-brand-icon {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        border-radius: 15px;
        background: #2563eb;
        color: #fff;
        font-size: 25px;
        box-shadow: 0 7px 18px rgba(37,99,235,.20);
    }

    .rf-brand-name {
        font-size: 24px;
        font-weight: 850;
        color: #172033;
        letter-spacing: -.6px;
    }

    .rf-brand-caption {
        font-size: 10px;
        color: #64748b;
        letter-spacing: 1.7px;
        font-weight: 800;
        margin-top: 3px;
    }

    .rf-hero {
        position: relative; overflow: hidden; padding: 38px;
        border: 1px solid #dbeafe; border-radius: 26px;
        background: radial-gradient(circle at 90% 12%, #dbeafe 0, transparent 30%),
                    linear-gradient(120deg, #ffffff 0%, #f2f7ff 100%);
        margin: 22px 0 26px;
        box-shadow: 0 14px 38px rgba(30,64,175,.07);
    }
    .rf-hero:after {
        content: "AI"; position: absolute; right: 42px; bottom: -36px;
        font-size: 150px; line-height: 1; font-weight: 900;
        letter-spacing: -12px; color: rgba(37,99,235,.055);
        pointer-events: none;
    }

    .rf-eyebrow {
        color: #2563eb;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 10px;
    }

    .rf-hero h1 {
        color: #172033;
        font-size: clamp(28px,3.2vw,43px);
        line-height: 1.12;
        margin: 0;
        letter-spacing: -1.3px;
    }

    .rf-hero p {
        color: #64748b;
        font-size: 15px;
        line-height: 1.7;
        margin: 14px 0 0;
        max-width: 780px;
    }

    .rf-section-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: 1.1px;
        text-transform: uppercase;
        margin-bottom: 6px;
    }

    .rf-score-card {
        background: linear-gradient(
            135deg,
            #ffffff 0%,
            #eff6ff 100%
        );
        border: 1px solid #dbeafe;
        border-radius: 20px;
        padding: 24px;
        margin: 8px 0 18px;
    }

    .rf-score-label {
        color: #475569;
        font-size: 12px;
        letter-spacing: 1.1px;
        font-weight: 800;
    }

    .rf-score-number {
        font-size: 48px;
        line-height: 1.15;
        font-weight: 850;
        letter-spacing: -1.5px;
        margin: 8px 0 12px;
    }

    .rf-score-track {
        height: 10px;
        width: 100%;
        border-radius: 20px;
        background: #dbeafe;
        overflow: hidden;
    }

    .rf-score-fill {
        height: 100%;
        border-radius: 20px;
    }

    .rf-metric {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 15px;
        padding: 16px;
        min-height: 112px;
        box-shadow: 0 2px 5px rgba(15,23,42,.025);
    }

    .rf-metric-label {
        color: #64748b;
        font-size: 11px;
        font-weight: 800;
        letter-spacing: .5px;
        text-transform: uppercase;
    }

    .rf-metric-value {
        color: #172033;
        font-size: 30px;
        font-weight: 850;
        line-height: 1.25;
        margin-top: 9px;
    }

    .rf-metric-note {
        color: #64748b;
        font-size: 11px;
        margin-top: 5px;
    }

    .rf-status {
        display: inline-block;
        padding: 5px 9px;
        border-radius: 999px;
        font-size: 10px;
        font-weight: 850;
        letter-spacing: .4px;
        white-space: nowrap;
    }

    .rf-status-good {
        background: #dcfce7;
        color: #166534;
    }

    .rf-status-warn {
        background: #fef3c7;
        color: #92400e;
    }

    .rf-status-gap {
        background: #fee2e2;
        color: #991b1b;
    }

    .rf-status-neutral {
        background: #e2e8f0;
        color: #334155;
    }

    div.stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #2563eb, #1d4ed8);
        border: 1px solid #2563eb; color: #fff; border-radius: 12px;
        min-height: 46px; font-weight: 750;
        box-shadow: 0 5px 14px rgba(37,99,235,.15);
        transition: transform .15s ease, box-shadow .15s ease;
    }
    div.stButton > button[kind="primary"]:hover {
        transform: translateY(-1px);
        box-shadow: 0 8px 18px rgba(37,99,235,.22);
    }

    div.stButton > button[kind="primary"]:hover {
        background: #1d4ed8;
        border-color: #1d4ed8;
        color: #ffffff;
    }

    div.stButton > button,
    div.stDownloadButton > button,
    div.stLinkButton > a {
        border-radius: 10px;
        font-weight: 650;
    }

    div[data-testid="stFileUploader"] {
        background: #ffffff;
        border: 1px dashed #bfdbfe;
        border-radius: 14px;
        padding: 10px;
    }

    div[data-testid="stExpander"] {
        border-color: #e2e8f0; border-radius: 14px; background: #fff;
    }
    div[data-testid="stVerticalBlockBorderWrapper"] {
        border-radius: 18px; border-color: #e2e8f0;
        background: #ffffff;
        box-shadow: 0 4px 16px rgba(15,23,42,.025);
    }
    div[data-testid="stExpander"] {
        border: 1px solid #e2e8f0; border-radius: 14px;
        background: #fff;
    }
    div[data-testid="stFileUploader"] button {
        border-radius: 9px;
    }
    .rf-top-note {
        color: #64748b; font-size: 12px; font-weight: 600;
        padding-top: 7px; text-align: right;
    }
    div[data-testid="stTextInput"] input,
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div,
    div[data-testid="stMultiSelect"] [data-baseweb="select"] > div {
        border-radius: 10px; border-color: #dbe3ef;
    }
    div[data-testid="stFileUploader"] section {
        background: #fbfdff; border-radius: 10px;
    }

    [data-testid="stDataFrame"] {
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        overflow: hidden;
    }

    .rf-footer {
        color: #94a3b8; border-top: 1px solid #e2e8f0;
        padding-top: 18px; font-size: 11px; line-height: 1.8;
        margin-top: 36px;
    }

    @media (max-width: 768px) {
        .block-container { padding-left: 1rem; padding-right: 1rem; }
        .rf-hero { padding: 22px; }
        .rf-hero:after { display: none; }
        .rf-brand-name { font-size: 21px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# SESSION STATE
# ============================================================

DEFAULTS = {
    "resume_text": "",
    "resume_pages": [],
    "jd_text": "",
    "analysis": None,
    "tailored_latex": "",
    "learning_plan": "",
    "recommended_resources": [],
}

for key, value in DEFAULTS.items():
    if key not in st.session_state:
        st.session_state[key] = value


def clear_results():
    for key, value in DEFAULTS.items():
        st.session_state[key] = value


# ============================================================
# PDF EXTRACTION
# ============================================================

def extract_uploaded_pdf_pages(uploaded_file):
    if uploaded_file is None:
        raise ValueError("Please upload a PDF file.")

    pdf_bytes = uploaded_file.getvalue()

    if not pdf_bytes:
        raise ValueError(f"{uploaded_file.name} is empty.")

    try:
        with fitz.open(
            stream=pdf_bytes,
            filetype="pdf",
        ) as pdf:
            pages = [
                page.get_text("text").strip()
                for page in pdf
            ]

    except Exception as exc:
        raise ValueError(
            f"Could not read {uploaded_file.name}: {exc}"
        ) from exc

    if not any(pages):
        raise ValueError(
            f"No selectable text found in {uploaded_file.name}. "
            "Scanned PDFs require OCR."
        )

    return pages


# ============================================================
# MATCH SCORE + EVIDENCE HELPERS
# ============================================================

def normalize_text(value):
    return re.sub(
        r"\s+",
        " ",
        str(value or ""),
    ).strip().casefold()


def calculate_job_match(skills):
    priority_weights = {
        "high": 3,
        "medium": 2,
        "low": 1,
    }

    status_scores = {
        "demonstrated": 1.0,
        "weak evidence": 0.5,
        "evidence needed": 0.0,
        "missing": 0.0,
    }

    weighted_total = 0.0
    total_weight = 0.0
    evaluated = []

    for item in skills:
        if not isinstance(item, dict) or not item.get("skill"):
            continue

        status = normalize_text(
            item.get("status", "evidence needed")
        )

        priority = normalize_text(
            item.get("priority", "medium")
        )

        weight = priority_weights.get(priority, 2)

        weighted_total += (
            weight * status_scores.get(status, 0.0)
        )

        total_weight += weight
        evaluated.append(item)

    score = (
        round(100 * weighted_total / total_weight)
        if total_weight
        else 0
    )

    return score, evaluated


def find_skill_evidence(skill, evidence, resume_pages):
    evidence_text = normalize_text(evidence)
    skill_text = normalize_text(skill)

    if len(evidence_text) >= 12:
        for page_number, page_text in enumerate(
            resume_pages,
            start=1,
        ):
            if evidence_text in normalize_text(page_text):
                for line in page_text.splitlines():
                    if evidence_text in normalize_text(line):
                        return page_number, line.strip()

                return page_number, str(evidence).strip()

    if skill_text:
        for page_number, page_text in enumerate(
            resume_pages,
            start=1,
        ):
            for line in page_text.splitlines():
                if skill_text in normalize_text(line):
                    return page_number, line.strip()

    tokens = [
        token
        for token in re.findall(
            r"[A-Za-z0-9+#.]+",
            str(skill or ""),
        )
        if len(token) > 2
    ]

    if tokens:
        for page_number, page_text in enumerate(
            resume_pages,
            start=1,
        ):
            for line in page_text.splitlines():
                normalized_line = normalize_text(line)

                if any(
                    normalize_text(token) in normalized_line
                    for token in tokens
                ):
                    return page_number, line.strip()

    return None, None


def build_evidence_rows(skills, resume_pages):
    rows = []

    for item in skills:
        if not isinstance(item, dict):
            continue

        skill = str(item.get("skill", "Unknown skill"))

        page_number, source_line = find_skill_evidence(
            skill,
            item.get("resume_evidence", ""),
            resume_pages,
        )

        rows.append({
            "Skill": skill,
            "Priority": str(item.get("priority", "medium")),
            "Status": str(item.get("status", "evidence needed")),
            "Resume page": (
                f"Page {page_number}"
                if page_number
                else "Not located"
            ),
            "Resume source line": (
                source_line or "No matching line located"
            ),
            "Job requirement": str(
                item.get("jd_requirement", "")
            ),
            "Recommended action": str(
                item.get("recommended_action", "")
            ),
        })

    return rows


# ============================================================
# UI COMPONENT HELPERS
# ============================================================

def render_metric(label, value, note, accent):
    st.markdown(
        f"""
        <div class="rf-metric">
            <div class="rf-metric-label">
                {html.escape(label)}
            </div>
            <div class="rf-metric-value" style="color:{accent}">
                {html.escape(str(value))}
            </div>
            <div class="rf-metric-note">
                {html.escape(note)}
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_skill_card(row):
    status = normalize_text(row["Status"])
    priority = normalize_text(row["Priority"])

    if status == "demonstrated":
        badge_class = "rf-status-good"
        badge_text = "DEMONSTRATED"

    elif status == "weak evidence":
        badge_class = "rf-status-warn"
        badge_text = "WEAK EVIDENCE"

    elif status in ("evidence needed", "missing"):
        badge_class = "rf-status-gap"
        badge_text = status.upper()

    else:
        badge_class = "rf-status-neutral"
        badge_text = status.upper()

    priority_color = {
        "high": "#dc2626",
        "medium": "#b45309",
        "low": "#64748b",
    }.get(priority, "#64748b")

    with st.container(border=True):
        left, right = st.columns([3, 2])

        with left:
            st.markdown(f"#### {row['Skill']}")

        with right:
            st.markdown(
                '<div style="text-align:right;padding-top:8px">'
                f'<span class="rf-status {badge_class}">'
                f'{html.escape(badge_text)}</span></div>',
                unsafe_allow_html=True,
            )

        st.markdown(
            '<div style="font-size:12px;font-weight:750;'
            f'color:{priority_color};margin:2px 0 14px">'
            f'Priority: {html.escape(priority.title())}'
            f' &nbsp; · &nbsp; '
            f'{html.escape(row["Resume page"])}</div>',
            unsafe_allow_html=True,
        )

        evidence_col, requirement_col = st.columns(2)

        with evidence_col:
            st.markdown("**Resume evidence**")
            st.write(row["Resume source line"])

        with requirement_col:
            st.markdown("**Job requirement**")
            st.write(row["Job requirement"] or "Not specified")

        if row["Recommended action"]:
            st.markdown("**Recommended next step**")
            st.info(row["Recommended action"])

# ============================================================
# MAIN-PAGE BRAND + NAVIGATION
# ============================================================

st.markdown(
    """
    <div class="rf-brand">
      <div class="rf-brand-icon">📄</div>
      <div>
        <div class="rf-brand-name">ResumeFramer AI</div>
        <div class="rf-brand-caption">CAREER INTELLIGENCE</div>
      </div>
    </div>
    """,
    unsafe_allow_html=True,
)

page = st.radio(
    "WORKSPACE NAVIGATION",
    [
        "Overview",
        "Resume Analysis",
        "Evidence Map",
        "LaTeX Resume",
        "Learning Roadmap",
        "Resources",
    ],
    horizontal=True,
    label_visibility="collapsed",
    key="main_page_navigation",
)


# ============================================================
# ANALYSIS SETTINGS ON MAIN PAGE
# ============================================================

with st.container(border=True):
    st.markdown("#### ⚙️ Analysis settings")

    settings_col1, settings_col2, settings_col3, settings_col4 = (
        st.columns([1.25, 1.25, 1, 1])
    )

    with settings_col1:
        st.text_input(
            "Groq model",
            value=MODEL,
            disabled=True,
            help="Configured in modules/llm.py",
        )

    with settings_col2:
        company = st.text_input(
            "Company name (optional)",
            placeholder="e.g. Google",
            key="company_name",
        )

    with settings_col3:
        role = st.text_input(
            "Target role (optional)",
            placeholder="e.g. SDE Intern",
            key="target_role",
        )

    with settings_col4:
        roadmap_days = st.selectbox(
            "Roadmap duration",
            [7, 14, 21, 30],
            index=1,
            key="roadmap_duration",
        )

    settings_bottom1, settings_bottom2, settings_bottom3 = (
        st.columns([1.25, 1.25, 2])
    )

    with settings_bottom1:
        language = st.selectbox(
            "Learning language",
            [
                "Python",
                "C++",
                "Java",
                "JavaScript",
                "No preference",
            ],
            key="learning_language",
        )

    with settings_bottom2:
        st.write("")
        st.write("")

        if st.button(
            "Clear current results",
            use_container_width=True,
        ):
            clear_results()
            st.rerun()

    with settings_bottom3:
        st.caption(
            "Built with Streamlit, PyMuPDF and Groq. "
            "Your API key stays in your local .env file."
        )


# ============================================================
# HERO HEADER
# ============================================================

st.markdown(
    """
    <div class="rf-hero">
        <div class="rf-eyebrow">YOUR PERSONAL AI CAREER COPILOT</div>
        <h1>Turn your resume into<br>your next opportunity.</h1>
        <p>
            Get a job-specific resume review, uncover skill gaps, generate
            an Overleaf-ready resume and build a practical learning plan —
            all in one workspace.
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# DOCUMENT UPLOAD + ANALYSIS
# ============================================================

with st.container(border=True):
    st.markdown("### Start with your documents")

    st.write(
        "Upload your resume and the job description "
        "you want to target."
    )

    upload_col1, upload_col2 = st.columns(2)

    with upload_col1:
        resume_file = st.file_uploader(
            "Resume PDF",
            type=["pdf"],
            key="resume_upload",
            help="Upload a text-based PDF resume.",
        )

    with upload_col2:
        jd_file = st.file_uploader(
            "Job description PDF",
            type=["pdf"],
            key="jd_upload",
            help="Upload the job description as a PDF.",
        )

    st.caption(
        "Maximum file size: 10 MB per PDF. Scanned PDFs need OCR."
    )

    analyze_clicked = st.button(
        "✨ Analyze resume against this job",
        type="primary",
        use_container_width=True,
        disabled=resume_file is None or jd_file is None,
    )


# ============================================================
# PROCESS DOCUMENTS
# ============================================================

if analyze_clicked:
    if resume_file.size > 10 * 1024 * 1024:
        st.error("Resume PDF must be 10 MB or smaller.")

    elif jd_file.size > 10 * 1024 * 1024:
        st.error("Job description PDF must be 10 MB or smaller.")

    else:
        try:
            with st.spinner(
                "Extracting PDF text and page evidence..."
            ):
                resume_pages = extract_uploaded_pdf_pages(
                    resume_file
                )

                jd_pages = extract_uploaded_pdf_pages(jd_file)

                resume_text = "\n\n".join(
                    resume_pages
                ).strip()

                jd_text = "\n\n".join(jd_pages).strip()

            with st.spinner(
                "Analyzing resume and job requirements..."
            ):
                result = analyze_documents(
                    resume_text=resume_text,
                    jd_text=jd_text,
                    company=company.strip(),
                    role=role.strip(),
                    model=MODEL,
                )

            st.session_state["resume_text"] = resume_text
            st.session_state["resume_pages"] = resume_pages
            st.session_state["jd_text"] = jd_text
            st.session_state["analysis"] = result
            st.session_state["tailored_latex"] = ""
            st.session_state["learning_plan"] = ""
            st.session_state["recommended_resources"] = []

            st.success("Analysis completed successfully.")

        except Exception as exc:
            st.error(f"Analysis failed: {exc}")


# ============================================================
# SHARED ANALYSIS DATA
# ============================================================

analysis = st.session_state.get("analysis")

skills = (
    analysis.get("skills", [])
    if isinstance(analysis, dict)
    else []
)

if not isinstance(skills, list):
    skills = []

match_score, match_skills = calculate_job_match(skills)

evidence_rows = (
    build_evidence_rows(
        match_skills,
        st.session_state.get("resume_pages", []),
    )
    if analysis
    else []
)

demonstrated_count = sum(
    normalize_text(item.get("status")) == "demonstrated"
    for item in match_skills
)

weak_count = sum(
    normalize_text(item.get("status")) == "weak evidence"
    for item in match_skills
)

gap_count = sum(
    normalize_text(item.get("status"))
    in ("evidence needed", "missing")
    for item in match_skills
)


# ============================================================
# OVERVIEW PAGE
# ============================================================

if page == "Overview":
    st.markdown("### Your workspace")

    st.write(
        "Start by uploading your resume and the job description. "
        "Your match score and personalized recommendations "
        "will appear here after analysis."
    )

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric(
            "Evidence match",
            f"{match_score}%" if analysis else "—",
            "Estimated alignment",
            "#2563eb",
        )

    with c2:
        render_metric(
            "Demonstrated",
            demonstrated_count if analysis else "—",
            "Skills with evidence",
            "#15803d",
        )

    with c3:
        render_metric(
            "Needs attention",
            weak_count + gap_count if analysis else "—",
            "Weak or missing evidence",
            "#b45309",
        )

    with c4:
        render_metric(
            "Skills reviewed",
            len(match_skills) if analysis else "—",
            "From job analysis",
            "#7c3aed",
        )

    st.markdown("### How it works")

    flow1, flow2, flow3 = st.columns(3)

    with flow1:
        with st.container(border=True):
            st.markdown("#### 01 · Analyze")
            st.write(
                "Compare resume evidence with job requirements."
            )

    with flow2:
        with st.container(border=True):
            st.markdown("#### 02 · Improve")
            st.write(
                "Inspect skill gaps and tailor your resume."
            )

    with flow3:
        with st.container(border=True):
            st.markdown("#### 03 · Prepare")
            st.write(
                "Generate a learning roadmap and find resources."
            )

    if analysis:
        st.markdown("### Recommended next steps")

        if gap_count + weak_count:
            st.info(
                f"{gap_count + weak_count} skill(s) need stronger "
                "evidence or review. Open the Evidence Map tab above."
            )
        else:
            st.success(
                "No weak or missing skills were flagged."
            )

        st.download_button(
            "Download analysis JSON",
            data=json.dumps(
                analysis,
                indent=2,
                ensure_ascii=False,
            ),
            file_name="resume_analysis.json",
            mime="application/json",
        )


# ============================================================
# RESUME ANALYSIS PAGE
# ============================================================

elif page == "Resume Analysis":
    st.markdown("### Resume analysis")

    if not analysis:
        st.info(
            "Upload your documents above and run the analysis."
        )

    else:
        try:
            coverage = max(
                0,
                min(
                    100,
                    float(analysis.get("coverage_score", 0)),
                ),
            )

        except (TypeError, ValueError):
            coverage = 0

        col1, col2 = st.columns(2)

        col1.metric(
            "Resume evidence coverage",
            f"{coverage:.0f}%",
        )

        col2.metric(
            "Skills evaluated",
            len(match_skills),
        )

        st.progress(coverage / 100)

        st.caption(
            "AI-estimated evidence coverage. This is not an official "
            "ATS score or hiring probability."
        )

        with st.container(border=True):
            st.markdown("#### Resume summary")
            st.write(analysis.get("resume_summary", ""))

        with st.container(border=True):
            st.markdown("#### Job description summary")
            st.write(analysis.get("jd_summary", ""))

        st.markdown("#### Resume strengths")

        strengths = analysis.get("resume_strengths", [])

        if isinstance(strengths, list) and strengths:
            for strength in strengths:
                st.markdown(f"- {strength}")
        else:
            st.caption("No strengths returned.")

        questions = analysis.get("questions_for_user", [])

        if isinstance(questions, list) and questions:
            st.markdown("#### Details to verify")

            for question in questions:
                st.warning(question)

        st.download_button(
            "Download analysis JSON",
            data=json.dumps(
                analysis,
                indent=2,
                ensure_ascii=False,
            ),
            file_name="resume_analysis.json",
            mime="application/json",
        )


# ============================================================
# EVIDENCE MAP PAGE
# ============================================================

elif page == "Evidence Map":
    st.markdown("### Job Match Score + Evidence Map")

    if not analysis:
        st.info(
            "Analyze your documents first to see the evidence map."
        )

    else:
        score_color = (
            "#15803d"
            if match_score >= 75
            else "#b45309"
            if match_score >= 50
            else "#b91c1c"
        )

        st.markdown(
            f"""
            <div class="rf-score-card">
                <div class="rf-score-label">
                    ESTIMATED EVIDENCE MATCH
                </div>
                <div class="rf-score-number"
                     style="color:{score_color}">
                    {match_score}%
                </div>
                <div class="rf-score-track">
                    <div class="rf-score-fill"
                         style="width:{match_score}%;
                                background:{score_color}">
                    </div>
                </div>
                <div style="color:#64748b;
                            font-size:12px;margin-top:10px">
                    Priority-weighted estimate · Not a hiring probability
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

        metric_cols = st.columns(4, gap="small")

        metric_values = [
            (
                "Demonstrated",
                demonstrated_count,
                "Evidence identified",
                "#15803d",
            ),
            (
                "Weak evidence",
                weak_count,
                "Needs stronger proof",
                "#b45309",
            ),
            (
                "Evidence gaps",
                gap_count,
                "Not demonstrated",
                "#b91c1c",
            ),
            (
                "Skills evaluated",
                len(match_skills),
                "In this analysis",
                "#2563eb",
            ),
        ]

        for col, (label, value, note, color) in zip(
            metric_cols,
            metric_values,
        ):
            with col:
                render_metric(
                    label,
                    value,
                    note,
                    color,
                )

        st.caption(
            "The score is calculated from AI-returned statuses and "
            "priorities. It is not a validated ATS score or "
            "hiring probability."
        )

        if evidence_rows:
            filter_col, priority_col = st.columns(2)

            with filter_col:
                status_filter = st.selectbox(
                    "Filter status",
                    [
                        "All statuses",
                        "demonstrated",
                        "weak evidence",
                        "evidence needed",
                        "missing",
                    ],
                    key="evidence_status_filter",
                )

            with priority_col:
                priority_filter = st.selectbox(
                    "Filter priority",
                    [
                        "All priorities",
                        "high",
                        "medium",
                        "low",
                    ],
                    key="evidence_priority_filter",
                )

            filtered_rows = [
                row
                for row in evidence_rows
                if (
                    status_filter == "All statuses"
                    or normalize_text(row["Status"])
                    == status_filter
                )
                and (
                    priority_filter == "All priorities"
                    or normalize_text(row["Priority"])
                    == priority_filter
                )
            ]

            for row in filtered_rows:
                render_skill_card(row)

            if not filtered_rows:
                st.info("No skills match these filters.")

            st.markdown("### Skills to strengthen")

            gaps = [
                row
                for row in evidence_rows
                if normalize_text(row["Status"])
                in (
                    "weak evidence",
                    "evidence needed",
                    "missing",
                )
            ]

            if gaps:
                for row in gaps:
                    st.markdown(
                        f"- **{row['Skill']}** · "
                        f"{row['Priority']} priority · "
                        f"{row['Status']}"
                    )

                    if row["Recommended action"]:
                        st.caption(
                            row["Recommended action"]
                        )
            else:
                st.success(
                    "No weak or missing skills were flagged."
                )

            csv_buffer = io.StringIO()

            writer = csv.DictWriter(
                csv_buffer,
                fieldnames=list(evidence_rows[0].keys()),
            )

            writer.writeheader()
            writer.writerows(evidence_rows)

            st.download_button(
                "Download evidence map CSV",
                data=csv_buffer.getvalue(),
                file_name="job_match_evidence_map.csv",
                mime="text/csv",
            )

        else:
            st.info("No skills were returned by the analysis.")


# ============================================================
# LATEX RESUME PAGE
# ============================================================

elif page == "LaTeX Resume":
    st.markdown("### Tailor your resume for Overleaf")

    if not analysis:
        st.info("Analyze your documents first.")

    else:
        st.write(
            "Generate an ATS-readable LaTeX resume using verified "
            "facts from your original resume."
        )

        if st.button(
            "Generate LaTeX resume",
            type="primary",
        ):
            try:
                with st.spinner("Generating LaTeX source..."):
                    latex = tailor_resume(
                        resume_text=st.session_state[
                            "resume_text"
                        ],
                        jd_text=st.session_state["jd_text"],
                        analysis=analysis,
                        model=MODEL,
                    )

                st.session_state["tailored_latex"] = latex

                st.success("LaTeX resume generated.")

            except Exception as exc:
                st.error(
                    f"Resume generation failed: {exc}"
                )

        latex = st.session_state.get(
            "tailored_latex",
            "",
        )

        if latex:
            edited_latex = st.text_area(
                "Edit main.tex source",
                value=latex,
                height=500,
                key="latex_editor",
            )

            st.download_button(
                "Download tailored_resume.tex",
                data=edited_latex,
                file_name="tailored_resume.tex",
                mime="text/plain",
                use_container_width=True,
            )

            st.link_button(
                "Open Overleaf",
                "https://www.overleaf.com/project",
                use_container_width=True,
            )

            st.info(
                "Compile the file in Overleaf and verify names, dates, "
                "skills and qualifications before using it."
            )


# ============================================================
# LEARNING ROADMAP PAGE
# ============================================================

elif page == "Learning Roadmap":
    st.markdown("### Personalized learning roadmap")

    if not analysis:
        st.info("Analyze your documents first.")

    else:
        needs_attention = [
            item["skill"]
            for item in match_skills
            if item.get("skill")
            and normalize_text(item.get("status"))
            in (
                "weak evidence",
                "evidence needed",
                "missing",
            )
        ]

        st.write(
            f"Plan duration: **{roadmap_days} days** · "
            f"Preferred language: **{language}**"
        )

        if needs_attention:
            st.markdown(
                "**Skills to focus on:** "
                + ", ".join(needs_attention)
            )

        else:
            st.caption(
                "No explicit gaps were identified. You can still use "
                "a roadmap to reinforce job-relevant skills."
            )

        if st.button(
            "Generate learning roadmap",
            type="primary",
        ):
            try:
                with st.spinner("Building your roadmap..."):
                    roadmap = build_learning_plan(
                        jd_text=st.session_state["jd_text"],
                        analysis=analysis,
                        missing_skills=needs_attention,
                        days=roadmap_days,
                        language=language,
                        model=MODEL,
                    )

                st.session_state["learning_plan"] = roadmap

            except Exception as exc:
                st.error(
                    f"Learning roadmap failed: {exc}"
                )

        roadmap = st.session_state.get(
            "learning_plan",
            "",
        )

        if roadmap:
            st.markdown(roadmap)

            st.download_button(
                "Download learning roadmap",
                data=roadmap,
                file_name="learning_roadmap.md",
                mime="text/markdown",
            )


# ============================================================
# LEARNING RESOURCES PAGE
# ============================================================

elif page == "Resources":
    st.markdown("### Learning resources")

    if not analysis:
        st.info("Analyze your documents first.")

    else:
        gap_skills = [
            item["skill"].strip()
            for item in match_skills
            if isinstance(item.get("skill"), str)
            and item["skill"].strip()
            and normalize_text(item.get("status"))
            in (
                "weak evidence",
                "evidence needed",
                "missing",
            )
        ]

        all_skills = [
            item["skill"].strip()
            for item in match_skills
            if isinstance(item.get("skill"), str)
            and item["skill"].strip()
        ]

        resource_options = list(
            dict.fromkeys(gap_skills or all_skills)
        )

        if not resource_options:
            st.info("No skills were returned by the analysis.")

        else:
            st.write(
                "Find tutorials, documentation, articles, GitHub "
                "projects and practice exercises for selected skills."
            )

            selected_skills = st.multiselect(
                "Choose skills",
                options=resource_options,
                default=resource_options[:5],
                key="resource_skill_selection",
            )

            if st.button(
                "Find learning resources",
                type="primary",
            ):
                try:
                    st.session_state[
                        "recommended_resources"
                    ] = get_resources_for_skills(
                        selected_skills,
                        language=language,
                    )

                except Exception as exc:
                    st.error(
                        f"Could not load resources: {exc}"
                    )

            for recommendation in st.session_state.get(
                "recommended_resources",
                [],
            ):
                with st.container(border=True):
                    st.markdown(
                        "#### "
                        + str(
                            recommendation.get(
                                "skill",
                                "Skill",
                            )
                        )
                    )

                    for resource in recommendation.get(
                        "resources",
                        [],
                    ):
                        st.markdown(
                            "**"
                            + str(
                                resource.get(
                                    "type",
                                    "Resource",
                                )
                            )
                            + "**"
                        )

                        st.write(
                            resource.get("description", "")
                        )

                        title = resource.get(
                            "title",
                            "Open resource",
                        )

                        url = resource.get("url", "")

                        if url:
                            st.markdown(
                                f"[{title}]({url})"
                            )


# ============================================================
# FOOTER
# ============================================================

st.markdown(
    """
    <div class="rf-footer">
        ResumeFramer AI · Built with Streamlit, PyMuPDF and Groq.<br>
        AI-generated analysis can contain errors. Verify all evidence,
        qualifications, dates and links before applying.
    </div>
    """,
    unsafe_allow_html=True,
)