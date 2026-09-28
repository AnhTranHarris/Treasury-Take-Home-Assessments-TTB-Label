from __future__ import annotations

import hashlib

import streamlit as st

from src.extraction.intake import FieldDraft
from src.ocr.factory import build_default_ocr_provider, choose_ocr_backend
from src.ocr.interface import OCRProvider
from src.orchestration.intake import analyze_label_intake
from src.orchestration.verifier import VerificationExecutionError, verify_label
from src.presentation import overall_message, result_rows
from src.validation.label_screening import LabelScreeningInput, screen_label
from src.validation.models import ApplicationReference, Status


@st.cache_resource(show_spinner=False)
def get_ocr_provider() -> OCRProvider:
    return build_default_ocr_provider()


def _show_status(result) -> None:
    status = result.overall_status
    message = overall_message(status)
    if status == Status.PASS:
        st.success(message)
    elif status == Status.FAIL:
        st.error(message)
    else:
        st.warning(message)


def _review_marker(label: str, draft: FieldDraft) -> None:
    if draft.review_required:
        st.warning(f"⚠ Review {label}: {draft.reason}")


def _seed_intake_state(image_digest: str, draft) -> None:
    if st.session_state.get("intake_image_digest") == image_digest:
        return

    st.session_state["intake_image_digest"] = image_digest
    st.session_state["intake_brand"] = draft.brand.value or ""
    st.session_state["intake_class_type"] = draft.class_type.value or ""
    st.session_state["intake_alcohol_content"] = draft.alcohol_content.value or ""
    st.session_state["intake_net_contents"] = draft.net_contents.value or ""
    st.session_state["intake_name_address"] = draft.name_address.value or ""
    st.session_state["intake_imported"] = draft.imported.value == "Yes"
    st.session_state["intake_country_origin"] = draft.country_origin.value or ""
    st.session_state["intake_warning"] = draft.government_warning.value or ""
    st.session_state["intake_age"] = draft.age_statement.value or ""
    st.session_state["intake_color"] = draft.color_disclosure.value or ""
    st.session_state["intake_commodity"] = draft.commodity_statement.value or ""


def _render_quick_review() -> None:
    st.markdown("### 1. Upload the alcohol label")
    st.caption(
        "The prototype reads the label, auto-fills TTB-oriented fields, and flags uncertain extraction for human review."
    )

    uploaded = st.file_uploader(
        "Upload a JPG or PNG label image",
        type=["jpg", "jpeg", "png"],
        key="quick_label_upload",
    )
    camera = st.camera_input("Or take a photo", key="quick_label_camera")
    selected_image = uploaded or camera

    if selected_image is None:
        st.info("Upload or photograph one distilled-spirits label to begin.")
        return

    image_bytes = selected_image.getvalue()
    image_digest = hashlib.sha256(image_bytes).hexdigest()

    try:
        with st.spinner("Reading the label and extracting TTB fields..."):
            intake_run = analyze_label_intake(image_bytes, get_ocr_provider())
    except (ImportError, OSError):
        st.error("The local OCR runtime could not load a required system library.")
        st.info("No label fields or compliance result were generated.")
        return
    except VerificationExecutionError as exc:
        st.error(str(exc))
        st.info("Try a clearer JPG/PNG image. No TTB intake fields were generated from the failed run.")
        return

    _seed_intake_state(image_digest, intake_run.draft)

    st.markdown("### 2. Review extracted label information")
    left, right = st.columns([1.0, 1.15], gap="large")

    with left:
        st.image(image_bytes, caption="Uploaded label — visually confirm any yellow review fields.", use_container_width=True)
        st.metric("OCR extraction time", f"{intake_run.elapsed_seconds:.2f} seconds")
        st.caption(f"Local OCR backend: {choose_ocr_backend().upper()}")

    with right:
        draft = intake_run.draft

        _review_marker("Brand name", draft.brand)
        brand = st.text_input("Brand name", key="intake_brand")

        _review_marker("Class / type designation", draft.class_type)
        class_type = st.text_input("Class / type designation", key="intake_class_type")

        _review_marker("Alcohol content", draft.alcohol_content)
        alcohol_content = st.text_input("Alcohol content statement", key="intake_alcohol_content")

        _review_marker("Net contents", draft.net_contents)
        net_contents = st.text_input("Net contents", key="intake_net_contents")

        _review_marker("Name / address", draft.name_address)
        name_address = st.text_input("Bottler / producer / importer name and address", key="intake_name_address")

        _review_marker("Import status", draft.imported)
        imported = st.checkbox("Imported product", key="intake_imported")

        if imported:
            _review_marker("Country of origin", draft.country_origin)
        country_origin = st.text_input(
            "Country of origin",
            key="intake_country_origin",
            disabled=not imported,
        )

        _review_marker("Government warning", draft.government_warning)
        warning = st.text_area("Government warning text", key="intake_warning", height=180)

        with st.expander("Conditional TTB disclosures", expanded=False):
            st.caption(
                "These items depend on product composition, age, or class/type. A blank field does not by itself prove noncompliance."
            )

            _review_marker("Age statement", draft.age_statement)
            age_statement = st.text_input("Age statement (if applicable)", key="intake_age")

            _review_marker("Color ingredient disclosure", draft.color_disclosure)
            color_disclosure = st.text_input("Color ingredient disclosure (if applicable)", key="intake_color")

            _review_marker("Commodity statement", draft.commodity_statement)
            commodity_statement = st.text_input("Commodity statement (if applicable)", key="intake_commodity")

    core_review_fields = {
        "brand": draft.brand,
        "class_type": draft.class_type,
        "alcohol_content": draft.alcohol_content,
        "net_contents": draft.net_contents,
        "name_address": draft.name_address,
        "imported": draft.imported,
        "government_warning": draft.government_warning,
    }
    if imported:
        core_review_fields["country_origin"] = draft.country_origin

    highlighted_fields = tuple(
        key for key, field_draft in core_review_fields.items() if field_draft.review_required
    )

    st.caption(
        "Yellow review notices mean OCR/extraction confidence is insufficient for silent acceptance. "
        "Visually inspect the uploaded label and edit the field before running the TTB checks."
    )

    review_confirmed = True
    if highlighted_fields:
        review_confirmed = st.checkbox(
            "I visually reviewed the highlighted core fields against the uploaded label.",
            value=False,
            key="intake_review_confirmed",
        )
        if not review_confirmed:
            st.info(
                "You can run the checks now, but highlighted core fields will remain REVIEW until you confirm them."
            )

    if not st.button("Run TTB label checks", type="primary", key="quick_run_checks"):
        with st.expander("OCR evidence"):
            for line in intake_run.ocr_lines:
                location = f" | box={line.box}" if line.box else ""
                st.write(f"{line.score:.3f} | {line.text}{location}")
        return

    screening = screen_label(
        LabelScreeningInput(
            brand=brand,
            class_type=class_type,
            alcohol_content=alcohol_content,
            net_contents=net_contents,
            name_address=name_address,
            imported=imported,
            country_origin=country_origin if imported else "",
            government_warning=warning,
            age_statement=age_statement,
            color_disclosure=color_disclosure,
            commodity_statement=commodity_statement,
            unresolved_review_fields=() if review_confirmed else highlighted_fields,
        )
    )

    st.markdown("### 3. TTB label screening")
    _show_status(screening)
    st.dataframe(result_rows(screening), use_container_width=True, hide_index=True)

    with st.expander("Human review advisories", expanded=True):
        for advisory in screening.manual_review_advisories:
            st.write(f"• {advisory}")

    with st.expander("OCR evidence"):
        for line in intake_run.ocr_lines:
            location = f" | box={line.box}" if line.box else ""
            st.write(f"{line.score:.3f} | {line.text}{location}")


