#!/usr/bin/env python3
"""
build_symbols.py — generates data/symbols.json + data/groups.json for the AltKeyCodes site.

Sources of truth (all verifiable, no invented data):
  * Legacy Windows Alt codes 1-255 -> Python codecs 'cp437' (OEM, 3-digit) and
    'cp1252' (ANSI, 0-prefixed 4-digit). Cross-checked against alt-codes.net's table.
  * Unicode names / categories / blocks -> Python stdlib `unicodedata` (Unicode 16.0.0).
  * HTML named entities -> Python stdlib `html.entities.codepoint2name`.
  * Curated aliases, LaTeX commands, and macOS Option shortcuts are hand-maintained
    tables at the bottom of this file. Nothing is guessed at runtime.

Run:  python3 build_symbols.py
"""
import html.entities
import json
import os
import unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "data")

# --------------------------------------------------------------------------
# 1. Legacy Windows Alt codes, derived from the actual codecs
# --------------------------------------------------------------------------

def legacy_alt_codes():
    """Return {codepoint: [alt-code strings]} for the classic 0-255 range.

    3-digit codes  -> OEM code page 437  (Alt + 1..255, no leading zero)
    0-prefixed     -> ANSI code page 1252 (Alt + 0128..0255)

    Codes 1-31 and 127 are control codes in cp437; they render as glyphs in the
    OEM font, so they are kept with the glyph the console font draws.
    """
    out = {}
    for n in range(1, 256):
        try:
            ch = bytes([n]).decode("cp437")
        except UnicodeDecodeError:
            continue
        cp = ord(ch)
        out.setdefault(cp, []).append(str(n))
    for n in range(128, 256):
        try:
            ch = bytes([n]).decode("cp1252")
        except UnicodeDecodeError:
            continue
        cp = ord(ch)
        code = "0" + str(n)
        if code not in out.setdefault(cp, []):
            out[cp].append(code)
    return out


LEGACY = legacy_alt_codes()


# --------------------------------------------------------------------------
# 2. Group definitions. Ranges are expanded, explicit lists are literal.
#    Groups are content decisions, not authoritative claims.
# --------------------------------------------------------------------------

def rng(a, b):
    return list(range(a, b + 1))


