# [프로젝트] Naver API 응답을 DTO로 변환하여 프로젝트에 사용하기

https://cs-study1.tistory.com/53
[프로젝트] Naver 데이터랩의 통합검색어 트랜드 API 를 SpringBoot 프로젝트를 통해 요청하고 응답받
이전 내용에서는 현재 진행 중인 SpringBoot 프로젝트에서 Google Trend API 를 사용하는 방법을 시도 해 봤다. 이번엔 추가로 국내 사용자들이 많이 이용하는 검색포털인 Naver 의 검색량도 API로 받아와
cs-study1.tistory.com
이전 포스팅에서는 Naver 데이터랩의 통합검색어 트랜드 API 에 대한 요청문을 만들고, SpringBoot Project 에서 이 요청문을 전송하여 응답을 받는 과정까지 진행하였다. 이제 이 요청에 대한 응답문을 서버에서 DTO로 받아들여서 필요한 정보만 추출하고, DB에 저장할 자료구조로 만들던가, View 로 전달할 수 있는 자료구조로 만들어 보도록 하자!
1. 응답문 구조에 맞게 클래스 생성. DTO to Domain 메서드 작성하기
{
  "msg": "요청이 성공됐습니다",
  "code": "SUCCESS",
  "data": "{\"startDate\":\"2024-11-01\",\"endDate\":\"2024-12-31\",\"timeUnit\":\"month\",\"results\":[{\"title\":\"모히또\",\"keywords\":[\"모히또\"],\"data\":[{\"period\":\"2024-11-01\",\"ratio\":94.84311},{\"period\":\"2024-12-01\",\"ratio\":100}]},{\"title\":\"마티니\",\"keywords\":[\"마티니\"],\"data\":[{\"period\":\"2024-11-01\",\"ratio\":82.82075},{\"period\":\"2024-12-01\",\"ratio\":90.97028}]}]}",
  "status": "200 OK"
}
응답문의 구조는 위와 같다. NaverTrendCocktailDTO 클래스를 생성하고, 응답문 구조에 맞게 필드를 작성해준다.
클래스의 구조는 아래처럼 작성하였다.
package org.toastit_v2.feature.trendcocktail.application.dto;

import com.fasterxml.jackson.annotation.JsonCreator;
import com.fasterxml.jackson.annotation.JsonProperty;

import lombok.Getter;
import lombok.NoArgsConstructor;
import org.toastit_v2.feature.trendcocktail.domain.TrendCocktail;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;
import java.util.stream.Collectors;

@Getter
@NoArgsConstructor
public class NaverTrendCocktailDTO {
    @JsonProperty("startDate")
    private String startDate;

    @JsonProperty("endDate")
    private String endDate;

    @JsonProperty("timeUnit")
    private String timeUnit;

    @JsonProperty("results")
    private List<Result> results;

    @JsonCreator
    public NaverTrendCocktailDTO(@JsonProperty("startDate") String startDate,
                                 @JsonProperty("endDate") String endDate,
                                 @JsonProperty("timeUnit") String timeUnit,
                                 @JsonProperty("results") List<Result> results) {
        this.startDate = startDate;
        this.endDate = endDate;
        this.timeUnit = timeUnit;
        this.results = results;
    }

    public TrendCocktail toDomain() {
        List<TrendCocktail.Result> domainResults = results.stream()
                .map(Result::toDomain)
                .collect(Collectors.toList());

        return TrendCocktail.builder()
                .startDate(startDate)
                .endDate(endDate)
                .timeUnit(timeUnit)
                .results(domainResults)
                .build();
    }

    @Getter
    @NoArgsConstructor
    public static class Result {
        @JsonProperty("title")
        private String title;

        @JsonProperty("keywords")
        private List<String> keywords;

        @JsonProperty("data")
        private List<Data> data;

        @JsonCreator
        public Result(@JsonProperty("title") String title,
                      @JsonProperty("keywords") List<String> keywords,
                      @JsonProperty("data") List<Data> data) {
            this.title = title;
            this.keywords = keywords;
            this.data = data;
        }

        public TrendCocktail.Result toDomain() {
            List<TrendCocktail.Result.Data> domainData = data.stream()
                    .map(Data::toDomain)
                    .collect(Collectors.toList());

            return TrendCocktail.Result.builder()
                    .title(title)
                    .keywords(keywords)
                    .data(domainData)
                    .build();
        }
    }

