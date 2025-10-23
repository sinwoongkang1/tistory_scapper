# [Network] OpenVPN 트러블슈팅 기록 -1

1. 원인 파악 –  VPN 서버와는 연결되는데, 통신은 되지 않는다.
Synology NAS에 VPN 서버(OpenVPN)를 구축하고,
외부 클라이언트(우분투 데스크탑, 맥북)에서 VPN 접속까지는 잘 됐는데…
VPN에 접속은 되지만
클라이언트 간 ping이 안 되고
인터넷 접속도 안 됐다
처음엔 설정이 잘못된 줄 알았지만, 오히려 클라이언트가 NAS까지는 통신이 잘 되는데,
VPN을 통해
다른 클라이언트로 가는 패킷이 NAS 나 라우터 에서 튕겨나가는 듯한 느낌
이 들었다.
2. 예상되는 문제별로 시도해본 것들
(1) 라우팅 문제 의심 (서버의 설정파일 수정하기)
push "route 10.8.0.0 255.255.255.0"
push "route 10.8.0.0 255.255.255.0"
push "redirect-gateway def1 bypass-dhcp"
push "dhcp-option DNS 8.8.4.4"
topology subnet 추가
client-to-client 추가
클라이언트, 서버 모두 라우팅 테이블 확인하고 수동으로 경로 추가도 시도
-> ping test 실패
(2) TUN 인터페이스 동작 확인
ifconfig, ip route 확인
클라이언트에서 destination이 자기 자신으로 되어 있는 점 발견
→ 라우팅 테이블 수정했지만 여전히 ping 실패
(3) 방화벽 문제 의심
윈도우, 우분투, 맥북 모두 방화벽 완전 해제
네트워크 프로필 개인/공용 전환도 시도
-> ping test 실패
(4) 서버의 포워딩/NAT 문제
NAS에서 ip_forward=1 설정
iptables에 MASQUERADE 룰 추가
iptables -t nat -A POSTROUTING -s 10.8.0.0/24 -o eth0 -j MASQUERADE
-> 여전히 ping test 실패
(5) 공유기 간섭 의심
ipTIME 공유기에서 VPN 서버 기능 OFF
포트포워딩 UDP 1194 → NAS로 설정
-> 역시나 ping test 실패
3. 결과
NAS에서는 모든 클라이언트에 ping이 잘 됐고,
NAS에서 외부 네트워크(8.8.8.8) ping 테스트 성공
클라이언트 → 클라이언트 간 ping은 끝내 실패
클라이언트에서 외부 인터넷(ping 8.8.8.8)도 안 됨
심지어 write to TUN/TAP : Invalid argument 에러가 반복적으로 로그에 찍힘
→ 터널링은 성공했지만 데이터 전달이 안 되는 전형적인 오류
4. 마무리 및 다음 시도할 것들
현재로선
VPN 설정은 구성됐지만
,
시놀로지 NAS의 VPNCenter 패키지가 내부적으로 TUN 디바이스나 라우팅을 제한하고 있을 가능성이 크다고 판단했다.
그래서 다음 시나리오를 고려 중:
VPNCenter 대신 OpenVPN 직접 설치 (Entware 등 활용)
완전 커스텀 구성 가능, 시스템 레벨에서 제약 없음
Tailscale / ZeroTier 같은 mesh 기반 VPN 사용
포트포워딩 없이도 내부 장비끼리 VPN 구성 가능
특히 공유기나 NAS의 간섭 없이 안정적임
Softether VPN 서버로 전환
시놀로지에서 더 안정적으로 작동한다는 사용자 피드백 다수 있음