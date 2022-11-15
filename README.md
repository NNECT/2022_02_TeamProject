# 2022_02_TeamProject
sns web app

## 데이터베이스

### <유저>
- 아이디
- 닉네임
- 비밀번호
- 가입일

### <메시지>
- 작성유저(Foriegn Key)
- 작성시간
- 수정시간
- 내용

### 댓글
- 대상메시지(Foriegn Key)
- 작성유저(Foriegn Key)
- 작성시간
- 수정시간
- 내용

### <태그>
- 태그이름
- 태그주소

### 유저링크
- 메시지(Foriegn Key)
- 대상유저(Foriegn Key)

### 팔로우
- 유저(Foriegn Key)
- 대상유저(Foriegn Key)

### 좋아요
- 유저(Foriegn Key)
- 대상메시지(Foriegn Key)

### 리트윗
- 유저(Foriegn Key)
- 대상메시지(Foriegn Key)