    @Getter
    @NoArgsConstructor
    public static class Data {
        @JsonProperty("period")
        private String period;

        @JsonProperty("ratio")
        private double ratio;

        @JsonCreator
        public Data(@JsonProperty("period") String period,
                    @JsonProperty("ratio") double ratio) {
            this.period = period;
            this.ratio = ratio;
        }

        public TrendCocktail.Result.Data toDomain() {
            return TrendCocktail.Result.Data.builder()
                    .period(period)
                    .ratio(ratio)
                    .build();
        }
    }

    public Map<String, List<Result>> getResultsByKeyword() {
        Map<String, List<Result>> keywordMap = new HashMap<>();
        for (Result result : results) {
            for (String keyword : result.getKeywords()) {
                keywordMap.computeIfAbsent(keyword, k -> new ArrayList<>()).add(result);
            }
        }
        return keywordMap;
    }
}
NaverTrendCocktailDTO
클래스의 구조는 다음과 같다.
클래스 선언 및 필드
◾@Getter: 설명 생락.
◾@NoArgsConstructor: 설명 생략.
◾필드
◽startDate: 응답문에서 데이터 시작 날짜를 나타내는 문자열.
◽endDate:
응답문에서
데이터 종료 날짜를 나타내는 문자열.
◽timeUnit:
응답문에서
시간 단위를 나타내는 문자열.
◽results:
응답문에서
트렌드 결과를 나타내는 Result 객체의 리스트.
생성자
◾@JsonCreator: Jackson 라이브러리의 어노테이션으로, JSON 데이터에서 객체를 생성할 때 사용됨.
◾@JsonProperty: JSON의 속성과 클래스 필드를 매핑하는 데 사용됨.
◾toDomain 메서드 : DTO를 도메인 객체인 TrendCocktail로 변환. results 리스트의 각 Result 객체를 TrendCocktail.Result 도메인 객체로 변환하여 새로운 리스트를 생성.
내부 클래스 Result
◾Result 클래스는 트렌드의 결과를 나타내며, 다음과 같은 필드를 갖는다
◽title: 결과의 제목.
◽keywords: 관련 키워드의 리스트.
◽data: 트렌드 데이터의 리스트 (Data 객체).
◽toDomain 메서드를 통해 Result DTO를 TrendCocktail.Result 도메인 객체로 변환.
내부 클래스 Data
◾Data 클래스는 각 트렌드 데이터의 세부 정보를 나타내며, 다음과 같은 필드를 갖는다
◽period: 데이터의 기간.
◽ratio: 비율을 나타내는 double 값.
◽toDomain 메서드를 통해 Data DTO를 TrendCocktail.Result.Data 도메인 객체로 변환.
getResultsByKeyword 메서드
이 메서드는 키워드를 기준으로 결과를 그룹화하여 Map<String, List<Result>> 형태로 반환.
각 키워드에 대해 해당 키워드를 포함하는 Result 객체 리스트를 생성하여 반환.
2. Domain 클래스 작성 및 Domain to Entity 메서드 작성하기
응답문을 DTO로 받고 Domain 으로 변환하는 메서드를 작성했기 때문에, 서버에서 사용할 수 있는 Domain 클래스를 생성하고, ratio 필드를 추출해서 검색량이 증가한 N개의 키워드만 반환하는 메서드를 만들어 준다. 이렇게 소팅 된 키워드들만을 DB에 저장하기 위해 Entity 로 변환하는 메서드도 만들어준다.
@Builder
@Getter
public class TrendCocktail {
    private String startDate;
    private String endDate;
    private String timeUnit;
    private List<Result> results;

    @Getter
    @Builder
    public static class Result {
        private String title;
        private List<String> keywords;
        private List<Data> data;

        @Getter
        @Builder
        public static class Data {
            private String period;
            private double ratio;
        }
    }

    public static List<String> getTopFiveKeywords(Map<String, List<NaverTrendCocktailDTO.Result>> keywordMap) {
        List<Map.Entry<String, Double>> keywordDifferences = new ArrayList<>();
        for (Map.Entry<String, List<NaverTrendCocktailDTO.Result>> entry : keywordMap.entrySet()) {
            String keyword = entry.getKey();
            List<NaverTrendCocktailDTO.Result> results = entry.getValue();
            double maxDifference = calculateMaxDifference(results);
            if (maxDifference > 0) {
                keywordDifferences.add(new AbstractMap.SimpleEntry<>(keyword, maxDifference));
            }
        }
        return getTopKeywords(keywordDifferences);
    }

