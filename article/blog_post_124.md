# [Network] pgcrypto 란 무엇인가? (개념편)

1.pgcrypto란?
pgcrypto
는 PostgreSQL에서 **암호화(Encryption)**와
해시(Hash)
기능을 사용할 수 있게 해주는
내장 확장 모듈이다.
아래 한 줄만 실행하면 PostgreSQL에서 SHA256, AES, bcrypt 같은 암호화 및 해시 함수를 자유롭게 사용할 수 있게 된다.
CREATE EXTENSION pgcrypto;
2. pgcrypto가 제공하는 기능
기능 종류
대표 함수
함수
해시 함수
digest(data, 'sha256')
SHA1, SHA256, MD5 등의 해시 생성
비밀번호 해시
crypt('비번', gen_salt('bf'))
bcrypt 방식 비밀번호 암호화
대칭키 암호화
pgp_sym_encrypt(data, key)
하나의 비밀키로 암호화/복호화
대칭키 복호화
pgp_sym_decrypt(data, key)
암호화된 데이터를 비밀키로 복호화
인코딩/디코딩
encode()
,
decode()
바이너리 데이터를 문자로 표현하거나 되돌림
3. 실무에서의 사용
데이터 베이스에서 사용자의 비밀번호 저장
: 평문 저장 대신 bcrypt +
crypt()
을 사용하여 암호화된 문장을 저장한다.
개인정보/민감 정보 암호화
: AES 또는 PGP 방식 암호화로 저장한다.
데이터 위변조 감지
: 해시 값을 따로 기록해 변경 여부를 확인한다.
-> PostgreSQL DB 를 사용하면서, 데이터가 암호화 될 필요가 있다면 pgcrypto 를 사용하면 된다!
4. 주의할 점 및 마무리
해시는 복호화할 수 없고, 암호화는 복호화 키가 필요하다
비밀번호는 무조건
crypt()
+
gen_salt()
조합을 쓰는 것을 추천한다
민감 정보 복호화를 위해
키 관리
도 중요하다
다음 편에서는 직접
pgcrypto
를 설치하고, 암호화/복호화 함수들에 대해 알아본 후 직접 저장한 데이터가 정말로 암호화 되어서 저장되어 있나 확인해보려 한다.