from bs4 import BeautifulSoup

SCORES_URL = "https://hemis.edu.af/student/scores-list"

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
                "credit": float(cols[2]),
                "attendance": {
                    "present": int(cols[3]),
                    "absent": int(cols[4])
                },
                "scores": {
                    "homework": float(cols[5]),
                    "activity": float(cols[6]),
                    "midterm": float(cols[7]),
                    "final": float(cols[8]),
                    "total": float(cols[9])
                },
                "status": cols[13],
                "final_approval": cols[14] if len(cols) > 14 else None
            }

            data[semester_key].append(subject)

    return data, None