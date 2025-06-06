# [명령어 알아보기] nice & renice

프로세스의 우선순위를 설정할 수 있는 명령어인 nice 와 renice 명령어에 대해 알아보자.
(리눅스 마스터 2급 시험 대비!!!)
nice
용도: 새로운 프로세스를 시작할 때 우선순위를 설정하여 시작하는 명령어.
사용:
nice -n [우선순위] [프로세스명]
우선순위는 -20(가장 높은 우선순위)부터 19(가장 낮은 우선순위)까지의 값을 가질 수 있고 기본 값은 0 이다.
입력한 우선순위는 0 값에서 증감 된다. (입력한 값으로 우선순위가 매겨진다)
ex) nice -n -10 bash
-> bash 쉘을 우선순위 10 으로 실행시킨다( 0 보다 우선순위가 높다 )
양수는 - n, 음수는 --n 으로 표현한다
renice
용도: 이미 실행 중인 프로세스의 우선순위를 변경한다.
사용
renice [우선순위] -p [PID]
[PID]는 프로세스 ID를 입력하면 된다. (옵션 -p 는 생략이 가능하다)
명령을 실행하면 해당 프로세스의 우선순위가 지정한 우선순위로 교체된다.
ex) renice -5 -p 1234 ( renice -5 1234 )
-> 이 명령어는 PID가 1234인 프로세스의 우선순위를 -5로 변경한다.
양수는 n, 음수는 -n 으로 표현한다.