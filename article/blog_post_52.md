# [프로젝트] SerpAPI + SpringBoot 로 Google Trend API 응답을 서버에서 활용하기

이전글
https://cs-study1.tistory.com/48
응답문의 구조에서 필요한 데이터는 현재 날짜를 기준으로, 전 달의
data , query, value 값 이다.
이러한 값만 이용하기 위해서, 일단 응답문에 대응하는 DTO 를 만들고, 이 DTO 에서 필요한 값을 추출하기로 한다.
1. DTO 클래스 작성
응답 데이터를 담기 위한 DTO 클래스를 생성한다. 필요한 필드만 명시하여 서버로 가져올 때 불필요한 리소스 낭비를 줄인다.
(필요한 데이터 = 이전 달의 data , query, value 값 )
DateCalculator 클래스를 만들어놨고, 정적 메서드들로 필요한 날짜들을 반환하는 기능들을 모아 놓았다.
API의 응답을 서버에서 사용하기 위한 객체로 가져오기 위한 DTO 클래스
필요한 날짜들을 가져오기 위해 메서드로 정의하여 모아놓은 DataCalculator 클래스
2. API에 대한 응답을 DTO 로 받아오도록 DTO convert  메서드와 문자열 parsing 메서드를 생성한다.
기존의 API 요청문에서 Map<String,Object> 타입으로 응답문을 리턴받도록 했기 때문에, Map<String,Object> 타입과 키워드를 인자로 입력 받아서 DTO 로 변환하는 메서드를 만들고, DTO 변환 시에 서버의 날자를 기준으로 이전 달의 검색량들을 더해서 가지고 있도록 구현한다.
{
"date": "Dec 8 – 14, 2024",
"timestamp": "1733616000",
"values": [
{
"query": "마티니",
"value": "71",
"extracted_value": 71
}
]
},
데이터 타입이 위와 같은 형식이고 날짜 타입이 "
Dec 8 – 14, 2024" 인 경우, 또
"Dec 29, 2024 – Jan 4, 2025" 인 경우로 응답이 오기 때문에
날짜 범위를 Parsing 하는 메서드도 추가한다. 이전달의 첫 날, 이전달의 마지막 날 같은 값은 앞서 만들어 놓은 DateCalculator 클래스를 이용한다.
DTO 변환 메서드
public GoogleTrendCocktailDTO googleTrendAPIConvertDTO(Map<String, Object> apiResponse, String query) {
        GoogleTrendCocktailDTO dto = new GoogleTrendCocktailDTO();
        dto.setQuery(query);

        // "data"에서 필요한 값을 추출
        Map<String, Object> data = (Map<String, Object>) apiResponse.get("data");
        Map<String, Object> interestOverTime = (Map<String, Object>) data.get("interest_over_time");
        List<Map<String, Object>> timelineData = (List<Map<String, Object>>) interestOverTime.get("timeline_data");

        // 현재 날짜 기준으로 전 달 계산

        int totalValue = 0;

        // timelineData에서 전 달의 extracted_value를 합산
        for (Map<String, Object> entry : timelineData) {
            String dateRange = (String) entry.get("date");
            LocalDate startDate = parseDateRange(dateRange);

            // 전 달인 경우에만 extracted_value 합산
            if (!startDate.isBefore(DateCalculator.firstDayOfLastMonth()) && !startDate.isAfter(DateCalculator.lastDayOfLastMonth_notFormatting())) {
                List<Map<String, Object>> values = (List<Map<String, Object>>) entry.get("values");
                if (!values.isEmpty()) {
                    // Integer로 가져오고 필요 시 변환
                    totalValue += (Integer) values.get(0).get("extracted_value");
                }
            }
        }
        dto.setValue(totalValue);

        // previousMonthData 설정
        String month = DateCalculator.firstDayOfLastMonth().getMonth().name().substring(0, 3).toUpperCase(); // 예: "DEC"
        String year = String.valueOf(DateCalculator.firstDayOfLastMonth().getYear()); // 예: "2024"
        dto.setPreviousMonthData(month + " - " + year);

        return dto;
    }
날짜 범위를 parsing 하는 메서드
private LocalDate parseDateRange(String dateRange) {
        // 다양한 구분자 처리
        String[] parts = dateRange.split("–| - "); // em dash와 hyphen 모두 처리

        // 형식이 올바르지 않은 경우 예외 처리
        if (parts.length < 2) {
            throw new IllegalArgumentException("Invalid date range format: " + dateRange);
        }

        // 시작 날짜 문자열 생성
        String startDateString = parts[0].trim();
        String endDateString = parts[1].trim();

        // 불필요한 정보 제거 (예: ", 2025"와 같은 부분)
        startDateString = startDateString.replaceAll(",\\s*\\d{4}$", ""); // 연도 제거
        endDateString = endDateString.replaceAll(",\\s*\\d{4}$", ""); // 연도 제거

        startDateString += ", " + parts[1].trim().split(",")[1].trim(); // 올바른 형식으로 연도 추가

        // DateTimeFormatter 설정
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMM d, yyyy", Locale.ENGLISH);

        // 날짜 파싱
        return LocalDate.parse(startDateString, formatter);
    }
