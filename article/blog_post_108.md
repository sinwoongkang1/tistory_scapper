# [Network] nslookup 과 dig, 뭐가 다를까?

- 주제의 선택 이유
어제
dig
명령어에 대해서 실습해봤는데,
dig
명령어와 비슷한 결과를 주는 명령어로
nslookup
이 있다는 것을 알게 되었다.
두 명령어 모두 특정 도메인이 어떤 IP 를 가리키는지 확인하는 명령어이지만, 실제로 동작 방식과 실제 사용에는 차이가 있을 것 이다. ( 다르니까 명령어도 다르겠지...)
이에 직접 명령어를 입력해보고 반환해주는 결과를 파악해서, 두 명령어가 실제로 어떤 차이가 있고 어떤 상황에서 쓰는 것이 적합한지 학습해보도록 한다.
1. nslookup 명령어는?
nslookup <recode> <domain_address> <server>
nslookup 명령어는 DNS record를 조회할 수 있는 커맨드 라인 명령어이다.
명령어 뒤에 아무것도 입력하지 않으면 인자 값을 입력하라고 > 다음 줄로 넘어간다
따라서 명령어와 함께 인자 값을 입력해야 한다.
인자값에는
레코드 종류
(A,PRT,CNAME,MX,NS,SOA,TXT),
도메인
네임(address.com),
지정할 수 있는
서버
가 있다.
<레코드 종류>
A
> IP 주소를 알고 싶을 때
PRT
> 특정 IP주소가 도메인과 일치하는지 알고 싶을 때
CNAME
> 도메인과 별도로 별칭이 있는지 (원래 이름)
MX
> 도메인으로 메일이 갈 때, 어떤 메일 서버가 수신하는지
NS
> 해당 도메인을 관리하는 도메인 서버가 누구인지
SOA
> 도메인 존에 관련된 정보가 무엇인지
TXT
> 기본 도메인 정보 외, 기타 정보는 무엇인지
2. 명령어 사용해보기
nslookup google.com
인자 값을 도메인만 입력했으므로, 기본 DNS 서버에 질의(로컬)
/etc/resolv.conf 또는 systemd-resolved 의 127.0.0.53 주소로 질의 함
Server:           127.0.0.53
Address:        127.0.0.53#53
현재 사용 중인 DNS 서버의 주소를 출력해줌. 명령어 입력 시 인자값으로 특정 DNS 서버 주소를 입력하지 않아서 로컬 DNS 에 질의 하였다. 아래 Address 는 포트 번호까지 반환되었다.
Non-authoritative answer:
해당 응답이 권한 있는 DNS 서버에서 직접 온 것이 아님을 명시 -> 캐시 된 응답이거나, 중간 DNS 서버를 거쳐 받은 결과이다.
Name:         google.com
Address :     127.217.161.206
Name:         google.com
Address:      2404:6800:400a:805::200e
도메인 이름과 IPv4 주소로 응답, 그리고 도메인 이름과 IPv6 주소로도 응답을 해준다.
3. dig 명령어와의 결과 비교
항목
dig
nslookup
응답 형식
상세하고 구조화됨
간단하고 요약적
기본 설치
최신 리눅스엔 별도 설치 필요
대부분 기본 포함
재귀/권한 구분
명확히 보임
일부 표현 생략됨
응답 정보
TTL, Authority, Additional까지 포함
간단한 IP 정보 중심
스크립트 활용
구조적 출력 → 스크립트 친화적
파싱은 다소 어려움
실무 사용성
서버/운영자 선호
사용자나 윈도우 환경에서 많이 사용
4. 활용적 측면에서의 차이점
4-1. dig 명령어
도메인의 DNS 구조를 정밀하게 분석할 때 유리하다. (응답이 더 상세하게 반환 됨)
TTL 및 캐시 유무 등을 확인 해야 할 때 써야 한다. (응답문에 정보가 있기 때문)
4-2. nslookup 명령어
윈도우 환경에서 DNS 관련 질의를 간단하게 확인할 때.
네트워크 진단 중 빠르게 IP 를 확인할 때.
리눅스 기본 명령으로 충분히 해결할 수 있을 때. (dig 는 별도로 설치해야 할 수도 있기 때문)
5. 유용한 옵션 정리
5-1. 특정
레코드
유형만 질의하기 (-query=
TYPE
or -type=
TYPE
)
nslookup -query=mx google.com        # MX 레코드 (메일서버 정보)
nslookup -type=ns naver.com          # NS 레코드 (네임서버 정보)
nslookup -type=txt google.com        # TXT 레코드 (SPF, 도메인 검증 등)
5-2. 지정한 DNS 서버에 질의하기
nslookup google.com 8.8.8.8
기본 DNS (로컬) 에 질의하지 않고, 8.8.8.8 주소를 가진 DNS 서버로 질의한다.
5-3. 질의와 응답에 대한 자세한 내부 정보를 출력하기
nslookup
> set debug
> google.com
레코드 타입, 클래스, TTL 정보까지 모두 출력된다. (dig 와 비슷)
5-4. 응답 대기 시간과 재시도 횟수 조절
nslookup
> set timeout=2
> set retry=1
> google.com
5-5. 기존 DNS 의 53번 포트 대신 다른 DNS 서버가 열려있는 경우, 다른 포트를 사용하기
nslookup
> set port= xxxx
> mycustomdns.local
6. 마무리
dig 명령어는 DNS 정보를 구조화된 형태로 상세하게 보여주기 때문에 정밀한 분석에 적합하고, nslookup 명령어는 필요한 정보만 빠르게 확인할 수 있어 간편한 진단에 유용할 것 같다.
실제로 사용한다면 두 명렁어 모두 필요한 상황에 맞게 활용될 수 있을 것 같고, 특히 nslookup은 -query, server, set debug 같은 옵션을 통해 MX, NS 레코드 등 주요 도메인 설정을 점검하거나, 외부 DNS와 내부 DNS 설정을 비교하는 데도 충분히 활용할 수 있을 것 같다. 또 dig를 사용하기 어려운 환경(윈도우)에서도 set debug 옵션을 활용하면 어느 정도 분석이 가능할 것 같다.