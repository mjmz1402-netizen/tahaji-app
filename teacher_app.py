import streamlit as st
from streamlit_mic_recorder import mic_recorder
from database import save_data, load_data
import time

# 1. نظام الحماية
PASSWORD = "1020"
if "auth" not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.set_page_config(page_title="دخول", layout="centered")
    st.title("🔐 دخول المعلم")
    pwd = st.text_input("الرمز السري:", type="password")
    if st.button("دخول"):
        if pwd == PASSWORD:
            st.session_state.auth = True
            st.rerun()
        else: st.error("❌ خطأ")
    st.stop()

# 2. البيانات والواجهة
st.set_page_config(page_title="لوحة المعلم", layout="wide")
data = load_data()
for k in ['lessons_archive','words','full_words','audio','limit','colored_indices','bg','current_lesson_name']:
    if k not in data: data[k] = {} if k in ['lessons_archive','audio','colored_indices'] else ([] if k in ['words','full_words'] else "")

st.markdown("""<style>.stApp { direction: rtl; } .char-box input { text-align: center; font-weight: bold; font-size: 38px; height: 75px; border: 2px solid #3498db; border-radius: 12px; } .red-text input { color: red !important; border-color: red !important; }</style>""", unsafe_allow_html=True)

st.title("👨‍🏫 لوحة المعلم")
if st.button("🔄 تحديث شامل"):
    data.update({'words':[],'full_words':[],'audio':{},'current_lesson_name':"",'colored_indices':{}})
    save_data(data); st.rerun()

c1, c2, c3 = st.columns([1, 2, 2])
data['limit'] = c1.number_input("⏱️ الزمن:", value=int(data.get('limit', 40)))
data['bg'] = c2.text_input("🖼️ الخلفية:", value=data.get('bg', ""))
data['current_lesson_name'] = c3.text_input("🏷️ اسم الدرس:", value=data.get('current_lesson_name', ""))

st.divider()
num = st.number_input("🔢 عدد الكلمات:", min_value=1, value=len(data['words']) or 1)
nw, nf = [], []

for i in range(num):
    st.write(f"### الكلمة ({i+1})")
    f_val = st.text_input(f"الكلمة كاملة {i}", value=data['full_words'][i] if i<len(data['full_words']) else "", key=f"f_{i}", label_visibility="collapsed")
    nf.append(f_val)
    old_w = data['words'][i] if i<len(data['words']) else ["","","",""]
    cols = st.columns([1,1,1,1,4]); chs = []
    for j in range(4):
        with cols[j]:
            kid = f"w_{i}_{j}"
            red = data['colored_indices'].get(kid, False)
            st.markdown(f'<div class="{"red-text" if red else "char-box"}">', unsafe_allow_html=True)
            v = st.text_input(f"L{j}_{i}", value=old_w[j] if j<len(old_w) else "", key=kid, label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            data['colored_indices'][kid] = st.checkbox("🔴", key=f"c_{i}_{j}", value=red)
            chs.append(v)
    nw.append(chs)
    a_cols = st.columns(2)