리...리팩토링은 일단 나중에 하도록 하자...
DTO 변환이 완료되면 "12월", "마니티"의 검색량인 ( 73 + 71 + 81 + 80 = 305 ) 가 객체의 필드값으로 되어 있을 것이고. dto.getValue() 값이 305 로 나오는지 테스트 코드를 작성하여 확인한다!
12월과 1월이 함께 겹치는 구간은 검색량에서 제외하도록 하였다.
3.테스트 코드 작성
단위 테스트 코드와 리팩토링은 잠시 미뤄두고 일단 응답이 DTO로 변환되는지, 또 문자열 parsing  이 제대로 되면서 DTO 의 필드 값들에 기대한 값들이 도출되는지 확인하는 테스트 코드를 작성한다.
API 응답의 경우, 월 제한량이 있기 때문에 매번 호출하여 테스트를 수행하는 것 보다는, 이미 호출 된 메서드를 .json 타입으로 저장하여 이를 활용하는 방법으로 테스트를 진행하도록 한다.
응답 본문 전체를 작성하고(복붙 하고)
src / test / resources
아래에 파일명.json 으로 저장한다.
googleResponseExample.json 으로 저장해주었다.
해당 파일의 내용은 응답 본문 전체를 그대로 옮겨 놓았다.
해당 파일을 응답문으로 사용하려면 ClassPathResource 타입의 인스턴스로 생성 (인자를 파일명으로 전달) 하고, ObjectMapper를 이용하여 응답문의 타입으로 반환 해주면 되는데, 복잡하니 실제 사용한 코드를 보면 아래와 같다
전체 테스트 코드의 주요 로직은
응답문을 DTO로 변환하고, 제대로 객체로 변환 됐다면 DTO의 인스턴스.getQuery() 는 검색어 "마티니" 와 같아야 한다.
DTO의 인스턴스.getValue() 는 12월의 "마티니" 검색량의 총 합인 305 가 리턴 되어야 한다.
DTO의 인스턴스.getPreviousMonthDate() 는 내가 직접 설정한 Month - year (DEC - 2024) 타입으로 나와야 한다.
@SpringBootTest
class GoogleTrendCocktailDTOTest {

    private final ObjectMapper objectMapper = new ObjectMapper();
    private String query = "마티니";

    @Test
    void googleTrendAPIConvertDTO() throws IOException {

        ClassPathResource classPathResource = new ClassPathResource("googleResponseExample.json");
        Map<String, Object> googleAPIResponse = objectMapper.readValue(classPathResource.getInputStream(), Map.class);
        
        GoogleTrendCocktailDTO googleTrendCocktailDTO = new GoogleTrendCocktailDTO();
        GoogleTrendCocktailDTO dto = googleTrendCocktailDTO.googleTrendAPIConvertDTO(googleAPIResponse, query);


        Assertions.assertThat(dto.getQuery()).isEqualTo(query);
        Assertions.assertThat(dto.getValue()).isEqualTo(305);
        Assertions.assertThat(dto.getPreviousMonthData()).isEqualTo(DateCalculator.lastMonth());
    }
}
언제나 기분이 좋은 초록불이다.
4.트러블 슈팅과 남은 일
<트러블 슈팅>
Google Trend API 요청문을 만드는 클래스에서 메서드와 필드를 모두 static 으로 만들어서, Service 클래스에서는 className.method() 로 간단하게 사용하려고 하였다.
하지만 요청문을 만드는 클래스에서 API key 를 필드로 가지고 있었고, 이 필드도 static 으로 선언하니, 실제 key 값이 주입되기 전에 메모리에 올라가서 Null 값을 가지게 되었다.
static 으로 선언한 요청문을 실행하니 권한이 없다는 401 에러가 발생하였고, 요청문을 만드는 클래스와 해당 필드와 메서드를 모두 static 에서 제외 하였더니, 요청문에 대한 응답이 제대로 반환 되었다.
<남은 일>
단위 테스트 코드 작성 ( 요청문을 만드는 메서드 및 DB 저장 메서드 등)
DTO 객체를 통해 View로 전달할 자료구조를 만들지, DB에 저장하는 로직을 구현할 지 회의를 통해 정해야 한다.
현재 1개의 키워드의 대한 응답을 받았는데, 한번에 여러 키워드를 요청하여 응답을 받을지, 한 키워드씩 응답을 받아서 특정 자료구조에 저장할 지 회의를 통해 정해야 한다.
메서드 들에 대한 리팩토링을 진행해야 한다.
밀린 커밋....을 해야 한다....ㅠㅠ