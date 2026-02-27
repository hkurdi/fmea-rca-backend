from app.services.auth_service import register_user, login_user, refresh_access_token, forgot_password, reset_password
from app.services.email_service import send_password_reset_email
from app.services.redis_service import set_reset_token, get_reset_token, delete_reset_token, get_leaderboard, increment_leaderboard_score
from app.services.scoring_service import submit_process_map, submit_hazard_analysis, submit_fishbone, submit_five_whys, submit_fmea_pip, submit_rca_pip, instructor_approve
from app.services.gamification_service import award_points, award_badge, check_and_award_badges, get_course_leaderboard