GROUPS = [
    # slug, display name, tagline, intent ("Type X"), members
    ("hearts", "Heart Symbols", "Hearts, love hearts and heart emoji you can type anywhere",
     "heart", rng(0x2661, 0x2665) + rng(0x2763, 0x2767) + rng(0x1F493, 0x1F49F) +
     [0x2765, 0x1F5A4, 0x1F90D, 0x1F90E, 0x1F9E1, 0x2764, 0x2665, 0x2661, 0x2662,
      0x1F498, 0x1F499, 0x1F49A, 0x1F49B, 0x1F49C, 0x1F49D, 0x1F49E, 0x1F49F]),

    ("check-marks", "Check Mark Symbols", "Tick marks, cross marks and ballot boxes",
     "check mark", [0x2713, 0x2714, 0x2715, 0x2716, 0x2717, 0x2718, 0x2610, 0x2611,
                    0x2612, 0x2705, 0x274C, 0x274E, 0x1F5F8, 0x1F5F9, 0x2719, 0x271A,
                    0x237B, 0x2B1A]),

    ("arrows", "Arrow Symbols", "Every arrow direction, from simple to double-struck",
     "arrow", rng(0x2190, 0x21FF) + rng(0x27F0, 0x27FF) + rng(0x2900, 0x297F) +
     rng(0x2B00, 0x2B11) + [0x2B95, 0x27A1, 0x2B05, 0x2B06, 0x2B07, 0x21E7, 0x21E9,
                            0x21E8, 0x21E6, 0x2794, 0x279C, 0x27A4, 0x27B3]),

    ("stars", "Star Symbols", "Stars, sparkles and asterisk marks",
     "star", [0x2605, 0x2606, 0x22C6, 0x2217, 0x2735, 0x2736, 0x2737, 0x2738, 0x2739,
              0x273A, 0x273B, 0x273C, 0x273D, 0x2729, 0x272A, 0x272B, 0x272C, 0x272D,
              0x272E, 0x272F, 0x2730, 0x2731, 0x2732, 0x2733, 0x2734, 0x2B50, 0x1F31F,
              0x1F320, 0x066D, 0x2042, 0x2051]),

    ("currency", "Currency Symbols", "Dollar, euro, pound, yen, rupee and every money sign",
     "currency", [0x0024, 0x00A2, 0x00A3, 0x00A4, 0x00A5, 0x20A0, 0x20A1, 0x20A2, 0x20A3,
                  0x20A4, 0x20A5, 0x20A6, 0x20A7, 0x20A8, 0x20A9, 0x20AA, 0x20AB, 0x20AC,
                  0x20AD, 0x20AE, 0x20AF, 0x20B0, 0x20B1, 0x20B2, 0x20B3, 0x20B4, 0x20B5,
                  0x20B6, 0x20B7, 0x20B8, 0x20B9, 0x20BA, 0x20BB, 0x20BC, 0x20BD, 0x20BE,
                  0x20BF, 0x09F2, 0x09F3, 0x0AF1, 0x0BF9, 0x0E3F, 0x17DB, 0x060B, 0x09F2,
                  0x5143, 0x5186, 0xFDFC, 0x20C0, 0x20C1]),

    ("math", "Math Symbols", "Operators, set theory, logic and calculus signs",
     "math symbol", [0x00B1, 0x00D7, 0x00F7, 0x2212, 0x2213, 0x2214, 0x2216, 0x2217, 0x2218,
                     0x2219, 0x221A, 0x221D, 0x221E, 0x2220, 0x2223, 0x2225, 0x2227, 0x2228,
                     0x2229, 0x222A, 0x222B, 0x222C, 0x222D, 0x222E, 0x2234, 0x2235, 0x223C,
                     0x223D, 0x2243, 0x2245, 0x2248, 0x224D, 0x2260, 0x2261, 0x2262, 0x2264,
                     0x2265, 0x2266, 0x2267, 0x226A, 0x226B, 0x226E, 0x226F, 0x2270, 0x2271,
                     0x2282, 0x2283, 0x2284, 0x2286, 0x2287, 0x2295, 0x2296, 0x2297, 0x2299,
                     0x229A, 0x22A2, 0x22A3, 0x22A5, 0x22C0, 0x22C1, 0x22C2, 0x22C3, 0x22C4,
                     0x22C5, 0x22C6, 0x22EE, 0x22EF, 0x2308, 0x2309, 0x230A, 0x230B, 0x27E8,
                     0x27E9, 0x27F5, 0x27F6, 0x27F7, 0x27FA, 0x2A00, 0x2A01, 0x2A02, 0x2A04,
                     0x2A2F, 0x2A3F, 0x2A7D, 0x2A7E, 0x2A85, 0x2A86, 0x2211, 0x220F, 0x222B,
                     0x2210, 0x2202, 0x2207, 0x2205, 0x2208, 0x2209, 0x220B, 0x220E, 0x22A4,
                     0x2320, 0x2321, 0x2393, 0x2394]),

    ("legal", "Legal and Trademark Symbols", "Copyright, registered, trademark and service marks",
     "copyright symbol", [0x00A9, 0x00AE, 0x2122, 0x2117, 0x211E, 0x2120, 0x2121, 0x1F16A,
                          0x1F16B, 0x1F16C, 0x24B8, 0x24C7, 0x24C5]),

    ("greek", "Greek Letters", "The Greek alphabet in upper and lower case",
     "greek letter", list(range(0x0391, 0x03A2)) + list(range(0x03A3, 0x03AA)) +
     list(range(0x03B1, 0x03CA)) + [0x03C2, 0x03D1, 0x03D2, 0x03D5, 0x03D6, 0x03F4, 0x03F5,
                                    0x2206, 0x220F, 0x2211, 0x221A, 0x221E, 0x03BC, 0x03C0]),

    ("box-drawing", "Box Drawing Characters", "Lines, corners and junctions for ASCII art and tables",
     "box drawing", rng(0x2500, 0x257F)),

    ("blocks", "Block Elements", "Full blocks, shades and quadrants",
     "block element", rng(0x2580, 0x259F)),

    ("geometric", "Geometric Shapes", "Circles, squares, triangles and diamonds",
     "geometric shape", rng(0x25A0, 0x25FF)),

    ("dingbats", "Dingbats", "Ornaments, crosses, flowers and flourishes",
     "dingbat", rng(0x2700, 0x27BF)),

    ("misc-symbols", "Miscellaneous Symbols", "Weather, zodiac-adjacent, chess, cards and more",
     "symbol", rng(0x2600, 0x26FF)),

    ("zodiac", "Zodiac Signs", "The twelve astrological signs, in order",
     "zodiac sign", rng(0x2648, 0x2653)),

    ("chess", "Chess Symbols", "White and black chess pieces",
     "chess symbol", rng(0x2654, 0x265F)),

    ("playing-cards", "Card Suit Symbols", "Spades, hearts, diamonds and clubs",
     "card suit", [0x2660, 0x2661, 0x2662, 0x2663, 0x2664, 0x2665, 0x2666, 0x2667,
                   0x1F0A0, 0x1F0B1, 0x1F0C1, 0x1F0D1, 0x1F0A1, 0x1F0B2, 0x1F0C2,
                   0x1F0D2, 0x1F0AB, 0x1F0BB, 0x1F0CB, 0x1F0DB]),

    ("music", "Music Symbols", "Notes, clefs and time signatures",
     "music note", [0x2669, 0x266A, 0x266B, 0x266C, 0x266D, 0x266E, 0x266F, 0x1D100,
                    0x1D101, 0x1D102, 0x1D103, 0x1D11E, 0x1D122, 0x1D11A, 0x1D13B,
                    0x1D13C, 0x1D13D, 0x1D13E, 0x1D13F, 0x1D140, 0x1D15D, 0x1D15E,
                    0x1D160, 0x1D161, 0x1D162]),

    ("weather", "Weather and Sky Symbols", "Sun, cloud, rain, snow, lightning and moon phases",
     "weather symbol", [0x2600, 0x2601, 0x2602, 0x2603, 0x2604, 0x2614, 0x2618, 0x261D,
                        0x2620, 0x263C, 0x263D, 0x263E, 0x26A1, 0x26C4, 0x26C5, 0x26C6,
                        0x26C7, 0x26C8, 0x26C9, 0x26CA, 0x26CB, 0x26CC, 0x26CD, 0x26CE,
                        0x26CF, 0x26D0, 0x26D1, 0x26D2, 0x26D3, 0x26D4, 0x2744, 0x2745,
                        0x2746, 0x1F300, 0x1F301, 0x1F302, 0x1F303, 0x1F304, 0x1F305,
                        0x1F306, 0x1F307, 0x1F308, 0x1F30A, 0x1F30B, 0x1F30C, 0x1F311,
                        0x1F312, 0x1F313, 0x1F314, 0x1F315, 0x1F316, 0x1F317, 0x1F318,
                        0x1F319, 0x1F31A, 0x1F31B, 0x1F31C, 0x1F31D, 0x1F31E, 0x1F324,
                        0x1F325, 0x1F326, 0x1F327, 0x1F328, 0x1F329, 0x1F32A, 0x1F32B,
                        0x1F32C, 0x1F4A7]),

    ("gender", "Gender and Identity Symbols", "Male, female, transgender and non-binary signs",
     "gender symbol", [0x2640, 0x2641, 0x2642, 0x26A4, 0x26A5, 0x26A6, 0x26A7, 0x26B2,
                       0x26B3, 0x26B4, 0x26B5, 0x26B6, 0x26B7, 0x26B8, 0x1F6BB]),

    ("superscript-subscript", "Superscript and Subscript", "Squared, cubed and every raised or lowered number",
     "superscript", list(range(0x2070, 0x207A)) + list(range(0x2080, 0x208A)) +
     [0x00B2, 0x00B3, 0x00B9, 0x00B0, 0x207A, 0x207B, 0x207C, 0x207D, 0x207E, 0x207F,
      0x208A, 0x208B, 0x208C, 0x208D, 0x208E, 0x2071, 0x02B0, 0x02B1]),

    ("fractions", "Fraction Symbols", "Vulgar fractions from a half to a ninth",
     "fraction", [0x00BC, 0x00BD, 0x00BE, 0x2044, 0x2150, 0x2151, 0x2152, 0x2153, 0x2154,
                  0x2155, 0x2156, 0x2157, 0x2158, 0x2159, 0x215A, 0x215B, 0x215C, 0x215D,
                  0x215E, 0x215F, 0x2189, 0x00E2, 0x2215, 0x00F7]),

    ("punctuation", "Punctuation and Quotation Marks", "Smart quotes, dashes, ellipsis and brackets",
     "punctuation", [0x00A1, 0x00BF, 0x00AB, 0x00BB, 0x2010, 0x2011, 0x2012, 0x2013, 0x2014,
                     0x2015, 0x2016, 0x2017, 0x2018, 0x2019, 0x201A, 0x201B, 0x201C, 0x201D,
                     0x201E, 0x201F, 0x2020, 0x2021, 0x2022, 0x2023, 0x2024, 0x2025, 0x2026,
                     0x2027, 0x2030, 0x2031, 0x2032, 0x2033, 0x2034, 0x2035, 0x2036, 0x2037,
                     0x2038, 0x2039, 0x203A, 0x203B, 0x203C, 0x203D, 0x203E, 0x203F, 0x2040,
                     0x2041, 0x2042, 0x2043, 0x2044, 0x2045, 0x2046, 0x2047, 0x2048, 0x2049,
                     0x204A, 0x204B, 0x204C, 0x204D, 0x204E, 0x204F, 0x2050, 0x2051, 0x2052,
                     0x2053, 0x2054, 0x2055, 0x2056, 0x2057, 0x00B7, 0x00B6, 0x00A7, 0x2E18,
                     0x2E19, 0x2E2E, 0x2E2F]),

    ("bullets", "Bullet and List Markers", "Bullets, dots and list markers for documents",
     "bullet", [0x2022, 0x2023, 0x2043, 0x25AA, 0x25AB, 0x25CF, 0x25CB, 0x25E6, 0x204C,
                0x204D, 0x2219, 0x00B7, 0x2024, 0x2025, 0x2027, 0x25D8, 0x29BE, 0x29BF,
                0x25C6, 0x25C7, 0x25B8, 0x25B9, 0x25FE, 0x25FD]),

    ("technical", "Technical and Miscellaneous Signs", "Keycaps, power, media control and interface glyphs",
     "technical symbol", rng(0x2300, 0x23FF)),

    ("smileys", "Smiley and Emotion Symbols", "Text smiles, faces and mood glyphs",
     "smiley", [0x2639, 0x263A, 0x263B, 0x1F600, 0x1F601, 0x1F602, 0x1F603, 0x1F604,
                0x1F605, 0x1F606, 0x1F609, 0x1F60A, 0x1F60B, 0x1F60C, 0x1F60D, 0x1F60E,
                0x1F60F, 0x1F610, 0x1F611, 0x1F612, 0x1F613, 0x1F614, 0x1F615, 0x1F616,
                0x1F617, 0x1F618, 0x1F619, 0x1F61A, 0x1F61B, 0x1F61C, 0x1F61D, 0x1F61E,
                0x1F61F, 0x1F620, 0x1F621, 0x1F622, 0x1F623, 0x1F624, 0x1F625, 0x1F626,
                0x1F627, 0x1F628, 0x1F629, 0x1F62A, 0x1F62B, 0x1F62C, 0x1F62D, 0x1F62E,
                0x1F62F, 0x1F630, 0x1F631, 0x1F632, 0x1F633, 0x1F634, 0x1F635, 0x1F636,
                0x1F637, 0x1F638, 0x1F639, 0x1F63A, 0x1F63B, 0x1F63C, 0x1F63D, 0x1F63E,
                0x1F63F, 0x1F640, 0x1F641, 0x1F642, 0x1F643, 0x1F644, 0x1F910, 0x1F911,
                0x1F912, 0x1F913, 0x1F914, 0x1F915, 0x1F917, 0x1F920, 0x1F922, 0x1F923,
                0x1F924, 0x1F925, 0x1F927, 0x1F928, 0x1F929, 0x1F92A, 0x1F92B, 0x1F92C,
                0x1F92D, 0x1F92E, 0x1F92F, 0x1F970, 0x1F971, 0x1F972, 0x1F973, 0x1F974,
                0x1F975, 0x1F976, 0x1F97A, 0x1F97B]),

    ("hands", "Hand and Gesture Symbols", "Pointing hands, thumbs, claps and peace signs",
     "hand symbol", [0x261D, 0x270A, 0x270B, 0x270C, 0x270D, 0x1F44A, 0x1F44B, 0x1F44C,
                    0x1F44D, 0x1F44E, 0x1F44F, 0x1F450, 0x1F446, 0x1F447, 0x1F448,
                    0x1F449, 0x1F595, 0x1F596, 0x1F918, 0x1F919, 0x1F91A, 0x1F91B,
                    0x1F91C, 0x1F91D, 0x1F91E, 0x1F91F, 0x1F932, 0x1F933, 0x1F93C,
                    0x1F93F, 0x1F44C, 0x1F450, 0x1F64C, 0x1F64F, 0x270B]),

    ("warning", "Warning, Hazard and Safety Signs", "Caution, radioactive, biohazard and prohibition signs",
     "warning symbol", [0x26A0, 0x2620, 0x2621, 0x2622, 0x2623, 0x2624, 0x2625, 0x2626,
                        0x2627, 0x2628, 0x2629, 0x262A, 0x262B, 0x262C, 0x262D, 0x262E,
                        0x262F, 0x2671, 0x2672, 0x2673, 0x2674, 0x2675, 0x2676, 0x2677,
                        0x2678, 0x2679, 0x267A, 0x267B, 0x267C, 0x267D, 0x267E, 0x267F,
                        0x2622, 0x2623, 0x26D4, 0x1F6AB, 0x1F6AD, 0x1F6B7, 0x1F6AF,
                        0x1F6B1, 0x1F6B3, 0x1F6B8]),

    ("french", "French Accent Alt Codes", "Type french accents, cedilla and ligatures on any keyboard",
     "french accent", [0x00C0, 0x00C2, 0x00C6, 0x00C7, 0x00C8, 0x00C9, 0x00CA, 0x00CB,
                       0x00CE, 0x00CF, 0x00D4, 0x00D9, 0x00DB, 0x00DC, 0x0152, 0x00E0,
                       0x00E2, 0x00E6, 0x00E7, 0x00E8, 0x00E9, 0x00EA, 0x00EB, 0x00EE,
                       0x00EF, 0x00F4, 0x00F9, 0x00FB, 0x00FC, 0x0153, 0x00FF, 0x0178]),

    ("german", "German Alt Codes", "Type German umlauts and Eszett on any keyboard",
     "german umlaut", [0x00C4, 0x00D6, 0x00DC, 0x00DF, 0x00E4, 0x00F6, 0x00FC, 0x20AC]),

    ("spanish", "Spanish Alt Codes", "Type Spanish accents, enye and inverted punctuation",
     "spanish accent", [0x00C1, 0x00C9, 0x00CD, 0x00D1, 0x00D3, 0x00DA, 0x00DC, 0x00E1,
                        0x00E9, 0x00ED, 0x00F1, 0x00F3, 0x00FA, 0x00FC, 0x00A1, 0x00BF]),

    ("italian", "Italian Alt Codes", "Type Italian accents on any keyboard",
     "italian accent", [0x00C0, 0x00C8, 0x00CC, 0x00D2, 0x00D9, 0x00E0, 0x00E8, 0x00EC,
                        0x00F2, 0x00F9, 0x00C7, 0x00E7, 0x00EC, 0x00C9]),

    ("portuguese", "Portuguese Alt Codes", "Type Portuguese accents, tilde and cedilla",
     "portuguese accent", [0x00C1, 0x00C2, 0x00C3, 0x00C7, 0x00C9, 0x00CA, 0x00CD, 0x00D3,
                           0x00D4, 0x00D5, 0x00DA, 0x00E1, 0x00E2, 0x00E3, 0x00E7, 0x00E9,
                           0x00EA, 0x00ED, 0x00F3, 0x00F4, 0x00F5, 0x00FA]),

    ("cyrillic", "Cyrillic Letters", "The Russian and Slavic alphabet",
     "cyrillic letter", list(range(0x0410, 0x0450)) + [0x0401, 0x0451, 0x0402, 0x0403,
                                                        0x0404, 0x0405, 0x0406, 0x0407,
                                                        0x0408, 0x0409, 0x040A, 0x040B,
                                                        0x040C, 0x040E, 0x040F]),
]

