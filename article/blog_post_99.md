# [Project] API 응답문 데이터 통일화 및 알고리즘 적용하기 -1

많은 사람들이 얘기한다.
응집도는 낮고 결합도는 높여야, 향후 유지보수가 쉬운 코드가 된다고.
하지만 만들어놓은지 좀 된 기능들은, 객체지향적 설계와 응집도를 떠나서 기억이 잘 나지 않는다.
대단한 기능은 아니지만, 두 검색엔진의 키워드 검색량(Google, Naver)을 API 응답으로 받아와서, 문자열을 pasing 하고,
검색량 증감을 기준으로 내림차순 정렬하는 로직을 완성했었다.
하지만 새로운 알고리즘의 도입으로 응답문의 문자열 Parsing , 도메인 변환, 엔티티변환, DB 저장 로직까지 새로 만드는 것이 낫다고 판단하였다.
이젠, 추천 알고리즘을 새로 도입했으니, 알고리즘만 수정하면 기획자의 의도대로 추천 알고리즘을 적용할 수 있도록 기능을 개발해 놓아야겠다.
오늘 작업할 전체적인 흐름은 아래와 같다.
요청문 생성 후 응답문 반환 확인   -> 응답문을 DTO 로 변환 및 데이터 검증   ->  DTO 파싱 메서드 만들기   -> 파싱 메서드 검증
1. .API 요청 및 응답이 제대로 이뤄지는지 확인하기
서버를 다시 띄우고, API 요청 메서드의 매개변수를 통일해주었다. Naver API 의 경우 한 번에 5개의 키워드에 대한 응답을 받을 수 있어서 매개변수로 List<String> 으로 요청했고, Google API 의 경우 한 번에 한개의 키워드에 대한 응답을 받을 수 있어서, 매개변수로 String 으로 요청했었다.
하지만 두 API 를 동시에 요청하고, 자료구조를 통해 키워드:총점 을 계산하여 DB 에 저정하기 위해 매개변수를 통일하였다.
혹시나 요청이 실패할까 조마조마 하며 요청문을 전송...!
Goolge API 응답문
Naver API 응답문
요청문을 성공적으로 요청하고 응답분을 회신 받았다.
Naver 응답문은 해당 날짜를 요청하기 때문에 보다 간단하게 Parsing 할 수 있어 보였고, Google 응답문은 특정 날짜를 입력하여 요청할 수 없기 때문에, 요청일을 기준으로 1년단위로 응답문이 생성되기 때문에, 시스템 날짜를 기준으로 Pasring 하도록 한다.
2. 응답문 검증 테스트(DTO 가 제대로 응답문과 매핑하는지 확인)
API 요청을 매번 할 수 없으니, 성공적으로 수신된 응답문을 .json 파일로 저장하고, 이 데이터를 String 으로 받아들여 DTO 로 잘 매핑되는지 확인하는 테스트코드를 작성한다.
import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;
import org.toastit_v2.feature.trendcocktail.application.dto.GoogleTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.dto.NaverTrendResponseDTO;

class TrendCocktailControllerTest {

    private String readJsonFromFile(String fileName) throws Exception {
        ClassPathResource resource = new ClassPathResource(fileName);
        return new String(Files.readAllBytes(Paths.get(resource.getURI())), StandardCharsets.UTF_8);
    }

    @Test
    @DisplayName("NaverTrendResponseDTO 생성 테스트")
    void fromNaverResponseFileTest() throws Exception {
        // test/resources 폴더에 저장된 naverResponse.json 파일을 읽어옴
        String jsonResponse = readJsonFromFile("naverResponseExample.json");

        // JSON 문자열(API 응답문)을 DTO 객체로 변환
        NaverTrendResponseDTO result = NaverTrendResponseDTO.fromJson(jsonResponse);

        // DTO 객체가 정상적으로 생성되었는지 검증
        assertNotNull(result);
        assertNotNull(result.getData());

        // 응답문의 날짜와 DTO 객체의 날짜 데이터 일치여부 검증
        assertEquals("2025-01-01" , result.getData().getStartDate());
        assertEquals("2025-02-28" , result.getData().getEndDate());

        //DTO 객체에 저장된 칵테일 키워드 값 출력
        System.out.println(result.getData().getResults().get(0).getKeywords());

        // 응답문의 검색량 값과 DTO 객체의 검색량 값 일치여부 검증
        assertEquals(100,result.getData().getResults().get(0).getData().get(0).getRatio());
        assertEquals(86.46507,result.getData().getResults().get(0).getData().get(1).getRatio());
    }