    private static double calculateMaxDifference(List<NaverTrendCocktailDTO.Result> results) {
        if (results == null || results.isEmpty()) {
            return 0;
        }
        return results.stream()
                .mapToDouble(result -> calculateRatioDifference(result))
                .max()
                .orElse(0);
    }

    private static double calculateRatioDifference(NaverTrendCocktailDTO.Result result) {
        if (result.getData().size() > 1) {
            double ratio1 = result.getData().get(0).getRatio();
            double ratio2 = result.getData().get(1).getRatio();
            return ratio1 - ratio2;
        }
        return 0;
    }

    private static List<String> getTopKeywords(List<Map.Entry<String, Double>> keywordDifferences) {
        keywordDifferences.sort((entry1, entry2) -> Double.compare(entry2.getValue(), entry1.getValue()));
        return keywordDifferences.stream()
                .limit(5)
                .map(Map.Entry::getKey)
                .collect(Collectors.toList());
    }

    public static List<TrendCocktailEntity> convertToEntities(List<String> keywords) {
        return keywords.stream()
                .map(keyword -> {
                    TrendCocktailEntity entity = new TrendCocktailEntity();
                    entity.setName(keyword);
                    return entity;
                })
                .collect(Collectors.toList());
    }
}
도메인 클래스인 TrendCocktail 클래스의 구조는 다음과 같다.
pirvate 로 선언된 필드들은 응답문의 내용과 같으므로 설명 생략
getTopFiveKeywords 메서드
getTopKeywords 메서드를 통해 최대 차이가 있는 상위 5개의 키워드를 리스트 형태로 반환.
calculateMaxDifference 메서드
calculateRatioDifference 메서드를 통해 나온 반환 값들을 가지고 스트림을 사용하여
각 Result 객체의 비율 차이를 계산하고
최대값을 반환
.
결과가 비어 있거나 null일 경우 0을 반환한다.
calculateRatioDifference 메서드
주어진 Result 객체의 첫 번째 데이터와 두 번째 데이터 간의 비율 차이를 계산한다.
즉 전전월 검색량 - 전월 검색량 의 차이 값을 반환.
데이터가 두 개 이상일 경우에만 차이를 계산하며, 그렇지 않으면 0을 반환.
getTopKeywords 메서드
calculateMaxDifference 메서드를 통해 계산된 키워드들의 검색량 차이 리스트를
내림차순으로 정렬하고, 상위 5개의 키워드를 반환한다.
convertToEntities 메서드
getTopFiveKeywords 메서드를 통해 나온 5개의 키워드 리스트를 TrendCocktailEntity 객체로 변환.
검색량 차이 계산 ->  차이 값으로 키워드 정렬 -> 정렬된 순서에서 5개를 도출 ->  키워드 5개를 List 로 반환
List<String> 으로 반환된 Domain 클래스 (TrendCocktail)의 메서드는 ThymeLeaf 나 view 에서 사용 가능한 자료구조 이므로, convertToEntities 메서드를 통해, TrendCocktail 타입으로 변경해주는 작업을 하여, Entity 로 DB에 저장할 수 있는 메서드 까지 만들어 주었다.
3. Entity 클래스 작성
convertToEntities 메서드를 통해 만들어진 TrendCocktail 타입 인스턴스는 5개의 칵테일 키워드만 가지고 있는 List 자료구조이다. 즉 [마티니,모히또,멘하탄,피나콜라다,블루하와이] 형식으로 되어 있다.
따라서 엔티티 저장시 반복문을 사용해서 칵테일의 키워드만 사용하면 되므로 id 와 name 만 필드로 선언 해 놓으면 될 것이다.
@Entity
@Setter
@Getter
public class TrendCocktailEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    
    Long id;

    String name;
}
4.마무리
전체적인 흐름상 응답 -> DTO -> Domain -> Entity 흐름으로 작성했는데, 응답문이 복잡하다보니 문자열을 Parsing 하는 메서드들이 복잡해 져서 메서드의 코드양이 많아졌다.
문자열을 Parsing 하고 각각의 클래스들을 변환하는 메서드들에 대한 테스트 코드들도 작성했는데, 이 테스트 코드들에 대한 구조 및 실행은 다음에 포스팅 하기로 한다.
(팀 전체 코드 병합 스케줄이 있어서 전체 브랜치들을 통합한 후에 테스트를 다시 할 예정이기 때문)