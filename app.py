import datetime
import matplotlib.pyplot as plt
import pandas as pd
from supabase import create_client
import streamlit as st
from streamlit_agraph import Config, Edge, Node, agraph

# -----------------------------------------------------------------------------
# 1. SİSTEM VE SAYFA YAPILANDIRMASI
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Şöhret Yelen Akademi",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Supabase Bağlantı Bilgileri
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "https://your-supabase-url.supabase.co")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "your-anon-key")

@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

try:
    supabase = init_supabase()
except Exception as e:
    st.error("Veritabanı bağlantısı kurulamadı. Lütfen .streamlit/secrets.toml ayarlarınızı kontrol edin.")

# Session State (Oturum) Durum Yönetimi
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False
if "username" not in st.session_state:
    st.session_state.username = ""
if "role" not in st.session_state:
    st.session_state.role = ""

# -----------------------------------------------------------------------------
# 2. YARDIMCI MANTIK VE VERİTABANI FONKSİYONLARI
# -----------------------------------------------------------------------------

def update_mistake_spaced_repetition(student_id: str, card_id: int, is_correct: bool):
    """Ebbinghaus Aralıklı Tekrar Modeli (SRS) Güncellemesi"""
    try:
        res = (
            supabase.table("student_mistakes")
            .select("*")
            .eq("student_id", student_id)
            .eq("card_id", card_id)
            .execute()
        )
        if not res.data:
            return

        current_item = res.data[0]
        current_level = current_item.get("box_level", 1)

        if is_correct:
            new_level = current_level + 1
            # 4. seviyeyi geçen soru kalıcı hafızaya alınır ve havuzdan düşer
            if new_level > 4:
                supabase.table("student_mistakes").delete().eq("id", current_item["id"]).execute()
                st.toast("🏆 Harika! Kavram kalıcı hafızaya alındı ve havuzdan çıkarıldı.", icon="🧠")
                return

            intervals = {2: 1, 3: 3, 4: 7, 5: 15}
            days_to_add = intervals.get(new_level, 1)
            next_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=days_to_add)

            supabase.table("student_mistakes").update({
                "box_level": new_level,
                "next_review_date": next_date.isoformat(),
                "status": "reviewing"
            }).eq("id", current_item["id"]).execute()

            st.toast(f"✅ Doğru! Soru Seviye {new_level}'e yükseldi ({days_to_add} gün sonra tekrar sorulacak).", icon="📅")
        else:
            # Yanlış cevap verildiğinde soru doğrudan Seviye 1'e geriler
            next_date = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=1)
            supabase.table("student_mistakes").update({
                "box_level": 1,
                "next_review_date": next_date.isoformat(),
                "status": "wrong"
            }).eq("id", current_item["id"]).execute()
            st.warning("❌ Yanlış cevap. Soru tekrar Seviye 1'e geriledi. Yarın tekrar çözülecek.")
    except Exception as e:
        st.error(f"SRS Güncelleme Hatası: {e}")


def create_automatic_assignment(student_id: str, subject: str, topic: str, teacher_id: str, due_days: int = 7):
    """Sınıf/Öğrenci Bazlı Otomatik Ödev Tanımlama"""
    try:
        cards_data = (
            supabase.table("flashcards")
            .select("id")
            .eq("subject", subject)
            .eq("topic", topic)
            .execute()
            .data
        )
        if not cards_data:
            st.error(f"❌ **{topic}** konusuna ait kayıtlı soru bulunamadı.")
            return False

        card_ids = [c["id"] for c in cards_data]
        due_date = (datetime.datetime.now() + datetime.timedelta(days=due_days)).isoformat()

        payload = {
            "student_id": student_id,
            "subject": subject,
            "topic": topic,
            "assigned_by": teacher_id,
            "card_ids": card_ids,
            "status": "pending",
            "due_date": due_date
        }
        supabase.table("assignments").insert(payload).execute()
        st.toast(f"✅ {student_id} için '{topic}' ödevi atandı!", icon="🎉")
        return True
    except Exception as e:
        st.error(f"Ödev atama hatası: {e}")
        return False

# -----------------------------------------------------------------------------
# 3. KULLANICI GİRİŞ ARAYÜZÜ (LOGIN)
# -----------------------------------------------------------------------------
if not st.session_state.authenticated:
    st.title("🎓 Şöhret Yelen Akademi")
    st.subheader("Sisteme Giriş Yapın")

    col_login, _ = st.columns([1, 1])
    with col_login:
        username_input = st.text_input("Kullanıcı Adı", value="ahmet_yildiz")
        role_input = st.selectbox("Rolünüz", ["Öğrenci", "Öğretmen"])

        if st.button("Giriş Yap", use_container_width=True):
            if username_input:
                st.session_state.authenticated = True
                st.session_state.username = username_input
                st.session_state.role = "student" if role_input == "Öğrenci" else "teacher"
                st.rerun()
            else:
                st.warning("Lütfen kullanıcı adınızı girin.")
    st.stop()

