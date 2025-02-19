# 🐳 Docker 의 localStack 을 활용한 AWS S3 업로드메서드 테스트코드 작성하기

< 문제 상황 >
팀 프로젝트 에서 AWS 를 이용하여 이미지를 업로드하는 메서드를 SpringBoot 에서 구현해야 했다.
하지만 AWS 계정이 팀원의 아이디로 만들어졌고, 처음에는 AWS에 접속이 가능했으나, 허용된 기기가 아니라는 둥
인증메일을 보낼테니 입력하고 로그인 하라는 둥...
AWS에 로그인 해서 내 업로드 메서드가 잘 동작하는지 확인 하려면 아이디를 만든 팀원에게 매번 실시간으로 메일 인증코드를 알려달라고 해야 하는 상황이였다.
<해결과정 탐색>
테스트 코드, Swagger, Postman 을 사용하여 메서드 동작 테스트를 해도 괜찮지 않을까? 생각했지만 역시 실제로 파일이 업로드 되고, 삭제되는 모습을 봐야 내 메서드 로직에 확신을 같고 팀원들에게 설명해 줄 수 있을 것 같다고 생각했다.
이에 방법을 찾아보니 로컬 스택이라는 이미지를 도커에서 pull하고 실행, 이후 SpringBoot 에서 이 localStack 을 저장소로 연결하는 빈을 생성하고 AWS 버킷에 이미지를 업로드 하는 메서드를 동작하면 localStack에 객체가 생긴다는 것으로 개념을 이해 하였다.
<진행 시켜>
0.SpringBoot 프로젝트에 의존성 추가 하기 (build.gradle)
testImplementation "org.testcontainers:localstack:1.16.3"
1. Docker 에서 localStack 받아오기 (로켓 모양 아이콘 까지 있는 것이 제일 공신력 있어보여서 저것을 받음)
2. Pull & Run 하면 -> 이미지를 받고 컨테이너에 올려서 실행. 제대로 실행하는지 터미널로 확인
docker ps
healthy 한 상태를 체크해야 한다
3. docker 명령어로 4566 포트를 사용, S3 서비스를 사용하라는 명령어를 입력한다.
docker run -d -p 4566:4566 -e SERVICES=s3 localstack/localstack
4. S3 서비스가 이용 가능한지 헬스체크를 해본다
curl http://localhost:4566/_localstack/health
4번째 줄에 "S3" : "available" 이 존재한다
근데 이용할 수 있는 것들을 보니 ec2도 있고 다양한 기능들이 있는 것 같다. 해당 서비스를 이용한 기능을 구현 시 사용할 수 있을 것 같다.
5. AWS 명령어를 이용하여  Bucket 생성하기
aws --endpoint-url=http://localhost:4566 s3 mb s3://testbucket
testbucket 이 생성되었다.
*참고로 특수문자를 이용한 생성을 해봤는데 Bucket 생성에 실패하여 소문자로만 작성했다.(특수문자 원래 안좋아함..)
6. 이제 도커 컨테이너가 실행중 (localStack 이 실행중) 이므로 S3 bucket bean 을 생성하는 코드를 활용하여 testbucket 에 연결 하는 코드를 작성하였다. 참고로 AWS 업로드 기능을 인터페이스로 작성했고, 구현체로 실제 AWS Bucket 을 빈으로 주입받는 클래스가 있다. 이에 AWS 업로드 기능 인터페이스를 구현하되 localStack 의 testbucket을 빈으로 주입받도록 구현체를 새로 만들었다. (역할과 구현의 분리를 시도해봤다.)
S3UpLoadService 인터페이스 기능 :
파일 업로드(파일명,폴더명)
,
임시 저장(파일명)
,
파일 이동(파일명, 이동할 폴더명)
FileNameSerive 인터페이스 기능 :
UUID 생성
,
메타데이터 생성
테스트패키지의
S3UpLoadServiceLocalStack
클래스가 localStack 과 연결되어 테스트를 할 클래스 이다. (S3UpLoadService 의 분신이다.)
package org.toastit_v2.feature.aws.service;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3Client;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Primary;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;
import org.toastit_v2.feature.aws.application.service.FileNameService;
import org.toastit_v2.feature.aws.application.service.S3UpLoadService;

