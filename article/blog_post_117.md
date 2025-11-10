# [Network] 네트워크 관리의 핵심 프로토콜 SNMP 1부 (개념편)

https://www.noction.com/blog/snmp-versions-evolution-security
<< 주제 선정의 이유 >>
EMS 를 만들고, 공급하는 회사에서 네트워크 인프라 관리 업무를 배우게 된다. EMS 가 동작하기 위한 기초적이면서도 가장 중요한 기술이자 프로토콜인 SNMP에 대해 심도 있게 알아보고, 추후 직접 사용해보면서 업무를 파악하는데 최대한 도움이 될 수 있도록 하기위해 SNMP 를 공부하는 것으로 주제를 선택하였다.
1. SNMP란?
SNMP(Simple Network Management Protocol)는 다양한 네트워크 장비(스위치, 라우터, 서버 등)의 상태 정보를
요청하거나, 알림을 받기 위한 통신 규약이다.
기업이나 기관에서 사용하는 EMS(Enterprise Management System)나 NMS(Network Management System) 같은 관리 솔루션들이 장비 상태를 수집하고 알람을 띄우는 데 사용하는 프로토콜이다.
즉 SNMP 를 이해하면, 네트워크 기기들이 보내는 신호들을 보고 지금 어떤 상태이구나 라는 것을 파악할 수 있다.
2.어떠한 상황에서 쓰이는가?
서버 CPU가 95% 이상 사용되고 있음 → EMS에서 CPU 사용 경고 발생
스위치 포트가 down 되었음 → 관리자에게 포트 상태 알림 전송
특정 장비의 온도, 메모리, 트래픽 상태 주기적 수집
이 모든 상황이
SNMP 기반의 통신
으로 이루어 진다.
3. SNMP의 기본 구성 요소
구성요소
역할
Manager
정보를 요청하는 주체. 보통 EMS, NMS가 이 역할을 함
Agent
정보를 제공하는 장비(스위치, 서버, 프린터 등)
MIB
(Management Information Base)
Agent가 보유한 정보 항목의 데이터베이스 (트리 구조)
OID
(Object Identifier)
각각의 정보를 식별하는 고유 번호 (예: CPU 사용률, 포트 상태 등)
4. SNMP의 작동 방식 (요약)
🔹 Manager → Agent : "지금 CPU 사용률이 얼마야?"
SNMP GET
🔹 Agent → Manager : "CPU는 82%야"
SNMP RESPONSE
🔹 Agent → Manager : "스위치 포트가 꺼졌어!"
SNMP TRAP (비동기 알림)
5. SNMP 버전별 차이점
버전
특징
v1
초창기 버전. 인증 기능 거의 없음
v2c
성능 개선. 여전히 community string 방식의 단순 인증 사용
v3
암호화 및 인증 기능 포함. 보안에 가장 적합함
6. SNMP가 제공하는 정보는 어떠한 것들이 있나?
시스템 이름, 운영 시간
CPU/메모리 사용률
포트 상태 (Up/Down)
네트워크 트래픽 (In/Out 바이트)
장비 온도, 팬 속도 등
▶ 이런 정보는 모두 OID 형태로 MIB에 저장되어 있고, 요청 시 가져올 수 있음
7. 내일  SNMP 실습 편에서 확인해야 할 것.
내일은 리눅스에서 SNMP 도구를 사용해
snmpget
으로 장비의 상태 정보 요청하기
snmpwalk
으로 전체 MIB 트리 탐색하기
실제 장비나 NAS에서 정보 수집해보기
를 직접 해보며, SNMP를 실제로 사용하면서, 내 네트워크 기기들에 대한 상태 정보를 파악해보고, 이러한 정보들을 어떻게 추출(?)해서 EMS 라는 솔루션에 적용할 수 있는지 알아보도록 하자.