# -----------------------------------------------------------------------------
# 4. YAN MENÜ (SIDEBAR) & OTURUM KONTROLÜ
# -----------------------------------------------------------------------------
st.sidebar.title("🎓 Şöhret Yelen Akademi")
st.sidebar.markdown(f"**Kullanıcı:** `{st.session_state.username}`")
st.sidebar.markdown(f"**Rol:** {'Öğretmen 👨‍🏫' if st.session_state.role == 'teacher' else 'Öğrenci 🧑‍🎓'}")

if st.sidebar.button("🚪 Çıkış Yap", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.username = ""
    st.session_state.role = ""
    st.rerun()

st.sidebar.markdown("---")

# -----------------------------------------------------------------------------
# 5. ÖĞRENCİ MODÜLÜ
# -----------------------------------------------------------------------------
if st.session_state.role == "student":
    st.title(f"👋 Hoş Geldin, {st.session_state.username}")

    tab_srs, tab_assignments, tab_graph = st.tabs([
        "🧠 Aralıklı Tekrar & Hafıza Kutuları",
        "📌 Atanan Ödevlerim",
        "🌐 Kişisel Bilgi Ağım"
    ])

    # --- TAB 1: ARALIKLI TEKRAR MODU ---
    with tab_srs:
        st.subheader("🧠 Hafıza Kutuları Durumu (Leitner Modeli)")

        try:
            mistakes_res = (
                supabase.table("student_mistakes")
                .select("box_level")
                .eq("student_id", st.session_state.username)
                .execute()
                .data
            )
            counts = {1: 0, 2: 0, 3: 0, 4: 0}
            for m in mistakes_res:
                lvl = m.get("box_level", 1)
                if lvl in counts:
                    counts[lvl] += 1
        except Exception:
            counts = {1: 0, 2: 0, 3: 0, 4: 0}

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("🔴 1. Seviye", f"{counts[1]} Soru", "1 Günlük Tekrar")
        c2.metric("🟧 2. Seviye", f"{counts[2]} Soru", "3 Günlük Tekrar")
        c3.metric("🟦 3. Seviye", f"{counts[3]} Soru", "7 Günlük Tekrar")
        c4.metric("🏆 4. Seviye", f"{counts[4]} Soru", "Kalıcı Hafıza")

        st.markdown("---")
        st.subheader("🔄 Bugün Çözülmesi Gereken Tekrar Kartları")

        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            due_cards_raw = (
                supabase.table("student_mistakes")
                .select("card_id, box_level, flashcards(*)")
                .eq("student_id", st.session_state.username)
                .lte("next_review_date", now_iso)
                .execute()
                .data
            )
        except Exception:
            due_cards_raw = []

        if not due_cards_raw:
            st.success("🎉 Harika! Bugün çözülmesi gereken hiçbir tekrar kartınız yok.")
        else:
            item = due_cards_raw[0]
            card = item["flashcards"]
            level = item["box_level"]

            progress_val = level * 0.25
            st.progress(progress_val, text=f"Öğrenme İlerlemesi: Seviye {level} / 4")

            with st.container(border=True):
                st.markdown(f"Ders / Konu: - **{card['topic']}**")
                st.markdown(f"### ❓ Soru: {card['term']}")

                options = [
                    card["definition"],
                    card["distractor_1"],
                    card["distractor_2"],
                    card["distractor_3"]
                ]
                user_ans = st.radio("Cevabınız:", options, key=f"ans_{card['id']}")

                if st.button("Cevabı Onayla", use_container_width=True):
                    is_correct = (user_ans == card["definition"])
                    update_mistake_spaced_repetition(st.session_state.username, card["id"], is_correct)
                    st.rerun()

    # --- TAB 2: ÖDEVLER ---
    with tab_assignments:
        st.subheader("📌 Öğretmen Tarafından Atanan Özel Çalışma Setleri")
        try:
            asgns = (
                supabase.table("assignments")
                .select("*")
                .eq("student_id", st.session_state.username)
                .execute()
                .data
            )
        except Exception:
            asgns = []

        if not asgns:
            st.info("Atanmış aktif ödeviniz bulunmamaktadır.")
        else:
            for asg in asgns:
                with st.container(border=True):
                    st.markdown(f"#### 📚 {asg['subject']} - {asg['topic']}")
                    st.caption(f"Atayan: {asg['assigned_by']} | Son Teslim: {asg['due_date'][:10]}")

    # --- TAB 3: KİŞİSEL KNOWLEDGE GRAPH ---
    with tab_graph:
        st.subheader("🌐 Bireysel Kavram Ağım ve Kör Noktalarım")
        st.caption("Fizik ve Matematik konularındaki kişisel kavramsal bağlarınız.")

        nodes = [
            Node(id="Trigonometri", label="Trigonometri\n(%40 Başarı)", size=25, color="#EF4444"),
            Node(id="Vektörler", label="Vektörler\n(%65 Başarı)", size=25, color="#3B82F6"),
            Node(id="Eğik Atış", label="Eğik Atış\n(%30 Başarı)", size=25, color="#F97316")
        ]
        edges = [
            Edge(source="Trigonometri", target="Vektörler"),
            Edge(source="Vektörler", target="Eğik Atış")
        ]
        config = Config(width=700, height=400, directed=True, physics=True)
        agraph(nodes=nodes, edges=edges, config=config)

# -----------------------------------------------------------------------------
# 6. ÖĞRETMEN MODÜLÜ
# -----------------------------------------------------------------------------
else:
    st.title("📊 Öğretmen Yönetim & Analiz Paneli")

    tab_t1, tab_t2 = st.tabs([
        "⚠️ Takılınan Konular & Otomatik Ödevlendirme",
        "🌐 Sınıf Düzeyi Knowledge Graph"
    ])

    # --- TAB 1: YANLIŞ ANALİZİ VE ÖDEV ATAMA ---
    with tab_t1:
        st.subheader("⚠️ En Çok Yanlış Yapılan Konular ve Anlık Ödevlendirme")

        try:
            mistakes_data = supabase.table("student_mistakes").select("*").execute().data
        except Exception:
            mistakes_data = []

        if not mistakes_data:
            st.info("Sistemde henüz kaydedilmiş yanlış soru verisi yok.")
        else:
            df = pd.DataFrame(mistakes_data)
            grouped = df.groupby(["student_id", "subject", "topic"]).size().reset_index(name="hata_sayisi")
            grouped = grouped.sort_values(by="hata_sayisi", ascending=False)

            col_chart, col_list = st.columns([5, 4])

            with col_chart:
                st.write("📊 **Konu Bazlı Sınıf Hata Frekansı:**")
                top_topics = df.groupby("topic").size().reset_index(name="toplam_hata").head(8)

                fig, ax = plt.subplots(figsize=(6, 3.5), dpi=150)
                ax.barh(top_topics["topic"], top_topics["toplam_hata"], color="#EF4444")
                ax.set_xlabel("Toplam Yanlış / Boş Frekansı")
                ax.spines["top"].set_visible(False)
                ax.spines["right"].set_visible(False)
                plt.tight_layout()
                st.pyplot(fig)

            with col_list:
                st.write("📋 **Öğrenci Bazlı Kritik Konular:**")
                for idx, row in grouped.iterrows():
                    with st.container(border=True):
                        st.markdown(f"👤 **Öğrenci:** `{row['student_id']}`")
                        st.markdown(f"📚 **Ders/Konu:** {row['subject']} - **{row['topic']}** ({row['hata_sayisi']} Hata)")

                        if st.button("⚡ Otomatik Ödev At", key=f"asgn_btn_{idx}"):
                            create_automatic_assignment(
                                student_id=row["student_id"],
                                subject=row["subject"],
                                topic=row["topic"],
                                teacher_id=st.session_state.username
                            )

    # --- TAB 2: SINIF DÜZEYİ KNOWLEDGE GRAPH ---
    with tab_t2:
        st.subheader("🌐 Sınıf Geneli Müfredat & Kör Nokta Haritası")
        st.caption("Kırmızı ve büyük düğümler sınıf genelinde yaşanan ortak kavramsal bariyerlerdir.")

        nodes = [
            Node(id="Dik Üçgen", label="Dik Üçgen / Eğim\nOrt: %88", size=20, color="#10B981"),
            Node(id="Trigonometri", label="Trigonometri (ORTAK KÖR NOKTA)\nOrt: %42 | 14 Öğrenci Riskli", size=45, color="#EF4444"),
            Node(id="Vektörler", label="Vektörler\nOrt: %61", size=28, color="#3B82F6"),
            Node(id="Eğik Atış", label="Eğik Atış (Tıkanılan Hedef)\nOrt: %35 | 16 Öğrenci Riskli", size=50, color="#F97316")
        ]
        edges = [
            Edge(source="Dik Üçgen", target="Trigonometri"),
            Edge(source="Trigonometri", target="Vektörler"),
            Edge(source="Vektörler", target="Eğik Atış")
        ]
        config = Config(width=750, height=450, directed=True, physics=True)

        col_g, col_a = st.columns([5, 3])
        with col_g:
            agraph(nodes=nodes, edges=edges, config=config)

        with col_a:
            with st.container(border=True):
                st.error("🚨 **Sınıf Genel Tıkanıklık Teşhisi**")
                st.markdown("**Ortak Kör Nokta:** Trigonometri")
                st.write("**Etkilenen Öğrenci:** 14 / 18 Öğrenci (%77)")
                st.warning("Eğik Atış konusuna geçilmeden önce Trigonometri türetim adımları tekrar edilmelidir.")
                if st.button("📢 Sınıfa Toplu Trigonometri Etüdü Tanımla"):
                    st.toast("14 öğrencinin paneline etüt seti başarıyla gönderildi!")
