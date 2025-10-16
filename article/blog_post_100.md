# [Project] API 응답문 데이터 통일화 및 알고리즘 적용하기 -2

https://cs-study1.tistory.com/99
[Project] API 응답문 데이터 통일화 및 알고리즘 적용하기 -1
많은 사람들이 얘기한다.응집도는 낮고 결합도는 높여야, 향후 유지보수가 쉬운 코드가 된다고.하지만 만들어놓은지 좀 된 기능들은, 객체지향적 설계와 응집도를 떠나서 기억이 잘 나지 않는
cs-study1.tistory.com
어제의 작업을 통해 각 API에 대한 요청 및 응답을 확인했고, 응답문을 내가 사용할 수 있게 Pasring 하는 작업을 한 뒤 테스트 코드로 검증하였다.
오늘은 Pasring 된 API 응답문을 도메인 객체로 전환할 수 있게, 도메인 클래스를 설계하고, 이 도메인 클래스에서 추천 알고리즘을 적용하여 [키워드 : 총점] 의 형식으로 만드려고 한다. 이 때 비로그인 유저와 로그인 유저가 각각 다른 추천 알고리즘 공식을 가지고 있기 때문에, 도메인에는 총점의 필드를 2개로 설정할 것이고, 이렇게 완성된 도메인을 DB에 저장하기 위한 엔티티로 변환 하려 한다.( 마찬가지로 모든 작업들에 대한 테스트코드 작성으로 메서드의 동작을 검증한다.)
Pasring된 DTO -> 도메인 변환, 알고리즘 적용 -> 엔티티 변환 -> DB 에 저장
1. Parsing 된 DTO 값을 인자로 받는 Domain  클래스 생성
도메인 객체는 칵테일 키워드, Google 검색량 차이 값, Naver 검색량 차이 값, 좋아요갯수, 총 조회수 를 필드로 갖는다.
또 로그인 유저와, 비로그인 유저별로 총점을 다르게 계산하는 메서드를 갖고, 또 DTO 를 도메인으로 변환하는 메서드도 갖는다.
마지막으로 엔티티로 변환하기 위해 좋아요, 조회수를 포함하는 converToEntity 메서드도 포함한다.
사실상 가장 많은 변환 작업 및, 알고리즘 계산 역할도 하는 핵심적인 친구이다.
아래는 작성한 도메인 클래스이다.
public class TrendCocktail {

    private String keyword;
    private double googleValue;
    private double naverValue;
    private int likeCount;
    private int totalViews;

    /**
     * DTO 파싱 결과로 얻은 데이터를 인자로 받아 도메인 객체를 생성합니다.
     * 예: keyword = "마티니", googleValue = 20, naverValue = -6
     *
     * @param keyword     칵테일 키워드
     * @param googleValue Google API 검생량 차이 값 (전전월 값 - 전월 값)
     * @param naverValue  Naver API 검색량 차이 값 (전전월 값 - 전월 값)
     * @return 생성된 TrendCocktail 도메인 객체
     */
    public static TrendCocktail convertToDomain(String keyword, Double googleValue, Double naverValue) {
        return TrendCocktail.builder()
                .keyword(keyword)
                .googleValue(googleValue)
                .naverValue(naverValue)
                .build();
    }

    /**
     * 로그인 유저의 총점계산 알고리즘
     * 총점 = googleValue + naverValue + 좋아요 + 조회수
     */
    public double calculateTotalScoreForLoginUser() {
        return googleValue * 0.92 + naverValue * 0.70 + likeCount * 0.6 + totalViews * 0.4;
    }

    /**
     * 비로그인 유저의 총점계산 알고리즘
     * 총점 = googleValue + naverValue
     */
    public double calculateTotalScoreForNonLoginUser() {
        return googleValue * 0.92 + naverValue * 0.70;
    }

    /**
     *
     * @param "칵테일에 대한 총 좋아요 갯수 입니다"
     * @param "칵테일에 대한 총 조회수 입니다"
     * @return DB 저장용 엔티티 반환
     */
    public TrendCocktailEntity convertToEntity(int likeCount, int totalViews) {
        TrendCocktail updatedDomain = TrendCocktail.builder()
                .keyword(this.keyword)
                .googleValue(this.googleValue)
                .naverValue(this.naverValue)
                .likeCount(likeCount)
                .totalViews(totalViews)
                .build();

        return TrendCocktailEntity.builder()
                .name(updatedDomain.getKeyword())
                .loginTotalScore(updatedDomain.calculateTotalScoreForLoginUser())
                .nonLoginTotalScore(updatedDomain.calculateTotalScoreForNonLoginUser())
                .build();
    }
}
2. Domain (TrendCocktail) 이 제대로 생성되고, Entity 로 변환되는지 테스트
import org.junit.jupiter.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.core.io.ClassPathResource;
import org.toastit_v2.feature.trendcocktail.application.dto.GoogleTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.dto.NaverTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.GoogleDTOParsing;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.NaverDTOParsing;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.volumeParsing.VolumeParsing;
import org.toastit_v2.feature.trendcocktail.infrastructure.persistence.mysql.entity.TrendCocktailEntity;