import java.io.IOException;
import java.util.UUID;

@Primary
@Service
public class S3UpLoadServiceLocalStack implements S3UpLoadService , FileNameService {

    private final AmazonS3Client amazonS3Client;

    private final String bucketName;

    private final String tempFolder = "temporary/";

    public S3UpLoadServiceLocalStack(
            AmazonS3Client amazonS3Client,
            @Value("${AWS_TEST_BUCKET_NAME}") String bucketName) {
        this.amazonS3Client = (AmazonS3Client) AmazonS3ClientBuilder.standard()
                .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration("http://localhost:4566","us-east-1"))
                .withCredentials(new AWSStaticCredentialsProvider(new BasicAWSCredentials("test","test")))
                .enablePathStyleAccess()
                .build();
        this.bucketName = bucketName;
        if (!amazonS3Client.doesBucketExistV2(bucketName)) {
            amazonS3Client.createBucket(bucketName);
        }
    }

    @Override
    public String makeFileName(MultipartFile file) {
        String originalFilename = file.getOriginalFilename();
        String uuid = UUID.randomUUID().toString();
        return uuid + "_" + originalFilename;
    }

    @Override
    public ObjectMetadata makeObjectMetadata(MultipartFile file) {
        ObjectMetadata metadata = new ObjectMetadata();
        metadata.setContentLength(file.getSize());
        metadata.setContentType(file.getContentType());
        return metadata;
    }

    @Override
    public String uploadFile(MultipartFile file,String folderName) throws IOException {
        String url = folderName + "/";
        String uniqueFileName = url + makeFileName(file);
        ObjectMetadata metadata = makeObjectMetadata(file);
        try {
            amazonS3Client.putObject(bucketName, uniqueFileName, file.getInputStream(), metadata);
        } catch (IOException exceptionMessage) {
            throw new RuntimeException("파일 업로드 과정에서 문제가 발생했습니다.", exceptionMessage);
        }
        return uniqueFileName;
    }

    @Override
    public String uploadFileToTemp(MultipartFile file) throws IOException {
        String originalFilename = makeFileName(file);
        String uniqueFileName = tempFolder + originalFilename ;
        ObjectMetadata metadata = makeObjectMetadata(file);
        try {
            amazonS3Client.putObject(bucketName, uniqueFileName, file.getInputStream(), metadata);
        } catch (IOException exceptionMessage) {
            throw new RuntimeException("임시 폴더에 파일 업로드 과정에서 문제가 발생했습니다.", exceptionMessage);
        }
        return originalFilename;
    }

    @Override
    public void moveFileToFinal(String fileName,String targetFolder) {
        String sourceKey = tempFolder + fileName;
        String destinationKey = targetFolder + "/" + fileName;
        if (amazonS3Client.doesObjectExist(bucketName, sourceKey)) {
            amazonS3Client.copyObject(bucketName, sourceKey, bucketName, destinationKey);
            amazonS3Client.deleteObject(bucketName, sourceKey);
        } else {
            throw new RuntimeException("해당 파일이 임시 폴더에 존재하지 않습니다: " + sourceKey);
        }

    }

}
참고로 AmazonS3Client 설정시 endpoint를 "us-east-1" 로 설정해야 오류가 나지 않는다.
@Profile 에노테이션으로 test 와 not test (!="test") 를 구분하여 실행하고 싶었는데 동작하지 않았다. 따라서 @Primary 를 테스트에 사용하고, 테스트가 끝나면 실제 서비스 클래스에 @Primary 를 붙여줄 예정.
7. 테스트 코드 작성
S3UpLoadServiceLocalStack 객체를 실제로 사용해볼 수 있는 테스트 코드를 작성한다.
package org.toastit_v2.feature.aws.service;

