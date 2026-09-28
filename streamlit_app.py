from __future__ import annotations

import hashlib

import streamlit as st

from src.extraction.intake import FieldDraft
from src.ocr.factory import build_default_ocr_provider, choose_ocr_backend
from src.ocr.interface import OCRProvider
from src.orchestration.intake import analyze_label_intake
from src.orchestration.verifier import VerificationExecutionError, verify_label
from src.presentation import overall_message, result_rows
from src.sample_labels import NO_SAMPLE, SAMPLE_LABELS, select_label_image
from src.validation.label_screening import LabelScreeningInput, screen_label
from src.validation.models import ApplicationReference, Status


@st.cache_resource(show_spinner=False)
def get_ocr_provider() -> OCRProvider:
    return build_default_ocr_provider()


def _apply_federal_theme() -> None:
    st.markdown(
        """
        <style>
        :root {
            --ttb-navy: #16365C;
            --ttb-blue: #005EA8;
            --ttb-green: #2E8540;
            --ttb-gold: #8A6500;
            --ttb-light-blue: #E7F3F8;
            --ttb-light-gray: #F4F5F6;
            --ttb-border: #AEB0B5;
            --ttb-text: #1B1B1B;
            --ttb-muted: #5C5C5C;
        }

        html, body, .stApp, [data-testid="stAppViewContainer"], section[data-testid="stMain"] {
            background: #FFFFFF !important;
            color: var(--ttb-text) !important;
        }

        .stApp {
            font-family: "Source Sans 3", "Source Sans Pro", Arial, Helvetica, sans-serif;
        }

        [data-testid="stHeader"] {
            background: rgba(255, 255, 255, 0.96) !important;
        }

        [data-testid="stWidgetLabel"],
        [data-testid="stMarkdownContainer"],
        [data-testid="stText"],
        div[role="radiogroup"] label,
        .stCheckbox label {
            color: var(--ttb-text) !important;
        }

        .block-container {
            max-width: 1200px;
            padding-top: 1.25rem;
            padding-left: 48px;
            padding-right: 48px;
            padding-bottom: 2rem;
        }

        h1, h2, h3, h4 {
            font-family: "Source Sans 3", "Source Sans Pro", Arial, Helvetica, sans-serif !important;
            color: var(--ttb-navy) !important;
            font-weight: 700 !important;
            letter-spacing: 0 !important;
        }

        h1 {
            font-size: 28px !important;
            line-height: 1.2 !important;
            margin-bottom: 0.35rem !important;
        }

        h2 {
            font-size: 22px !important;
            line-height: 1.25 !important;
        }

        h3 {
            font-size: 19px !important;
            line-height: 1.3 !important;
            border-bottom: 2px solid var(--ttb-blue);
            padding-bottom: 0.35rem;
            margin-top: 1.5rem !important;
        }

        p, label, .stCaption, [data-testid="stMarkdownContainer"] {
            font-family: "Source Sans 3", "Source Sans Pro", Arial, Helvetica, sans-serif !important;
        }

        p, label, [data-testid="stMarkdownContainer"] p {
            font-size: 14px !important;
            line-height: 1.45 !important;
        }

        .stCaption, [data-testid="stCaptionContainer"] {
            font-size: 13px !important;
            color: var(--ttb-muted) !important;
        }

        a {
            color: var(--ttb-blue) !important;
        }

        div[data-testid="stFileUploaderDropzone"] {
            background: var(--ttb-light-gray) !important;
            border: 1px solid var(--ttb-border) !important;
            border-radius: 2px !important;
            color: var(--ttb-gold) !important;
        }

        div[data-testid="stFileUploaderDropzone"] *,
        div[data-testid="stFileUploaderDropzone"] button,
        div[data-testid="stFileUploaderDropzone"] small,
        div[data-testid="stFileUploaderDropzone"] span,
        div[data-testid="stFileUploaderDropzone"] p {
            color: var(--ttb-gold) !important;
        }

        div[data-testid="stFileUploaderDropzone"] svg {
            color: var(--ttb-gold) !important;
            fill: currentColor !important;
        }

        .stButton > button:disabled,
        .stButton > button:disabled *,
        button[disabled],
        button[disabled] * {
            color: var(--ttb-gold) !important;
            -webkit-text-fill-color: var(--ttb-gold) !important;
        }

        input:disabled,
        textarea:disabled,
        [aria-disabled="true"] {
            color: var(--ttb-gold) !important;
            -webkit-text-fill-color: var(--ttb-gold) !important;
        }

        [data-baseweb="input"] input,
        [data-baseweb="textarea"] textarea {
            color: var(--ttb-text) !important;
        }

        .stButton > button,
        div[data-testid="stPopover"] > button {
            border-radius: 2px !important;
            font-family: "Source Sans 3", "Source Sans Pro", Arial, Helvetica, sans-serif !important;
            font-weight: 600 !important;
        }

        .stButton > button[kind="primary"] {
            background: var(--ttb-blue) !important;
            border-color: var(--ttb-blue) !important;
        }

        .stButton > button[kind="primary"]:hover {
            background: var(--ttb-navy) !important;
            border-color: var(--ttb-navy) !important;
        }

        div[data-testid="stAlert"] {
            border-radius: 2px !important;
        }

        [data-testid="stDataFrame"] {
            border: 1px solid var(--ttb-border);
            border-radius: 2px;
        }

        .federal-topbar {
            background: var(--ttb-navy);
            color: white;
            padding: 10px 16px;
            border-bottom: 4px solid var(--ttb-green);
            margin: -0.25rem 0 1rem 0;
        }

        .federal-topbar .eyebrow {
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.035em;
            text-transform: uppercase;
            opacity: 0.95;
        }

        .federal-topbar .agency {
            font-size: 16px;
            font-weight: 700;
            margin-top: 2px;
        }

        .prototype-banner {
            background: var(--ttb-light-blue);
            border-left: 5px solid var(--ttb-blue);
            color: var(--ttb-text);
            padding: 10px 14px;
            margin-bottom: 1rem;
            font-size: 13px;
            line-height: 1.4;
        }

        .project-byline {
            margin-top: 0.15rem;
            margin-bottom: 0.65rem;
            color: var(--ttb-muted);
            font-size: 13px;
        }

        .section-kicker {
            color: var(--ttb-green);
            font-size: 12px;
            font-weight: 700;
            letter-spacing: 0.04em;
            text-transform: uppercase;
            margin-bottom: 0.15rem;
        }

        @media (max-width: 800px) {
            .block-container {
                padding-left: 20px;
                padding-right: 20px;
            }
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def _render_federal_header() -> None:
    st.markdown(
        """
        <div class="federal-topbar">
            <div class="eyebrow">U.S. Department of the Treasury · TTB-inspired submission layout</div>
            <div class="agency">Alcohol Label Verification Prototype</div>
        </div>
        <div class="prototype-banner">
            <strong>Unofficial take-home prototype.</strong>
            This project is not an official TTB system and does not represent a complete legal-compliance determination.
        </div>
        """,
        unsafe_allow_html=True,
    )


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


def _label_image_input(key_prefix: str):
    camera_key = f"{key_prefix}_camera_disabled"

    st.markdown(
        f"""
        <style>
        .st-key-{camera_key} button {{
            width: 100% !important;
            min-height: 68px !important;
            height: 68px !important;
            background: var(--st-secondary-background-color) !important;
            color: var(--ttb-gold) !important;
            border: 1px solid var(--st-border-color) !important;
            border-radius: var(--st-base-radius) !important;
            font-weight: 600 !important;
            opacity: 0.72 !important;
            cursor: not-allowed !important;
            justify-content: center !important;
        }}

        [data-testid="stFileUploaderDropzone"] {{
            min-height: 68px !important;
            background: var(--st-secondary-background-color) !important;
            border-color: var(--st-border-color) !important;
            border-radius: var(--st-base-radius) !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**Choose a built-in sample label or upload your own JPG/PNG image**")
    sample_col, upload_col, photo_col = st.columns([1.6, 3.2, 1.2], gap="small")

    with sample_col:
        sample_name = st.selectbox(
            "Built-in sample labels",
            options=[NO_SAMPLE, *SAMPLE_LABELS.keys()],
            key=f"{key_prefix}_sample",
            label_visibility="collapsed",
            help="Seven AI-generated development and stress-test labels are included in this repository.",
        )

    with upload_col:
        uploaded = st.file_uploader(
            "Upload a JPG or PNG label image",
            type=["jpg", "jpeg", "png"],
            key=f"{key_prefix}_upload",
            label_visibility="collapsed",
        )

    with photo_col:
        st.button(
            "Take a photo",
            icon=":material/photo_camera:",
            disabled=True,
            width="stretch",
            key=camera_key,
            help="Live camera capture is disabled in this prototype pending broader mobile/browser/camera-device testing.",
        )

    st.caption(
        "Samples were AI-generated with ChatGPT for development/testing and are not certified TTB labels. "
        "They were not used to train a custom model. You can upload your own label instead."
    )
    if uploaded is not None and sample_name != NO_SAMPLE:
        st.info("Your uploaded file is being used instead of the selected built-in sample.")

    return select_label_image(sample_name, uploaded)


def _seed_intake_state(image_digest: str, draft) -> None:
    if st.session_state.get("intake_image_digest") == image_digest:
        return

    st.session_state["intake_image_digest"] = image_digest
    st.session_state["intake_review_confirmed"] = False
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
    st.markdown("### Step 1 — Upload the alcohol label")
    st.caption(
        "The prototype reads the label, auto-fills TTB-oriented fields, and flags uncertain extraction for human review."
    )

    selected_image = _label_image_input("quick_label")

    if selected_image is None:
        st.info("Select a built-in sample or upload your own distilled-spirits label to begin. Live camera capture is disabled.")
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

    st.markdown("### Step 2 — Review extracted label information")
    left, right = st.columns([1.0, 1.15], gap="large")

    with left:
        st.image(
            image_bytes,
            caption=f"{'Built-in sample' if selected_image.source == 'sample' else 'Uploaded file'}: "
                    f"{selected_image.name} — visually confirm any yellow review fields.",
            use_container_width=True,
        )
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

    st.markdown("### Step 3 — Review supported screening results")
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
    selected_image = _label_image_input("compare_label")

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
    _apply_federal_theme()
    _render_federal_header()

    st.markdown('<div class="section-kicker">Take-home assessment prototype</div>', unsafe_allow_html=True)
    st.title("AI-Powered Alcohol Label Verification")
    st.markdown(
        '<div class="project-byline"><strong>Made by Anh Tran (Harris)</strong> using vibe coding with ChatGPT · '
        '<a href="https://github.com/AnhTranHarris/Treasury-Take-Home-Assessments-TTB-Label">GitHub source</a></div>',
        unsafe_allow_html=True,
    )
    st.caption(
        "Distilled-spirits prototype. OCR extracts visible label evidence; deterministic Python rules evaluate "
        "the supported checks. Human review remains required where the prototype is uncertain."
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
