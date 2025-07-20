# Fastlane Configuration

이 프로젝트는 iOS와 Android 플랫폼별로 분리된 Fastlane 구성을 사용합니다.

## 파일 구조

```
src/fastlane/
├── Fastfile                 # 메인 파일 (플랫폼 import)
├── helpers/
│   └── CommonHelper.rb      # 공통 헬퍼 메서드들
├── ios/
│   └── Fastfile            # iOS 전용 lanes
└── android/
    └── Fastfile            # Android 전용 lanes
```

## 사용법

### iOS 빌드 및 배포

```bash
# iOS TestFlight 배포
fastlane ios beta \
  ipa:./build/Runner.ipa \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8

# iOS App Store 배포 (안전 모드)
fastlane ios release \
  ipa:./build/Runner.ipa \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8 \
  force:true

# iOS 개발용 빠른 업로드 (non-interactive 모드)
fastlane ios dev_release \
  ipa:./build/Runner.ipa \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8 \
  force:true \
  skip_app_version_update:true

# iOS 자동 배포 (바이너리만, 안전)
fastlane ios auto_release \
  ipa:./build/Runner.ipa \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8

# iOS 자동 배포 + 심사 제출 (바이너리만)
fastlane ios auto_release \
  ipa:./build/Runner.ipa \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8 \
  submit_for_review:true \
  automatic_release:true
```

### Android 빌드 및 배포

```bash
# Android APK 빌드 (Debug)
fastlane android build_debug project_dir:./android/

# Android APK 빌드 (Release)
fastlane android build_release \
  project_dir:./android/ \
  store_file:./android/keystore.jks \
  store_password:YOUR_STORE_PASSWORD \
  key_alias:YOUR_KEY_ALIAS \
  key_password:YOUR_KEY_PASSWORD

# Android AAB 빌드
fastlane android build_aab \
  project_dir:./android/ \
  store_file:./android/keystore.jks \
  store_password:YOUR_STORE_PASSWORD \
  key_alias:YOUR_KEY_ALIAS \
  key_password:YOUR_KEY_PASSWORD

# Google Play Internal Testing 배포
fastlane android internal \
  aab:./android/app/build/outputs/bundle/release/app-release.aab \
  json_key:./google-play-service-account.json \
  package_name:com.yourcompany.yourapp

# Google Play Beta 배포
fastlane android beta \
  aab:./android/app/build/outputs/bundle/release/app-release.aab \
  json_key:./google-play-service-account.json \
  package_name:com.yourcompany.yourapp

# Google Play Production 배포
fastlane android release \
  aab:./android/app/build/outputs/bundle/release/app-release.aab \
  json_key:./google-play-service-account.json \
  package_name:com.yourcompany.yourapp
```

## 공통 기능

### 릴리즈 노트 설정

릴리즈 노트는 여러 방법으로 전달할 수 있습니다:

1. **JSON 문자열**: `'{"en-US":"English notes","ko":"Korean notes"}'`
2. **키:값 쌍**: `'en-US:English notes,ko:Korean notes'`
3. **파일 경로**: `'file:./release_notes.json'`
4. **기본 문자열**: `'Bug fixes and improvements'`

### 빌드 정보 추출

- iOS: IPA 파일에서 Bundle ID, 버전, 빌드 번호 추출
- Android: APK 파일에서 Package Name, 버전명, 버전 코드 추출

## 설정 파일

### iOS App Store Connect API 키

1. App Store Connect에서 API 키 생성
2. `.p8` 파일 다운로드
3. `api_key_id`, `api_key_issuer_id`, `api_key_path` 설정

### Android Google Play Console

1. Google Play Console에서 서비스 계정 생성
2. JSON 키 파일 다운로드
3. `json_key` 파라미터에 파일 경로 설정

## Lane 목록

### iOS Lanes
- `ios:export` - IPA 내보내기
- `ios:beta` - TestFlight 배포
- `ios:release` - App Store 배포 (안전 모드)
- `ios:dev_release` - 개발용 빠른 업로드
- `ios:auto_release` - 자동 배포 (바이너리만, 안전)

### Android Lanes
- `android:build_debug` - Debug APK 빌드
- `android:build_release` - Release APK 빌드
- `android:build_aab` - AAB 빌드
- `android:internal` - Internal Testing 배포
- `android:alpha` - Alpha Testing 배포
- `android:beta` - Beta Testing 배포
- `android:release` - Production 배포
- `android:dev_release` - 개발용 빠른 업로드
- `android:auto_release` - 완전 자동 배포

## 문제 해결

### Non-Interactive Mode 오류
```
Could not retrieve response as fastlane runs in non-interactive mode
```

**해결방법:**
- `force:true` 파라미터 추가
- `skip_app_version_update:true` 파라미터 추가

```bash
fastlane ios release \
  ipa:./build/Runner.ipa \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8 \
  force:true \
  skip_app_version_update:true
```

### 메타데이터만 업로드하고 싶은 경우
```bash
fastlane ios release \
  skip_binary_upload:true \
  skip_metadata:false \
  api_key_id:YOUR_API_KEY_ID \
  api_key_issuer_id:YOUR_ISSUER_ID \
  api_key_path:./AuthKey_XXXXX.p8
```
