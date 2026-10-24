import streamlit as st
import streamlit.components.v1 as components
from supabase import create_client

# ---------------------------------------------------------
# 1. SAYFA YAPILANDIRMASI & TEMA SEÇİMİ
# ---------------------------------------------------------
st.set_page_config(
    page_title="Şöhret Yelen Akademi - Yönetim & Eğitim LMS",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------
# 2. SUPABASE BAĞLANTISI (SECRETS YÖNETİMİ)
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
# 3. YAN MENÜ (SIDEBAR) & YÖNETİCİ BİLGİSİ
# ---------------------------------------------------------
with st.sidebar:
  st.title("🎓 Şöhret Yelen Akademi")
  st.caption("Yapılandırmacı & Mantık Odaklı LMS")
  st.markdown("---")
  st.markdown("**👤 Yetkili Eğitmen:** Şöhret Yelen")
  st.markdown("**🛡️ Rol:** Kurucu / Master Yönetici")
  st.markdown("---")
  st.markdown("### 📌 Sistem İstatistikleri")

  # Veritabanı canlı soru sayısını çekme
  try:
    res = supabase.table("flashcards").select("id", count="exact").execute()
    total_q = res.count if res.count is not None else 0
    st.metric(label="Toplam Kayıtlı Soru", value=total_q)
  except Exception:
    st.metric(label="Toplam Kayıtlı Soru", value="-")

  st.info(
      "💡 *İlkokul ve ortaokul için 4 şık (A-D), Lise kademeleri için 5 şık"
      " (A-E) otomatik uygulanır.*"
  )

# ---------------------------------------------------------
# 4. ANA BAŞLIK
# ---------------------------------------------------------
st.title("📚 Şöhret Yelen Akademi | Öğretmen & İçerik Yönetim Paneli")
st.markdown(
    "Fizik, Matematik ve Fen Bilgisi pedagojik içerik, soru bankası ve dinamik"
    " ödevlendirme sistemi."
)
st.markdown("---")

# ---------------------------------------------------------
# 5. MODÜLER SEKME (TAB) YAPISI
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs([
    "🎯 Kritik Kazanımlar & Ödevlendirme",
    "🔗 Kavram Haritası, Konu Anlatımı & Medya",
    "➕ Yeni Soru & Flashcard Ekle",
    "📚 Soru Deposu & Arşiv",
])

# =========================================================
# SEKME 1: KRİTİK KAZANIMLAR VE ÖDEVLENDİRME
# =========================================================
with tab1:
  st.subheader("🎯 Kritik Kazanımlar ve Akıllı Ödevlendirme")
  st.markdown(
      "Öğrencilerin kavram yanılgılarını takip edin ve kademelere uygun"
      " ödevler planlayın."
  )

  col_k1, col_k2 = st.columns(2)
  with col_k1:
    st.selectbox(
        "Kazanım Analizi İçin Sınıf Seçin",
        [
            "İlkokul Matematik (1-4. Sınıf)",
            "Ortaokul Matematik & Fen (5-8. Sınıf)",
            "LGS Hazırlık (8. Sınıf Özel)",
            "Lise Matematik (9-12. Sınıf)",
            "Lise Fizik (9-12. Sınıf)",
        ],
    )
  with col_k2:
    st.selectbox(
        "Zorluk Kademesi Hedefi", ["Tüm Seviyeler", "🟢 Kolay", "🟡 Orta", "🔴 Zor"]
    )

  st.info(
      "📊 Henüz öğrenci analiz verisi girilmedi. Sorular eklendikçe dinamik"
      " ödev havuzu burada listelenecektir."
  )

# =========================================================
# SEKME 2: KAVRAM HARİTASI, KONU ANLATIMI VE MEDYA
# =========================================================
with tab2:
  st.subheader("🔗 Kavram Haritası, Etkileşimli Konu Anlatımı & Medya")
  st.markdown(
      "Formül türetme adımları, görsel diyagramlar, animasyonlar ve GeoGebra"
      " simülasyonları."
  )

  sub_tab_a, sub_tab_b, sub_tab_c = st.tabs(
      ["📖 Konu Özeti & Formül Türetimi", "🖼️ Visual & GIF / MP4 Medya", "📐 GeoGebra / PhET Simülasyon"]
  )

  with sub_tab_a:
    st.markdown("### 💡 Formül Nereden Geldi? (Derivasyon Odaklı Anlatım)")
    st.write(
        "Örnek Konu: **Newton'un 2. Hareket Yasası ($F = m \\cdot a$)**"
    )
    st.warning(
        "**Kavram Yanılgısı:** Kuvvet, bir cismin sahip olduğu bir özellik"
        " değildir; etkileşimin sonucudur!"
    )
    st.success(
        "**Derivasyon:** Bir cisme uygulanan net kuvvet arttıkça ivme artar ($F"
        " \\propto a$). Kütle arttıkça ivmelenmek zorlaşır ($a \\propto 1/m$)."
        " Buradan $F = m \\cdot a$ bağıntısına ulaşılır."
    )

  with sub_tab_b:
    st.markdown("### 🎬 Visual & Animasyon Gömme Alanı")
    gorsel_url = st.text_input(
        "Görsel veya GIF URL'si Gömdürün:",
        placeholder="https://example.com/animasyon.gif",
    )
    if gorsel_url:
      try:
        st.image(
            gorsel_url,
            caption="Konu Anlatım Görseli / Animasyonu",
            use_container_width=True,
        )
      except Exception as e:
        st.error(f"Görsel yüklenemedi: {e}")
    else:
      st.info(
          "Yukarıdaki alana resim (PNG/JPG) veya animasyon (GIF) linki girerek"
          " anlatımlara görsel ekleyebilirsiniz."
      )

  with sub_tab_c:
    st.markdown("### 📐 Canlı Etkileşimli GeoGebra / PhET Simülasyonu")
    sim_embed_code = st.text_input(
        "GeoGebra / PhET Embed (iframe) Linki:",
        placeholder="https://www.geogebra.org/material/iframe/id/...",
    )
    if sim_embed_code:
      components.iframe(sim_embed_code, height=500, scrolling=True)
    else:
      st.info(
          "GeoGebra veya PhET simülasyon iframe bağlantısını buraya yapıştırarak"
          " öğrencinin deneyimlemesini sağlayabilirsiniz."
      )

# =========================================================
# SEKME 3: YENİ SORU / FLASHCARD EKLE
# =========================================================
with tab3:
  st.subheader("➕ Yeni Soru & Flashcard Ekleme Paneli")
  st.markdown(
      "Seçilen sınıf seviyesine göre **şık sayısı (4 veya 5)** ve **zorluk"
      " derecesi** otomatik ayarlanır."
  )

  with st.form("add_question_form", clear_on_submit=True):
    c1, c2, c3 = st.columns([2, 2, 1])

    with c1:
      subject = st.selectbox(
          "Ders Seçin", ["Fizik", "Matematik", "Fen Bilgisi"]
      )
      grade = st.selectbox(
          "Sınıf Düzeyi",
          [
              "İlkokul / 1-4. Sınıf",
              "Ortaokul / 5. Sınıf",
              "Ortaokul / 6. Sınıf",
              "Ortaokul / 7. Sınıf",
              "Ortaokul / 8. Sınıf (LGS Hazırlık)",
              "Lise / 9. Sınıf",
              "Lise / 10. Sınıf",
              "Lise / 11. Sınıf",
              "Lise / 12. Sınıf (YKS)",
          ],
      )

    with c2:
      topic = st.text_input(
          "Konu / Alt Kazanım", placeholder="Örn: Newton Yasaları / Kesirler"
      )
      question_type = st.selectbox(
          "Soru Tipi",
          [
              "Kazanım Kavrama",
              "Yeni Nesil / Beceri Temelli",
              "LGS Çıkmış / Örnek Soru",
              "ÖSYM / YKS Formatı",
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
        "Soru Görseli URL (Varsa)",
        placeholder="https://... (Görselli soru ise resim bağlantısı)",
    )

    # DİNAMİK ŞIK SAYISI MANTIĞI: Lise seçildiyse 5 şık, diğerlerinde 4 şık
    is_lise = "Lise" in grade
    option_count = 5 if is_lise else 4
    option_labels = ["A", "B", "C", "D", "E"][:option_count]

    st.markdown(
        f"**Seçenekler ({option_count} Şık - {'Lise Seviyesi' if is_lise else 'İlkokul/Ortaokul Seviyesi'}):**"
    )

    sc1, sc2 = st.columns(2)
    with sc1:
      opt_a = st.text_input("A Şıkkı Metni")
      opt_b = st.text_input("B Şıkkı Metni")
      opt_c = st.text_input("C Şıkkı Metni")
    with sc2:
      opt_d = st.text_input("D Şıkkı Metni")
      opt_e = st.text_input("E Şıkkı Metni") if is_lise else ""

    correct_answer = st.selectbox(
        "🎯 Doğru Cevap Hangi Şık?",
        option_labels,
        format_func=lambda x: f"{x} Şıkkı",
    )

    st.markdown("---")
    st.markdown("**Pedagojik Notlar & Tanımlar (İsteğe Bağlı):**")
    tc1, tc2 = st.columns(2)
    with tc1:
      term = st.text_input(
          "Önemli Terim / Kavram", placeholder="Örn: İvme / Sürtünme Kuvveti"
      )
      misconception = st.text_input(
          "Olası Kavram Yanılgısı",
          placeholder="Örn: Hız ile ivmeyi karıştırma",
      )
    with tc2:
      definition = st.text_area(
          "Terim Tanımı / Açıklaması",
          placeholder="Kavramın mantıksal açıklaması...",
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
              "option_e": opt_e if is_lise else None,
              "correct_answer": correct_answer,
              "term": term if term else None,
              "definition": definition if definition else None,
              "misconception": misconception if misconception else None,
          }
          supabase.table("flashcards").insert(payload).execute()
          st.success(
              "Soru ve seçenekler başarıyla Supabase veritabanına kaydedildi!"
              " 🎉"
          )
        except Exception as err:
          st.error(f"Veritabanına kaydederken hata oluştu: {err}")
      else:
        st.warning(
            "Lütfen Soru Metni, Konu ve en azından A ve B şıklarını doldurun."
        )

# =========================================================
# SEKME 4: SORU DEPOSU VE ARŞİV
# =========================================================
with tab4:
  st.subheader("📚 Soru Bankası & Dijital Arşiv")
  st.markdown(
      "Gelişmiş filtreleme alanıyla kayıtlı tüm soruları inceleyin ve arayın."
  )

  # Filtreleme Arayüzü
  fc1, fc2, fc3 = st.columns(3)
  with fc1:
    filter_grade = st.selectbox(
        "Sınıf Seviyesine Göre Filtrele",
        ["Tümü", "İlkokul", "Ortaokul", "LGS", "Lise"],
    )
  with fc2:
    filter_diff = st.selectbox(
        "Zorluğa Göre Filtrele", ["Tümü", "🟢 Kolay", "🟡 Orta", "🔴 Zor"]
    )
  with fc3:
    search_keyword = st.text_input(
        "🔍 Kelime ile Arama Yap", placeholder="Metin veya konu yazın..."
    )

  st.markdown("---")

  try:
    response = (
        supabase.table("flashcards").select("*").order("id", desc=True).execute()
    )
    questions = response.data

    if questions:
      # Filtreleme mantığı
      filtered_list = []
      for q in questions:
        q_grade = str(q.get("grade") or "")
        q_diff = str(q.get("difficulty") or "")
        q_text = str(q.get("question_text") or "")
        q_topic = str(q.get("topic") or "")

        # Kademe filtresi
        match_grade = (filter_grade == "Tümü") or (
            filter_grade.lower() in q_grade.lower()
        )
        # Zorluk filtresi
        match_diff = (filter_diff == "Tümü") or (filter_diff in q_diff)
        # Kelime araması
        sk = search_keyword.lower()
        match_search = (
            (sk == "") or (sk in q_text.lower()) or (sk in q_topic.lower())
        )

        if match_grade and match_diff and match_search:
          filtered_list.append(q)

      st.write(
          f"Bulunan Soru Sayısı: **{len(filtered_list)}** / Total:"
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

          # Varsa Soru Görseli
          img_link = item.get("image_url")
          if img_link:
            st.image(
                img_link, caption="Soru Görseli", use_container_width=False
            )

          st.markdown("---")
          st.markdown("**Şıklar:**")

          st.markdown(
              f"- **A)** {item.get('option_a', '-')}"
              + (" ✅" if c_ans == "A" else "")
          )
          st.markdown(
              f"- **B)** {item.get('option_b', '-')}"
              + (" ✅" if c_ans == "B" else "")
          )
          st.markdown(
              f"- **C)** {item.get('option_c', '-')}"
              + (" ✅" if c_ans == "C" else "")
          )
          st.markdown(
              f"- **D)** {item.get('option_d', '-')}"
              + (" ✅" if c_ans == "D" else "")
          )

          opt_e_val = item.get("option_e")
          if opt_e_val:
            st.markdown(
                f"- **E)** {opt_e_val}" + (" ✅" if c_ans == "E" else "")
            )

          st.markdown(f"\n🎯 **Doğru Cevap:** **{c_ans} Şıkkı**")

          # Pedagojik Detaylar
          term_val = item.get("term")
          def_val = item.get("definition")
          misc_val = item.get("misconception")

          if term_val or def_val or misc_val:
            st.info(
                f"📌 **Kavram:** {term_val or '-'} \n\n"
                f"📖 **Açıklama:** {def_val or '-'} \n\n"
                f"⚠️ **Kavram Yanılgısı Notu:** {misc_val or '-'}"
            )
    else:
      st.info(
          "Henüz veritabanına kayıtlı bir soru bulunmamaktadır. 'Yeni Soru"
          " Ekle' sekmesinden ekleyebilirsiniz."
      )

  except Exception as e:
    st.error(f"Soru deposu yüklenirken bir hata oluştu: {e}")
