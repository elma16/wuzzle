#!/usr/bin/env python3

try:
    import pycountry
except ImportError:
    pycountry = None

code_to_flag = {
    "BLM": "st-barthelemey",
    "CCK": "cocos-keeling-islands",
    "CIV": "cote-divoire",
    "FLK": "falkland-islands",
    "ENG": "england",
    "SCO": "scotland",
    "WLS": "wales",
    "ATG": "antigua-and-barbuda",
    "BIH": "bosnia-herzegovina",
    "BRN": "brunei",
    "CUW": "curacao",
    "COD": "congo--kinshasa",
    "COG": "congo--brazzaville",
    "FSM": "micronesia",
    "HKG": "hong-kong-sar-china",
    "HMD": "heard-mcdonald-islands",
    "KNA": "st-kitts-nevis",
    "KOR": "south-korea",
    "LAO": "laos",
    "IRN": "iran",
    "MAF": "st-martin",
    "MDA": "moldova",
    "PRK": "north-korea",
    "PSE": "palestine-territories",
    "RUS": "russia",
    "SGS": "south-georgia-south-sandwich-islands",
    "SHN": "st-helena",
    "SJM": "svalbard-jan-mayen",
    "STP": "sao-tome-principe",
    "SXM": "sint-maarten",
    "SYR": "syria",
    "TCA": "turks-caicos-islands",
    "TTO": "trinidad-tobago",
    "TWN": "taiwan",
    "TZA": "tanzania",
    "VAT": "vatican-city",
    "VCT": "saint-vincent-grenadines",
    "VEN": "venezuela",
    "VGB": "british-virgin-islands",
    "VIR": "us-virgin-islands",
    "VNM": "vietnam",
    "WLF": "wallis-futuna",
}


def _require_pycountry():
    if pycountry is None:
        raise ImportError("pycountry is required. Install with 'pip install wuzzle[country]'.")


def country_code_to_latex_emoji(country_code):
    # Check your custom dictionary first
    if country_code in code_to_flag:
        country_name = code_to_flag[country_code]
    else:
        _require_pycountry()
        try:
            country_name = pycountry.countries.get(alpha_3=country_code).name
        except AttributeError:
            return "\\emoji{question}"

    country_name_formatted = country_name.replace(" ", "-").lower()

    return f"\\emoji{{flag-{country_name_formatted}}}"


def get_all_country_codes():
    _require_pycountry()
    return sorted([country.alpha_3 for country in pycountry.countries])


if pycountry is not None:
    country_codes = get_all_country_codes()
else:
    country_codes = []
