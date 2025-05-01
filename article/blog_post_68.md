# [Baekjoon] 1874 - 스택수열

import sys
userInputLine = int(sys.stdin.readline().strip())

stack = []
stack_2 = []
compareArray = []
array = []
brray = []
signal = []

for _ in range(userInputLine):
    userInputNumber = int(sys.stdin.readline().strip())
    stack.append(userInputNumber)
    stack_2.append(userInputNumber)
    compareArray.append(userInputNumber)

compareArray.sort()


while True:
    if len(array) == 0 and len(compareArray) != 0:
        array.append(compareArray[0])
        signal.append("+")
    elif len(compareArray) == 0:
        break
    else:
        if stack[0] != array[-1]:
            array.append(compareArray[0])
            signal.append("+")
    while True:
        if len(array) == 0:
            break
        elif array[-1] == stack[0]:
            brray.append(array[-1])
            if array[-1] in compareArray:
                del compareArray[0]
            del stack[0]
            del array[-1]
            signal.append("-")
        else:
            if array[-1] != stack[0]:
                if array[-1] in compareArray:
                    del compareArray[0]
                break
            else:
                sing = "none"
                break
 
if stack_2 == brray:
    print(*signal,sep="\n")
else:
    print("NO")
예제 출력도 맞게 나오고, 디버깅 상 로직은 제대로 흘러가는데
자료구조를 너무 많이 선언하고 조건문도 매우 복잡하게 만들었다.
리펙토링 하거나 새로운 접근을 해야 할 필요가 있다
count = 1
temp = True
stack = []
op = []

N = int(input())
for i in range(N):
    num = int(input())
 
    while count <= num:
        stack.append(count)
        op.append('+')
        count += 1

    
    if stack[-1] == num:
        stack.pop()
        op.append('-')
    
    else:
        temp = False
        break

if temp == False:
    print("NO")
else:
    for i in op:
        print(i)