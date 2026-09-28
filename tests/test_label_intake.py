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



def test_kuroyama_exact_abv_does_not_swallow_net_contents_or_japanese_subtitle():
    lines = [
        OCRLine("KUROYAMA", 0.994, (60, 405, 675, 552)),
        OCRLine("RESERVE", 0.999, (159, 504, 577, 599)),
        OCRLine("黑山瀣蔵", 0.824, (254, 580, 479, 634)),
        OCRLine("90% ALC/VOL | 550 ML", 0.987, (160, 890, 569, 930)),
        OCRLine("BOTTLE SIZE:", 1.0, (848, 722, 1000, 746)),
        OCRLine("550 ML", 0.991, (1051, 722, 1133, 746)),
        OCRLine("SPIRIT TYPE:", 0.988, (848, 654, 991, 677)),
        OCRLine("JAPANESE WHISKY", 1.0, (1049, 651, 1259, 679)),
        OCRLine("ORIGIN:", 1.0, (848, 789, 940, 815)),
        OCRLine("JAPAN", 1.0, (1046, 786, 1126, 818)),
    ]
    draft = extract_label_intake(lines)
    assert draft.brand.value == "KUROYAMA RESERVE"
    assert draft.class_type.value == "JAPANESE WHISKY"
    assert draft.alcohol_content.value == "90% ALC/VOL"
    assert draft.net_contents.value == "550 ML"
    assert draft.country_origin.value == "JAPAN"


def test_blackhaven_structured_origin_wins_and_address_stops_before_warning():
    lines = [
        OCRLine("IMPORTED BY:", 0.961, (1036, 252, 1202, 274)),
        OCRLine("ASHCROFT & WREN SPIRITS, NEW YORK, NY", 0.986, (874, 277, 1361, 302)),
        OCRLine("GOVERNMENT WARNING:", 1.0, (852, 351, 1187, 380)),
        OCRLine("DISTILLED IN ENGLAND", 0.999, (170, 639, 605, 670)),
        OCRLine("ORIGIN:", 1.0, (870, 796, 965, 819)),
        OCRLine("ENGLAND", 1.0, (1138, 796, 1251, 819)),
        OCRLine("PRODUCT OF GREAT BRITAIN", 0.997, (190, 1004, 587, 1027)),
    ]
    draft = extract_label_intake(lines)
    assert draft.name_address.value == "IMPORTED BY: ASHCROFT & WREN SPIRITS, NEW YORK, NY"
    assert "GOVERNMENT WARNING" not in draft.name_address.value
    assert draft.country_origin.value == "ENGLAND"
    assert not draft.country_origin.review_required


def test_iron_harbor_brand_excludes_strength_descriptor_and_import_conflict_reviews():
    lines = [
        OCRLine("DISTILLED AND BOTTLED IN USA", 0.999, (859, 133, 1357, 167)),
        OCRLine("IMPORTED BY: IRON HARBOR SPIRITS,", 0.995, (851, 171, 1369, 203)),
        OCRLine("SAVANNAH, GA", 0.984, (1007, 202, 1216, 235)),
        OCRLine("IRON HARBOR", 0.998, (24, 262, 753, 466)),
        OCRLine("DISTILLING CO.", 0.999, (181, 430, 588, 485)),
        OCRLine("CASK STRENGTH", 0.993, (135, 630, 642, 689)),
        OCRLine("GOVERNMENT WARNING:", 1.0, (837, 250, 1384, 300)),
    ]
    draft = extract_label_intake(lines)
    assert draft.brand.value == "IRON HARBOR DISTILLING CO."
    assert "GOVERNMENT WARNING" not in draft.name_address.value
    assert draft.imported.value == "Yes"
    assert draft.imported.review_required


def test_copper_fox_recovers_street_address_and_domestic_status_without_yellow_noise():
    lines = [
        OCRLine("Copper Fox", 0.972, (501, 315, 1125, 500)),
        OCRLine("DISTILLING CO", 0.982, (601, 467, 990, 507)),
        OCRLine("COPPER FOX", 0.995, (122, 612, 390, 649)),
        OCRLine("DISTILLING CO.", 0.999, (137, 651, 376, 681)),
        OCRLine("BOURBON", 1.0, (593, 697, 1009, 764)),
        OCRLine("KENTUCKY STRAIGHT", 0.997, (101, 711, 412, 734)),
        OCRLine("1207 MAPLE ROW", 0.998, (144, 741, 370, 761)),
        OCRLine("LEXINGTON,KY", 0.992, (153, 768, 359, 792)),
    ]
    draft = extract_label_intake(lines)
    assert draft.brand.value == "Copper Fox DISTILLING CO"
    assert draft.class_type.value == "BOURBON"
    assert "1207 MAPLE ROW" in draft.name_address.value
    assert "LEXINGTON,KY" in draft.name_address.value
    assert draft.imported.value == "No"
    assert not draft.imported.review_required


def test_ember_coast_prefers_spirit_type_anchor_and_excludes_website_from_address():
    lines = [
        OCRLine("EMBER COAST", 0.982, (128, 155, 955, 263)),
        OCRLine("DISTILLERY", 0.999, (352, 262, 711, 298)),
        OCRLine("SMALL BATCH CRAFT SPIRITS", 0.986, (261, 305, 793, 337)),
        OCRLine("CAPE CITRUS DRY GIN", 0.969, (79, 354, 976, 426)),
        OCRLine("A bright and aromatic distilled gin crafted in small batches with citrus-forward", 0.999, (36, 432, 1020, 468)),
        OCRLine("SPIRIT TYPE:", 0.999, (711, 1133, 815, 1169)),
        OCRLine("Distilled Dry Gin", 1.0, (829, 1136, 979, 1166)),
        OCRLine("ORIGIN:", 0.999, (711, 1168, 777, 1201)),
        OCRLine("California, USA", 0.998, (830, 1168, 967, 1198)),
        OCRLine("Produced and bottled by Ember Coast Distillery, 118 Harbor Lane, Oakland, CA 94607", 0.986, (163, 1401, 890, 1431)),
        OCRLine("www.embercoastdistillery.com", 1.0, (214, 1431, 839, 1477)),
    ]
    draft = extract_label_intake(lines)
    assert draft.brand.value == "EMBER COAST DISTILLERY"
    assert draft.class_type.value == "Distilled Dry Gin"
    assert draft.country_origin.value == "California, USA"
    assert draft.name_address.value.endswith("CA 94607")
    assert "www." not in draft.name_address.value
    assert draft.imported.value == "No"
    assert not draft.imported.review_required


def test_missing_conditional_disclosures_are_neutral_not_yellow_review():
    draft = extract_label_intake([OCRLine("BOURBON", 1.0, (10, 10, 100, 30))])
    assert not draft.age_statement.review_required
    assert not draft.color_disclosure.review_required
    assert not draft.commodity_statement.review_required
