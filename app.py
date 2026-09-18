import streamlit as st
from deep_translator import GoogleTranslator

# ---------- Page Configuration ----------
st.set_page_config(
    page_title="Universal Text Translator",
    page_icon="🌐",
    layout="centered"
)

# ---------- Language List ----------
# deep-translator can fetch all languages Google Translate supports
@st.cache_data
def get_languages():
    langs = GoogleTranslator().get_supported_languages(as_dict=True)
    # langs = {'english': 'en', 'french': 'fr', ...}
    return langs

languages = get_languages()
language_names = sorted(languages.keys())

# ---------- Header ----------
st.title("🌐 Universal Text Translator")
st.write("Translate text between any two languages, instantly.")

st.divider()

# ---------- Layout: Two columns for language selection ----------
col1, col2 = st.columns(2)

with col1:
    source_lang = st.selectbox(
        "From",
        options=["auto (detect language)"] + language_names,
        index=0
    )

with col2:
    target_lang = st.selectbox(
        "To",
        options=language_names,
        index=language_names.index("english") if "english" in language_names else 0
    )

# ---------- Text Input ----------
input_text = st.text_area(
    "Enter text to translate",
    height=150,
    placeholder="Type or paste your text here..."
)

# ---------- Translate Button ----------
if st.button("Translate", type="primary", use_container_width=True):
    if not input_text.strip():
        st.warning("Please enter some text to translate.")
    else:
        try:
            source_code = "auto" if source_lang.startswith("auto") else languages[source_lang]
            target_code = languages[target_lang]

            with st.spinner("Translating..."):
                translated = GoogleTranslator(
                    source=source_code,
                    target=target_code
                ).translate(input_text)

            st.subheader("Translated Text")
            st.success(translated)

            # Optional: show a copy-friendly text box too
            st.text_area("Copy from here:", value=translated, height=150)

        except Exception as e:
            st.error(f"Something went wrong: {e}")

# ---------- Footer ----------
st.divider()
st.caption("Built with Python & Streamlit • Powered by Google Translate")