# Names too generic to be useful on their own; the curated alias table fills these in.
SKIP_CATEGORIES = {"Cn", "Co", "Cs", "Cc", "Cf"}


def unicode_entries():
    seen = {}
    for slug, name, tagline, intent, members in GROUPS:
        for cp in members:
            if cp in seen:
                seen[cp]["groups"].append(slug)
                continue
            try:
                ch = chr(cp)
            except ValueError:
                continue
            cat = unicodedata.category(ch)
            if cat in SKIP_CATEGORIES:
                continue
            try:
                raw = unicodedata.name(ch)
            except ValueError:
                continue
            seen[cp] = {
                "cp": cp,
                "glyph": ch,
                "unicode_name": raw,
                "name": title_case_unicode_name(raw),
                "category": cat,
                "block": block_name(cp),
                "groups": [slug],
            }
    return seen


# Control codes 1-31 and 127 are not printable Unicode, but the IBM PC OEM
# console font draws a picture glyph in their cell. These are the classic
# nostalgic Alt codes (Alt+3 = a heart) and alt-codes.net's whole 1-31 column.
# Mapping is the long-standing CP437 graphical / "code page 437" table.
OEM_CONTROL_PICTURES = {
    0x01: 0x263A, 0x02: 0x263B, 0x03: 0x2665, 0x04: 0x2666, 0x05: 0x2663,
    0x06: 0x2660, 0x07: 0x2022, 0x08: 0x25D8, 0x09: 0x25CB, 0x0A: 0x25D9,
    0x0B: 0x2642, 0x0C: 0x2640, 0x0D: 0x266A, 0x0E: 0x266B, 0x0F: 0x263C,
    0x10: 0x25BA, 0x11: 0x25C4, 0x12: 0x2195, 0x13: 0x203C, 0x14: 0x00B6,
    0x15: 0x00A7, 0x16: 0x25AC, 0x17: 0x21A8, 0x18: 0x2191, 0x19: 0x2193,
    0x1A: 0x2192, 0x1B: 0x2190, 0x1C: 0x221F, 0x1D: 0x2194, 0x1E: 0x25B2,
    0x1F: 0x25BC, 0x7F: 0x2302,
}


