StatusCode 번호

# 200 /200
성공적으로 요청

# 201 / 201
성공적으로 요청 및 데이터 생성됨

# 4001 / 400
POST 요청을 해야 하는데 GET 요청으로 했을 때

# 4200 / 400
올바르지 않은 API키

# 4800 / 408
타임아웃(2초)

# 5009 / 500
Unknown Error

# 5100 / 500
FastText 모델 파일 찾기/로드 실패

# 5101 / 500
언어값 판단 실패

# 5200 / 500
Gemini API가 반환한 값이 JSON 형식이 아닌 경우

# 5201 / 500
Gemini API가 반환한 JSON에 Score, RecommandedTrans, Rating 키 중 하나라도 없거나 null인 경우

# 5203 / 500
Gemini API가 The model is overloaded. Please try again later. 라고 출력한 경우

# 5204 / 500
TranslatedLang과 RecommandedTrans이 다르거나 EvaluationLang과 Rating이 다른 경우