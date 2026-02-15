import streamlit as st
import google.generativeai as genai
import json, re, time

st.set_page_config(page_title="מתווך בקליק", layout="centered")
st.markdown("""<style>
* { direction: rtl !important; text-align: right !important; }
.lesson-box { background:#fdfdfd; padding:20px; border-radius:12px; border-right:6px solid #1E88E5; line-height:1.8; margin-bottom:20px; }
.explanation-box { padding:15px; border-radius:8px; margin-top:10px; border-right:5px solid; }
.success { background:#e8f5e9; border-color:#4caf50; color:#2e7d32; }
.error { background:#ffebee; border-color:#f44336; color:#c62828; }
.timer-box { font-size:20px; font-weight:bold; color:#d32f2f; text-align:center; background:#fff1f1; padding:10px; border-radius:10px; border:1px solid #d32f2f; margin-bottom:15px; }
</style>""", unsafe_allow_html=True)

S = st.session_state
if 'user' not in S:
    S.update({'user':'','step':'login','lt':'','qa':False,'qi':0,'qans':{},'qq':[],'cq':set(),'ei':0,'eans':{},'eq':[],'start_time':None})

def parse_j(t):
    try:
        m = re.search(r'\[\s*\{.*\}\s*\]', t, re.DOTALL)
        return json.loads(m.group()) if m else None
    except: return None
