# HealthBridge 앱 업데이트 배포

**현재 공개 버전: [0.5.0 / code12](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.5.0)** (2026-11-09 사용자 승인). [APK 다운로드](https://github.com/gy7604/HealthBridge-Updates/releases/download/v0.5.0/HealthBridge-0.5.0.apk) · [업데이트 목록](https://raw.githubusercontent.com/gy7604/HealthBridge-Updates/main/latest.json)

기기 내 암호화 장기 기록과 기존 분석 기능을 유지하며, 수동 동기화 후 최근 걸음·심박·수면을 선택하는 표시 처리를 보완했습니다. 선택 공유·인증·조회·분석의 준비 코드는 합성 자료로 검증했습니다. **서버 건강정보 전송·ChatGPT 실제 연결·AI 연동은 계속 비활성**입니다. 실제 로그인·계정 연결·외부 건강정보 전송을 켜지 않습니다. 6시간 자동동기화 고도화는 후순위입니다.

사용자는 이 서명 후보를 설치한 뒤 **기존 기록·권한·설정 보존과 수동 동기화 후 걸음·심박·수면 정상 표시**를 확인했습니다. 이는 사용자 실기기 확인이며 자동화가 기기를 읽거나 설치한 결과는 아닙니다.

[정식 게시 실행 42632299702](https://github.com/gy7604/HealthBridge-Updates/actions/runs/42632299702)이 성공했습니다. 검증된 동일 APK를 재빌드·재서명 없이 재사용했습니다. 공개 APK와 업데이트 목록을 인증 없이 내려받아 후보와 바이트·버전·패키지·크기·SHA-256·기존 인증서가 일치하는 것을 재검증했습니다. 권한 선언도 0.4.0과 같습니다. 게시 과정에서 운영 DB 변경·유료 자원 사용·실제 건강정보 전송은 하지 않았습니다.

기존 패키지·서명·암호화 저장소·설정을 유지하는 업데이트입니다. **앱을 삭제하거나 데이터를 초기화하지 말고**, 앱 안 업데이트 확인 또는 위 공식 APK로 기존 앱 위에 업데이트하세요. 이미 이 후보를 설치했다면 동일 버전이므로 다시 설치할 필요가 없습니다.

APK SHA-256: `a36022a8a518742e43463dae0f7cf707339b2b913acad661dfcd2e6878d3f3a3` (10,943,777 bytes).

이전 [0.4.0/code11](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.4.0), [0.3.1/code10](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.3.1), [0.2.2/code8](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.2.2), [0.2.1/code7](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.2.1), [0.2.0/code6](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.2.0), [0.1.4/code5](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.1.4) 릴리스도 보관합니다.

이 저장소는 버전별 사용자 승인 후 APK와 업데이트 목록만 공개하는 배포 전용 공간입니다. 앱 소스·건강정보·사용 기록·백업·키·비밀번호·토큰은 보관하지 않습니다. 기존 서버·DB·MCP·PC 빌더를 유지합니다. 이 저장소에서는 앱을 빌드하거나 설치하지 않습니다.
