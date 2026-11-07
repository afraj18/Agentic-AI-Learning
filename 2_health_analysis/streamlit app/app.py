import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI


load_dotenv()

st.set_page_config(
    page_title="Luma | Blood report companion",
    page_icon="✳",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Manrope:wght@400;500;600;700;800&display=swap');
    :root { --ink:#182b32; --muted:#6c7d80; --teal:#176c67; --mint:#e8f4ef; --line:#dfe9e5; }
    html, body, [class*="css"] { font-family:'DM Sans',sans-serif; color:var(--ink); }
    .stApp { background: radial-gradient(ellipse at 85% 0%, #e4f4ed 0, transparent 35%), #f7faf8; }
    [data-testid="stHeader"] { background:transparent; }
    .block-container { max-width:1180px; padding-top:2.2rem; padding-bottom:4rem; }
    h1,h2,h3 { font-family:'Manrope',sans-serif !important; letter-spacing:-.04em; }
    .brand { color:var(--teal); font-size:.82rem; font-weight:700; letter-spacing:.16em; text-transform:uppercase; }
    .hero { font-family:'Manrope',sans-serif; font-size:clamp(2.5rem,5.2vw,4.5rem); line-height:1.02; font-weight:700; letter-spacing:-.065em; margin:.65rem 0 1rem; max-width:760px; }
    .hero span { color:var(--teal); }
    .lede { color:var(--muted); font-size:1.08rem; max-width:620px; line-height:1.7; }
    .surface { background:rgba(255,255,255,.86); border:1px solid var(--line); border-radius:24px; padding:1.35rem 1.5rem; box-shadow:0 12px 36px rgba(26,57,49,.045); }
    .section-kicker { font-size:.76rem; text-transform:uppercase; letter-spacing:.12em; color:var(--teal); font-weight:700; margin-bottom:.4rem; }
    .note { background:#edf5f1; border:1px solid #dcebe3; border-radius:14px; padding:12px 16px; color:#49635c; font-size:.9rem; }
    div[data-testid="stFileUploader"] { border-radius:16px; }
    .stButton > button { border-radius:999px; padding:.72rem 1.45rem; border:0; background:#176c67; color:#fff; font-weight:700; box-shadow:0 8px 20px #176c6730; }
    .stButton > button:hover { background:#105752; color:#fff; transform:translateY(-1px); }
    div[data-testid="stTabs"] button { font-weight:600; }
    @media (max-width:700px) { .block-container { padding:1.4rem 1rem 3rem; } .surface { padding:1rem; border-radius:18px; } }
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="brand">✳ Luma · personal health insights</div>', unsafe_allow_html=True)
st.markdown('<div class="hero">Make sense of your<br><span>blood work.</span></div>', unsafe_allow_html=True)
st.markdown(
    '<div class="lede">A clear, two-step read of your report: first the numbers and their ranges, then a practical food guide.</div>',
    unsafe_allow_html=True,
)
st.write("")

left, right = st.columns([1.12, .88], gap="large")
with left:
    st.markdown('<div class="section-kicker">01 · Add your report</div>', unsafe_allow_html=True)
    st.markdown('<div class="surface">', unsafe_allow_html=True)
    upload = st.file_uploader("Upload a plain text report", type=["txt"], help="Text files only. You can also paste report text below.")
    pasted_report = st.text_area("Or paste the report", height=235, placeholder="Paste the blood report, including its reference ranges…", label_visibility="collapsed")
    st.markdown('</div>', unsafe_allow_html=True)
with right:
    st.markdown('<div class="section-kicker">02 · Before you begin</div>', unsafe_allow_html=True)
    st.markdown(
        '<div class="surface"><h3 style="margin-top:0">A little context</h3><p style="color:#6c7d80;line-height:1.65">The report is analyzed in two stages. Reference ranges are taken from the text you provide, so include the full report for the most useful extraction.</p><div class="note">For educational support only. This is not a diagnosis or a substitute for advice from your clinician.</div></div>',
        unsafe_allow_html=True,
    )

blood_report = pasted_report.strip()
if upload is not None:
    try:
        uploaded_text = upload.getvalue().decode("utf-8").strip()
        if uploaded_text:
            blood_report = uploaded_text
    except UnicodeDecodeError:
        st.error("This file could not be read as UTF-8 text. Please save it as a .txt file and try again.")

st.write("")
run = st.button("Analyze report", disabled=not blood_report, type="primary")
if run:
    api_key = os.getenv("GOOGLE_API_KEY") or os.getenv("GEMINI_API_KEY")
    if not api_key:
        st.error("Add GOOGLE_API_KEY to your .env file (or environment) before analyzing.")
    else:
        try:
            with st.spinner("Reading your report and preparing your guide…"):
                llm = ChatGoogleGenerativeAI(model="gemma-4-31b-it", google_api_key=api_key)

                extraction_prompt = f"""
You are a medical data extraction assistant.

From blood report below, extract all test values and classify each one as HIGH, LOW and NORMAL
based on the refernce ranges provided in the report 

Format your response as :
Test Name : Value | Status : HIGH/LOW/NORMAL | Referene : Range

Blood Report : 
{blood_report}
"""
                extraction_response = llm.invoke(extraction_prompt)
                extraction_value = extraction_response.text

                diet_prompt = f"""
You are clinical nutritionist specializing in Sri Lankan Diatery Habits.

Based on the blood work analysis below, Write: 
1. A Short health summary in 3 lines explaining the patients condition in simple language
2. A short, Practical Indian diet plan having only two section (1) foods to avoid (2) foods to eat more of. 
Do not include any other section in diet plan

Blood work analysis: 
{extraction_value}
"""
                diet_resp = llm.invoke(diet_prompt)

            st.markdown('<div class="section-kicker">03 · Your results</div>', unsafe_allow_html=True)
            tab1, tab2 = st.tabs(["Blood values", "Summary & food guide"])
            with tab1:
                st.markdown('<div class="surface">', unsafe_allow_html=True)
                st.markdown(extraction_value)
                st.markdown('</div>', unsafe_allow_html=True)
            with tab2:
                st.markdown('<div class="surface">', unsafe_allow_html=True)
                st.markdown(diet_resp.text)
                st.markdown('</div>', unsafe_allow_html=True)
            st.caption("AI-generated information can be incomplete or inaccurate. Discuss results and diet changes with a qualified healthcare professional.")
        except Exception as exc:
            st.error(f"Analysis failed: {exc}")
