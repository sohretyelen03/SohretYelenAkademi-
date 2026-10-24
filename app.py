import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI
# ---------------------------------------------------------
st.set_page_config(
    page_title="Şöhret Yelen Akademi - Güvenli LMS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 2. SUPABASE BAĞLANTISI
# ---------------------------------------------------------
SUPABASE_URL = st.secrets.get("SUPABASE_URL", "")
SUPABASE_KEY = st.secrets.get("SUPABASE_KEY", "")


@st.cache_resource
def init_supabase():
  if not SUPABASE_URL or not SUPABASE_KEY:
    st.error(
        "Supabase bağlantı bilgileri (URL / Key) Streamlit Secrets içinde"
        " bulunamadı!"
    )
    st.stop()
  return create_client(SUPABASE_URL, SUPABASE_KEY)


supabase = init_supabase()

# ---------------------------------------------------------
# 3. OTURUM (SESSION STATE) KONTROLÜ
# ---------------------------------------------------------
if "authenticated" not in st.session_state:
  st.session_state["authenticated"] = False

# =========================================================
# GİRİŞ EKRANI (Eğer oturum açılmadıysa)
# =========================================================
if not st.session_state["authenticated"]:
  st.markdown("<br><br>", unsafe_allow_html=True)
  col1, col2, col3 = st.columns([1, 2, 1])

  with col2:
    st.markdown(
        "<h2 style='text-align: center;'>🎓 Şöhret Yelen Akademi</h2>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align: center; color: gray;'>EBA Tarzı Yapılandırmacı"
        " Eğitim ve Yönetim Paneli</p>",
        unsafe_allow_html=True,
    )
    st.markdown("---")

    with st.form("login_form"):
      st.markdown("### 🔐 Yetkili Girişi")
      email_input = st.text_input(
          "E-posta Adresi", placeholder="ornek@sohretyelen.com"
      )
      password_input = st.text_input(
          "Şifre", type="password", placeholder="••••••••"
      )
      submit_login = st.form_submit_button(
          "Güvenli Giriş Yap", use_container_width=True
      )

      if submit_login:
        if email_input and password_input:
          try:
            response = supabase.auth.sign_in_with_password({
                "email": email_input,
                "password": password_input,
            })
            if response.user:
              st.session_state["authenticated"] = True
              st.session_state["user_email"] = email_input
              st.success("Giriş başarılı! Yönlendiriliyorsunuz...")
              st.rerun()
          except Exception as e:
            st.error(
                "Giriş başarısız! E-posta veya şifre hatalı.\nHata: {e}"
            )
        else:
          st.warning("Lütfen e-posta ve şifrenizi giriniz.")

    st.info(
        "💡 *Not: Supabase Authentication üzerinden yetkilendirilmiş hesap"
        " gereklidir.*"
    )

  st.stop()

# =========================================================
# ANA UYGULAMA SABİTLERİ (YKS KONULARI)
# =========================================================
TYT_MAT_KONULARI = [
    "Temel Kavramlar & Sayılar",
    "Bölme - Bölünebilme & EBOB-EKOK",
    "Rasyonel Sayılar & Basit Eşitsizlikler",
    "Mutlak Değer & Üslü-Köklü İfadeler",
    "Çarpanlara Ayırma & Oran-Orantı",
    "Problemler (Sayı, Kesir, Yaş, Yüzde, Hareket)",
    "Mantık, Kümeler & Fonksiyonlar",
    "Permütasyon, Kombinasyon, Olasılık",
    "TYT Geometri (Doğroda-Üçgende Açılar, Çokgenler)",
]

TYT_FIZIK_KONULARI = [
    "Fizik Bilimine Giriş & Madde ve Özellikleri",
    "Kuvvet, Hareket & Vektörler (Temel)",
    "İş, Güç ve Enerji",
    "Isı, Sıcaklık ve Genleşme",
    "Basınç ve Kaldırma Kuvveti",
    "Elektrostatik & Elektrik Akımı",
    "Dalgalar & Optik (Yansıma, Kırılma, Mercekler)",
]

AYT_MAT_KONULARI = [
    "Polinomlar & 2. Dereceden Denklemler",
    "Karmaşık Sayılar & Eşitsizlik Sistemleri",
    "Parabol & Fonksiyon Uygulamaları",
    "Trigonometri (Teoremler, Denklemler, Grafikler)",
    "Logaritma & Diziler (Aritmetik/Geometrik)",
    "Limit ve Süreklilik",
    "Türev & Uygulamaları (Maks-Min, Teğet Eğimi)",
    "İntegral & Alan Hesabı",
    "AYT Analitik Geometri & Çemberin Analitiği",
]

AYT_FIZIK_KONULARI = [
    "Vektörler & Bağıl Hareket",
    "Newton'un Hareket Yasaları & 1D/2D Atışlar",
    "İş, Enerji ve Çizgisel Momentum",
    "Tork, Denge & Kütle Merkezi",
    "Elektriksel Alan, Potansiyel & Kondansatörler",
    "Manyetizma, İndüksiyon & Alternatif Akım",
    "Düzgün Çembersel Hareket & Dönerek Öteleme",
    "Basit Harmonik Hareket & Kepler Yasaları",
    "Dalga Mekaniği (Girişim, Kırınım, Doppler)",
    "Atom Fiziğine Giriş, Fotoelektrik & Modern Fizik",
]

# ---------------------------------------------------------
# YAN MENÜ (SIDEBAR)
# ---------------------------------------------------------
with st.sidebar:
  st.title("🎓 Şöhret Yelen Akademi")
  st.caption("EBA Tarzı Yapılandırmacı LMS")
  st.markdown("---")
  st.markdown(f"**👤 Aktif Eğitmen:** {st.session_state.get('user_email', '-')}")
  st.markdown("**🛡️ Rol:** Kurucu / Master Yönetici")
  st.markdown("---")
  st.markdown("### 📌 Sistem İstatistikleri")

  try:
    res = supabase.table("flashcards").select("id", count="exact").execute()
    total_q = res.count if res.count is not None else 0
    st.metric(label="Toplam Kayıtlı Soru", value=total_q)
  except Exception:
    st.metric(label="Toplam Kayıtlı Soru", value="-")

  st.markdown("---")
  if st.button("🚪 Oturumu Kapat (Çıkış Yap)", use_container_width=True):
    supabase.auth.sign_out()
    st.session_state["authenticated"] = False
    st.rerun()

# ---------------------------------------------------------
# ANA BAŞLIK
# ---------------------------------------------------------
st.title("📚 Şöhret Yelen Akademi | Dijital Eğitim Portalı")
st.markdown(
    "İlkokul, Ortaokul, LGS ve **YKS (TYT/AYT Matematik & Fizik)** EBA Tarzı"
    " Yönetim ve İçerik Merkezi."
)
st.markdown("---")

# ---------------------------------------------------------
# EBA TARZI 5'Lİ MODÜLER SEKME YAPISI
# ---------------------------------------------------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🏛️ Ana Pano",
    "🎯 Çalışma Kağıdı & Ödev",
    "🔗 Konu Sayfaları & Yanılgılar",
    "➕ Yeni Soru Ekle",
    "📚 Soru Deposu & Sunum Modu",
])