def title_case_unicode_name(raw):
    """'CHECK MARK' -> 'Check Mark'. Unicode names are upper case by definition;
    title case is how every reference table displays them."""
    return " ".join(w.capitalize() for w in raw.split())


# Unicode block boundaries (subset relevant to the groups above).
BLOCKS = [
    (0x0020, 0x007F, "Basic Latin"), (0x00A0, 0x00FF, "Latin-1 Supplement"),
    (0x0100, 0x017F, "Latin Extended-A"), (0x0180, 0x024F, "Latin Extended-B"),
    (0x0250, 0x02AF, "IPA Extensions"), (0x02B0, 0x02FF, "Spacing Modifier Letters"),
    (0x0300, 0x036F, "Combining Diacritical Marks"), (0x0370, 0x03FF, "Greek and Coptic"),
    (0x0400, 0x04FF, "Cyrillic"), (0x0500, 0x052F, "Cyrillic Supplement"),
    (0x0600, 0x06FF, "Arabic"), (0x0900, 0x097F, "Devanagari"),
    (0x0E00, 0x0E7F, "Thai"), (0x1E00, 0x1EFF, "Latin Extended Additional"),
    (0x2000, 0x206F, "General Punctuation"), (0x2070, 0x209F, "Superscripts and Subscripts"),
    (0x20A0, 0x20CF, "Currency Symbols"), (0x20D0, 0x20FF, "Combining Diacritical Marks for Symbols"),
    (0x2100, 0x214F, "Letterlike Symbols"), (0x2150, 0x218F, "Number Forms"),
    (0x2190, 0x21FF, "Arrows"), (0x2200, 0x22FF, "Mathematical Operators"),
    (0x2300, 0x23FF, "Miscellaneous Technical"), (0x2400, 0x243F, "Control Pictures"),
    (0x2440, 0x245F, "Optical Character Recognition"), (0x2460, 0x24FF, "Enclosed Alphanumerics"),
    (0x2500, 0x257F, "Box Drawing"), (0x2580, 0x259F, "Block Elements"),
    (0x25A0, 0x25FF, "Geometric Shapes"), (0x2600, 0x26FF, "Miscellaneous Symbols"),
    (0x2700, 0x27BF, "Dingbats"), (0x27C0, 0x27EF, "Miscellaneous Mathematical Symbols-A"),
    (0x27F0, 0x27FF, "Supplemental Arrows-A"), (0x2800, 0x28FF, "Braille Patterns"),
    (0x2900, 0x297F, "Supplemental Arrows-B"), (0x2980, 0x29FF, "Miscellaneous Mathematical Symbols-B"),
    (0x2A00, 0x2AFF, "Supplemental Mathematical Operators"), (0x2B00, 0x2BFF, "Miscellaneous Symbols and Arrows"),
    (0x2E00, 0x2E7F, "Supplemental Punctuation"), (0x3000, 0x303F, "CJK Symbols and Punctuation"),
    (0x1D100, 0x1D1FF, "Musical Symbols"), (0x1D400, 0x1D7FF, "Mathematical Alphanumeric Symbols"),
    (0x1F300, 0x1F5FF, "Miscellaneous Symbols and Pictographs"), (0x1F600, 0x1F64F, "Emoticons"),
    (0x1F680, 0x1F6FF, "Transport and Map Symbols"), (0x1F900, 0x1F9FF, "Supplemental Symbols and Pictographs"),
    (0x1F0A0, 0x1F0FF, "Playing Cards"), (0x1F16A, 0x1F16F, "Enclosed Alphanumeric Supplement"),
]


def block_name(cp):
    for a, b, n in BLOCKS:
        if a <= cp <= b:
            return n
    return "Unicode"


# --------------------------------------------------------------------------
# 3. Curated tables — hand-maintained. This is where search quality comes from.
# --------------------------------------------------------------------------

