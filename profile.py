from bs4 import BeautifulSoup

def parse_student_profile(html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    data = {}

    # --- Profile image ---
    profile_pic_div = soup.select_one(".profile-userpic img")
    if profile_pic_div and profile_pic_div.has_attr("src"):
        data["profile_image"] = profile_pic_div["src"]

    # --- Sidebar info ---
    sidebar = soup.select_one(".profile-usertitle")
    if sidebar:
        rows = sidebar.find_all("div")
        if len(rows) >= 4:
            data["name"] = rows[0].get_text(strip=True)
            data["student_id"] = rows[1].get_text(strip=True)
            data["department"] = rows[2].get_text(strip=True)
            data["university"] = rows[3].get_text(strip=True)

    # --- Main profile fields ---
    for group in soup.select(".form-group"):
        label = group.find("label")
        if not label:
            continue

        key = label.get_text(strip=True)

        # value may be inside div or p
        value_div = group.find_all("div")[-1] if group.find_all("div") else None
        value = value_div.get_text(" ", strip=True) if value_div else None

        if value:
            data[key] = value

    return data