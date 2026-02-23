import requests
from bs4 import BeautifulSoup
import os
import pickle


from logout import logout
from profile import parse_student_profile
from scores import get_scores_page
from final_score import get_final_scores_page

LOGIN_PAGE = "https://hemis.edu.af/login"
LOGIN_POST = "https://hemis.edu.af/student/login"
PROFILE_URL = "https://hemis.edu.af/student/profile"
SESSION_FILE = "hemis_session.pkl"

def save_session(session: requests.Session):
    with open(SESSION_FILE, "wb") as f:
        pickle.dump(session.cookies, f)

def load_session() -> requests.Session | None:
    if not os.path.exists(SESSION_FILE):
        return None
    session = requests.Session()
    with open(SESSION_FILE, "rb") as f:
        cookies = pickle.load(f)
        session.cookies.update(cookies)
    return session

def is_logged_in(session: requests.Session) -> bool:
    try:
        resp = session.get(PROFILE_URL, timeout=20)
        return resp.status_code == 200 and "login" not in resp.url.lower()
    except requests.RequestException:
        return False

def login_first(email: str, password: str, remember_me_input: str) -> tuple[str | None, requests.Session | None, str | None]:
    """Perform login with optional 'remember me'."""
    remember_me = remember_me_input.strip().lower() in ("y", "yes")
    session = requests.Session()

    # 1️⃣ Get login page
    try:
        r = session.get(LOGIN_PAGE, timeout=30)
        r.raise_for_status()
    except requests.RequestException as e:
        return None, None, f"❌ Failed to load login page: {e}"

    soup = BeautifulSoup(r.text, "html.parser")
    token_tag = soup.find("input", {"name": "_token"})
    if not token_tag:
        return None, None, "❌ CSRF token not found"
    token = token_tag["value"]

    # 2️⃣ Post login
    payload = {
        "_token": token,
        "form": "login",
        "guard": "student",
        "email": email,
        "password": password
    }

    try:
        login_resp = session.post(LOGIN_POST, data=payload, allow_redirects=True, timeout=30)
        login_resp.raise_for_status()
    except requests.RequestException as e:
        return None, None, f"❌ Login request failed: {e}"

    if "login" in login_resp.url.lower():
        return None, None, "❌ Login failed (wrong credentials or time restriction)"

    # 3️⃣ Fetch profile page
    try:
        profile_resp = session.get(PROFILE_URL, timeout=30)
        profile_resp.raise_for_status()
    except requests.RequestException as e:
        return None, session, f"❌ Failed to load profile page: {e}"

    # 4️⃣ Save session if user chose remember me
    if remember_me:
        save_session(session)
        print("💾 Session saved for future runs")

    return profile_resp.text, session, None



def check_login():
    session = load_session()
    if session and is_logged_in(session):
        print("✅ Using saved session")
        try:
            profile_resp = session.get(PROFILE_URL, timeout=20)
            profile_resp.raise_for_status()
            return profile_resp.text, session, None
        except requests.RequestException as e:
            return None, None, f"❌ Failed to load profile: {e}"
    # Always return a tuple even if session is invalid
    return None, None, "❌ No valid session found"
#   /check
#   call chekc_login()
#   if there is a vlid session and it can load the profile page
#   get
#   no body in request
#   response: 
#       sucess - profile session None
#       fail - None None "message"

#   /login
#  call login()
#   post:
#   body: email, password, remember_me
#   response: 
#       sucess - profile session None
#       fail - None None "message"

def login(email: str = None, password: str = None) -> tuple[str | None, requests.Session | None, str | None]:
    if not email:
        email = input("📧 Enter email: ").strip()
    if not password:
        password = input("🔑 Enter password: ").strip()
    remember_me_input = input("💾 Remember me? (y/n): ").strip()

    html, session, error = login_first(email=email, password=password, remember_me_input=remember_me_input)
    return html, session, error



# html, session, error = login()
