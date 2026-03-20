#!/bin/bash

BASE_URL="http://localhost:8000"
PASS=0
FAIL=0

GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

check() {
  local label=$1
  local expected=$2
  local actual=$3
  if [ "$actual" == "$expected" ]; then
    echo -e "${GREEN}PASS${NC} — $label"
    ((PASS++))
  else
    echo -e "${RED}FAIL${NC} — $label (expected $expected, got $actual)"
    ((FAIL++))
  fi
}

echo "=============================="
echo " FMEA/RCA Backend API Tests"
echo "=============================="

# 1. Health check
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/health)
check "Health check" "200" "$STATUS"

# 2. Register users (409 is fine on re-runs)
curl -s -o /dev/null -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"instructor@fmea.com","password":"testpass123","full_name":"Test Instructor"}'

curl -s -o /dev/null -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@usf.edu","password":"testpass123","full_name":"Test Student","usf_id":"U99999999"}'

# 3. Promote instructor in DB BEFORE logging in
echo "— Promoting instructor role in DB..."
docker exec fmea_rca_db psql -U fmea_user -d fmea_rca_db -c \
  "UPDATE users SET role='INSTRUCTOR' WHERE email='instructor@fmea.com';" > /dev/null 2>&1
check "Promote instructor role" "0" "$?"

# 4. Login as student
STUDENT_RESP=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@usf.edu","password":"testpass123"}')
STUDENT_TOKEN=$(echo $STUDENT_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
check "Student login" "True" "$(echo $STUDENT_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 5. Login as instructor (AFTER promotion)
INSTRUCTOR_RESP=$(curl -s -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"instructor@fmea.com","password":"testpass123"}')
INSTRUCTOR_TOKEN=$(echo $INSTRUCTOR_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['access_token'])" 2>/dev/null)
check "Instructor login" "True" "$(echo $INSTRUCTOR_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 6. Get current user
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/auth/me \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get current user" "200" "$STATUS"

# Check register (201 first run, 409 on re-runs — both are fine)
REG_STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"newregtest@usf.edu","password":"testpass123","full_name":"Reg Test"}')
if [ "$REG_STATUS" == "201" ] || [ "$REG_STATUS" == "409" ]; then
  echo -e "${GREEN}PASS${NC} — Register new user"
  ((PASS++))
else
  echo -e "${RED}FAIL${NC} — Register new user (expected 201 or 409, got $REG_STATUS)"
  ((FAIL++))
fi

# 7. Duplicate registration rejected
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"student@usf.edu","password":"testpass123","full_name":"Dup"}')
check "Duplicate registration rejected" "409" "$STATUS"

# 8. Wrong password rejected
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"student@usf.edu","password":"wrongpass"}')
check "Wrong password rejected" "401" "$STATUS"

# 9. Unauthenticated request rejected
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/cases/)
check "Unauthenticated request rejected" "403" "$STATUS"

# 10. Create course as student (should fail)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/courses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"name":"Unauthorized Course"}')
check "Create course as student rejected" "403" "$STATUS"