import com.amazonaws.auth.AWSStaticCredentialsProvider;
import com.amazonaws.auth.BasicAWSCredentials;
import com.amazonaws.client.builder.AwsClientBuilder;
import com.amazonaws.services.s3.AmazonS3;
import com.amazonaws.services.s3.AmazonS3ClientBuilder;
import com.amazonaws.services.s3.model.ObjectMetadata;
import org.assertj.core.api.Assertions;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;
import org.toastit_v2.feature.aws.application.service.S3UpLoadService;


import java.io.IOException;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@SpringBootTest
class S3UpLoadServiceImplTest {

    @Autowired
    private S3UpLoadServiceLocalStack s3UpLoadServiceLocalStack;

    @Autowired
    private AmazonS3 s3Client;

    MultipartFile file = new MockMultipartFile("file", "test.txt", "text/plain", "123456789".getBytes());

    @BeforeEach
    public void setUp() {
        s3Client = AmazonS3ClientBuilder.standard()
                .withEndpointConfiguration(new AwsClientBuilder.EndpointConfiguration("http://localhost:4566", "us-east-1"))
                .withCredentials(new AWSStaticCredentialsProvider(new BasicAWSCredentials("test", "test")))
                .enablePathStyleAccess()
                .build();

    }

    @Test
    @DisplayName("UUID 파일 이름 생성 테스트")
    void makeUUIDFilename(){
        String fileName = s3UpLoadServiceLocalStack.makeFileName(file);
        Assertions.assertThat(fileName).isNotEqualTo(file.getOriginalFilename());
    }

    @Test
    @DisplayName("메타데이터 생성 확인 테스트")
    void makeMetaDataTest() {
        ObjectMetadata objectMetadata = s3UpLoadServiceLocalStack.makeObjectMetadata(file);
        String contentType = objectMetadata.getContentType();
        long contentLength = objectMetadata.getContentLength();
        Assertions.assertThat(contentType).isEqualTo("text/plain");
        Assertions.assertThat(contentLength).isEqualTo(file.getSize());
    }

    @Test
    @DisplayName("localStack 버킷에 파일 업로드 테스트")
    void uploadFile() throws IOException {
        // Given
        MultipartFile file = new MockMultipartFile("file", "test.txt", "text/plain", "Hello World".getBytes());

        // When
        String folderName = "myUploadTestFolder";
        String fileUrl = s3UpLoadServiceLocalStack.uploadFile(file,folderName);

        // Then
        // 1. 업로드 한 파일의 URL 이 null 이 아니라면 테스트 성공
        // 2. 업로드 한 파일의 원본이름은 UUID 가 추가된 업도르 파일명과 다르므로, 둘의 이름이 다르면 테스트 성공
        // 3. 원하는 폴더에 파일이 업로드 되어있으면 업로드 성공
        System.out.println("localStack upload fileUrl ==================== " + fileUrl);
        Assertions.assertThat(fileUrl).isNotNull();
        Assertions.assertThat(fileUrl).isNotEqualTo(file.getOriginalFilename());
        Assertions.assertThat(folderName+"/"+fileUrl).isNotNull();

    }

    @Test
    @DisplayName("로컬스텍 temporary 폴더에 파일 임시 저장 테스트")
    void uploadFileToTemp() throws IOException {
        // Given
        MultipartFile tempFile = new MockMultipartFile("tempFile", "test.txt", "text/plain", "Hello World".getBytes());

        // When
        String tempFileUrl = s3UpLoadServiceLocalStack.uploadFileToTemp(tempFile);

        //Then
        // 1. 업로드 한 파일의 URL 이 null 이 아니라면 테스트 성공
        System.out.println("tempFileUrl ==================== " + tempFileUrl);
        Assertions.assertThat(tempFileUrl).isNotNull();
    }

