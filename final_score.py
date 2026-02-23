from bs4 import BeautifulSoup

FINAL_SCORES_URL = "https://hemis.edu.af/student/final-scores-list"


def clean(val):
    val = val.strip()
    return val if val else None


def get_final_scores_page(session):
    resp = session.get(FINAL_SCORES_URL, timeout=30)

    if resp.status_code != 200:
        return None, "❌ Failed to load final scores page"

    if "login" in resp.url.lower():
        return None, "❌ Session expired"

    soup = BeautifulSoup(resp.text, "html.parser")
    data = {}

    for sem in soup.select("div.semester-scores"):

        # ---- semester number ----
        header = sem.select_one("tr.group-by td")
        if not header:
            continue

        semester_no = header.get_text(strip=True).split(":")[-1].strip()
        semester_key = f"semester_{semester_no}"

        data[semester_key] = {
            "courses": [],
            "summary": None
        }

        # ---- courses table ----
        course_table = sem.select_one("table.stripe")
        if course_table:
            rows = course_table.select("tr")[2:]  # skip group-by + header

            for row in rows:
                cols = [clean(td.get_text()) for td in row.find_all("td")]
                if len(cols) != 11:
                    continue

                data[semester_key]["courses"].append({
                    "index": int(cols[0]),
                    "subject": cols[1],
                    "academic_year": cols[2],
                    "chance_1": cols[3],
                    "chance_2": cols[4],
                    "chance_3": cols[5],
                    "chance_4": cols[6],
                    "credit": float(cols[7]),
                    "passing_score": float(cols[8]),
                    "passing_chance": int(cols[9]),
                    "weighted_score": float(cols[10])
                })

        # ---- semester summary ----
        summary_row = sem.select_one("table.results tr.passed-semester")
        if summary_row:
            cols = [clean(td.get_text()) for td in summary_row.find_all("td")]

            if len(cols) == 8:
                data[semester_key]["summary"] = {
                    "academic_year": cols[0],
                    "semester": cols[1],
                    "average": float(cols[2]),
                    "grade": cols[3],
                    "passed": cols[4],
                    "promoted": cols[5],
                    "total_credits": float(cols[6]),
                    "passed_credits": float(cols[7])
                }

    return data, None