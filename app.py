"""Notice-to-Action: a free, source-grounded public demo."""

from __future__ import annotations

import base64
import os
import shutil
from io import BytesIO
from pathlib import Path

import streamlit as st
from notice_parser import CATEGORIES, parse_notice


st.set_page_config(page_title="Notice to Action", page_icon="📌", layout="wide")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;600;700&family=Outfit:wght@400;500;600;700;800&display=swap');
:root {color-scheme:light}
.stApp {background:linear-gradient(155deg,#eaf3ff 0%,#f8fbff 39%,#eff7ff 100%);color:#102a45}
html,body,[class*="css"],.stApp {font-family:'DM Sans',system-ui,sans-serif}
.stApp, .stApp p, .stApp label, .stApp span, .stApp li,
[data-testid="stMarkdownContainer"], [data-testid="stWidgetLabel"],
[data-testid="stCaptionContainer"] {color:#102a45}
.block-container {max-width:1020px;padding-top:3.5rem;padding-bottom:2.5rem}
h1,h2,h3 {font-family:'Outfit',system-ui,sans-serif;color:#102a45;letter-spacing:-.03em}
.brand {display:inline-block!important;background:#d7eaff!important;border:2px solid #729fd5!important;border-radius:10px!important;padding:.48rem .9rem!important;color:#102a45!important;font-size:1.02rem!important;font-weight:800!important;letter-spacing:.10em!important;line-height:1.35!important}
.brand, .brand * {opacity:1!important;visibility:visible!important;color:#102a45!important}
.masthead {padding:1.25rem 0 .35rem}
.masthead h1 {font-size:clamp(2rem,4.2vw,3.3rem);line-height:1.12;margin:.55rem 0 .55rem;color:#102a45!important}
.masthead p {font-size:1rem;line-height:1.55;margin:.35rem 0;color:#244260!important}
.hero-illustration {display:block;max-width:240px;max-height:190px;width:100%;height:auto;margin:auto}
.hero {border:1px solid #c5dafa;border-radius:28px;background:linear-gradient(115deg,#fff 5%,#eaf3ff 100%);padding:2.5rem 2.7rem;box-shadow:0 15px 45px #1634520d}
.hero h1 {font-size:clamp(2.4rem,5vw,4rem);line-height:1.08;margin:.8rem 0 .85rem}
.hero p {max-width:590px;color:#567087;font-size:1.08rem;line-height:1.65;margin:0}
.accent {color:#134f9f}
.eyebrow {border-radius:99px;background:#dcecff;color:#134f9f;display:inline-block;padding:.4rem .8rem;font-size:.79rem;font-weight:800}
.stButton>button[kind="primary"] {border-radius:12px;background:#dcecff;border:2px solid #2464aa;color:#102a45;padding:.55rem 1.25rem;font-weight:800}
.stButton>button[kind="primary"]:hover {background:#bcd9ff;border-color:#134f9f;color:#102a45}
div[data-testid="stFileUploader"] {background:#fff;border:1px solid #aac9ed;border-radius:16px;padding:1rem}
div[data-testid="stFileUploaderDropzone"] {background:#f8fbff;border:1px dashed #7ea9d9}
div[data-testid="stFileUploader"] button {background:#eaf3ff;color:#102a45;border:1px solid #8fb7e5}
div[data-testid="stFileUploader"] button:hover {background:#dcecff;color:#102a45}
div[data-testid="stTextArea"] textarea {background:#fff!important;color:#102a45!important;border:2px solid #8fb7e5;border-radius:14px;caret-color:#134f9f}
div[data-testid="stTextArea"] textarea::placeholder {color:#385878!important;opacity:1}
div[data-testid="stTextArea"] textarea:focus {border-color:#134f9f;box-shadow:0 0 0 3px #dcecff}
div[data-testid="stTabs"] [data-baseweb="tab-list"] {gap:.6rem;border-bottom:1px solid #b7d0ef}
div[data-testid="stTabs"] button[data-baseweb="tab"] {background:#e5f0ff;border:1px solid #b7d0ef;border-radius:12px 12px 0 0;padding:.6rem 1rem}
div[data-testid="stTabs"] button[data-baseweb="tab"] p {color:#123e76!important;font-weight:750}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] {background:#fff;border-color:#2464aa;border-bottom-color:#fff}
div[data-testid="stTabs"] button[data-baseweb="tab"][aria-selected="true"] p {color:#102a45!important}
.result-card {background:#fff;border:1px solid #dfe9f0;padding:1.05rem 1.2rem;border-radius:16px;margin:.6rem 0;box-shadow:0 4px 18px #102c4a09}
.result-card strong {color:#173755}
.result-card small {color:#667e91}
.muted {color:#647b8e;font-size:.9rem}
@media(max-width:650px) {
  .block-container {padding:2rem .9rem 2.5rem}
  .masthead {padding:.4rem 0 0}
  .masthead h1 {font-size:2rem}
  .hero-illustration {max-width:160px;max-height:125px;margin:.3rem auto}
  div[data-testid="stTabs"] button[data-baseweb="tab"] {padding:.45rem .55rem}
}
</style>
""", unsafe_allow_html=True)


def configure_image_ocr(pytesseract, ocr_language: str = "English + Bengali") -> None:
    """Use a Windows installer location if Tesseract is absent from PATH."""
    if shutil.which("tesseract") is None and os.name == "nt":
        candidates = [
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Tesseract-OCR" / "tesseract.exe",
            Path(os.environ.get("LOCALAPPDATA", "")) / "Programs" / "Tesseract-OCR" / "tesseract.exe",
        ]
        for candidate in candidates:
            if candidate.is_file():
                pytesseract.pytesseract.tesseract_cmd = str(candidate)
                break
        else:
            raise ValueError(
                "Image OCR needs the separate Tesseract OCR Windows installer. "
                "Install it with the required language data, then restart the app; "
                "or paste the notice text instead."
            )
    try:
        languages = set(pytesseract.get_languages(config=""))
    except pytesseract.TesseractNotFoundError as exc:
        raise ValueError(
            "Tesseract OCR was not found. Install its Windows program and restart the app, "
            "or paste the notice text instead."
        ) from exc
    required = {"eng"} if ocr_language == "English" else {"eng", "ben"}
    missing = required - languages
    if missing:
        raise ValueError(
            "Tesseract OCR is installed, but language data is missing: "
            + ", ".join(sorted(missing))
            + ". Install the missing language data and restart the app."
        )


def read_file(raw: bytes, filename: str, ocr_language: str = "English + Bengali") -> tuple[str, str]:
    ext = Path(filename).suffix.lower()
    if ext == ".txt":
        return raw.decode("utf-8-sig", errors="replace"), "Text file"
    if ext == ".pdf":
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(raw))
        if reader.is_encrypted:
            raise ValueError("Password-protected PDFs are not supported")
        if len(reader.pages) > 15:
            raise ValueError("For this demo, PDF files must have at most 15 pages")
        text = "\n".join((page.extract_text() or "") for page in reader.pages)
        return text, "PDF text extraction (scanned pages may need OCR)"
    if ext in {".png", ".jpg", ".jpeg"}:
        import pytesseract
        from PIL import Image, ImageOps, UnidentifiedImageError

        configure_image_ocr(pytesseract, ocr_language)
        try:
            with Image.open(BytesIO(raw)) as image:
                if image.width * image.height > 20_000_000:
                    raise ValueError("Image exceeds the 20-megapixel limit")
                image = ImageOps.exif_transpose(image).convert("RGB")
                original_width, original_height = image.size
                if min(image.size) < 900:
                    scale = min(3, 3000 / max(image.size))
                    image = image.resize(
                        (round(image.width * scale), round(image.height * scale)),
                        Image.Resampling.LANCZOS,
                    )
                    image = ImageOps.autocontrast(ImageOps.grayscale(image))
                lang = "eng" if ocr_language == "English" else "eng+ben"
                # Never store the upload on disk; OCR runs in memory.
                return (
                    pytesseract.image_to_string(image, lang=lang, config="--psm 6"),
                    f"Image OCR · {original_width}×{original_height} pixels · {ocr_language} (verify every extracted line)",
                )
        except pytesseract.TesseractError as exc:
            raise ValueError("Image OCR failed. Check that English and Bengali language data are installed.") from exc
        except UnidentifiedImageError as exc:
            raise ValueError("The image could not be opened") from exc
    raise ValueError("Supported files: PDF, TXT, PNG, JPG")


hero = Path(__file__).resolve().parent / "assets" / "notice-illustration.svg"
left, right = st.columns([1.55, 0.45], gap="medium", vertical_alignment="center")
with left:
    st.markdown("""<div class="masthead">
    <div class="brand">NOTICE / TO / ACTION</div>
    <h1>Never lose the <span class="accent">important line.</span></h1>
    <p>For students &amp; applicants · Free demo</p>
    <p>Turn a university notice, scholarship update or job circular into a short, checkable list. Every result points back to the text it came from.</p>
    </div>""", unsafe_allow_html=True)
with right:
    data = base64.b64encode(hero.read_bytes()).decode("ascii")
    st.markdown(f'<img class="hero-illustration" alt="Illustration of a notice and a checklist" src="data:image/svg+xml;base64,{data}">', unsafe_allow_html=True)

st.divider()
st.subheader("Read a notice")
st.caption("Choose the notice type, then upload a public notice or paste its text. The results are evidence lines to check, not verified answers. Avoid private identifiers.")
category = st.selectbox("Notice type", CATEGORIES, help="Choose the type yourself; the app does not guess it from an image.")
ocr_language = st.selectbox("Image language", ["English", "English + Bengali"], help="Only used for image uploads; choose English for a notice whose main text is English.")
tab_file, tab_text = st.tabs(["Upload a notice", "Paste text"])
with tab_file:
    uploaded = st.file_uploader("PDF, TXT, PNG or JPG", type=["pdf", "txt", "png", "jpg", "jpeg"], max_upload_size=8)
with tab_text:
    typed = st.text_area("Notice text", height=210, placeholder="Example: Applications close on 15 October 2026. Please apply online and attach your CV and transcript.")

if st.button("Find key details", type="primary", use_container_width=False):
    try:
        if typed.strip() and uploaded is not None:
            st.info("Both inputs are present. This run uses the pasted text; clear it to use the uploaded file.")
        if typed.strip():
            source_text, source_method = typed.strip(), "Pasted text"
        elif uploaded is not None:
            data = uploaded.getvalue()
            if len(data) > 8 * 1024 * 1024:
                raise ValueError("File must be 8 MB or smaller")
            source_text, source_method = read_file(data, uploaded.name, ocr_language)
        else:
            raise ValueError("Paste notice text or upload a supported file")

        if not source_text.strip():
            raise ValueError("No readable text was found. For a scanned PDF, upload a clear page image instead.")
        found = parse_notice(source_text, category)
        st.session_state["result"] = (source_method, category, found, source_text)
    except (ValueError, OSError, ImportError, RuntimeError) as exc:
        st.session_state.pop("result", None)
        st.error(f"Could not read this notice: {exc}")
    except Exception:
        st.session_state.pop("result", None)
        st.error("This file could not be processed. Try pasting its text or uploading a clearer image.")

if "result" in st.session_state:
    method, category_used, result, original = st.session_state["result"]
    st.divider()
    st.subheader(f"Review the {category_used.lower()}")
    st.caption(f"Reading method: {method}. These are matched source lines, not a summary or an eligibility decision.")
    if method.startswith("Image OCR"):
        st.warning("Image OCR can misread words, numbers and layout. Open 'Text read' below and compare it with the original image before trusting a date or instruction.")
        import re
        size_match = re.search(r"(\d+)×(\d+) pixels", method)
        if size_match and min(map(int, size_match.groups())) < 900:
            st.error("This image is small for a dense notice. OCR may change words and dates. Use the original PDF or a clearer scan; treat all results from this image as unverified.")
    for note in result["notes"]:
        st.info(note)
    date_tab, detail_tab, original_tab = st.tabs(["📅 Dates by purpose", "📋 Notice details", "🔎 Text read"])
    with date_tab:
        for label, items in result["dates"].items():
            st.markdown(f"**{label}**")
            if not items:
                st.caption("Not clearly found in the supplied text.")
            for item in items:
                st.write(item.text)
                st.caption(f"Parsed date {item.normalized_date} · source line {item.line_number}: {item.source} · verify against the original")
    with detail_tab:
        for label, items in result["fields"].items():
            with st.expander(f"{label} · {len(items)} matching line(s)", expanded=bool(items)):
                if not items:
                    st.caption("Not clearly found in the supplied text.")
                for item in items:
                    st.write(item.text)
                    st.caption(f"Source line {item.line_number} · verify the whole notice and any conditions")
    with original_tab:
        st.caption("This is the text the app actually received. OCR and PDF extraction may miss or reorder text.")
        st.text(original[:12_000])
        if len(original) > 12_000:
            st.caption("Only the first 12,000 characters are displayed here.")

st.divider()
st.caption("Notice to Action · Evidence-first prototype · Check the issuing organization's original notice before applying.")
