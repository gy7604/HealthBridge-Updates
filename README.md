# HealthBridge 앱 업데이트 배포

**현재 공개 버전: [0.4.0 / code11](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.4.0)** (2026-11-09 사용자 승인). [APK 다운로드](https://github.com/gy7604/HealthBridge-Updates/releases/download/v0.4.0/HealthBridge-0.4.0.apk) · [업데이트 목록](https://raw.githubusercontent.com/gy7604/HealthBridge-Updates/main/latest.json)

최대 180일의 기기 내 암호화 누적 기록과 7/30/90일 비교·수면·심박·운동 분석을 유지하며, 장기 기록의 원본 변경·삭제 확인을 보완했습니다. 잘못되거나 범위를 벗어난 변경 자료는 기존 기록과 확인 위치를 보존하고 검토 대상으로 남깁니다. 확인되지 않은 과거 기록은 보존하며 공유 미리보기를 보류할 수 있습니다.

선택 집계 미리보기와 합성 인증·보관정책·읽기 연결 검증 기반을 포함합니다. **서버 건강정보 전송·ChatGPT 실제 연결·AI 연동은 계속 비활성**입니다. 실제 로그인이나 외부 전송을 새로 켜지 않습니다. 6시간 자동동기화 고도화는 후순위입니다.

게시 실행 [42617873236](https://github.com/gy7604/HealthBridge-Updates/actions/runs/42617873236)이 검증된 서명 후보를 그대로 재사용해 성공했습니다. 공개 APK와 업데이트 목록을 인증 없이 다운로드하여 후보와 바이트·버전·패키지·크기·SHA-256·기존 인증서가 일치하는 것을 재검증했습니다. 게시 과정에서 새 앱 빌드·재서명·운영 DB 변경·유료 자원 생성·서버 건강정보 전송·휴대전화 설치는 하지 않았습니다.

기존 패키지·서명·건강정보 읽기 권한·암호화 저장소·설정을 유지하는 업데이트입니다. **앱을 삭제하거나 데이터를 초기화하지 말고**, 앱 안 업데이트 확인 또는 위 공식 APK로 기존 앱 위에 업데이트하세요. 0.4.0 설치 후 실제 기록·권한·설정 보존과 제공자 동작 확인은 별도 실기기 확인 대상입니다.

APK SHA-256: `a49e1c799c5083a10c432c65bb2d46265953c772d75ed05af9757192501919b2` (10,919,201 bytes).

이전 [0.3.1/code10](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.3.1), [0.2.2/code8](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.2.2), [0.2.1/code7](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.2.1), [0.2.0/code6](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.2.0), [0.1.4/code5](https://github.com/gy7604/HealthBridge-Updates/releases/tag/v0.1.4) 릴리스도 보관합니다.

이 저장소는 버전별 사용자 승인 후 APK와 업데이트 목록만 공개하는 배포 전용 공간입니다. 앱 소스·건강정보·사용 기록·백업·키·비밀번호·토큰은 보관하지 않습니다. 기존 서버·DB·MCP·PC 빌더는 유지합니다. 이 저장소에서는 앱을 빌드하거나 설치하지 않습니다.