import java.nio.channels.AsynchronousServerSocketChannel;
import java.nio.charset.StandardCharsets;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.util.Collection;
import java.util.Map;
import java.util.Set;

import static org.junit.jupiter.api.Assertions.*;

class TrendCocktailTest {

    private String readJsonFromFile(String fileName) throws Exception {
        ClassPathResource resource = new ClassPathResource(fileName);
        return new String(Files.readAllBytes(Paths.get(resource.getURI())), StandardCharsets.UTF_8);
    }

    private TrendCocktail trendCocktail;
    private String googleKeyword ;
    private Double googleValue ;
    private String naverKeyword ;
    private Double naverValue ;
    private int likeCount = 50;
    private int totalView = 100;

    @BeforeEach
    void setUp() throws Exception {
        // GoogleDTO -> Parsing 과정 -> googleKeyword : 칵테일 이름, googleValue : 검색량 차이
        String googleResponse = readJsonFromFile("googleResponseExample.json");
        GoogleTrendResponseDTO googleResult = GoogleTrendResponseDTO.fromJson(googleResponse);
        GoogleDTOParsing google = new GoogleDTOParsing(googleResult);
        Map<String, Double> googleVolume = google.parseVolume();

        for (Map.Entry<String, Double> entry : googleVolume.entrySet()) {
            googleKeyword = entry.getKey();
            googleValue = entry.getValue();
        }

        // NaverDTO -> Parsing 과정 -> naverKeyword : 칵테일 이름, naverValue : 검색량 차이
        String naverResponse = readJsonFromFile("naverResponseExample.json");
        NaverTrendResponseDTO naverResult = NaverTrendResponseDTO.fromJson(naverResponse);
        VolumeParsing naver = new NaverDTOParsing(naverResult);
        Map<String, Double> naverVolume = naver.parseVolume();

        for (Map.Entry<String, Double> entry : naverVolume.entrySet()) {
            naverKeyword = entry.getKey();
            naverValue = entry.getValue();
        }
    }

    @Test
    @DisplayName("도메인 생성 및 데이터 검증")
    void domainCreateTest() throws Exception {
        //Domain 생성 및 검증
        trendCocktail = TrendCocktail.convertToDomain(googleKeyword, googleValue, naverValue);
        Assertions.assertEquals(googleKeyword,trendCocktail.getKeyword());
        Assertions.assertEquals(googleValue,trendCocktail.getGoogleValue());
        Assertions.assertEquals(naverValue,trendCocktail.getNaverValue());
    }

    @Test
    @DisplayName("도메인 -> 엔티티 변환 테스트")
    void domainToEntityTest() throws Exception {
        trendCocktail = TrendCocktail.convertToDomain(googleKeyword, googleValue, naverValue);
        TrendCocktailEntity trendCocktailEntity = trendCocktail.convertToEntity(likeCount, totalView);

        Assertions.assertEquals(googleKeyword,trendCocktailEntity.getName());
        Assertions.assertEquals(trendCocktailEntity.getNonLoginTotalScore(),(googleValue*0.92+naverValue*0.70));
        Assertions.assertEquals(trendCocktailEntity.getLoginTotalScore(),(googleValue*0.92+naverValue*0.70+likeCount*0.6+totalView*0.4));
    }
}
테스트에 성공!
테스트 방법은, DTO parsing 객체와 Domain이 같은 데이터를 가지고 있는지 검증했고
Domain 이 Entity 로 변환되고서도 같은 데이터를 가지고 있는지 검증하였다.
3. 엔티티 클래스 설계(테이블 생성) 및 DB 저장하기
데이터베이스에 아래와 같이 저장될 수 있게 테이블을 설계한다.
no
칵테일 이름
로그인 유저용 점수
비로그인 유저용 점수
1
마티니
15.0
-86.16125
..
..
..
..
import jakarta.persistence.Entity;
import jakarta.persistence.GeneratedValue;
import jakarta.persistence.GenerationType;
import jakarta.persistence.Id;
import lombok.AllArgsConstructor;
import lombok.Builder;
import lombok.Getter;
import lombok.NoArgsConstructor;