def _render_reference_compare() -> None:
    st.markdown("### Application / reference information")
    brand = st.text_input("Brand name", value="Stone's Throw", key="compare_brand")
    class_type = st.text_input("Class / type", value="Kentucky Straight Bourbon Whiskey", key="compare_class")
    abv = st.number_input(
        "Alcohol content (% Alc./Vol.)",
        min_value=0.0,
        max_value=100.0,
        value=45.0,
        step=0.1,
        key="compare_abv",
    )
    net_contents = st.text_input("Net contents", value="750 mL", key="compare_net")
    name_address = st.text_input(
        "Bottler / producer / importer name and address",
        value="Old Tom Distillery, Louisville, KY",
        key="compare_name",
    )
    imported = st.checkbox("Imported product", value=False, key="compare_imported")
    country_origin = st.text_input(
        "Country of origin",
        value="",
        disabled=not imported,
        key="compare_country",
    )

    st.markdown("### Label image")
    uploaded = st.file_uploader(
        "Upload a JPG or PNG label image",
        type=["jpg", "jpeg", "png"],
        key="compare_label_upload",
    )
    camera = st.camera_input("Or take a photo", key="compare_label_camera")
    selected_image = uploaded or camera

    if not st.button("Verify against reference", type="primary", key="compare_verify"):
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
    except (ImportError, OSError):
        st.error("The local OCR runtime could not load a required system library.")
        st.info(
            "This is a deployment-environment problem, not a label-compliance result. "
            "The application did not evaluate the uploaded label."
        )
        return
    except VerificationExecutionError as exc:
        st.error(str(exc))
        st.info("Try a clearer JPG/PNG image. The prototype did not generate a compliance result from the failed run.")
        return

    _show_status(run.result)
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


def main() -> None:
    st.set_page_config(page_title="TTB Label Verification Prototype", page_icon="🔎", layout="wide")
    st.title("AI-Powered Alcohol Label Verification")
    st.caption(
        "Distilled-spirits prototype. OCR extracts visible label evidence; deterministic Python rules evaluate "
        "the supported checks. This is not a complete legal-compliance determination."
    )

    mode = st.radio(
        "Choose workflow",
        ("Quick Label Review", "Compare to Reference"),
        horizontal=True,
        help=(
            "Quick Label Review auto-fills TTB-oriented fields from the label. "
            "Compare to Reference preserves the original application/reference comparison workflow."
        ),
    )

    if mode == "Quick Label Review":
        _render_quick_review()
    else:
        _render_reference_compare()


if __name__ == "__main__":
    main()