    @Test
    @DisplayName("로컬스택의 임시저장 파일 -> 특정 폴더로 저장 테스트")
    void moveFileToTarget() throws IOException {
        // Given
        String fileName = "editTestFile.jpg";
        MultipartFile movingTestFile = new MockMultipartFile("editTestFile", fileName, "image/jpeg", "test image content".getBytes());

        // When 1.파일을 임시 폴더에 저장
        String uploadedFileToTemp = s3UpLoadServiceLocalStack.uploadFileToTemp(movingTestFile);

        // When 2.임시폴더에 저장된 파일을 확인 후, final 폴더로 복사 후 삭제
        // When 3.목표한 폴더명을 지정하여 이동
        String anyFolderName = "myFolder";
        s3UpLoadServiceLocalStack.moveFileToFinal(uploadedFileToTemp,anyFolderName);

        //Then
        // 해당 파일이 존재한다면 테스트 성공
        // myFolder/테스트파일 이 존재하면 테스트 성공
        Assertions.assertThat(uploadedFileToTemp).isNotNull();
        Assertions.assertThat(anyFolderName+"/"+uploadedFileToTemp).isNotNull();

    }
}
주요 테스트 로직
1. UUID를 잘 생성하는가 -> 예) 업로드한 파일명 (example.jpg) 과 UUID 가 생성된 아이디(3e9o_dio3d_dskdf_example.jpg)가 다르면 테스트 성공.
2.메타 데이터 생성시, 초기 파일 정보와 메타데이터가 동일하면 테스트 성공 (파일 콘텐츠 타입, 파일 길이 등)
3.파일 업로드시
-UUID 생성하여 업로드 시 올린 파일 이름과 다를 것.(UUID가 추가 됐는지 확인)
-localStack의 해당 폴더에 실제 파일이 있는지 확인할 것. (null 값이 아니여야 할 것)
-입력한 폴더로 실제로 업로드 되었는지 확인할 것. (입력한 폴더명 = 실제 파일 위치)
4.파일 임시 저장
-임시저장 파일이 null 이 아닐경우 테스트 성공
-파일 경로 출력해보기(삭제 예정) : temporary/ 로 시작해야 함
5.임시 저장 파일 이동
-파일을 임시저장한다
-해당 메서드에 파일명을 입력하고, 이동하고자 하는 폴더명을 입력한다.
-해당 파일이 존재하고, 이동하고자 하는 폴더 명 아래에 있을경우 테스트 성공
<결과>
모든 테스트들이 성공했다.
로컬 스택 내부에 생성된 객체와 폴더들
업로드 / 임시저장 / 특정폴더에 업로드 된 파일명이 로컬스택에 업로드 된 상황과 일치하는 것을 확인할 수 있다.
<소요시간 및 회고>
로컬 스택 의존성 추가 및 도커 셋팅 1시간
클래스 생성 및 테스트 코드 작성 1시간
테스트 코드 검증 및 코드 오류 수정 1시간 이내
AWS 에 실제로 로그인 하지 않고 메서드들이 실제로 작동할 수 있는지 테스트 할 수 있는 방법을 알게되어 매우 보람차고(중간중간 에러가 많이 발생하지 않았다) 유용하다. mock 테스트는 내가 로직을 정해놓고 테스트하는 방법인데 뭔가 짜고치는 고스톱 같은 느낌이라 찜찜했는데, 실제로 객체가 만들어지는 모습을 보니 내가 작성한 메서드에 확신을 갖게 되었다.
에노테이션을 통해 두개의 구현체를 테스트용도와 실제 사용 객체로 구분해서 사용하고 싶었는데, @Profile 에노테이션이 의도한대로 동작하지 않았다. 이부분은 추후 검토해보기로 하자
참고로 도커 컨테이너 종료시 저장된 모든 객체들은 삭제된다...