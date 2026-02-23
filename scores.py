from bs4 import BeautifulSoup

SCORES_URL = "https://hemis.edu.af/student/scores-list"

# Helper functions for safe conversion
def safe_float(s, default=0.0):
    try:
        s = s.strip().replace(",", ".")  # handle comma decimal
        return float(s) if s else default
    except (ValueError, AttributeError):
        return default

def safe_int(s, default=0):
    try:
        s = s.strip()
        return int(s) if s else default
    except (ValueError, AttributeError):
        return default

def get_scores_page(session):
    resp = session.get(SCORES_URL, timeout=30)

    if resp.status_code != 200:
        return None, "❌ Failed to load scores page"

    if "login" in resp.url.lower():
        return None, "❌ Session expired"

    soup = BeautifulSoup(resp.text, "html.parser")
    data = {}

    tables = soup.select("table.table")

    for table in tables:
        # Semester row
        semester_row = table.select_one("tr.group-by")
        if not semester_row:
            continue

        semester_text = semester_row.get_text(strip=True)
        semester_number = semester_text.split(":")[-1].strip()
        semester_key = f"semester_{semester_number}"

        data[semester_key] = []

        rows = table.select("tr")[2:]  # skip group-by + header

        for row in rows:
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if len(cols) < 14:
                continue

            subject = {
                "subject": cols[1],
                "credit": safe_float(cols[2]),
                "attendance": {
                    "present": safe_int(cols[3]),
                    "absent": safe_int(cols[4])
                },
                "scores": {
                    "homework": safe_float(cols[5]),
                    "activity": safe_float(cols[6]),
                    "midterm": safe_float(cols[7]),
                    "final": safe_float(cols[8]),
                    "total": safe_float(cols[9])
                },
                "status": cols[13],
                "final_approval": cols[14] if len(cols) > 14 else None
            }

            data[semester_key].append(subject)

    return data, None