    @Test
    @DisplayName("GoogleTrendResponseDTO 생성 테스트")
    void fromGoogleResponseFileTest() throws Exception {
        // test/resources 폴더에 저장된 googleResponse.json 파일을 읽어옴
        String jsonResponse = readJsonFromFile("googleResponseExample.json");

        // JSON 문자열(API 응답문)을 DTO 객체로 변환
        GoogleTrendResponseDTO result = GoogleTrendResponseDTO.fromJson(jsonResponse);

        // DTO 객체가 정상적으로 생성되었는지 검증
        assertNotNull(result);
        assertNotNull(result.getData());

        //DTO 객체의 칵테일 키워드 검증
        String keyword = result.getData().getSearch_parameters().get("q").toString();
        assertEquals("마티니", keyword);
    }
}
응답문이 DTO 객체에 잘 매핑되어 원하는 값을 추출할 수 있게 되었다.
3. 응답문 Pasring 메서드 만들기
이제 volumePasring 이라는 인터페이스를 만들고, 각각 응답문에 맞게 데이터를 Parsing 하는 구현체를 만들어준다.
- 인터페이스 생성
import java.util.Map;

public interface VolumeParsing {
    /**
     * 각 칵테일 키워드에 대해 계산된 volume 값을 반환합니다.
     * 계산 공식: 두번째 ratio 값 - 첫번째 ratio 값
     *
     * @return Map with key: 칵테일 키워드, value: 계산된 volume 값.
     */
    Map<String, Double> parseVolume();
}
- Naver API 응답문 작업용 코드
import org.toastit_v2.feature.trendcocktail.application.dto.NaverTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.volumeParsing.VolumeParsing;
import java.util.HashMap;
import java.util.Map;

public class NaverDTOParsing implements VolumeParsing {

    private final NaverTrendResponseDTO naverTrendResponseDTO;

    public NaverDTOParsing(NaverTrendResponseDTO naverTrendResponseDTO) {
        this.naverTrendResponseDTO = naverTrendResponseDTO;
    }

    @Override
    public Map<String, Double> parseVolume() {
        Map<String, Double> volumeMap = new HashMap<>();
        if (naverTrendResponseDTO == null || naverTrendResponseDTO.getData() == null
                || naverTrendResponseDTO.getData().getResults() == null) {
            return volumeMap;
        }
        for (NaverTrendResponseDTO.Result result : naverTrendResponseDTO.getData().getResults()) {
            if (result.getData() != null && result.getData().size() >= 2) {
                double firstRatio = result.getData().get(0).getRatio();
                double secondRatio = result.getData().get(1).getRatio();
                double computedVolume = secondRatio - firstRatio;
                volumeMap.put(result.getTitle(), computedVolume);
            }
        }
        return volumeMap;
    }
}
- Google 응답문 작업용 코드
import org.toastit_v2.feature.trendcocktail.application.dto.parser.volumeParsing.VolumeParsing;
import java.util.Map;
import org.toastit_v2.feature.trendcocktail.application.dto.GoogleTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.service.utilly.DateCalculator;
import java.time.LocalDate;
import java.time.format.DateTimeFormatter;
import java.util.*;
import java.util.stream.Collectors;

public class GoogleDTOParsing implements VolumeParsing {

    private final GoogleTrendResponseDTO googleTrendResponseDTO;

    public GoogleDTOParsing(GoogleTrendResponseDTO googleTrendResponseDTO) {
        this.googleTrendResponseDTO = googleTrendResponseDTO;
    }

    @Override
    public Map<String, Double> parseVolume() {
        Map<String, Double> volumeMap = new HashMap<>();
        if (googleTrendResponseDTO == null ||
                googleTrendResponseDTO.getData() == null ||
                googleTrendResponseDTO.getData().getInterest_over_time() == null ||
                googleTrendResponseDTO.getData().getInterest_over_time().getTimeline_data() == null) {
            return volumeMap;
        }

        List<GoogleTrendResponseDTO.TimelineData> timelineList =
                googleTrendResponseDTO.getData().getInterest_over_time().getTimeline_data();

        LocalDate firstDayLastMonth = DateCalculator.firstDayOfLastMonth();
        LocalDate lastDayLastMonth = DateCalculator.lastDayOfLastMonth_notFormatting();
        LocalDate firstDayTwoMonthsAgo = LocalDate.parse(DateCalculator.firstDayOfTwoMonthsAgo(),
                DateTimeFormatter.ofPattern("yyyy-MM-dd"));
        LocalDate lastDayTwoMonthsAgo = firstDayTwoMonthsAgo.withDayOfMonth(firstDayTwoMonthsAgo.lengthOfMonth());

        List<GoogleTrendResponseDTO.TimelineData> filteredList = timelineList.stream()
                .filter(entry -> {
                    try {
                        LocalDate startDate = parseDateRange(entry.getDate());
                        return (startDate != null) &&
                                ((!startDate.isBefore(firstDayTwoMonthsAgo) && !startDate.isAfter(lastDayTwoMonthsAgo)) ||
                                        (!startDate.isBefore(firstDayLastMonth) && !startDate.isAfter(lastDayLastMonth)));
                    } catch (Exception e) {
                        return false;
                    }
                })
                .collect(Collectors.toList());
                
        if (filteredList.size() < 2) {
            return volumeMap;
        }

        GoogleTrendResponseDTO.TimelineData firstEntry = filteredList.get(0);
        GoogleTrendResponseDTO.TimelineData secondEntry = filteredList.get(1);

        if (firstEntry.getValues() != null && !firstEntry.getValues().isEmpty() &&
                secondEntry.getValues() != null && !secondEntry.getValues().isEmpty()) {
            double firstValue = firstEntry.getValues().get(0).getExtracted_value();
            double secondValue = secondEntry.getValues().get(0).getExtracted_value();
            double computedVolume = secondValue - firstValue;
            String query = firstEntry.getValues().get(0).getQuery();
            volumeMap.put(query, computedVolume);
        }
        return volumeMap;
    }

