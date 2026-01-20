import streamlit as st
from streamlit_mic_recorder import mic_recorder
from streamlit_autorefresh import st_autorefresh 
from database import load_data, save_data
import os, time

# 1. الإعدادات والبيانات
st.set_page_config(layout="wide")
data = load_data()
if not os.path.exists("recordings"): os.makedirs("recordings")

S = st.session_state
t_lim = int(data.get('limit', 40))

if S.get('started') and S.get('mode') == "s":
    st_autorefresh(interval=1000, key="timer_refresh")

bg_link = data.get('bg', "") 
colored_indices = data.get('colored_indices', {})

if 'started' not in S: S.started, S.curr, S.mode, S.sec = False, 0, "s", t_lim
if 'last_curr' not in S: S.last_curr = 0
if 'play_audio' not in S: S.play_audio = False

# 2. تنسيق CSS المستقر
st.markdown(f"""<style>
    header,footer{{visibility:hidden;}}
    .stApp {{
        direction:rtl; background: url("{bg_link}") no-repeat center center fixed !important;
        background-size: cover !important;
    }}
    .c-box {{ 
        background: white !important; border: 4px solid #3498db; border-radius: 12px;
        color: black; font-size: 45px; font-weight: bold; text-align: center; 
        padding: 10px 0; margin: 5px; width: 100%; height: 90px;
        display: flex; align-items: center; justify-content: center;
    }}
    .red-text {{ color: red !important; }}
    .word-hint {{
        background-color: rgba(255, 255, 255, 0.9);
        border-bottom: 5px solid #2e7d32; padding: 10px 60px; border-radius: 15px;
        text-align: center; display: inline-block;
    }}
    .timer-text {{
        color: red !important; font-size: 70px !important; font-weight: bold !important;
        text-align: center !important; text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
    }}
    .stMicrophoneButton button {{ 
        height: 45px !important; width: 100% !important; border-radius: 10px !important;
    }}
</style>""", unsafe_allow_html=True)

pg = st.sidebar.radio("القائمة:", ["اللعب 🚀", "الدرجات 🎓"])

if pg == "اللعب 🚀":
    if not S.started:
        st.markdown('<div style="text-align:center; padding-top:50px;">', unsafe_allow_html=True)
        
        # زر البداية في عمود منظم
        _, center_col, _ = st.columns([1, 1, 1])
        with center_col:
            if st.button("🚀 إبدأ التحدي", use_container_width=True): 
                archive = data.get('lessons_archive', {})
                selected = S.get('selected_lesson_key')
                if selected and selected in archive:
                    lesson = archive[selected]
                    # تحميل بيانات الدرس المختار
                    S.active_words = lesson['words']
                    S.active_full = lesson.get('full_words', [""] * len(lesson['words']))
                    S.active_audio = lesson['audio']
                    S.active_colors = lesson.get('colored_indices', {})
                    S.sec = int(lesson.get('limit', 40))
                else:
                    # في حال لم يختر شيئاً يستخدم البيانات الافتراضية
                    S.active_words = data.get('words', [])
                    S.active_full = data.get('full_words', [])
                    S.active_audio = data.get('audio', {})
                    S.active_colors = colored_indices
                
                S.started = True; st.rerun()
            
            # سهم اختيار الدرس صغير وبسيط
            archive = data.get('lessons_archive', {})
            if archive:
                S.selected_lesson_key = st.selectbox("🎯 الدرس:", list(archive.keys()), label_visibility="collapsed")
        
        st.markdown('</div>', unsafe_allow_html=True)
        st.stop()
    
    # واجهة التحدي باستخدام البيانات المحددة
    words = S.get('active_words', [])
    full_words = S.get('active_full', [])
    audio_data = S.get('active_audio', {})
    active_colors = S.get('active_colors', {})

    if S.curr < len(words):
        if S.last_curr != S.curr:
            S.sec = t_lim; S.last_curr = S.curr; S.mode = "s"; S.play_audio = False

        if S.curr < len(full_words) and full_words[S.curr]:
            st.markdown(f'<div style="text-align:center; width:100%;"><div class="word-hint"><h1 style="margin:0; font-size:60px; color:#1b5e20;">{full_words[S.curr]}</h1></div></div>', unsafe_allow_html=True)

        word_data = words[S.curr]
        _, main_cols, _ = st.columns([1, 4, 1])
        with main_cols:
            char_cols = st.columns(4)
            for i in range(4):
                char = word_data[i] if i < len(word_data) else ""
                is_red = active_colors.get(f"w_{S.curr}_{i}", False)
                cl = "c-box red-text" if is_red else "c-box"
                char_cols[i].markdown(f'<div class="{cl}">{char}</div>', unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        m_col = st.columns([1.5, 2, 1.5])[1]
        with m_col:
            if S.mode == "s":
                if S.sec > 0:
                    S.sec -= 1
                    st.markdown(f'<p class="timer-text">{int(S.sec)}</p>', unsafe_allow_html=True)
                else:
                    S.curr += 1; S.sec = t_lim; st.rerun()

                if st.button("📢 استمع للتهجي", use_container_width=True): 
                    S.play_audio = True

                if S.get('play_audio'):
                    aud = audio_data.get(f"s_{S.curr}")
                    if aud: st.audio(aud, format="audio/mp3", autoplay=True)
                
                audio_result = mic_recorder(
                    start_prompt="🎙️ سجل نطقك", 
                    stop_prompt="✅ توقف واحفظ", 
                    key=f"mic_v2_{S.curr}",
                    use_container_width=True
                )
                
                if audio_result:
                    with open(f"recordings/ans_{S.curr}.mp3", "wb") as f:
                        f.write(audio_result['bytes'])
                    st.success("✅ تم حفظ تسجيلك بنجاح!")
                
                if st.button("🎓 تصحيح الكلمة ➡️", use_container_width=True): 
                    S.mode = "c"; st.rerun()
            else:
                st.audio(audio_data.get(f"c_{S.curr}"), autoplay=True)
                if st.button("الكلمة التالية ⏮️", use_container_width=True):
                    S.curr += 1; S.mode = "s"; st.rerun()
    else:
        st.success("🏆 انتهى التحدي!"); st.balloons()
        if st.button("🔄 إعادة"): S.started, S.curr = False, 0; st.rerun()

else:
    st.title("🎓 ملخص نتائج الطالب")
    all_words = data.get('words', [])
    for i, w in enumerate(all_words):
        with st.container():
            c1, c2, c3 = st.columns([1, 4, 1.5])
            c1.write(f"### #{i+1}")
            c2.write(f"كلمة: {' '.join(w)}")
            p_ans = f"recordings/ans_{i}.mp3"
            if os.path.exists(p_ans): c2.audio(p_ans)
            st.markdown("---")