# cp -> search aliases people actually type.
ALIASES = {
    0x2713: ["tick", "checkmark", "check mark", "correct", "ok", "okay", "approve", "approved",
             "done", "yes", "success", "valid", "tick mark", "checkbox"],
    0x2714: ["heavy check", "bold tick", "checkmark", "tick", "done", "approved", "yes", "valid"],
    0x2715: ["multiplication x", "cross", "cancel", "no", "wrong", "delete", "close", "x mark"],
    0x2716: ["heavy x", "cross", "cancel", "no", "wrong", "denied", "close"],
    0x2717: ["ballot x", "cross", "no", "wrong", "incorrect", "invalid", "reject"],
    0x2718: ["heavy ballot x", "cross", "no", "wrong", "incorrect", "denied"],
    0x2705: ["white heavy check mark", "green check", "done", "approved", "yes", "complete", "emoji"],
    0x274C: ["cross mark", "red x", "no", "wrong", "denied", "cancel", "emoji"],
    0x274E: ["negative squared cross", "red x", "no", "wrong", "emoji"],
    0x2610: ["ballot box", "checkbox", "empty box", "unchecked", "tick box"],
    0x2611: ["ballot box with check", "checkbox", "checked", "tick box", "done"],
    0x2612: ["ballot box with x", "checkbox", "unchecked", "no", "ballot"],
    0x2665: ["heart", "love", "card heart", "valentine", "red heart", "suit"],
    0x2661: ["white heart", "outline heart", "love", "valentine"],
    0x2764: ["heavy heart", "red heart", "love", "valentine", "emoji", "heart emoji"],
    0x1F494: ["broken heart", "heartbreak", "sad", "emoji", "split"],
    0x1F495: ["two hearts", "love", "couple", "emoji"],
    0x1F496: ["sparkling heart", "love", "emoji", "glitter"],
    0x1F497: ["growing heart", "love", "emoji"],
    0x1F498: ["cupid", "heart with arrow", "love", "emoji", "valentine"],
    0x1F499: ["blue heart", "emoji", "love", "trust"],
    0x1F49A: ["green heart", "emoji", "love"],
    0x1F49B: ["yellow heart", "emoji", "love", "friendship"],
    0x1F49C: ["purple heart", "emoji", "love", "military", "veteran"],
    0x1F49D: ["heart with ribbon", "emoji", "gift", "valentine"],
    0x1F49E: ["revolving hearts", "emoji", "love"],
    0x1F49F: ["heart decoration", "emoji", "love"],
    0x1F5A4: ["black heart", "emoji", "dark", "goth"],
    0x1F90D: ["white heart emoji", "emoji", "love"],
    0x1F90E: ["brown heart", "emoji", "love"],
    0x1F9E1: ["orange heart", "emoji", "love"],
    0x00B0: ["degree", "degrees", "degree sign", "temperature", "celsius", "fahrenheit", "angle", "circle"],
    0x00B1: ["plus minus", "plus or minus", "plus-minus", "tolerance", "error", "margin", "range"],
    0x00D7: ["multiply", "multiplication", "times", "multiply sign", "cross product", "dimensions"],
    0x00F7: ["divide", "division", "divided by", "obelus", "division sign"],
    0x2212: ["minus", "minus sign", "subtract", "subtraction", "en dash minus"],
    0x2248: ["approximately", "approx", "almost equal", "about", "tilde equal", "roughly"],
    0x2260: ["not equal", "does not equal", "inequality", "unequal", "neq"],
    0x2264: ["less than or equal", "less or equal", "lte", "at most", "maximum"],
    0x2265: ["greater than or equal", "greater or equal", "gte", "at least", "minimum"],
    0x221E: ["infinity", "infinite", "endless", "forever", "loop", "lemniscate"],
    0x221A: ["square root", "sqrt", "radical", "root", "checkmark-like"],
    0x2211: ["sum", "summation", "sigma", "total", "autosum"],
    0x220F: ["product", "n-ary product", "product notation"],
    0x222B: ["integral", "calculus", "integrate", "antiderivative"],
    0x2202: ["partial", "partial derivative", "del", "curly d"],
    0x2207: ["nabla", "gradient", "del operator", "backwards delta"],
    0x2205: ["empty set", "null set", "diameter", "slash circle", "no entry"],
    0x2208: ["element of", "belongs to", "is in", "epsilon set"],
    0x2261: ["equivalent", "identical to", "congruent", "triple bar", "same as"],
    0x2262: ["not identical", "not equivalent", "inequivalent"],
    0x00A9: ["copyright", "copyright sign", "c in circle", "copy", "all rights reserved", "intellectual property"],
    0x00AE: ["registered", "registered trademark", "r in circle", "registered mark", "r"],
    0x2122: ["trademark", "tm", "trade mark", "tm sign", "brand"],
    0x2117: ["sound recording copyright", "phonorecord", "p in circle", "music copyright", "record"],
    0x211E: ["prescription take", "pharmacy", "rx", "medicine", "take thou"],
    0x1F16A: ["marque de commerce", "canadian trademark", "mc"],
    0x1F16B: ["registered canadian", "marque deposee", "mr"],
    0x20AC: ["euro", "euro sign", "eur", "european currency", "euro symbol"],
    0x00A3: ["pound", "pound sterling", "gbp", "british pound", "quid", "hash-like"],
    0x00A5: ["yen", "yuan", "jpy", "cny", "japanese yen", "chinese yuan", "rmb"],
    0x00A2: ["cent", "cents", "us cent", "penny", "copper"],
    0x20B9: ["rupee", "indian rupee", "inr", "indian currency"],
    0x20BD: ["ruble", "rouble", "rub", "russian ruble"],
    0x20BA: ["lira", "turkish lira", "try", "turkish currency"],
    0x20AA: ["shekel", "new shekel", "ils", "israeli currency"],
    0x20A9: ["won", "korean won", "krw", "south korea currency"],
    0x20B1: ["peso sign", "philippine peso", "php", "peso"],
    0x20A6: ["naira", "ngn", "nigerian currency"],
    0x20BE: ["lari", "georgian lari", "gel"],
    0x20BF: ["bitcoin", "btc", "bitcoin sign", "crypto"],
    0x20B4: ["hryvnia", "ukrainian hryvnia", "uah"],
    0x2605: ["star", "filled star", "solid star", "rating", "favourite", "favorite", "bookmark"],
    0x2606: ["star", "outline star", "hollow star", "empty star", "rating"],
    0x2B50: ["star emoji", "gold star", "rating", "favourite", "glowing star"],
    0x272A: ["circled star", "star", "rating"],
    0x273D: ["heavy teardrop spoked asterisk", "sparkle", "flower", "snowflake"],
    0x2744: ["snowflake", "snow", "winter", "frost", "ice crystal"],
    0x2745: ["tight trifoliate snowflake", "snowflake", "snow"],
    0x2746: ["heavy chevron snowflake", "snowflake", "snow"],
    0x2022: ["bullet", "bullet point", "dot", "list marker", "field bullet", "round bullet"],
    0x00B7: ["middle dot", "interpunct", "middle dot", "centered dot", "katakana middle dot"],
    0x25CF: ["black circle", "filled circle", "dot", "bullet", "record"],
    0x25CB: ["white circle", "hollow circle", "ring", "degree-like", "circle outline"],
    0x25AA: ["small black square", "square bullet", "filled square"],
    0x25A0: ["black square", "filled square", "square", "box"],
    0x25A1: ["white square", "hollow square", "box", "checkbox"],
    0x25B2: ["up triangle", "triangle", "filled triangle", "increase", "ascending"],
    0x25B3: ["white up triangle", "triangle", "outline triangle", "delta"],
    0x25BC: ["down triangle", "triangle", "decrease", "descending"],
    0x25C6: ["black diamond", "diamond", "filled diamond", "gem", "suit"],
    0x25C7: ["white diamond", "diamond outline", "hollow diamond"],
    0x2190: ["left arrow", "back arrow", "previous", "back"],
    0x2192: ["right arrow", "forward arrow", "next", "implies", "to", "arrow"],
    0x2191: ["up arrow", "increase", "ascending", "up"],
    0x2193: ["down arrow", "decrease", "descending", "download", "down"],
    0x2194: ["left right arrow", "bidirectional", "swap", "horizontal arrow"],
    0x21D2: ["rightwards double arrow", "implies", "therefore", "logic", "double arrow"],
    0x21D4: ["left right double arrow", "if and only if", "iff", "equivalence"],
    0x27A1: ["black rightwards arrow", "arrow emoji", "next", "right"],
    0x2B05: ["leftwards black arrow", "arrow emoji", "back", "left"],
    0x2B06: ["upwards black arrow", "arrow emoji", "up", "north"],
    0x2B07: ["downwards black arrow", "arrow emoji", "down", "south"],
    0x2794: ["heavy wide-headed rightwards arrow", "fat arrow", "double arrow", "implies"],
    0x27F6: ["long rightwards arrow", "long arrow", "to", "right"],
    0x266A: ["music note", "eighth note", "quaver", "song", "music", "sound", "tune"],
    0x266B: ["beamed eighth notes", "music notes", "double note", "music"],
    0x266C: ["beamed sixteenth notes", "music notes", "music"],
    0x2669: ["quarter note", "crotchet", "music note", "music"],
    0x266D: ["flat", "music flat", "flat sign", "accidental", "bemolle"],
    0x266E: ["natural", "music natural", "natural sign", "accidental"],
    0x266F: ["sharp", "music sharp", "sharp sign", "accidental", "diesis", "hash"],
    0x1D11E: ["treble clef", "g clef", "clef", "music", "staff"],
    0x1D122: ["bass clef", "f clef", "clef", "music"],
    0x2044: ["fraction slash", "solidus", "fraction"],
    0x00BD: ["one half", "half", "1/2", "fraction", "vulgar fraction"],
    0x00BC: ["one quarter", "quarter", "1/4", "fraction"],
    0x00BE: ["three quarters", "3/4", "fraction"],
    0x2153: ["one third", "1/3", "fraction"],
    0x2154: ["two thirds", "2/3", "fraction"],
    0x00B2: ["squared", "superscript 2", "to the power of 2", "square", "m2", "power of two"],
    0x00B3: ["cubed", "superscript 3", "to the power of 3", "cube", "m3", "power of three"],
    0x00B9: ["superscript 1", "to the power of 1", "power of one"],
    0x2070: ["superscript 0", "to the power of 0", "power of zero"],
    0x2074: ["superscript 4", "to the power of 4", "power of four"],
    0x2081: ["subscript 1", "subscript one", "chemical formula"],
    0x2082: ["subscript 2", "subscript two", "chemical formula", "co2"],
    0x2026: ["ellipsis", "three dots", "dot dot dot", "continuation", "omission"],
    0x2014: ["em dash", "long dash", "dash", "punctuation"],
    0x2013: ["en dash", "dash", "range", "hyphen-like"],
    0x2018: ["left single quote", "smart quote", "opening quote", "single quotation mark"],
    0x2019: ["right single quote", "apostrophe", "smart apostrophe", "closing quote"],
    0x201C: ["left double quote", "smart quote", "opening quote", "curly quote"],
    0x201D: ["right double quote", "smart quote", "closing quote", "curly quote"],
    0x00AB: ["left guillemet", "angle quote", "french quote", "chevron quote"],
    0x00BB: ["right guillemet", "angle quote", "french quote", "chevron quote"],
    0x00A1: ["inverted exclamation", "spanish exclamation", "upside down exclamation"],
    0x00BF: ["inverted question mark", "spanish question mark", "upside down question mark"],
    0x2020: ["dagger", "obelisk", "footnote", "dead"],
    0x2021: ["double dagger", "diesis", "footnote", "diesis"],
    0x00A7: ["section sign", "section", "silcrow", "legal section", "paragraph"],
    0x00B6: ["pilcrow", "paragraph mark", "paragraph sign", "break"],
    0x2032: ["prime", "minutes", "feet", "arcminute", "single prime"],
    0x2033: ["double prime", "seconds", "inches", "arcsecond"],
    0x2030: ["per mille", "permille", "per thousand", "salinity"],
    0x2600: ["sun", "sunny", "sunshine", "black sun", "weather"],
    0x2601: ["cloud", "cloudy", "overcast", "weather"],
    0x2614: ["umbrella with rain drops", "rain", "showers", "weather"],
    0x26A1: ["high voltage", "lightning", "thunder", "electricity", "power", "zap", "danger"],
    0x263A: ["white smiling face", "smiley", "smile", "happy", "emoji"],
    0x2639: ["white frowning face", "sad", "frown", "unhappy"],
    0x263B: ["black smiling face", "smiley", "happy", "smile"],
    0x2640: ["female sign", "female", "venus", "woman", "gender"],
    0x2642: ["male sign", "male", "mars", "man", "gender"],
    0x26A5: ["male with stroke", "transgender", "gender", "intersex"],
    0x26B2: ["neuter", "gender", "non-binary", "agender"],
    0x2611: ["ballot box with check", "checkbox", "checked", "done", "tick box"],
    0x26A0: ["warning sign", "warning", "caution", "alert", "attention", "triangle warning"],
    0x2620: ["skull and crossbones", "skull", "poison", "danger", "death", "pirate"],
    0x2622: ["radioactive sign", "radiation", "nuclear", "hazard"],
    0x2623: ["biohazard sign", "biohazard", "hazard", "biological"],
    0x26D4: ["no entry", "prohibited", "forbidden", "banned", "denied"],
    0x1F6AB: ["no entry sign", "prohibited", "forbidden", "banned", "emoji"],
    0x2654: ["white chess king", "king", "chess"],
    0x2655: ["white chess queen", "queen", "chess"],
    0x2656: ["white chess rook", "rook", "castle", "chess"],
    0x2657: ["white chess bishop", "bishop", "chess"],
    0x2658: ["white chess knight", "knight", "horse", "chess"],
    0x2659: ["white chess pawn", "pawn", "chess"],
    0x2660: ["spade", "spades", "card suit", "poker", "black spade"],
    0x2663: ["club", "clubs", "clover", "card suit", "poker"],
    0x2666: ["diamond suit", "diamonds", "card suit", "poker", "red diamond"],
    0x2667: ["white club", "club outline", "card suit"],
    0x2664: ["white spade", "spade outline", "card suit"],
    0x2662: ["white diamond suit", "diamond outline", "card suit"],
    0x2648: ["aries", "zodiac", "ram"],
    0x2649: ["taurus", "zodiac", "bull"],
    0x264A: ["gemini", "zodiac", "twins"],
    0x264B: ["cancer", "zodiac", "crab"],
    0x264C: ["leo", "zodiac", "lion"],
    0x264D: ["virgo", "zodiac", "maiden"],
    0x264E: ["libra", "zodiac", "scales"],
    0x264F: ["scorpio", "zodiac", "scorpion"],
    0x2650: ["sagittarius", "zodiac", "archer"],
    0x2651: ["capricorn", "zodiac", "goat"],
    0x2652: ["aquarius", "zodiac", "water bearer"],
    0x2653: ["pisces", "zodiac", "fish"],
    0x0391: ["alpha", "greek", "greek letter"],
    0x0392: ["beta", "greek", "greek letter"],
    0x0393: ["gamma", "greek", "greek letter"],
    0x0394: ["delta", "greek", "change", "difference", "increment"],
    0x0398: ["theta", "greek", "angle"],
    0x039B: ["lambda", "greek", "wavelength"],
    0x039C: ["mu", "greek", "micro", "mean"],
    0x03A0: ["pi", "greek", "product", "circle constant"],
    0x03A3: ["sigma", "greek", "sum", "standard deviation"],
    0x03A6: ["phi", "greek", "golden ratio"],
    0x03A9: ["omega", "greek", "ohm", "resistance"],
    0x03B1: ["alpha", "greek lower case", "angle", "significance"],
    0x03B2: ["beta", "greek lower case", "beta coefficient"],
    0x03B3: ["gamma", "greek lower case", "gamma radiation"],
    0x03B5: ["epsilon", "greek lower case", "small quantity"],
    0x03BB: ["lambda", "greek lower case", "wavelength", "eigenvalue"],
    0x03BC: ["mu sign", "micro sign", "micrometer", "micron", "greek mu"],
    0x03C0: ["pi lower case", "pi symbol", "circle constant", "3.14159"],
    0x03C3: ["sigma lower case", "standard deviation"],
    0x03C6: ["phi lower case", "golden ratio"],
    0x03C9: ["omega lower case", "angular frequency", "ohm"],
    0x00E9: ["e acute", "accent e", "french e", "e with accent", "resume", "cafe"],
    0x00E8: ["e grave", "accent grave", "french e"],
    0x00EA: ["e circumflex", "french e", "accent circonflexe"],
    0x00EB: ["e diaeresis", "e umlaut", "french e"],
    0x00E0: ["a grave", "french a", "accent grave"],
    0x00E7: ["c cedilla", "french c", "cedilla", "c with tail"],
    0x00F1: ["n tilde", "spanish n", "enye", "n with tilde"],
    0x00FC: ["u umlaut", "german u", "u with umlaut"],
    0x00E4: ["a umlaut", "german a", "a with umlaut"],
    0x00F6: ["o umlaut", "german o", "o with umlaut"],
    0x00DF: ["eszett", "sharp s", "german s", "double s", "ss"],
    0x00C4: ["a umlaut capital", "german a upper"],
    0x00D6: ["o umlaut capital", "german o upper"],
    0x00DC: ["u umlaut capital", "german u upper"],
    0x00E9: ["e acute", "french e", "spanish e", "accent aigu"],
    0x00ED: ["i acute", "spanish i", "accent aigu"],
    0x00F3: ["o acute", "spanish o"],
    0x00FA: ["u acute", "spanish u"],
    0x00E1: ["a acute", "spanish a", "portuguese a"],
    0x1F600: ["grinning face", "smiley", "happy", "emoji", "smile"],
    0x1F602: ["face with tears of joy", "laughing", "lol", "emoji", "crying laughing"],
    0x1F60D: ["smiling face with heart eyes", "love", "emoji"],
    0x1F614: ["pensive face", "sad", "emoji"],
    0x1F622: ["crying face", "sad", "tears", "emoji"],
    0x1F621: ["enraged face", "angry", "mad", "emoji"],
    0x1F44D: ["thumbs up", "like", "approve", "ok", "emoji"],
    0x1F44E: ["thumbs down", "dislike", "disapprove", "emoji"],
    0x1F44F: ["clapping hands", "applause", "clap", "emoji"],
    0x1F64F: ["folded hands", "pray", "please", "thank you", "emoji"],
    0x270A: ["raised fist", "fist", "emoji"],
    0x270B: ["raised hand", "hand", "stop", "high five", "emoji"],
    0x270C: ["victory hand", "peace", "peace sign", "emoji"],
    0x1F596: ["vulcan salute", "spock", "live long and prosper", "emoji"],
    0x2318: ["command", "cmd", "apple command", "mac"],
    0x2325: ["option key", "alt key", "mac alt"],
    0x21E7: ["shift key", "shift symbol", "upward arrow with tip"],
    0x2303: ["control key", "ctrl", "caret key"],
    0x238B: ["escape key", "esc"],
    0x23CE: ["return key", "enter key", "carriage return"],
    0x2423: ["space symbol", "visible space", "blank"],
    0x26A1: ["zap", "lightning bolt", "high voltage", "power", "electricity", "thunder"],
    0x2712: ["black nib", "pen", "nib", "signature"],
    0x270E: ["lower right pencil", "pencil", "edit", "write"],
    0x270F: ["pencil", "edit", "write", "note"],
    0x2699: ["gear", "settings", "configuration", "cog", "preferences"],
    0x2691: ["black flag", "flag", "milestone"],
    0x26F3: ["flag in hole", "golf", "golf flag"],
    0x267B: ["recycling symbol", "recycle", "reuse", "environment"],
    0x265F: ["black chess pawn", "pawn", "chess"],
    0x1F512: ["locked", "lock", "padlock", "secure", "privacy"],
    0x1F513: ["unlocked", "open lock", "padlock open", "insecure"],
    0x2764: ["red heart", "love heart", "heart emoji", "valentine", "love"],
}

