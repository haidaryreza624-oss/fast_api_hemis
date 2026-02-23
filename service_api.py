from fastapi import FastAPI
from pydantic import BaseModel
from login import check_login, login_first, PROFILE_URL  # import your functions
from profile import parse_student_profile  # import your profile parser
from logout import logout  # import your logout function
from final_score import get_final_scores_page  # import your final scores function
from scores import get_scores_page  # import your scores function
session = [None]
app = FastAPI()


class LoginRequest(BaseModel):
    email: str
    password: str
    remember_me: bool = False


@app.get("/check")
def check():
    """Check saved session and load profile"""
    html, session[0], error = check_login()
    if html!=None:
        return {"profile": parse_student_profile(html), "error": error}
    return {"profile":html, "error": error}
# return profile:none in failer
# return profile:[clean data] in success



@app.post("/login")
def login_endpoint(data: LoginRequest):
    """Login with email and password"""
    html, session[0], error = login_first(
        email=data.email,
        password=data.password,
        remember_me_input="y" if data.remember_me else "n"
    )
    if html!=None:
        return {"profile": parse_student_profile(html), "error": error}
    return {"profile":html, "error": error}
# return profile:none session:none in failer
# return profile:[clean data] session:[session object] in success
# does not handle missing fields in request body



@app.post("/logout")
def logout_endpoint():
    """
    Calls logout function from logout_script.py
    """
    try:
        message = logout()  # call your logout logic
        return {"success": True, "message": message}
    except Exception as e:
        return {"success": False, "message": f"❌ Logout failed: {e}"}
# return success:true in success
# return success:false in failure


@app.get("/final-scores")
def final_scores():
    """
    Uses the session saved in SESSION[0] to get final scores.
    """
    
    if session[0] == None:
        return {"success": False, "message": "❌ No active session. Please login first."}
    
    try:
        data, error = get_final_scores_page(session[0])
        if error:
            return {"success": False, "message": error}
        return {"success": True, "final_scores": data}
    except Exception as e:
        return {"success": False, "message": f"❌ Failed to get final scores: {e}"}
    

@app.get("/scores")
def scores():
    """
    Uses the session stored in SESSION[0] to fetch scores page.
    """
   
    if session[0] == None:
        return {"success": False, "message": "❌ No active session. Please login first."}

    try:
        data, error = get_scores_page(session[0])
        if error:
            return {"success": False, "message": error}
        return {"success": True, "scores": data}
    except Exception as e:
        return {"success": False, "message": f"❌ Failed to get scores: {e}"}