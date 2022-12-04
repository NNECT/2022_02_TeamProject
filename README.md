# 2022_02_TeamProject
sns web app

## 개발환경
- Python (3.9)
- Django (3.2.16)
- Bootstrap (5.2.2)

## 개발계획
- Navbar
  - _왼쪽위: 로고 (완료)_
  - _오른쪽위: 스택 (완료)_
    - _로그인이 되지 않았을 경우 로그인 버튼 (완료)_
    - _로그인이 되었을 경우 개인정보 변경 / 로그아웃 버튼 (완료)_
- 메인주소
  - _로그인이 되지 않았을 경우 로그인 창 (완료)_
  - _로그인이 되었을 경우 타임라인 (완료)_
- 타임라인
  - _메시지를 1줄로 카드형 출력 (완료)_
  - _자신의 타임라인에서는 맨 위에 메시지 작성창 (완료)_
    - 메시지 작성 기능
  - _이미지가 있을 경우 이미지 출력 (완료)_
  - _자신의 메시지일 경우 수정/삭제 버튼 (완료)_
    - _수정 작성창 (완료)_
      - 수정 기능
    - _삭제 확인창 (완료)_
      - 삭제 기능
  - _댓글버튼: 댓글 수만 보여주고 누를 경우 메시지창으로 이동 (완료)_
  - 좋아요, 리트윗 버튼: 토글 on/off형
    - 자신의 메시지일 경우 비활성화
- 메시지 페이지
  - _메시지 출력 (완성)_
  - _로그인했을 경우 댓글 작성창 (완성)_
    - 댓글 작성 기능
  - _댓글 출력 (완성)_
- _유저 타임라인 (user/<id>) (완료)_

## 데이터베이스
- User(AbstractUser)
  >- username
  >- password
  >- nickname
  >- follow(ManyToManyField: follower ↔ User)
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