# cp -> (macOS Option shortcut, note). Only entries that are short and well documented.
MAC_OPTION = {
    0x00B0: ("⌥⇧8", "Degree sign"),
    0x00A9: ("⌥G", "Copyright"),
    0x00AE: ("⌥R", "Registered"),
    0x2122: ("⌥2", "Trademark"),
    0x2022: ("⌥8", "Bullet"),
    0x00F7: ("⌥/", "Divide"),
    0x2260: ("⌥=", "Not equal"),
    0x00B1: ("⌥⇧=", "Plus minus"),
    0x2264: ("⌥,", "Less than or equal"),
    0x2265: ("⌥.", "Greater than or equal"),
    0x2211: ("⌥W", "Summation"),
    0x221A: ("⌥V", "Square root"),
    0x03C0: ("⌥P", "Pi"),
    0x2202: ("⌥D", "Partial differential"),
    0x0192: ("⌥F", "Function / florin"),
    0x03A9: ("⌥Z", "Omega"),
    0x00E5: ("⌥A", "Angstrom / a with ring"),
    0x00A0: ("⌥Space", "Non-breaking space"),
    0x2013: ("⌥-", "En dash"),
    0x2014: ("⌥⇧-", "Em dash"),
    0x2018: ("⌥]", "Left single quote"),
    0x2019: ("⌥⇧]", "Right single quote"),
    0x201C: ("⌥[", "Left double quote"),
    0x201D: ("⌥⇧]", "Right double quote"),
    0x201E: ("⌥⇧W", "Double low quote"),
    0x2026: ("⌥;", "Ellipsis"),
    0x00AB: ("⌥\\", "Left guillemet"),
    0x00BB: ("⌥⇧\\", "Right guillemet"),
    0x00A1: ("⌥1", "Inverted exclamation"),
    0x00BF: ("⌥⇧/", "Inverted question mark"),
    0x00AC: ("⌥L", "Not sign"),
    0x00B4: ("⌥⇧E", "Acute accent"),
    0x00A8: ("⌥U", "Diaeresis / umlaut accent"),
    0x02C6: ("⌥I", "Circumflex accent"),
    0x02DC: ("⌥N", "Small tilde accent"),
    0x00AF: ("⌥⇧-", "Macron"),
    0x00F8: ("⌥O", "O with stroke"),
    0x00E6: ("⌥'", "AE ligature"),
    0x00DF: ("⌥S", "Sharp s / Eszett"),
    0x2020: ("⌥T", "Dagger"),
    0x2030: ("⌥⇧R", "Per mille"),
    0x20AC: ("⌥⇧2", "Euro"),
    0x00A3: ("⌥3", "Pound sterling"),
    0x00A5: ("⌥Y", "Yen"),
    0x00A2: ("⌥4", "Cent"),
    0x0192: ("⌥F", "Florin"),
    0x2044: ("⌥⇧1", "Fraction slash"),
    0x2039: ("⌥⇧3", "Left single angle quote"),
    0x203A: ("⌥⇧4", "Right single angle quote"),
    0xFB01: ("⌥5", "fi ligature"),
    0xFB02: ("⌥6", "fl ligature"),
    0x00A7: ("⌥6", "Section sign"),
    0x00B6: ("⌥7", "Pilcrow"),
    0x2022: ("⌥8", "Bullet"),
    0x00AA: ("⌥9", "Feminine ordinal"),
    0x00BA: ("⌥0", "Masculine ordinal"),
    0x00E7: ("⌥C", "C cedilla"),
    0x00A4: ("⌥⇧2", "Currency sign"),
    0x2610: ("", ""),
}