# =========================================================
# SEKME 1: 🏛️ ANA PANO (EBA Tarzı Dashboard)
# =========================================================
with tab1:
  st.subheader("🏛️ Şöhret Yelen Akademi - Yönetim Panosu")
  st.markdown(
      "Sistemdeki tüm materyallere hızlıca erişin ve genel durumu gözlemleyin."
  )

  # Üst Özet Kartları (Metrikler)
  col_m1, col_m2, col_m3, col_m4 = st.columns(4)
  with col_m1:
    st.metric(
        label="📚 Toplam Soru Havuzu",
        value=total_q if "total_q" in locals() else "0",
    )
  with col_m2:
    st.metric(label="🎯 Aktif Sınav Kademeleri", value="İlkokul - LGS - YKS")
  with col_m3:
    st.metric(label="🧪 Fizik & Matematik", value="Entegre Modül")
  with col_m4:
    st.metric(label="🛡️ Güvenlik Durumu", value="Aktif (Supabase Auth)")

  st.markdown("---")
  st.markdown("### ⚡ Hızlı Erişim Kısayolları")

  hc1, hc2, hc3 = st.columns(3)
  with hc1:
    st.info("🎯 **Çalışma Kağıdı Oluştur**\n\nSeçtiğin konulardan test föyü hazırla.")
  with hc2:
    st.success(
        "🔗 **Konu & Yanılgı İncele**\n\nFizik/Matematik formül ve tuzakları."
    )
  with hc3:
    st.warning("➕ **Soru Ekle**\n\nDinamik şıklar ve zorluk dereceleriyle ekle.")

  st.markdown("---")
  st.markdown(
      "💡 *Sol sekmeleri kullanarak dilediğiniz modüle anında geçiş"
      " yapabilirsiniz.*"
  )

