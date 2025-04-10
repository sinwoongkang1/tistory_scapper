# [프로젝트] Naver 데이터랩의 통합검색어 트랜드 API 를 SpringBoot 프로젝트를 통해 요청하고 응답받기

이전 내용에서는 현재 진행 중인 SpringBoot 프로젝트에서 Google Trend API 를 사용하는 방법을 시도 해 봤다. 이번엔 추가로 국내 사용자들이 많이 이용하는 검색포털인 Naver 의 검색량도 API로 받아와 프로젝트에서 사용해 보는 법을 시도해 보려 한다. 이렇게 두 개의 API를 통해 도출한 데이터(검색어 TOP5)를 가지고 추천 알고리즘을 사용자가 선택하게 하거나, 자체적으로 가중치를 부여해서 사용자에게 추천해주는 방법을 고려해보려 한다.
1.API key 를 발급 받기위해 네이버 개발자센터로 들어간다.
2.애플리케이션 정보를 등록하여 API key 를 발급 받는다.
현재 진행 중인 프로젝트는 WAS 가 localhost 에서 실행하고, API 요청문을 발송할 것이기 때문에, 웹 서비스 URL에 localhost:8080 을 추가해 본다. (Swagger 테스트도 할 건데 여기서도 돼야 하니까 일단 추가해본다.)
애플리케이션 등록이 완료되면 API 요청에 필요한 Key 와 Passward가 발급된다. 월간 요청량도 1,000회로 구글보다 많다.
이제 Springboot에서 요청문을 만들어서 실제 응답이 오는지 확인해 본다.
3.Springboot에서 API 요청문 생성 메서드 만들기
서비스 클래스에서 요청문 생성 메서드를 작성하면 너무 복잡해서, 요청문 생성 클래스를 생성했다. 이 클래스에서 restTemlate 를 이용하여 요청문을 만들어서 서비스 클래스에서는 이용만 하도록 했다.
API 키와 패스워드는 필드에 직접 명시할 경우 Git push 할 때 Git Protection 기능에 의해 Push 가 거부 되므로, 참조 값을 이용해서 명시하도록 한다.
Naver DataLaB Trend API 는 한번에 키워드 5개에 대한 요청이 가능하기 때문에, 내가 검색하고 싶은 키워드 N 개가 있다면 5개씩 나누어 보낼 수 있도록 메서드를 만들어 주어야 한다.
이전달의 첫날, 이전달의 마지막날과 같은 날짜 데이터는 DataCalculator 라는 클래스에 정적 메서드로 만들어서 API 들을 호출할 때 함께 사용하고 있다.( 이전 포스팅 참고)
Naver 의 검색량은 1달 단위로 검색이 가능하고(google API 는 1주 단위), 만약 12월의 데이터가 90 이라면 이는 11월의 값을 100으로 상정하여 10%가 감소했다는 것을 의미한다. 따라서 서버에 접속한 사용자가 12월에 우리 홈페이지에 접속 했다면, 10월과 11월의 검색량 차이를 가져와 검색량 값의 변화량을 데이터로 사용하기로 한다.
@Component
public class NaverAPIRequestMaker {

    private RestTemplate restTemplate;

    public NaverAPIRequestMaker(RestTemplate restTemplate) {
        this.restTemplate = restTemplate;
    }

    @Value("${api.naver.client-id}")
    private String clientId;

    @Value("${api.naver.client-secret}")
    private String clientSecret;

    private HttpHeaders createHeaders() {
        HttpHeaders headers = new HttpHeaders();
        headers.set("X-Naver-Client-Id", clientId);
        headers.set("X-Naver-Client-Secret", clientSecret);
        headers.set("Content-Type", "application/json");
        return headers;
    }

    private String createRequestBody(List<String> sublist) {
        StringBuilder keywordGroupBuilder = new StringBuilder();
        keywordGroupBuilder.append("\"keywordGroups\":[");

        for (int j = 0; j < sublist.size(); j++) {
            keywordGroupBuilder.append(createKeywordGroup(sublist.get(j)));
            if (j < sublist.size() - 1) {
                keywordGroupBuilder.append(",");
            }
        }
        keywordGroupBuilder.append("]");
        return String.format("{\"startDate\":\"%s\",\"endDate\":\"%s\",\"timeUnit\":\"month\",%s}",
                DateCalculator.firstDayOfTwoMonthsAgo(),
                DateCalculator.lastDayOfLastMonth(),
                keywordGroupBuilder.toString());
    }

    private String createKeywordGroup(String keyword) {
        return String.format("{\"groupName\":\"%s\",\"keywords\":[\"%s\"]}", keyword, keyword);
    }

    private ResponseEntity<String> sendRequest(String url, HttpHeaders headers, String requestBody) {
        HttpEntity<String> entity = new HttpEntity<>(requestBody, headers);
        return restTemplate.exchange(url, HttpMethod.POST, entity, String.class);
    }

    public String createNaverTrendAPIRequest(List<String> keywords) {
        String url = "https://openapi.naver.com/v1/datalab/search";
        HttpHeaders headers = createHeaders();
        StringBuilder finalResponse = new StringBuilder();
        for (int i = 0; i < keywords.size(); i += 5) {
            List<String> sublist = keywords.subList(i, Math.min(i + 5, keywords.size()));
            String requestBody = createRequestBody(sublist);
            ResponseEntity<String> response = sendRequest(url, headers, requestBody);
            finalResponse.append(response.getBody());
            if (i + 5 < keywords.size()) {
                finalResponse.append("||");
            }
        }
        return finalResponse.toString();
    }
}
4. Controller 클래스 작성 후 Swagger 를 통한 API 요청문 전송, 응답 확인하기
프로젝트에서 제공하는 기본 칵테일들을 List 자료구조로 반환 받는 메서드를 만들어 달라고 팀원분께 요청해 놨다. 리스트에 있는 칵테일들을 5개 씩 순회하면서 요청문을 만들도록 설계했기 때문에, 지금 테스트를 위한 요청문을 보낼 땐 임시로 List<Stirng> 자료구조에 2개의 값만 담아서 요청해 보도록 한다.
응답 본문으로 모히또와 마티니에 대한 ratio 값들이 담겨 왔다. 구조는 아래와 같다.
현재 블로그 작성 기준 2025년 1월 이므로 2024년의 11월과 12월의 값을 가져왔다. 이 두 값의 차이를 가지고
프로젝트에서 제공하는 모든 칵테일들을 정렬하여 검색량이 많아진 TOP  5 칵테일을 도출할 수 있다.
{
  "msg": "요청이 성공됐습니다",
  "code": "SUCCESS",
  "data": "{\"startDate\":\"2024-11-01\",\"endDate\":\"2024-12-31\",\"timeUnit\":\"month\",\"results\":[{\"title\":\"모히또\",\"keywords\":[\"모히또\"],\"data\":[{\"period\":\"2024-11-01\",\"ratio\":94.84311},{\"period\":\"2024-12-01\",\"ratio\":100}]},{\"title\":\"마티니\",\"keywords\":[\"마티니\"],\"data\":[{\"period\":\"2024-11-01\",\"ratio\":82.82075},{\"period\":\"2024-12-01\",\"ratio\":90.97028}]}]}",
  "status": "200 OK"
}
응답을 잘 받아 왔으니, 이제 DTO 객체를 만들어 서버에서 사용하는 객체로 반환하거나, 따로 저장하지 않고 바로 View 로 전달하는 방법을 다음에 이어서 해보도록 하자.
두 방법을 구현해 놓고 Front-end 분들과 회의를 통해 필요한 자료 형태로 전달해주도록 하자.