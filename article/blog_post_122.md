# [Network] SNMP 의 Version 별 차이 알아보기

https://www.noction.com/blog/snmp-versions-evolution-security
네트워크 장비를 관리할 때 빠질 수 없는 프로토콜은
SNMP(Simple Network Management Protocol) 이다.
하지만 SNMP도 여러 버전(v1, v2c, v3)이 있어서 그 차이를 잘 알아야, 상황에 맞게 적용하여 사용할 수 있다.
오늘은 각 버전의
차이점과 실무에서 어떻게 선택하는지
알아보자!
1. SNMP v1
최초 버전 (1988년)
구조:
Manager-Agent 모델
(기본 구조는 모든 버전 동일)
인증 방식:
community string
(문자열 하나, 예:
public
,
private
)
보안:
거의 없음
(비밀번호 없이 누구나 읽을 수 있음)
지원 메시지: GET, SET, GETNEXT, TRAP
어떤 실무 환경에서 사용되나?
구형 장비
가 v1만 지원하는 경우 사용
지금은
거의 사용되지 않음
2. SNMP v2c
v1의 확장판 (1993년)
인증 방식: 여전히
community string
보안: v1과 동일 →
암호화 없음
성능:
Bulk 요청 지원
→ 한 번에 여러 데이터를 가져올 수 있음 (트래픽 절감)
지원 메시지: GETBULK 추가 (대량 조회), INFORM 추가 (확인 가능한 알림)
어떤 실무 환경에서 사용되나?
보안이
크게 중요하지 않은 내부망
장비가 많고 트래픽 절약
이 필요할 때 → GETBULK 사용
3. SNMP v3
보안이 강화된 버전 (1998년)
인증 방식:
사용자 기반(User-based)
보안 기능:
암호화 + 인증
인증: MD5, SHA 등으로 사용자 확인
암호화: DES, AES로 데이터 암호화 가능
유연성: 보안 레벨을 상황에 맞게 설정 가능
noAuthNoPriv
: 인증X, 암호화X
authNoPriv
: 인증O, 암호화X
authPriv
: 인증O, 암호화O
어떤 실무 환경에서 사용되나?
외부망
,
보안이 중요한 환경
사내망에서도 표준 보안정책
을 지켜야 할 때
VPN, 클라우드 환경
에서 필수
4. 한눈에 비교 해보기
항목
v1
v2c
v3
출시 연도
1988
1993
1998
인증 방식
community string
community string
사용자 기반 (User-based)
암호화
없음
없음
DES, AES
인증
없음
없음
MD5, SHA 등
성능 (Bulk)
미지원
지원
지원
알림 (Trap)
TRAP (비확인성)
TRAP, INFORM (확인)
TRAP, INFORM (확인)
5. 실무에서는 어떤 버전을 써야 할까?
환경
추천 버전
내부망, 보안 덜 중요
v2c (간단 + 빠름)
외부망, 클라우드
v3 (암호화 필수)
구형 장비
v1 (지원 안 하면 어쩔 수 없음)
6. 마무리
snmp 는 버전에 따라 인증방식, 암호화, 성능 등에 차이가 있다는 것을 알게 되었다. 최근 버전에 가까워 질수록, 성능도 좋아지고 보안에 유리한 것은 사실이지만, 그렇다고 해서 항상 최신 버전만을 사용해야 한다고 강제할 순 없다. 네트워크의 모든 기술이 그렇듯, 상황과 장비에 따라 알맞는 기술이 존재하기 때문에, 아무리 오래된 기술이라도 그 필요가 있을 수 있다는 것을 놓치지 말자!