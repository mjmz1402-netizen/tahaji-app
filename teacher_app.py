import streamlit as st
from streamlit_mic_recorder import mic_recorder
from database import save_data, load_data
import time

# --- 1. إعدادات الصفحة مباشرة بدون حماية ---
st.set_page_config(page_title="لوحة المعلم - محمد 2", layout="wide")
data = load_data()

# التأكد من وجود المفاتيح الأساسية
keys = ['lessons_archive', 'words', 'full_words', 'audio', 'limit', 'colored_indices', 'bg', 'current_lesson_name']
for k in keys:
    if k not in data: 
        data[k] = {} if k in ['lessons_archive', 'audio', 'colored_indices'] else ([] if k in ['words', 'full_words'] else "")
if not data.get('limit'): data['limit'] = 40

st.markdown("""<style>
    .stApp { direction: rtl; }
    .char-box input {
        text-align: center !important; font-weight: bold !important;
        font-size: 38px !important; height: 75px !important; width: 75px !important;
        border: 2px solid #3498db !important; border-radius: 12px !important;
    }
    .red-text input { color: red !important; border-color: red !important; }
    h1, h2, h3, h4 { text-align: right; }
</style>""", unsafe_allow_html=True)

col_t, col_r = st.columns([5, 1])
with col_t: st.title("👨‍🏫 لوحة المعلم (دخول مباشر)")
with col_r: 
    if st.button("🔄 تحديث"):
        data.update({'words': [], 'full_words': [], 'audio': {}, 'current_lesson_name': "", 'colored_indices': {}})
        save_data(data); st.rerun()

st.subheader("⚙️ الإعدادات العامة")
c_timer, c_bg, c_name = st.columns([1, 2, 2])
data['limit'] = c_timer.number_input("⏱️ الزمن (ثانية):", value=int(data.get('limit', 40)))
data['bg'] = c_bg.text_input("🖼️ رابط الخلفية:", value=data.get('bg', ""))
data['current_lesson_name'] = c_name.text_input("🏷️ عنوان الدرس الحالي:", value=data.get('current_lesson_name', ""))

st.divider()

num_words = st.number_input("🔢 عدد الكلمات:", min_value=1, value=len(data['words']) if data['words'] else 1, step=1)
new_words_list, new_full_words = [], [] 

for i in range(num_words):
    st.markdown(f"### 📝 الكلمة رقم ({i+1})")
    f_val = st.text_input(f"الكلمة كاملة {i+1}", value=data['full_words'][i] if i < len(data['full_words']) else "", key=f"f_{i}")
    new_full_words.append(f_val)

    old_data = data['words'][i] if i < len(data['words']) else ["", "", "", ""]
    char_cols = st.columns([1, 1, 1, 1, 6]) 
    current_chars = []
    
    for idx in range(4):
        with char_cols[idx]:
            kid = f"w_{i}_{idx}"
            is_red = data['colored_indices'].get(kid, False)
            st.markdown(f'<div class="{"red-text" if is_red else "char-box"}">', unsafe_allow_html=True)
            char_val = st.text_input(f"حرف {idx+1}", value=old_data[idx] if idx < len(old_data) else "", key=kid, label_visibility="collapsed")
            st.markdown('</div>', unsafe_allow_html=True)
            data['colored_indices'][kid] = st.checkbox("🔴", key=f"c_{i}_{idx}", value=is_red)
            current_chars.append(char_val)
    new_words_list.append(current_chars)
    
    aud_cols = st.columns(2)
    with aud_cols[0]:
        s_rec = mic_recorder(start_prompt=f"🎤 سجل تهجي {i+1}", key=f"ms_{i}")
        if s_rec: data['audio'][f"s_{i}"] = s_rec['bytes']
        if f"s_{i}" in data['audio']: st.audio(data['audio'][f"s_{i}"])
    with aud_cols[1]:
        c_rec = mic_recorder(start_prompt=f"🎤 سجل نطق {i+1}", key=f"mc_{i}")
        if c_rec: data['audio'][f"c_{i}"] = c_rec['bytes']
        if f"c_{i}" in data['audio']: st.audio(data['audio'][f"c_{i}"])
    st.markdown("---")

data['words'], data['full_words'] = new_words_list, new_full_words

if st.button("💾 حفظ وإرسال للطالب + أرشفة", use_container_width=True):
    lesson_name = data['current_lesson_name'] if data['current_lesson_name'] else f"درس {time.strftime('%Y-%m-%d %H:%M')}"
    data['lessons_archive'][lesson_name] = {
        'words': data['words'], 'full_words': data['full_words'], 
        'audio': data['audio'].copy(), 'limit': data['limit'], 'bg': data['bg'],
        'colored_indices': data['colored_indices'].copy()
    }
    save_data(data); st.success(f"✅ تم الحفظ والأرشفة بنجاح باسم: {lesson_name}")

st.divider()

st.subheader("📚 مخزن الدروس")
archive = data.get('lessons_archive', {})
if archive:
    for name in list(archive.keys()):
        col_n, col_act, col_del = st.columns([4, 1, 1])
        with col_n: st.info(f"📖 {name}")
        with col_act:
            if st.button("✅ تفعيل", key=f"act_{name}"):
                arc = archive[name]
                data.update({
                    'words': arc['words'], 'audio': arc['audio'], 'full_words': arc.get('full_words', []),
                    'limit': arc['limit'], 'bg': arc['bg'], 'current_lesson_name': name,
                    'colored_indices': arc.get('colored_indices', {})
                })
                save_data(data); st.rerun()
        with col_del:
            if st.button("🗑️ حذف", key=f"del_{name}"):
                del data['lessons_archive'][name]; save_data(data); st.rer