# cp -> LaTeX command (math mode unless noted).
LATEX = {
    0x00B0: ("^\\circ", "math"), 0x00B1: ("\\pm", "math"), 0x00D7: ("\\times", "math"),
    0x00F7: ("\\div", "math"), 0x2212: ("-", "math"), 0x2248: ("\\approx", "math"),
    0x2260: ("\\neq", "math"), 0x2264: ("\\leq", "math"), 0x2265: ("\\geq", "math"),
    0x221E: ("\\infty", "math"), 0x221A: ("\\sqrt{}", "math"), 0x2211: ("\\sum", "math"),
    0x220F: ("\\prod", "math"), 0x222B: ("\\int", "math"), 0x2202: ("\\partial", "math"),
    0x2207: ("\\nabla", "math"), 0x2205: ("\\emptyset", "math"), 0x2208: ("\\in", "math"),
    0x2209: ("\\notin", "math"), 0x2229: ("\\cap", "math"), 0x222A: ("\\cup", "math"),
    0x2282: ("\\subset", "math"), 0x2283: ("\\supset", "math"), 0x2286: ("\\subseteq", "math"),
    0x2287: ("\\supseteq", "math"), 0x2261: ("\\equiv", "math"), 0x223C: ("\\sim", "math"),
    0x2245: ("\\cong", "math"), 0x2192: ("\\rightarrow", "math"), 0x2190: ("\\leftarrow", "math"),
    0x2194: ("\\leftrightarrow", "math"), 0x21D2: ("\\Rightarrow", "math"),
    0x21D4: ("\\Leftrightarrow", "math"), 0x22A5: ("\\perp", "math"), 0x2225: ("\\parallel", "math"),
    0x2220: ("\\angle", "math"), 0x2234: ("\\therefore", "math"), 0x2235: ("\\because", "math"),
    0x2200: ("\\forall", "math"), 0x2203: ("\\exists", "math"), 0x220B: ("\\ni", "math"),
    0x2295: ("\\oplus", "math"), 0x2297: ("\\otimes", "math"), 0x22C5: ("\\cdot", "math"),
    0x2026: ("\\ldots", "text"), 0x2014: ("---", "text"), 0x2013: ("--", "text"),
    0x2018: ("`", "text"), 0x2019: ("'", "text"), 0x201C: ("``", "text"), 0x201D: ("''", "text"),
    0x00A9: ("\\textcopyright", "text"), 0x00AE: ("\\textregistered", "text"),
    0x2122: ("\\texttrademark", "text"), 0x00A7: ("\\S", "text"), 0x00B6: ("\\P", "text"),
    0x2020: ("\\dag", "text"), 0x2021: ("\\ddag", "text"), 0x00A3: ("\\pounds", "text"),
    0x20AC: ("\\euro", "text"), 0x00A5: ("\\textyen", "text"),
    0x2605: ("\\bigstar", "math"), 0x2606: ("\\star", "math"),
    0x2713: ("\\checkmark", "math"), 0x2717: ("\\times", "math"),
    0x03B1: ("\\alpha", "math"), 0x03B2: ("\\beta", "math"), 0x03B3: ("\\gamma", "math"),
    0x03B4: ("\\delta", "math"), 0x03B5: ("\\epsilon", "math"), 0x03B8: ("\\theta", "math"),
    0x03BB: ("\\lambda", "math"), 0x03BC: ("\\mu", "math"), 0x03C0: ("\\pi", "math"),
    0x03C3: ("\\sigma", "math"), 0x03C6: ("\\phi", "math"), 0x03C9: ("\\omega", "math"),
    0x0391: ("A", "math"), 0x0394: ("\\Delta", "math"), 0x03A3: ("\\Sigma", "math"),
    0x03A9: ("\\Omega", "math"), 0x03A6: ("\\Phi", "math"), 0x0398: ("\\Theta", "math"),
    0x00B2: ("^2", "math"), 0x00B3: ("^3", "math"), 0x00B9: ("^1", "math"),
    0x00BC: ("\\frac{1}{4}", "math"), 0x00BD: ("\\frac{1}{2}", "math"),
    0x00BE: ("\\frac{3}{4}", "math"), 0x2153: ("\\frac{1}{3}", "math"),
    0x2154: ("\\frac{2}{3}", "math"),
}