    private LocalDate parseDateRange(String dateRange) {
        if (dateRange == null || dateRange.isEmpty()) {
            throw new IllegalArgumentException("Date range cannot be null or empty");
        }
 
        String[] parts = dateRange.split("–|-");
        if (parts.length < 2) {
            throw new IllegalArgumentException("Invalid date range format: " + dateRange);
        }
        String startDatePart = parts[0].trim();
        String secondPart = parts[1].trim();
        String[] subParts = secondPart.split(",");
        String year = (subParts.length > 1) ? subParts[1].trim() : String.valueOf(LocalDate.now().getYear());
        String fullDate = startDatePart + ", " + year;  
        DateTimeFormatter formatter = DateTimeFormatter.ofPattern("MMM d, yyyy", Locale.ENGLISH);
        return LocalDate.parse(fullDate, formatter);
    }
}
4. 각각의 Pasing 메서드가 키워드: 점수 형태로 데이터를 잘 Pasing 했는지, 테스트 코드를 작성한다.
- Google 의 DTO Pasing Test 코드. Parsing 한 결과를 출력하도록 하였다.
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;
import org.toastit_v2.feature.trendcocktail.application.dto.GoogleTrendResponseDTO;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

class GoogleDTOParsingTest {

    private String readJsonFromFile(String fileName) throws Exception {
        ClassPathResource resource = new ClassPathResource(fileName);
        return new String(Files.readAllBytes(Paths.get(resource.getURI())), StandardCharsets.UTF_8);
    }

    @Test
    @DisplayName("구글 응답문 파싱 테스트")
    void fromGoogleResponseFileTest() throws Exception {
        // test/resources 폴더에 저장된 googleResponse.json 파일을 읽어옴
        String jsonResponse = readJsonFromFile("googleResponseExample.json");

        // JSON 문자열(API 응답문)을 DTO 객체로 변환
        GoogleTrendResponseDTO result = GoogleTrendResponseDTO.fromJson(jsonResponse);

        GoogleDTOParsing google = new GoogleDTOParsing(result);

        Map<String, Double> volumeMap = google.parseVolume();
        volumeMap.forEach((keyword, volume) ->
                System.out.println("키워드 : " + keyword + ", 검색량 차이: " + volume)
        );
    }
}
- Naver 의 DTO Pasing Test 코드. Parsing 한 결과를 출력하도록 하였다.
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;
import org.toastit_v2.feature.trendcocktail.application.dto.NaverTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.volumeParsing.VolumeParsing;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Map;

class NaverDTOParsingTest {

    private String readJsonFromFile(String fileName) throws Exception {
        ClassPathResource resource = new ClassPathResource(fileName);
        return new String(Files.readAllBytes(Paths.get(resource.getURI())), StandardCharsets.UTF_8);
    }

    @Test
    @DisplayName("네이버 응답문 파싱 테스트")
    void fromNaverResponseFileTest() throws Exception {
        String jsonResponse = readJsonFromFile("naverResponseExample.json");

        NaverTrendResponseDTO result = NaverTrendResponseDTO.fromJson(jsonResponse);

        VolumeParsing naver = new NaverDTOParsing(result);
        Map<String, Double> volumeMap = naver.parseVolume();
        volumeMap.forEach((keyword, volume) ->
                System.out.println("키워드 : " + keyword + ", 검색량 차이: " + volume)
        );
    }
}
각각의 응답문에 대하여 Pasring 메서드가 잘 작동하여, 검색일 기준으로 [2개월 전 검색량 - 1개월전 검색량] 을 계산하여
칵테일 키워드와 함께 잘 반환하고 있는 것을 확인할 수 있다.
내일부터는 이 통일화된 데이터를 알고리즘에 맞게 계산하여 자료구조에 저장하고, 한번에 DB 에 저장하는 로직을 만들어야겠다!