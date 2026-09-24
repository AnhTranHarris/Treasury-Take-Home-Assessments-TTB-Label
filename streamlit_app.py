from __future__ import annotations

import streamlit as st

from src.ocr.factory import build_default_ocr_provider, choose_ocr_backend
from src.ocr.interface import OCRProvider
from src.orchestration.verifier import VerificationExecutionError, verify_label
from src.presentation import overall_message, result_rows
from src.validation.models import ApplicationReference, Status


@st.cache_resource(show_spinner=False)
def get_ocr_provider() -> OCRProvider:
    return build_default_ocr_provider()


def main() -> None:
    st.set_page_config(page_title="TTB Label Verification Prototype", page_icon="🔎", layout="wide")
    st.title("AI-Powered Alcohol Label Verification")
    st.caption(
        "Distilled-spirits prototype. AI/OCR extracts evidence; deterministic Python rules evaluate "
        "the supported automated checks. This is not a complete legal-compliance determination."
    )
    st.caption(f"Local OCR backend: {choose_ocr_backend().upper()}")

    st.markdown("### Application / reference information")
    brand = st.text_input("Brand name", value="Stone's Throw")
    class_type = st.text_input("Class / type", value="Kentucky Straight Bourbon Whiskey")
    abv = st.number_input("Alcohol content (% Alc./Vol.)", min_value=0.0, max_value=100.0, value=45.0, step=0.1)
    net_contents = st.text_input("Net contents", value="750 mL")
    name_address = st.text_input("Bottler / producer / importer name and address", value="Old Tom Distillery, Louisville, KY")
    imported = st.checkbox("Imported product", value=False)
    country_origin = st.text_input("Country of origin", value="", disabled=not imported)

    st.markdown("### Label image")
    uploaded = st.file_uploader("Upload a JPG or PNG label image", type=["jpg", "jpeg", "png"])
    camera = st.camera_input("Or take a photo")
    selected_image = uploaded or camera

    if not st.button("Verify label", type="primary"):
        return

    missing = []
    for label, value in (
        ("Brand name", brand),
        ("Class / type", class_type),
        ("Net contents", net_contents),
        ("Name and address", name_address),
    ):
        if not value.strip():
            missing.append(label)
    if imported and not country_origin.strip():
        missing.append("Country of origin")
    if selected_image is None:
        missing.append("Label image")

    if missing:
        st.error("Please provide: " + ", ".join(missing))
        return

    reference = ApplicationReference(
        brand=brand.strip(),
        class_type=class_type.strip(),
        abv=float(abv),
        net_contents=net_contents.strip(),
        name_address=name_address.strip(),
        imported=imported,
        country_origin=country_origin.strip() if imported else None,
    )

    try:
        with st.spinner("Reading label and checking supported requirements..."):
            run = verify_label(reference, selected_image.getvalue(), get_ocr_provider())
    except VerificationExecutionError as exc:
        st.error(str(exc))
        st.info("Try a clearer JPG/PNG image. The prototype did not generate a compliance result from the failed run.")
        return

    status = run.result.overall_status
    message = overall_message(status)
    if status == Status.PASS:
        st.success(message)
    elif status == Status.FAIL:
        st.error(message)
    else:
        st.warning(message)

    st.metric("Processing time", f"{run.elapsed_seconds:.2f} seconds")
    st.dataframe(result_rows(run.result), use_container_width=True, hide_index=True)

    with st.expander("Human review advisories", expanded=True):
        for advisory in run.result.manual_review_advisories:
            st.write(f"• {advisory}")

    with st.expander("OCR evidence"):
        if not run.ocr_lines:
            st.write("No text lines were returned by local OCR.")
        for line in run.ocr_lines:
            location = f" | box={line.box}" if line.box else ""
            st.write(f"{line.score:.3f} | {line.text}{location}")


if __name__ == "__main__":
    main()
