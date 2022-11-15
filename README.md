# 2022_02_TeamProject
sns web app

## 데이터베이스

### <유저>
- 아이디
- 닉네임
- 비밀번호
- 가입일
- 팔로우유저(ManyToManyField)

### <메시지>
- 작성유저(Foriegn Key)
- 작성시간
- 수정시간
- 내용
- 태그(ManyToManyField)
- 유저링크(ManyToManyField)
- 좋아요(ManyToManyField)
- 리트윗(ManyToManyField)

### <댓글>
- 대상메시지(Foriegn Key)
- 작성유저(Foriegn Key)
- 작성시간
- 수정시간
- 내용

### <태그>
- 태그이름
- 태그주소
