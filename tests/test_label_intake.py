from src.extraction.intake import extract_label_intake
from src.ocr.interface import OCRLine


def ttb_two_panel_lines():
    return [
        OCRLine("ENJOY CHILLED.", 1.0, (383, 33, 525, 56)),
        OCRLine("PRODUCED IN CANADA", 0.968, (359, 84, 550, 103)),
        OCRLine("12345", 1.0, (48, 118, 258, 190)),
        OCRLine("IMPORTED BY:12345 IMPORTS", 0.981, (335, 109, 575, 128)),
        OCRLine("MIAMI,FL", 0.988, (414, 132, 495, 152)),
        OCRLine("GOVERNMENT WARNING:", 0.999, (339, 167, 542, 183)),
        OCRLine("IMPORTS", 1.0, (95, 187, 216, 210)),
        OCRLine("(1) According to the Surgeon", 0.981, (339, 180, 567, 197)),
        OCRLine("General, women should not", 0.986, (339, 194, 558, 209)),
        OCRLine("drink alcoholic beverages", 0.999, (339, 206, 546, 222)),
        OCRLine("during pregnancy because", 0.994, (339, 218, 552, 235)),
        OCRLine("of the risk of birth defects.", 0.976, (339, 231, 552, 247)),
        OCRLine("RUM WITH", 0.957, (96, 247, 214, 266)),
        OCRLine("(2) Consumption of alcoholic", 0.992, (339, 244, 567, 259)),
        OCRLine("beverages impairs your", 0.995, (338, 257, 526, 273)),
        OCRLine("COCONUT LIQUEUR", 0.979, (50, 268, 265, 287)),
        OCRLine("ability to drive a car or", 0.996, (338, 269, 524, 286)),
        OCRLine("operate machinery. and may", 0.995, (339, 282, 564, 299)),
        OCRLine("cause health problems.", 0.999, (339, 296, 525, 310)),
        OCRLine("18% ALC/VOL.", 0.974, (43, 310, 159, 327)),
        OCRLine("200 ML", 0.927, (195, 309, 260, 328)),
        OCRLine("IMPORTED", 1.0, (87, 344, 225, 364)),
    ]


def test_spatial_intake_joins_multiline_brand_and_class_without_cross_column_contamination():
    draft = extract_label_intake(ttb_two_panel_lines())
    assert draft.brand.value == "12345 IMPORTS"
    assert draft.class_type.value == "RUM WITH COCONUT LIQUEUR"


def test_spatial_warning_excludes_left_panel_text():
    draft = extract_label_intake(ttb_two_panel_lines())
    assert "IMPORTS" not in draft.government_warning.value.replace("IMPORTED", "")
    assert "RUM WITH" not in draft.government_warning.value
    assert "COCONUT LIQUEUR" not in draft.government_warning.value
    assert "cause health problems." in draft.government_warning.value


def test_country_is_extracted_semantically_from_origin_phrase():
    draft = extract_label_intake(ttb_two_panel_lines())
    assert draft.country_origin.value == "CANADA"
    assert draft.imported.value == "Yes"


def test_address_collects_importer_and_following_location():
    draft = extract_label_intake(ttb_two_panel_lines())
    assert "12345 IMPORTS" in draft.name_address.value
    assert "MIAMI,FL" in draft.name_address.value


def test_abv_and_net_contents_are_autofilled():
    draft = extract_label_intake(ttb_two_panel_lines())
    assert draft.alcohol_content.value == "18% ALC/VOL."
    assert draft.net_contents.value == "200 ML"


def test_low_ocr_score_marks_field_for_review():
    lines = [OCRLine("43% ALC/VOL.", 0.72, (10, 10, 100, 30))]
    draft = extract_label_intake(lines)
    assert draft.alcohol_content.review_required
    assert "0.72" in draft.alcohol_content.reason