# =========================================================
# SEKME 2: 🎯 ÇALIŞMA KAĞIDI & ÖDEV OLUŞTURUCU
# =========================================================
with tab2:
  st.subheader("🎯 Akıllı Çalışma Kağıdı & Test Föyü Hazırlayıcı")
  st.markdown(
      "Soru deposundan kriterlere uygun soruları süzerek çalışma kağıdı"
      " oluşturun."
  )

  wc1, wc2, wc3 = st.columns(3)
  with wc1:
    work_grade = st.selectbox(
        "Seviye / Sınav Grubu",
        ["İlkokul", "Ortaokul", "LGS", "TYT", "AYT", "Lise"],
        key="w_grade",
    )
  with wc2:
    work_diff = st.selectbox(
        "Zorluk Hedefi",
        ["Tümü", "🟢 Kolay", "🟡 Orta", "🔴 Zor"],
        key="w_diff",
    )
  with wc3:
    work_limit = st.slider(
        "Soru Adedi Seçin", min_value=1, max_value=20, value=5
    )

  if st.button("🚀 Çalışma Kağıdını Derle", use_container_width=True):
    try:
      resp = supabase.table("flashcards").select("*").execute()
      q_data = resp.data
      if q_data:
        matched_qs = [
            q
            for q in q_data
            if work_grade.lower() in str(q.get("grade", "")).lower()
            and (work_diff == "Tümü" or work_diff in str(q.get("difficulty", "")))
        ]
        selected_qs = matched_qs[:work_limit]

        if selected_qs:
          st.success(
              f"🎉 Başarıyla {len(selected_qs)} soruluk çalışma kağıdı"
              " derlendi!"
          )
          st.markdown("---")
          for idx, item in enumerate(selected_qs, 1):
            st.markdown(f"**Soru {idx}:** {item.get('question_text')}")
            if item.get("image_url"):
              st.image(item.get("image_url"), width=300)
            st.markdown(
                f"- A) {item.get('option_a')}\n- B)"
                f" {item.get('option_b')}\n- C) {item.get('option_c')}\n- D)"
                f" {item.get('option_d')}"
                + (
                    f"\n- E) {item.get('option_e')}"
                    if item.get("option_e")
                    else ""
                )
            )
            st.caption(
                f"Doğru Cevap: {item.get('correct_answer')} | Zorluk:"
                f" {item.get('difficulty')}"
            )
            st.markdown("---")
        else:
          st.warning(
              "Bu kriterlere uygun veritabanında soru bulunamadı. Lütfen önce"
              " soru ekleyin."
          )
    except Exception as e:
      st.error(f"Çalışma kağıdı oluşturulurken hata: {e}")

