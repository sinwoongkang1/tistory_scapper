# 🧬 [유클리드 호제법]을 이용한 최대공약수 찾기

기본 원리
유클리드 호제법의 기본 아이디어는 다음과 같다.
두 정수 ( a )와 ( b )가 있을 때, ( a )를 ( b )로 나눈 나머지를 ( r )이라고 할 때,
( a )와 ( b )의 최대공약수는 ( b )와 ( r )의 최대공약수와 같다.
즉, 다음과 같은 관계가 성립...!
GCD(𝑎,𝑏)=GCD(𝑏,𝑟)
이 과정을 반복하여 나머지가 0이 될 때까지 진행하다가
나머지가 0이 되는 순간, 그때의 ( b )가 ( a )와 ( b )의 최대공약수이다.
알고리즘 단계
두 수 ( a )와 ( b )를 입력받는다고 가정.
나머지 ( r )을 계산: ( r =  a%b )
( b )가 0이 아니면, ( a )를 ( b )로, ( b )를 ( r )로 업데이트.
2번과 3번을 반복.
( b )가 0이 되면, 그때의 ( a )가 최대공약수.
import math

a,b = map(int,input().split())

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return abs(a)
    
result = gcd(a,b)

print(result)
예시
예를 들어, ( a = 48 )이고 ( b = 18 )일 때.
( 48 \mod 18 = 12 ) (나머지)
( 18 \mod 12 = 6 )
( 12 \mod 6 = 0 )
여기서 ( b )가 0이 되었으므로, 최대공약수는 ( 6 ).
시간 복잡도
유클리드 호제법의 시간 복잡도는 ( O(\log(\min(a, b))) )
각 단계에서 ( b )의 값이 줄어드는 속도가 빠르기 때문에, 전체적인 반복 횟수는 두 수의 크기에 비례하여 로그 시간 복잡도로 줄어든다.
즉 a 값이  b 보다 작다면 O(log a) 의 시간복잡도로 나타낼 수 있다. (a로 나누어 줄어들기 때문)