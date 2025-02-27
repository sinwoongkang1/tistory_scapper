# 🧬[깊이우선탐색 알고리즘] 노가다로 알아보기

깊이우선탐색과 너비우선탐색은 그래프나 트리구조를 탐색하는 두 가지 기본적인 알고리즘 이다. (Ai 말씀)
각각의 특징과 차이점을 잘 비교하여, 효율적으로 사용하면 일반 적인 탐색 방법보다 효율적으로 사용할 수 있을 것 같다.
원래는 두 가지 방법을 다 알아보고 싶었는데, 잘 이해가 되지 않아 디버깅 모드로 노가다를 해서 하루에 하나씩 알아보기로 하자......
깊이 우선 탐색 (Depth First Search)
-깊이를 우선적으로 탐색한다는 이름처럼, 그래프나 트리구조의 자료형태가 있는 경우, 같은 레벨에 있는 노드(?) 들을 탐색하고 지나가는 것이 아니라, 하나의 노드에 연결된 마지막 까지 탐색하고 나온다음에, 그 옆에 있는 노드를 또 끝까지 검색하고 나오는 방법 같다고 생각했다. (너비 는 이 반대겠네)
🤖 :DFS는 가능한 한 깊게 노드를 탐색한 후, 더 이상 탐색할 노드가 없으면 마지막으로 방문한 노드로 돌아가서 다른 경로를 탐색하는 방식입니다. 스택을 사용하여 구현할 수 있으며, 재귀적으로도 쉽게 구현할 수 있습니다.
특징
구현 방식 : 스택
탐색 방법 : 한 방향으로 최대한 깊이 탐색 후, 더 이상 갈 곳이 없으면 백 트래킹
시간 복잡도 : O(V+E) V : 정점 수 E : 간선 수
의미와 느낌은 이미 파악 완료 한 것 같다. 구현 방법이 궁금하다!!
def dfs_iterative(graph, start):
    visited = set()  # 방문한 노드를 저장할 집합
    stack = [start]  # 시작 노드를 스택에 추가

    while stack:
        vertex = stack.pop()  # 스택에서 노드 하나를 꺼냄
        if vertex not in visited:
            visited.add(vertex)  # 방문 처리
            print(vertex)  # 방문한 노드 출력
            # 인접 노드를 스택에 추가 (역순으로 추가하여 원래 순서를 유지)
            stack.extend(reversed(graph[vertex]))

# 그래프 정의 (인접 리스트)
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D', 'E'],
    'C': ['A', 'F'],
    'D': ['B'],
    'E': ['B', 'F'],
    'F': ['C', 'E']
}

dfs_iterative(graph, 'A')
디버그야 고마워!!
IDE 의 디버그 모드를 사용하여 DFS 를 구현한 코드를 탐독 해봤다.
1. map 자료 구조로 만들어진 그래프를 탐색한다
A
├── B
│   ├── D
│   └── E
└── C   |
    └── F
2. def dfs_iterative(graph, start)
그래프와 시작점A 를 인자로 받는 메서드가 실행된다
3. visited = set()
visited 라는 자료구조는 set 으로 선언했는데, 인접 리스트에 중복해서 표현 해 놨으니 이걸 없애려고 중복을 허용하지 않는 자료구조를 선언한 것 같다.
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {}
start = 'A'
4. stack = [start]
시작 노드를 stack 배열에 추가한다.
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {}
start = 'A'
stack = ['A']
5. while stack:
stack 의 자료구조에 데이터가 있으면 반복된다 (자료구조에 아무것도 없으면 종료)
6. vertex = stack.pop()
stack 에서 노드를 하나 꺼내고 vertex 에 저장한다 ( pop은 꺼내고 지우니 stack 은 빈다.)
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {}
start = 'A'
stack = []
vertax = 'A'
7. if vertax not in visited:
visited 자료구조에는 A 가 없으므로 이하 구문이 실행된다.
visited.add(vertex)
방문한 노드를 set 자료 구조에 저장
print(vertex)
방문한 노드를 출력한다
stack.extend(reversed(graph[vertex]))
인접한 노드를 스택에 추가한다 (역순으로 추가하여 원래 순서를 유지한다)
스택 은 마지막에 추가된 노드가 먼저 처리되므로 pop() 을 수행하기 위해서 B 를 계속 탐색해야 한다.
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {}
start = 'A'
stack = ['C','B']
vertax = 'A'
while 문 1회 진행 완료 -----
2-1 . while stack :
2-2. vertex = stack.pop()
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {'A'}
start = 'A'
stack = ['C','B']
->
stack = ['C',]
vertax = 'A'
->
vertax = 'B'
2-3 if vertex not in visited
visited.add(vertex)
print(vertex)
stack.extend(reversed(graph[vertex]))
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {'B','A'}
start = 'A'
stack = ['C','E','D','A']
vertax = 'B'
while 문 2회 진행 완료 -----
3-1 . while stack :
3-2. vertex = stack.pop()
여기서 vertex = A 가 된다. 스택이 현재 [C E D A] 순으로 저장되어 있기 때문
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {'B','A'}
start = 'A'
stack = ['C','E','D']
vertax = 'A'
3-3. if vertex not in viseted
visited = {'B','A'}
에 vertax = 'A' 값이 있으므로, if 아래 구문이 실행되지 않고 while 문으로 복귀
while 문 3회 진행 완료 -----
4-1 . while stack :
4-2. vertex = stack.pop()
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {'B','A'}
start = 'A'
stack = ['C','E','D']
-> stack = ['C','E']
vertax = 'A'
-> vertax = 'D'
4-3. if vertex not in viseted
D 가 visited 에 없으므로 if 이하 구문 실행
visited.add(vertex)
print(vertex)
stack.extend(reversed(graph[vertex]))
graph = {'A': ['B', 'C'], 'B': ['A', 'D', 'E'], 'C': ['A', 'F'], 'D': ['B'], 'E': ['B', 'F'], 'F': ['C', 'E']}
visited = {'D','B','A'}
start = 'A'
stack = ['C','E','B']
vertax = 'D'
이 정도 까지 써보며 확인하니 어떻게 코드가 동작하는지 감이 왔다(힘들어서 아님)
1. 시작 노드를 추가하고 방문했으니 stack 에 저장.
2. A 노드에 연결된 B C 노드의 순서 (stack.pop() 을 위해  사실은 역순으로) 대로 방문하기 위해 B 를 방문
3. B에 연결된 노드는 A D E 인데(실제 E D A 순), A 는 방문했으니 지우고,  D 를 방문
4. D를 방문하는데 연결된 노드가 있다면 호출해서 스택에 역순으로 추가 반복
이렇게 옆에 있는 노드는 무시하고 연결된 노드들만 순차적으로 방문해 나가는 로직이였다.
근데 이 탐색 방법을 문제풀이에 적용하려면 코드를 이해 했어도 외우는게 좋을 것 같다.
그리고 아마 특정 노드를 방문할 때 count 값을 올려주는 방법으로 문제를 풀지 않을까 싶다.
다음은 너비 우선 탐색 노가다를 해봐야 겠다.