# =========================================================
# SEKME 3: 🔗 KAVRAM HARİTASI, KONU SAYFALARI & YANILGILAR
# =========================================================
with tab3:
  st.subheader("🔗 YKS & Ders Konu Sayfaları ve Kavram Yanılgıları")
  st.markdown(
      "Formül derivasyonları, animasyon alanları ve öğrencilerin en sık"
      " düştüğü tuzaklar."
  )

  yks_exam_type = st.radio(
      "Sınav / Alan Türü:",
      ["🔴 TYT (Temel Yeterlilik)", "🟣 AYT (Alan Yeterlilik)"],
      horizontal=True,
  )

  if "TYT" in yks_exam_type:
    sub_t_mat, sub_t_fiz = st.tabs(
        ["📐 TYT Matematik Sayfaları", "🧲 TYT Fizik Sayfaları"]
    )

    with sub_t_mat:
      st.selectbox("TYT Matematik Konusu:", TYT_MAT_KONULARI)
      st.markdown("### 💡 Konu Özeti & Formül Çıkarımı")
      st.latex(r"(a+b)^2 = a^2 + 2ab + b^2")
      st.warning(
          "⚠️ **Kavram Yanılgısı:** Öğrenciler genellikle $(a+b)^2$ ifadesini"
          " $a^2 + b^2$ olarak açma hatası yaparlar."
      )

    with sub_t_fiz:
      st.selectbox("TYT Fizik Konusu:", TYT_FIZIK_KONULARI)
      st.markdown("### 💡 Fizik Bilimine Giriş & Madde")
      st.success(
          "💡 **İpucu:** Özkütle ($d = m/V$) ayırt edici bir özelliktir ancak"
          " tek başına sabit değildir; sıcaklık ve basınçla değişebilir!"
      )

  else:
    sub_a_mat, sub_a_fiz = st.tabs(
        ["📐 AYT Matematik Sayfaları", "🧲 AYT Fizik Sayfaları"]
    )

    with sub_a_mat:
      st.selectbox("AYT Matematik Konusu:", AYT_MAT_KONULARI)
      st.markdown("### 📐 Türev & Teğet Eğimi")
      st.latex(r"f'(x) = \lim_{h \to 0} \frac{f(x+h) - f(x)}{h}")
      st.warning(
          "⚠️ **Kavram Yanılgısı:** Türevin sıfır olduğu noktalar her zaman"
          " yerel ekstremum olmak zorunda değildir (Örn: $f(x)=x^3$). Başlangıç"
          " büküm noktası olabilir."
      )

    with sub_a_fiz:
      st.selectbox("AYT Fizik Konusu:", AYT_FIZIK_KONULARI)
      st.markdown("### 🧲 Düzgün Çembersel Hareket & İvme")
      st.latex(r"a_c = \frac{v^2}{r} = \omega^2 r")
      st.success(
          "💡 **Mantıksal Temel:** Cisim sabit hızla dönse bile hız vektörünün"
          " yönü sürekli değiştiği için merkezcil ivme daima mevcuttur."
      )

