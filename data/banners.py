"""Banner schedule (days 1-403 of the community banner list).

Source: the "Bleach Mobile 3D banner list" made by Hermes with help from the Bleach Discord
(bm3d.info). Every banner runs exactly 4 days; the pattern is Rate-Up (4 days), Limited
(4 days), then 3 days without a banner.

Each entry is (first_day, last_day, type, name), both days inclusive.
Days that are not listed have no active banner.
Edit SCHEDULE (and BANNER_LAST_DAY in config.py) when the list is extended or corrected;
BANNERS is built from it.
"""

SCHEDULE: list[tuple[int, int, str, str]] = [
    (4, 7, "Limited", "Ulquiorra"),
    (11, 14, "Rate-Up", "Toshiro & Byakuya"),
    (15, 18, "Limited", "Arrancar Aizen"),
    (22, 25, "Rate-Up", "White Ichigo & Isshin"),
    (26, 29, "Limited", "Trained Ichigo"),
    (33, 36, "Rate-Up", "Nel Tu & Soi Fon"),
    (37, 40, "Limited", "Adult Nel"),
    (44, 47, "Rate-Up", "Grimmjow & Tosen"),
    (48, 51, "Limited", "Shinji"),
    (55, 58, "Rate-Up", "Unohana & Mayuri"),
    (59, 62, "Limited", "Toshiro (RF)"),
    (66, 69, "Rate-Up", "Aizen Sosuke & Gin"),
    (70, 73, "Limited", "Ulquiorra (RF)"),
    (77, 80, "Rate-Up", "Kenpachi & Komamura"),
    (81, 84, "Limited", "Glorious Byakuya"),
    (88, 91, "Rate-Up", "Grimmjow & Tosen"),
    (92, 95, "Limited", "Grimmjow (RF)"),
    (99, 102, "Rate-Up", "White Ichigo & Isshin"),
    (103, 106, "Limited", "Barragan"),
    (110, 113, "Rate-Up", "Nel Tu & Soi Fon"),
    (114, 117, "Limited", "Swimsuit Unohana"),
    (121, 124, "Rate-Up", "Grimmjow & Tosen"),
    (125, 128, "Limited", "Nnoitra"),
    (132, 135, "Rate-Up", "Unohana & Mayuri"),
    (136, 139, "Limited", "Kuukaku"),
    (143, 146, "Rate-Up", "Aizen Sosuke & Gin"),
    (147, 150, "Limited", "Captain Urahara"),
    (154, 157, "Rate-Up", "Kenpachi & Komamura"),
    (158, 161, "Limited", "Halibel"),
    (165, 168, "Rate-Up", "Grimmjow & Tosen"),
    (169, 172, "Limited", "Yoruichi (Armored)"),
    (176, 179, "Rate-Up", "White Ichigo & Isshin"),
    (180, 183, "Limited", "Arrancar Gin"),
    (187, 190, "Rate-Up", "Nel Tu & Soi Fon"),
    (191, 194, "Limited", "Yammy"),
    (198, 201, "Rate-Up", "Unohana & Mayuri"),
    (202, 205, "Limited", "Ulquiorra"),
    (209, 212, "Rate-Up", "Aizen Sosuke & Gin"),
    (213, 216, "Limited", "Arrancar Aizen"),
    (220, 223, "Rate-Up", "Kenpachi & Komamura"),
    (224, 227, "Limited", "Trained Ichigo"),
    (231, 234, "Rate-Up", "Grimmjow & Tosen"),
    (235, 238, "Limited", "Adult Nel"),
    (242, 245, "Rate-Up", "White Ichigo & Isshin"),
    (246, 249, "Limited", "Shinji"),
    (253, 256, "Rate-Up", "Nel Tu & Soi Fon"),
    (257, 260, "Limited", "Toshiro (RF)"),
    (264, 267, "Rate-Up", "Grimmjow & Tosen"),
    (268, 271, "Limited", "Ulquiorra (RF)"),
    (275, 278, "Rate-Up", "Unohana & Mayuri"),
    (279, 282, "Limited", "Glorious Byakuya"),
    (286, 289, "Rate-Up", "Aizen Sosuke & Gin"),
    (290, 293, "Limited", "Grimmjow (RF)"),
    (297, 300, "Rate-Up", "Kenpachi & Komamura"),
    (301, 304, "Limited", "Barragan"),
    (308, 311, "Rate-Up", "Grimmjow & Tosen"),
    (312, 315, "Limited", "Swimsuit Unohana"),
    (319, 322, "Rate-Up", "White Ichigo & Isshin"),
    (323, 326, "Limited", "Nnoitra"),
    (330, 333, "Rate-Up", "Nel Tu & Soi Fon"),
    (334, 337, "Limited", "Kuukaku"),
    (341, 344, "Rate-Up", "Grimmjow & Tosen"),
    (345, 348, "Limited", "Captain Urahara"),
    (352, 355, "Rate-Up", "Unohana & Mayuri"),
    (356, 359, "Limited", "Halibel"),
    (363, 366, "Rate-Up", "Aizen Sosuke & Gin"),
    (367, 370, "Limited", "Yoruichi (Armored)"),
    (374, 377, "Rate-Up", "Kenpachi & Komamura"),
    (378, 381, "Limited", "Arrancar Gin"),
    (385, 388, "Rate-Up", "Grimmjow & Tosen"),
    (389, 392, "Limited", "Yammy"),
    (396, 399, "Rate-Up", "Unohana & Mayuri"),
    (400, 403, "Limited", "Ulquiorra"),
]


def _expand(schedule):
    banners = {}
    for first, last, kind, name in schedule:
        for day in range(first, last + 1):
            banners[day] = {"type": kind, "name": name}
    return banners


BANNERS: dict[int, dict[str, str]] = _expand(SCHEDULE)