# --------------------------------------------------------------------------
# 4. Assemble the record for each symbol
# --------------------------------------------------------------------------

def html_entity(ch):
    """Named entity if the HTML5 spec defines one, else decimal + hex numeric."""
    cp = ord(ch)
    named = html.entities.codepoint2name.get(cp)
    return {
        "named": f"&{named};" if named else None,
        "decimal": f"&#{cp};",
        "hex": f"&#x{cp:X};",
    }


def escape_forms(cp):
    css = f"\\{cp:04X}" if cp <= 0xFFFF else f"\\{cp:06X}"
    cpp = f"\\u{cp:04X}" if cp <= 0xFFFF else f"\\U{cp:08X}"
    js = f"\\u{cp:04X}" if cp <= 0xFFFF else f"\\u{{{cp:X}}}"
    return css, cpp, js


def build():
    uni = unicode_entries()
    symbols = []

    # Control codes carry an OEM picture glyph: the Alt code belongs to the
    # picture the console font draws, not to the invisible control character.
    oem_pictures = {}
    for code, target in OEM_CONTROL_PICTURES.items():
        oem_pictures.setdefault(target, []).append(str(code))

    for cp, info in uni.items():
        ch = info["glyph"]
        css, cpp, js = escape_forms(cp)
        aliases = ALIASES.get(cp, [])
        legacy = list(LEGACY.get(cp, []))
        for code in oem_pictures.get(cp, []):
            if code not in legacy:
                legacy.append(code)
        legacy.sort(key=lambda c: (len(c), c))
        mac, mac_note = MAC_OPTION.get(cp, ("", ""))
        latex, latex_mode = LATEX.get(cp, ("", ""))
        is_oem_picture = cp in oem_pictures

        symbols.append({
            "id": f"u{cp:04X}",
            "glyph": ch,
            "name": info["name"],
            "unicode_name": info["unicode_name"],
            "codepoint": cp,
            "unicode": f"U+{cp:04X}",
            "entity": html_entity(ch),
            "css": css,
            "python": cpp,
            "js": js,
            "utf8": " ".join(f"{b:02X}" for b in ch.encode("utf-8")),
            "block": info["block"],
            "category": info["category"],
            "groups": info["groups"],
            "aliases": aliases,
            "alt_legacy": legacy,
            "alt_decimal": str(cp) if cp <= 0xFFFF else "",
            "alt_hex": f"{cp:X}",
            "oem_picture": is_oem_picture,
            "mac_option": mac,
            "mac_note": mac_note,
            "latex": latex,
            "latex_mode": latex_mode,
            # Popularity drives ordering on hub pages. Curated aliases are the
            # best available proxy for demand without inventing search volumes.
            "weight": len(aliases) * 10 + (30 if legacy else 0) + (15 if mac else 0),
        })

    # Attach the legacy-only glyphs that Unicode groups did not already cover.
    covered = {s["codepoint"] for s in symbols}
    for cp, codes in LEGACY.items():
        if cp in covered:
            continue
        ch = chr(cp)
        cat = unicodedata.category(ch)
        if cat in SKIP_CATEGORIES:
            continue
        try:
            raw = unicodedata.name(ch)
        except ValueError:
            raw = f"Character {cp}"
        css, cpp, js = escape_forms(cp)
        symbols.append({
            "id": f"u{cp:04X}", "glyph": ch, "name": title_case_unicode_name(raw),
            "unicode_name": raw, "codepoint": cp, "unicode": f"U+{cp:04X}",
            "entity": html_entity(ch), "css": css, "python": cpp, "js": js,
            "utf8": " ".join(f"{b:02X}" for b in ch.encode("utf-8")),
            "block": block_name(cp), "category": cat, "groups": [],
            "aliases": ALIASES.get(cp, []), "alt_legacy": codes,
            "alt_decimal": str(cp) if cp <= 0xFFFF else "", "alt_hex": f"{cp:X}",
            "oem_picture": cp in oem_pictures,
            "mac_option": MAC_OPTION.get(cp, ("", ""))[0],
            "mac_note": MAC_OPTION.get(cp, ("", ""))[1],
            "latex": LATEX.get(cp, ("", ""))[0],
            "latex_mode": LATEX.get(cp, ("", ""))[1],
            "weight": len(ALIASES.get(cp, [])) * 10 + 30,
        })

    symbols.sort(key=lambda s: (-s["weight"], s["codepoint"]))

    groups = []
    by_cp = {s["codepoint"]: s for s in symbols}
    for slug, name, tagline, intent, members in GROUPS:
        present = [by_cp[c] for c in members if c in by_cp]
        if not present:
            continue
        present.sort(key=lambda s: (-s["weight"], s["codepoint"]))
        groups.append({
            "slug": slug, "name": name, "tagline": tagline, "intent": intent,
            "count": len(present), "symbols": [s["id"] for s in present],
        })

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "symbols.json"), "w", encoding="utf-8") as f:
        json.dump(symbols, f, ensure_ascii=False, separators=(",", ":"))
    with open(os.path.join(DATA, "groups.json"), "w", encoding="utf-8") as f:
        json.dump(groups, f, ensure_ascii=False, indent=1)

    # ---- report ----
    print(f"symbols: {len(symbols)}")
    print(f"groups:  {len(groups)}")
    print(f"with legacy alt code: {sum(1 for s in symbols if s['alt_legacy'])}")
    print(f"with aliases:         {sum(1 for s in symbols if s['aliases'])}")
    print(f"with mac shortcut:    {sum(1 for s in symbols if s['mac_option'])}")
    print(f"with latex:           {sum(1 for s in symbols if s['latex'])}")
    print(f"with named entity:    {sum(1 for s in symbols if s['entity']['named'])}")
    print("\ngroup counts:")
    for g in groups:
        print(f"  {g['slug']:<24} {g['count']:>5}  {g['name']}")


if __name__ == "__main__":
    build()