# 11. Create course as instructor
COURSE_RESP=$(curl -s -X POST $BASE_URL/courses/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d '{"name":"PharmD Case Studies","description":"Spring 2026"}')
COURSE_ID=$(echo $COURSE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create course (instructor)" "True" "$(echo $COURSE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 12. Get all courses
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/courses/ \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get all courses" "200" "$STATUS"

# 13. Create case as instructor
CASE_RESP=$(curl -s -X POST $BASE_URL/cases/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d '{"title":"Medication Error Case","description":"Patient received wrong dose","patient_info":{"name":"John Doe","age":65},"mode":"exercise","allow_resubmit":true}')
CASE_ID=$(echo $CASE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create case (instructor)" "True" "$(echo $CASE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 14. Create case as student (should fail)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/cases/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"title":"Unauthorized","description":"x","patient_info":{},"mode":"exercise","allow_resubmit":true}')
check "Create case as student rejected" "403" "$STATUS"

# 15. Get all cases
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/cases/ \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get all cases" "200" "$STATUS"

# 16. Get case by ID
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/cases/$CASE_ID \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get case by ID" "200" "$STATUS"

# 17. Assign case to course
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/cases/$CASE_ID/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d "{\"course_id\":$COURSE_ID}")
check "Assign case to course" "201" "$STATUS"

# 18. Duplicate case assignment rejected
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/cases/$CASE_ID/assign \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d "{\"course_id\":$COURSE_ID}")
check "Duplicate case assignment rejected" "409" "$STATUS"

# 19. Create team
TEAM_RESP=$(curl -s -X POST $BASE_URL/teams/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d "{\"name\":\"Team Alpha\",\"course_id\":$COURSE_ID}")
TEAM_ID=$(echo $TEAM_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create team" "True" "$(echo $TEAM_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 20. Get student ID
STUDENT_ID=$(curl -s $BASE_URL/auth/me \
  -H "Authorization: Bearer $STUDENT_TOKEN" | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)

# 21. Add member to team
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/teams/$TEAM_ID/members \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d "{\"user_id\":$STUDENT_ID}")
check "Add member to team" "201" "$STATUS"

# 22. Duplicate team member rejected
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/teams/$TEAM_ID/members \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d "{\"user_id\":$STUDENT_ID}")
check "Duplicate team member rejected" "409" "$STATUS"

# 23. Create process map
PM_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/fmea/process-map \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"case_id\":$CASE_ID,\"content\":{\"steps\":[\"Order entry\",\"Review\",\"Dispensing\"]}}")
PM_ID=$(echo $PM_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create process map" "True" "$(echo $PM_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 24. Get process map
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/cases/$CASE_ID/fmea/process-map \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get process map" "200" "$STATUS"

# 25. Create hazard analysis
HA_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/fmea/hazard-analysis \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"case_id\":$CASE_ID,\"rows\":{\"hazards\":[{\"step\":\"Order entry\",\"failure\":\"Wrong dose\",\"severity\":9}]}}")
HA_ID=$(echo $HA_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create hazard analysis" "True" "$(echo $HA_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 26. Create FMEA PIP
FMEA_PIP_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/fmea/pip \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"case_id\":$CASE_ID,\"content\":{\"problem\":\"Wrong dose\",\"plan\":\"Double check\",\"resources\":\"Pharmacy\",\"timeline\":\"3 months\",\"measure\":\"Error rate\"}}")
FMEA_PIP_ID=$(echo $FMEA_PIP_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create FMEA PIP" "True" "$(echo $FMEA_PIP_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 27. Create fishbone
FB_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/rca/fishbone \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"case_id\":$CASE_ID,\"problem_statement\":\"Patient received wrong medication dose\"}")
FB_ID=$(echo $FB_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create fishbone" "True" "$(echo $FB_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 28. Get fishbone
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/cases/$CASE_ID/rca/fishbone \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get fishbone" "200" "$STATUS"

# 29. Add fishbone node
NODE_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/rca/fishbone/$FB_ID/nodes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d '{"label":"Communication failure","level":"major","order_index":0}')
NODE_ID=$(echo $NODE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Add fishbone node" "True" "$(echo $NODE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 30. Add child fishbone node
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST $BASE_URL/cases/$CASE_ID/rca/fishbone/$FB_ID/nodes \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"parent_id\":$NODE_ID,\"label\":\"No handoff protocol\",\"level\":\"primary\",\"order_index\":0}")
check "Add child fishbone node" "201" "$STATUS"

# 31. Create 5 whys
FW_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/rca/five-whys \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"case_id\":$CASE_ID,\"problem\":\"Wrong dose given\",\"iterations\":{\"why1\":{\"question\":\"Why wrong dose?\",\"answer\":\"Order unclear\"},\"why2\":{\"question\":\"Why unclear?\",\"answer\":\"No standard\"},\"why3\":{\"question\":\"Why no standard?\",\"answer\":\"Policy gap\"},\"why4\":{\"question\":\"Why policy gap?\",\"answer\":\"No review\"},\"why5\":{\"question\":\"Why no review?\",\"answer\":\"No resources\"}}}")
FW_ID=$(echo $FW_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create 5 whys" "True" "$(echo $FW_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 32. Create RCA PIP
RCA_PIP_RESP=$(curl -s -X POST $BASE_URL/cases/$CASE_ID/rca/pip \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $STUDENT_TOKEN" \
  -d "{\"case_id\":$CASE_ID,\"content\":{\"problem\":\"Unclear orders\",\"plan\":\"Standardize format\",\"resources\":\"IT pharmacy\",\"timeline\":\"6 months\",\"measure\":\"Order clarity rate\"}}")
RCA_PIP_ID=$(echo $RCA_PIP_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Create RCA PIP" "True" "$(echo $RCA_PIP_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 33. Submit process map for scoring
SCORE_RESP=$(curl -s -X POST "$BASE_URL/scoring/submit/process-map/$PM_ID?course_id=$COURSE_ID" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
SCORE_ID=$(echo $SCORE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['data']['id'])" 2>/dev/null)
check "Submit process map for scoring" "True" "$(echo $SCORE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 34. Submit locked submission (should fail)
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/scoring/submit/process-map/$PM_ID?course_id=$COURSE_ID" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Submit locked submission rejected" "403" "$STATUS"

# 35. Submit fishbone for scoring
FB_SCORE_RESP=$(curl -s -X POST "$BASE_URL/scoring/submit/fishbone/$FB_ID?course_id=$COURSE_ID" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Submit fishbone for scoring" "True" "$(echo $FB_SCORE_RESP | python3 -c "import sys,json; print(json.load(sys.stdin)['success'])" 2>/dev/null)"

# 36. Instructor review score
STATUS=$(curl -s -o /dev/null -w "%{http_code}" -X PATCH $BASE_URL/scoring/$SCORE_ID/review \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $INSTRUCTOR_TOKEN" \
  -d '{"instructor_score":28.0,"feedback":"Good work, minor gaps"}')
check "Instructor review score" "200" "$STATUS"

# 37. Get user scores
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/scoring/user/$STUDENT_ID \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get user scores" "200" "$STATUS"

# 38. Get leaderboard
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/gamification/leaderboard/$COURSE_ID \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get leaderboard" "200" "$STATUS"

# 39. Get my points
STATUS=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL/gamification/points/me?course_id=$COURSE_ID" \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get my points" "200" "$STATUS"

# 40. Get my badges
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/gamification/badges/me \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Get my badges" "200" "$STATUS"

# 41. Fishbone not found
STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL/cases/99999/rca/fishbone \
  -H "Authorization: Bearer $STUDENT_TOKEN")
check "Fishbone not found returns 404" "404" "$STATUS"

echo ""
echo "=============================="
echo " Results: $PASS passed, $FAIL failed"
echo "=============================="