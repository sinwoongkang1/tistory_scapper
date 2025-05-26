# [알고리즘] input() 과 sys.stdin.readline().strip() 의 출력차이는?

브론즈4 등급의 간단한 문제였는데, 입력을 sys 로 받고 출력하는 것과 input  으로 받고 출력하는 것이 결과가 달랐다.
먼저 sys 로 작성한 코드는 아래와 같고
import sys

test_case = int(sys.stdin.readline().strip())
numbers= []
sentence = []
for i in range(test_case):
    numbers.append(int(i)+1)
    input_line = sys.stdin.readline().strip()
    sentence.append(input_line)

for i in range(test_case):
    print(str(numbers[i])+".",sentence[i])
input 으로 입력받는 코드는 아래와 같다.
test_case = int(input())
numbers= []
sentence = []
for i in range(test_case):
    numbers.append(int(i)+1)
    input_line = str(input())
    sentence.append(input_line)

for i in range(test_case):
    print(str(numbers[i])+".",sentence[i])
코드 흐름은 똑같고 단순히 사용자의 입력을 input () 으로 받는 것과 sys.stdin.readline().strip() 으로 받는것으로 출력의 결과가 달라지게 되고 하나는 오답 처리, 하나는 정답 처리가 되었다.
input() 함수를 사용하여 사용자로부터 입력을 받으면 기본적으로 표준 입력에서 한 줄을 읽고, 입력이 끝날 때까지 대기
sys.stdin.readline()을 사용하여 입력을 받으면 입력된 한 줄을 즉시 읽고, 줄바꿈 문자까지 포함하여 반환. 이 경우 줄바꿈 문자를 제거하기 위해 strip() 메서드를 호출.
input()은 사용자가 입력을 완료한 후 Enter 키를 눌러야 하는 반면, sys.stdin.readline()은 표준 입력 버퍼에서 직접 읽기 때문에 입력 대기 방식이 조금 더 원활할 수 있음.
input()은 입력이 잘못되었을 때 예외를 발생시킬 수 있지만, sys.stdin.readline()은 입력을 읽고 나서 strip()을 호출하는 방식이므로 예외 처리 방식이 다를 수 있다.
즉 출력의 형식에서는 큰 차이가 발생하지 않을 수 있다. 하지만 입력에서 잘못된 입력이 들어올 경우 예외 발생시 처리 방식이 달라서 차이가 나타날 수 있다. 알고리즘 채점 시 여러 값을 대입하고 올바른 결과나 예외처리까지 포함하여 채첨한다면 두 방식에서 결과가 달라질 수도 있을 것 같다.