# =========================================================
# SEKME 4: ➕ YENİ SORU EKLEME
# =========================================================
with tab4:
  st.subheader("➕ Yeni Soru & Flashcard Ekleme Paneli")
  st.markdown(
      "Seçilen seviyeye göre şık sayısı (4 veya 5) otomatik ayarlanır."
  )

  with st.form("add_question_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
      subject = st.selectbox(
          "Ders Seçin", ["Fizik", "Matematik", "Fen Bilgisi"]
      )
      grade = st.selectbox(
          "Sınıf / Sınav Seviyesi",
          [
              "İlkokul / 1-4. Sınıf",
              "Ortaokul / 5-7. Sınıf",
              "Ortaokul / 8. Sınıf (LGS)",
              "Lise / 9. Sınıf",
              "Lise / 10. Sınıf",
              "Lise / 11. Sınıf",
              "Lise / 12. Sınıf",
              "YKS / TYT Hazırlık",
              "YKS / AYT Hazırlık",
          ],
      )

    with c2:
      topic = st.text_input(
          "Konu / Alt Kazanım",
          placeholder="Örn: AYT Türev / TYT Hareket / Ebob-Ekok",
      )
      question_type = st.selectbox(
          "Soru Tipi",
          [
              "Kazanım Kavrama",
              "Yeni Nesil / Beceri Temelli",
              "LGS Çıkmış / Örnek Soru",
              "ÖSYM / TYT Formatı",
              "ÖSYM / AYT Formatı",
          ],
      )

    with c3:
      difficulty = st.radio(
          "Zorluk Derecesi", ["🟢 Kolay", "🟡 Orta", "🔴 Zor"]
      )

    st.markdown("---")
    question_text = st.text_area(
        "Soru Metni", placeholder="Sorunun detaylı metnini buraya yazın..."
    )
    image_url = st.text_input(
        "Soru Görseli URL (Varsa)", placeholder="https://..."
    )

    is_five_options = (
        ("Lise" in grade) or ("YKS" in grade) or ("TYT" in grade) or ("AYT" in grade)
    )
    option_count = 5 if is_five_options else 4
    option_labels = ["A", "B", "C", "D", "E"][:option_count]

    st.markdown(
        f"**Seçenekler ({option_count} Şık - {'Lise / YKS Formatı' if is_five_options else 'İlkokul / Ortaokul Formatı'}):**"
    )

    sc1, sc2 = st.columns(2)
    with sc1:
      opt_a = st.text_input("A Şıkkı Metni")
      opt_b = st.text_input("B Şıkkı Metni")
      opt_c = st.text_input("C Şıkkı Metni")
    with sc2:
      opt_d = st.text_input("D Şıkkı Metni")
      opt_e = st.text_input("E Şıkkı Metni") if is_five_options else ""

    correct_answer = st.selectbox(
        "🎯 Doğru Cevap Hangi Şık?",
        option_labels,
        format_func=lambda x: f"{x} Şıkkı",
    )

    st.markdown("---")
    st.markdown("**Pedagojik Notlar & Yanılgılar:**")
    tc1, tc2 = st.columns(2)
    with tc1:
      term = st.text_input("Önemli Terim / Kavram", placeholder="Örn: Türev")
      misconception = st.text_input(
          "Olası Kavram Yanılgısı", placeholder="Örn: Sıfır türev noktası"
      )
    with tc2:
      definition = st.text_area(
          "Terim Tanımı / Açıklaması", placeholder="Kavramın mantığı..."
      )

    submit_btn = st.form_submit_button("💾 Soruyu Veritabanına Kaydet")

    if submit_btn:
      if question_text and topic and opt_a and opt_b:
        try:
          payload = {
              "subject": subject,
              "grade": grade,
              "topic": topic,
              "difficulty": difficulty,
              "question_type": question_type,
              "question_text": question_text,
              "image_url": image_url if image_url else None,
              "option_a": opt_a,
              "option_b": opt_b,
              "option_c": opt_c,
              "option_d": opt_d,
              "option_e": opt_e if is_five_options else None,
              "correct_answer": correct_answer,
              "term": term if term else None,
              "definition": definition if definition else None,
              "misconception": misconception if misconception else None,
          }
          supabase.table("flashcards").insert(payload).execute()
          st.success("Soru başarıyla kaydedildi! 🎉")
        except Exception as err:
          st.error(f"Hata oluştu: {err}")
      else:
        st.warning("Lütfen gerekli alanları doldurun.")

# =========================================================
# SEKME 5: 📚 SORU DEPOSU & İNTERAKTİF SUNUM / ÇÖZÜM MODU
# =========================================================
with tab5:
  st.subheader("📚 Soru Bankası & İnteraktif Soru Çözüm Modu")
  st.markdown(
      "Ders işlerken veya soru çözerken şıkları gizleyip açabileceğiniz sunum"
      " modu."
  )

  presentation_mode = st.toggle(
      "🖥️ İnteraktif Soru Çözüm / Sunum Modunu Aktif Et (Şıkları Gizle)"
  )

  fc1, fc2, fc3 = st.columns(3)
  with fc1:
    filter_grade = st.selectbox(
        "Kademe Filtresi",
        ["Tümü", "İlkokul", "Ortaokul", "LGS", "TYT", "AYT", "Lise"],
    )
  with fc2:
    filter_diff = st.selectbox(
        "Zorluk Filtresi", ["Tümü", "🟢 Kolay", "🟡 Orta", "🔴 Zor"]
    )
  with fc3:
    search_keyword = st.text_input("🔍 Kelime Ara", placeholder="Konu veya metin...")

  st.markdown("---")

  try:
    response = (
        supabase.table("flashcards").select("*").order("id", desc=True).execute()
    )
    questions = response.data

    if questions:
      filtered_list = []
      for q in questions:
        q_grade = str(q.get("grade") or "")
        q_diff = str(q.get("difficulty") or "")
        q_text = str(q.get("question_text") or "")
        q_topic = str(q.get("topic") or "")

        match_grade = (filter_grade == "Tümü") or (
            filter_grade.lower() in q_grade.lower()
        )
        match_diff = (filter_diff == "Tümü") or (filter_diff in q_diff)
        sk = search_keyword.lower()
        match_search = (
            (sk == "") or (sk in q_text.lower()) or (sk in q_topic.lower())
        )

        if match_grade and match_diff and match_search:
          filtered_list.append(q)

      st.write(
          f"Bulunan Soru: **{len(filtered_list)}** / Toplam:"
          f" **{len(questions)}**"
      )

      for item in filtered_list:
        c_ans = item.get("correct_answer", "-")
        diff_badge = item.get("difficulty", "🟢 Kolay")

        with st.expander(
            f"[{item.get('subject', 'Ders')}] {item.get('grade', 'Sınıf')} |"
            f" Konu: {item.get('topic', '-')} ({diff_badge})"
        ):
          st.markdown(f"**Zorluk:** {diff_badge}")
          st.markdown(f"**Soru Metni:**\n{item.get('question_text')}")

          if item.get("image_url"):
            st.image(
                item.get("image_url"),
                caption="Soru Görseli",
                use_container_width=False,
            )

          st.markdown("---")

          # Eğer İnteraktif Sunum Modu Açıksa şıkları gizle/aç düğmesi koy
          if presentation_mode:
            show_options = st.checkbox(
                f"👁️ Şıkları Göster (Soru ID: {item.get('id')})", value=False
            )
            if show_options:
              st.markdown("**Şıklar:**")
              st.markdown(
                  f"- **A)** {item.get('option_a')}"
                  + (" ✅" if c_ans == "A" else "")
              )
              st.markdown(
                  f"- **B)** {item.get('option_b')}"
                  + (" ✅" if c_ans == "B" else "")
              )
              st.markdown(
                  f"- **C)** {item.get('option_c')}"
                  + (" ✅" if c_ans == "C" else "")
              )
              st.markdown(
                  f"- **D)** {item.get('option_d')}"
                  + (" ✅" if c_ans == "D" else "")
              )
              if item.get("option_e"):
                st.markdown(
                    f"- **E)** {item.get('option_e')}"
                    + (" ✅" if c_ans == "E" else "")
                )
              st.markdown(f"\n🎯 **Doğru Cevap:** **{c_ans} Şıkkı**")
          else:
            st.markdown("**Şıklar:**")
            st.markdown(
                f"- **A)** {item.get('option_a')}"
                + (" ✅" if c_ans == "A" else "")
            )
            st.markdown(
                f"- **B)** {item.get('option_b')}"
                + (" ✅" if c_ans == "B" else "")
            )
            st.markdown(
                f"- **C)** {item.get('option_c')}"
                + (" ✅" if c_ans == "C" else "")
            )
            st.markdown(
                f"- **D)** {item.get('option_d')}"
                + (" ✅" if c_ans == "D" else "")
            )
            if item.get("option_e"):
                st.markdown(
                    f"- **E)** {item.get('option_e')}"
                    + (" ✅" if c_ans == "E" else "")
                )
            st.markdown(f"\n🎯 **Doğru Cevap:** **{c_ans} Şıkkı**")

          # Pedagojik Notlar
          if (
              item.get("term")
              or item.get("definition")
              or item.get("misconception")
          ):
            st.info(
                f"📌 **Kavram:** {item.get('term') or '-'} \n\n"
                f"📖 **Açıklama:** {item.get('definition') or '-'} \n\n"
                f"⚠️ **Kavram Yanılgısı:** {item.get('misconception') or '-'}"
            )
    else:
      st.info("Kayıtlı soru bulunamadı.")
  except Exception as e:
    st.error(f"Soru deposu yüklenirken hata oluştu: {e}")
