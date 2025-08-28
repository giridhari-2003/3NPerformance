import streamlit as st
import tempfile
import os
from Quaity_evaluater import summarize_quality_report, analyze_document_quality_file

st.set_page_config(
    page_title="Document Quality Validator",
    page_icon="📄",
    layout="centered",
)

st.title("📑 Document Quality Validator")
st.markdown(
    """
    Upload your document (PDF, JPG, PNG, etc.) and check if it meets the quality standards.
    """
)

uploaded_file = st.file_uploader(
    "Upload a document",
    type=["pdf", "png", "jpg", "jpeg", "webp", "tiff", "bmp"],
    help="Supported formats: PDF, JPG, JPEG, PNG, TIFF, WebP"
)


if uploaded_file is not None:
    st.info("Processing document...")

    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(uploaded_file.name)[-1]) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name
    detailed_report = analyze_document_quality_file(str(temp_path))
    print(detailed_report)
    summary = summarize_quality_report(detailed_report)
    
    result = summary["quality_checker"]
    reason = summary["reason"]
    
    os.remove(temp_path)

    st.subheader("📊 Analysis Result")
    if result == "pass":
        st.success("✅ Document Passed Quality Check")

    elif result == "fail":
        st.error("❌ Document Failed Quality Check")
        st.warning(f"Reason: {reason if reason else 'Unknown issue'}")

    # Preview if Image
    if uploaded_file.type in ["image/png", "image/jpeg", "image/webp", "image/tiff", "image/bmp"]:
        st.subheader("🖼️ Document Preview")
        st.image(uploaded_file, use_container_width=True)

