# 2022_02_TeamProject
sns web app

## 개발환경
- Python (3.9)
- Django (3.2.16)
- Bootstrap (5.2.2)

## 개발계획
- Navbar
  - 왼쪽위: 로고
  - 오른쪽위: 스택
    - 로그인이 되지 않았을 경우 로그인 버튼
    - 로그인이 되었을 경우 개인정보 변경
- 메인주소
  - 로그인이 되지 않았을 경우 로그인 창
  - 로그인이 되었을 경우 타임라인
- 타임라인
  - 메시지를 1줄로 카드형 출력
  - 이미지가 있을 경우 이미지 출력
  - 자신의 메시지일 경우 수정/삭제 버튼
  - 댓글버튼: 댓글 수만 보여주고 누를 경우 메시지창으로 이동
  - 좋아요, 리트윗 버튼: 토글 on/off형
    - 자신의 메시지일 경우 비활성화
  - 자신의 타임라인에서는 맨 위에 메시지 작성창
- 유저 타임라인 (user/<id>)
  - 자신의 id일 경우 메인주소로 리다이렉트

## 데이터베이스

- User(AbstractUser)
  >- username
  >- password
  >- nickname
  >- follow(ManyToManyField)
- Tag
  >- name
  >- slug
- MessageCard
  >- author (Foriegn Key → User)
  >- created_at
  >- updated_at
  >- head_image
  >- content
  >- tag (ManyToManyField: tag_message ↔ Tag)
  >- link_user (ManyToManyField: link_message ↔ User)
  >- like_user (ManyToManyField: like_message ↔ User)
  >- forward_user (ManyToManyField: forward_message ↔ User)
- Reply
  >- message (Foriegn Key → MessageCard)
  >- author (Foriegn Key → User)
  >- created_at
  >- updated_at
  >- content