@Entity
@Getter
@Builder
@NoArgsConstructor
@AllArgsConstructor
public class TrendCocktailEntity {
    @Id
    @GeneratedValue(strategy = GenerationType.AUTO)
    private Long id;
    
    private String name;
    
    private Double loginTotalScore;
    
    private Double nonLoginTotalScore;
    
}
DB 저장을 위해 JpaRepository 인터페이스를 상속받는 TrendCocktailService 객체에 save 메서드를 만들어준다.
(JpaRepository 의 기본 save 메서드를 사용할 것이기 때문에 인터페이스에 따로 구현할 내용은 없다.)
- JpaTrendCoctailRepository 클래스
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.toastit_v2.feature.trendcocktail.infrastructure.persistence.mysql.entity.TrendCocktailEntity;

@Repository
public interface JPATrendCocktailRepository extends JpaRepository<TrendCocktailEntity,Long> {
}
-TrendCocktailService 클래스, 맨 아래 save 메서드 추가
package org.toastit_v2.feature.trendcocktail.application.service;

import org.springframework.stereotype.Service;
import org.toastit_v2.feature.trendcocktail.application.port.TrendCocktailRepository;
import org.toastit_v2.feature.trendcocktail.application.service.utilly.apiMaker.GoogleAPIRequestMaker;
import org.toastit_v2.feature.trendcocktail.application.service.utilly.apiMaker.NaverAPIRequestMaker;
import org.toastit_v2.feature.trendcocktail.infrastructure.persistence.mysql.custom.JPATrendCocktailRepository;
import org.toastit_v2.feature.trendcocktail.infrastructure.persistence.mysql.entity.TrendCocktailEntity;

import java.util.List;
import java.util.Map;

@Service
public class TrendCocktailService implements TrendCocktailRepository {

    private final JPATrendCocktailRepository jpaRepository;
    private final GoogleAPIRequestMaker googleAPIRequestMaker;
    private final NaverAPIRequestMaker naverAPIRequestMaker;


    public TrendCocktailService(JPATrendCocktailRepository jpaRepository, GoogleAPIRequestMaker googleAPIRequestMaker, NaverAPIRequestMaker naverAPIRequestMaker) {
        this.jpaRepository = jpaRepository;
        this.googleAPIRequestMaker = googleAPIRequestMaker;
        this.naverAPIRequestMaker = naverAPIRequestMaker;

    }

    /**
     * Naver DataLaB 에 키워드들의 검색량을 응답받는 요청문을 전송하는 메서드 입니다.
     *
     * @param keywords : Project 에서 제공하는 칵테일 리스트를 입력받을 수 있습니다.
     * @return 요청문을 반환 합니다.
     */
    @Override
    public String naverTrendAPIRequest(String keywords) {
        return naverAPIRequestMaker.createNaverTrendAPIRequest(keywords);
    }

    /**
     * Google Trend API 를 통해 특정 키워드의 검색량을 응답받는 요청문을 전송하는 메서드 입니다.
     * @param keywords : 검색량을 응답받고 싶은 키워드를 입력합니다.
     * @return : 요청문을 반환합니다.
     */
    @Override
    public String googleTrendAPIRequest(String keywords) {
       return googleAPIRequestMaker.createGoogleTrendAPIRequest(keywords);
    }

    public void save(TrendCocktailEntity trendCocktail) {
    jpaRepository.save(trendCocktail);
    }
}
4. 마무리
오늘은 응답문을 Pasring 하여 Domain 으로 변환하고, 또 Entity 로 변환하는 작업을 마치고 데이터를 검증 완료하였다.
그리고 이 Entity를 DB 에 저장할 수 있도록 구현했다. JpaRepository의 save 메서드는 검증된 메서드이기 때문에 딱히 검증하지 않아도 된다고 생각한다.
다음 포스팅에서는
API 요청 - 객체간 변환(DTO - Doamin - Entity) - DB 저장
과정이 자동으로 이뤄지도록 스케쥴러 기능을 이용하여, 서버가 자동으로 칵테일에 대한 점수를 DB 에 저장하도록 만들고, 컨트롤러에서는 이 값들을 로그인 유저용, 비로그인 유저용 데이터를 조회할 수 있는 엔드포인트를 만들어서, 칵테일 추천 부분을 마무리 하도록 하자!