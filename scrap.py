
from profile import parse_student_profile
from scores import get_scores_page
from login import login
from final_score import get_final_scores_page

email = 'haidaryreza624@gmail.com'
password= 'Wanda123@'


html, session,error = login('y',email,password)


if error:
    print(error)
else:
    print("✅ Profile page loaded")
    print(parse_student_profile(html))
    if(input() == "score"):
        print(get_final_scores_page(session=session))
        # print(get_scores_page(session))
    # print(html)  # full profile page HTML


