import os
import requests

SESSION_FILE = "hemis_session.pkl"
LOGOUT_URL = "https://hemis.edu.af/student/logout"

def logout(session: requests.Session | None = None):
    """Logs out from HEMIS and deletes saved session cookies."""
    # 1️⃣ Try server-side logout
    if session:
        try:
            # HEMIS logout may require POST with CSRF token
            resp = session.get(LOGOUT_URL, timeout=20)
            if resp.status_code == 200:
                print("✅ Logged out from server")
            else:
                print(f"⚠️ Server logout returned status: {resp.status_code}")
        except requests.RequestException as e:
            print(f"⚠️ Failed to logout from server: {e}")

    # 2️⃣ Delete local session file
    if os.path.exists(SESSION_FILE):
        os.remove(SESSION_FILE)
        print("💾 Local session removed")
    else:
        print("ℹ️ No local session to remove")

# ------------------------------
# Example usage
# ------------------------------
if __name__ == "__main__":
    import pickle

    # Load session if exists
    session = None
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "rb") as f:
            cookies = pickle.load(f)
            session = requests.Session()
            session.cookies.update(cookies)

    logout(session)