# 2022_02_TeamProject
sns web app

## 데이터베이스

### <유저>
- 아이디(Primary Key)
- 닉네임
- 비밀번호
- 가입일
- 팔로우 유저

### <메시지>
- id(Primary Key)
- 작성유저(Foriegn Key)
- 작성시간
- 수정시간
- 내용
- 링크유저(Foriegn Key)
- 태그(Foriegn Key)
- 좋아요유저(Foriegn Key)
- 리트윗유저(Foriegn Key)

### <태그>
- id(Primary Key)
- 태그이름
- 태그주소
