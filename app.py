import time
import streamlit as st
from deep_translator import GoogleTranslator, MyMemoryTranslator
from langdetect import detect, DetectorFactory

DetectorFactory.seed = 0  # makes langdetect's results consistent

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


# ---------- Robust translation function ----------
# Caching means the exact same text+language pair is never re-translated,
# which also cuts down on repeat calls that can trigger rate limits.
@st.cache_data(show_spinner=False)
def translate_text(text: str, source_code: str, target_code: str) -> str:
    # If "auto" was selected, detect the language locally first.
    # This avoids spending one of our limited Google requests just on detection.
    if source_code == "auto":
        try:
            source_code = detect(text)
        except Exception:
            source_code = "auto"

    last_error = None

    # 1) Try Google Translate, with a couple of quick retries
    for attempt in range(2):
        try:
            return GoogleTranslator(source=source_code, target=target_code).translate(text)
        except Exception as e:
            last_error = e
            time.sleep(1.5)  # brief pause before retrying

    # 2) If Google is still rate-limited/unavailable, fall back to MyMemory
    try:
        fallback_source = source_code if source_code != "auto" else "en"
        return MyMemoryTranslator(source=fallback_source, target=target_code).translate(text)
    except Exception as e:
        last_error = e

    # 3) If both services failed, raise a clear error
    raise RuntimeError(
        "Translation services are temporarily busy. Please try again in a few seconds."
    ) from last_error

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
                translated = translate_text(input_text, source_code, target_code)

            st.subheader("Translated Text")
            st.success(translated)

            # Optional: show a copy-friendly text box too
            st.text_area("Copy from here:", value=translated, height=150)

        except Exception as e:
            st.error(str(e))
            st.info("This is usually temporary — please click Translate again in a moment.")

# ---------- Footer ----------
st.divider()
st.caption("Built with Python & Streamlit • Powered by Google Translate")
