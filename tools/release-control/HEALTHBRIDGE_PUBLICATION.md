# HealthBridge 승인 후 게시

소유자 전용 이슈에서 정확한 후보 요청 ID, snapshot SHA, 버전 코드, APK SHA256, 기존 feed blob SHA, 전달 ZIP SHA256, 승인된 파일 링크와 변경 설명을 고정한다. 파일은 candidate.apk와 비밀 없는 receipt.json 두 개만 허용한다. 원래 인증서·패키지·버전·파일 해시를 실제 APK 바이트와 다시 비교한다.

최초 게시 전에는 APK와 latest.json이 없었다. 2026-11-03 사용자의 명시 승인 후 0.1.4/code5를 empty baseline으로 처음 게시했다. 현재는 release/latest.json이 존재하므로 empty를 다시 사용하지 않는다. 이후에는 실제 현재 feed blob을 고정하고 더 높은 버전과 버전별 승인을 확인한다. 설치 전 휴대폰의 실제 버전·서명을 별도로 확인한다.

이후 버전은 기존 latest.json blob SHA를 지정하며 기존 공개 release와 feed가 일치하고 버전 코드가 증가해야 한다. 원본 소유자 댓글, 15분 유효기간, 고정 helper, 첫 실행, 별도 HEALTHBRIDGE_PUBLICATION_ENABLED 게이트를 확인한다.

명령 형식은 에이전트용이며 사용자가 외울 필요는 없다.

`/healthbridge-publish approve REQUEST_ID SNAPSHOT_SHA VERSION_CODE APK_SHA256 BASELINE_FEED_BLOB_SHA_OR_empty OUTER_ZIP_SHA256 APPROVED_FILE_URL`

빈 줄 뒤에 사용자에게 보여 준 변경 설명을 넣는다. 링크는 승인된 *.oaiusercontent.com/files/ 파일 참조만 허용하고 redirect는 거부한다. 공개 승인 전에는 비공개 후보 링크를 공개 이슈에 기록하지 않는다. 앱 소스·건강정보·키·로그는 전달하지 않는다.

게시 순서는 검증 → 새 draft 1회 생성 → APK 업로드·서버 해시 확인 → 승인·기존 상태 재확인 → release 공개 → latest.json 조건부 갱신이다. 첫 게시 중 생긴 기존 draft, 이미 생성된 feed, 승인 변경·만료, 서명·해시 불일치, 부분 실패를 자동으로 재시도하거나 덮어쓰지 않는다. release 공개 후 feed 실패는 수동 조정이 필요한 부분 완료다.

게시 기능은 사용자 승인으로 활성화했다. APK 공개·설치·앱 내 업데이트는 계속 실제 버전별 별도 승인을 받는다. 기존 비공개 앱 소스·서버·DB·MCP·PC 빌더는 이 도구가 사용하거나 변경하지 않는다. 이 저장소에서는 APK를 빌드·실행·설치하지 않는다.

로컬 합성 보호 검사는 `python -B -m unittest discover -s tools/release-control -v`로 실행한다. 실제 서버 업로드·release/feed 일치와 인증 없는 다운로드는 [Actions 41585608752](https://github.com/gy7604/HealthBridge-Updates/actions/runs/41585608752) 및 공개 파일 재검증으로 완료했다. 앱에 사용한 실제 Java 다운로드 코드를 같은 바이트로 컴파일해 공개 APK를 받고 SDK로 원래 서명을 재검증했다. APK SHA256은 `b38d5cf0964a24185bc94916e12d00a0c3c0982155f9de788d28ffecaaf5cca1`, 최초 feed blob은 `afa5e26d269348ed7d6b23a752d23f33133352ae`다. 이 결과는 휴대폰 설치·앱 내 업데이트·실제 건강정보 연동 시험이 아니며 재빌드도 하지 않았다.

