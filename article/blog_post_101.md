# [Project] API 응답문 데이터 통일화 및 알고리즘 적용 마무리

오늘의 작업을 통해 Project 에서
API 요청 - 객체간 변환(DTO - Doamin - Entity) - DB 저장
과정이 자동으로 이뤄지도록 하자.
이 과정을 통해 서버가 자동으로 칵테일에 대한 점수를 DB 에 저장하도록 만들고, 컨트롤러에서는 이 값들을 로그인 유저용, 비로그인 유저용 데이터를 조회할 수 있는 엔드포인트를 만들어서, 칵테일 추천 부분을 마무미 해보자.
1. API 요청 스케줄 기능 생성
앞서 만든
API 요청 - DTO 전달 - DTO Parsing - Domain 변환 - Entity 변환 - DB 저장
과정을 자동으로 수행할 수 있는 스케줄러 객체를 생성한다. 현재 작업 월이 3월이면 1월과 2월의 검색 변화량을 가져오는 것이기 때문에, 매월 초 한 번 API 를 요청하고 응답 받으면 된다.
칵테일명은 나중에 List<String> 으로 팀원이 만들어 주면 반복문으로 API를 요청할 수 있도록 수정해주면 된다.
일단 좋아요 수와 조회수를 같이 저장하는 식으로 구현했는데, 향후 다른 팀원이 구현한 테이블에서 좋아요와 조회수를
DB에서 조회하는 로직이 완성되면, 스케줄러에서 분리하여 컨트롤러에서 구현해야 한다.
이렇게 하면 칵테일 검색량에 대한 총점수는 월 1회 마다 저장하고, (로그인)사용자의 요청이 올 때마다 좋아요 수와 조회수를 실시간으로 반영하여, 칵테일을 추천해줄 수 있다.
- 스케쥴러 객체 생성
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.GoogleDTOParsing;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.NaverDTOParsing;
import org.toastit_v2.feature.trendcocktail.application.dto.parser.volumeParsing.VolumeParsing;
import org.toastit_v2.feature.trendcocktail.application.service.TrendCocktailService;
import org.toastit_v2.feature.trendcocktail.application.dto.GoogleTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.application.dto.NaverTrendResponseDTO;
import org.toastit_v2.feature.trendcocktail.domain.TrendCocktail;
import org.toastit_v2.feature.trendcocktail.infrastructure.persistence.mysql.entity.TrendCocktailEntity;
import java.util.Map;


@Component
public class TrendCocktailScheduler {

    private final TrendCocktailService trendCocktailService;

    public TrendCocktailScheduler(TrendCocktailService trendCocktailService) {
        this.trendCocktailService = trendCocktailService;
    }

    // 매월 1일 0시에 실행
    @Scheduled(cron = "0 0 0 1 * *")
    public void updateCocktailRecommendations() {
        // 실제로 칵테일명은 List 로 받기 때문에 반복문으로 처리 할 예정임.
        String cocktailKeyword = "마티니";

        String googleResponse = trendCocktailService.googleTrendAPIRequest(cocktailKeyword);
        GoogleTrendResponseDTO googleDTO = GoogleTrendResponseDTO.fromJson(googleResponse);
        GoogleDTOParsing googleParser = new GoogleDTOParsing(googleDTO);
        Map<String, Double> googleVolume = googleParser.parseVolume();

        String naverResponse = trendCocktailService.naverTrendAPIRequest(cocktailKeyword);
        NaverTrendResponseDTO naverDTO = NaverTrendResponseDTO.fromJson(naverResponse);
        VolumeParsing naverParser = new NaverDTOParsing(naverDTO);
        Map<String, Double> naverVolume = naverParser.parseVolume();

        // 키워드 값 추출
        String keyword = googleVolume.keySet().iterator().next();
        double googleValue = googleVolume.get(keyword);
        double naverValue = naverVolume.get(keyword);

        // 도메인 객체 생성
        TrendCocktail domain = TrendCocktail.convertToDomain(keyword, googleValue, naverValue);

        // DB 저장 (나중에 좋아요/조회 수는 BaseCocktail DI 를 통해 해결)
        TrendCocktailEntity entity = domain.convertToEntity(0, 0);
        trendCocktailService.save(entity);
    }
}
2. DB에서 유저별 추천 칵테일 5개를 조회하는 메서드 생성
JpaRepository 이기 때문에, 쿼리문 작성 없이 키워드로 메서드를 생성해준다.
Repository 에서 작성 후, Service 클래스에서 구현하고 이를 Controller 객체에서 실행한다.
-Repository 에서 작성
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.stereotype.Repository;
import org.toastit_v2.feature.trendcocktail.infrastructure.persistence.mysql.entity.TrendCocktailEntity;
import java.util.List;

@Repository
public interface JPATrendCocktailRepository extends JpaRepository<TrendCocktailEntity,Long> {
    List<String> findTop5ByOrderByLoginTotalScoreDesc();
    List<String> findTop5ByOrderByNonLoginTotalScoreDesc();
}
3. Service Layer 에서 구현
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

    /**
     * 로그인 사용자용 총점을 기준으로 상위 5개 칵테일 이름 조회하는 메서드 입니다
     * @return 칵테일 리스트 5개를 반환 합니다.
     */
    public List<String> findTopLoginCocktails() {
        return jpaRepository.findTop5ByOrderByLoginTotalScoreDesc();
    }

    /**
     * 비로그인 사용자용 총점을 기준으로 상위 5개 칵테일 이름 조회하는 메서드 입니다
     * @return 칵테일 리스트 5개를 반환 합니다.
     */
    public List<String> findTopNonLoginCocktails() {
        return jpaRepository.findTop5ByOrderByNonLoginTotalScoreDesc();
    }
}
-4. Controller 에서 실행
로그인 유저와 비로그인 유저의 엔드포인트를 분리하였다. 향 후 캐시나 쿠키를 검증하여 비로그인 유저나 로그인 유저를 검증하는 방법으로 합의된다면, 하나의 메서드로 통일하고 조건문으로 분리하면 된다.
추 후 좋아요 갯수와, 조회수를 DB에서 조회하는 메서드를 전달받으면 이를 추가하도록 한다.
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RestController;
import org.toastit_v2.feature.trendcocktail.application.service.TrendCocktailService;
import java.util.List;


@RestController
public class TrendCocktailController {

    private final TrendCocktailService trendCocktailService;

    public TrendCocktailController(TrendCocktailService trendCocktailService) {
        this.trendCocktailService = trendCocktailService;
    }

    @PostMapping("/test/trendCocktail/loginUser")
    public List<String> getTopLoginCocktails() {
        return trendCocktailService.findTopLoginCocktails();
    }

    @PostMapping("/test/trendCocktail/nonLoginUser")
    public List<String> getTopNonLoginCocktails() {
        return trendCocktailService.findTopNonLoginCocktails();
    }
}
5. 마무리
실제로 서버를 동작 시킨 후 ( 개발 버전의 서버), DB 에 실제로 저장이 되는지 확인하고, 스케줄러 기능이 제대로 동작하는지 확인해보고 싶지만, 이를 테스트 환경에서도 확인해볼 수 있는지 공부한 후 테스트 코드를 작성해 보려 한다.
아직은 Mock 주입에 대한 개념적 이해와, 신뢰가 부족하기 때문에 보고 따라하는 식의 테스트 보다는, 먼저 이해하고 정릭가 되면 테스트를 진행하고자 한다.