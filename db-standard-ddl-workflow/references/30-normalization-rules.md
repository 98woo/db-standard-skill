# 30. 한글명 정규화 규칙

이 문서는 한글 테이블명 / 컬럼명을 canonical term 또는 canonical word sequence로 바꾸는 규칙을 정의한다.

## 1. 공통 규칙

- 문자, 숫자, 언더바만 사용한다.
- 단수형 사용을 원칙으로 한다.
- 의미 없는 접두어 / 접미사는 금지한다.
- 띄어쓰기는 물리 식별자 단계에서 언더바로 표기한다.
- 컬럼 / 테이블 약어는 표준 단어 사전의 `word_eng_abbr_nm` 만 사용한다.
- 최종 한글명은 term hit 시 canonical `trm_nm`, word sequence hit 시 canonical `word_nm` 기준으로 확정한다.

## 2. 정규화 순서

1. raw text 보존
2. 앞뒤 공백 제거
3. 연속 공백을 1개 공백으로 정리
4. 파생어 / 복합어 정규화 적용
5. exact term 조회
6. term exact miss 시 term synonym 조회
7. term exact / synonym 모두 miss 시 exact word 조회
8. word exact miss 시 word synonym / prohibited-word 조회
9. canonical term 또는 canonical `word_nm` 으로 치환
10. 최종 term 또는 word sequence 확정

## 2.1 재사용 우선 원칙

표준화는 신규 등록보다 기존 사전 재사용을 우선한다.

재사용 판단 순서:

1. 용어 exact match
2. 용어 synonym match
3. 단어 exact match
4. 단어 synonym match
5. prohibited-word match
6. 신규 등록 검토

적용 원칙:

- 위 1~5 중 하나라도 단일 canonical 후보로 확정되면 신규 등록을 하지 않는다.
- term synonym은 원 입력을 유지하는 규칙이 아니라 canonical `trm_nm`, `trm_eng_abbr_nm`, `dmn_nm`으로 치환하는 규칙이다.
- word synonym / prohibited-word는 원 입력을 유지하는 규칙이 아니라 canonical `word_nm`으로 치환하는 규칙이다.
- 후보가 2건 이상이면 임의 선택하지 않고 pending decision으로 돌린다.
- 단일 canonical 후보를 사용자 선호만으로 거부하면 신규 등록으로 우회하지 않고 pending decision으로 돌린다.
- 신규 단어 / 신규 용어 등록은 재사용 후보가 없을 때만 검토한다.
- live lookup 없이 후보를 추측해 재사용하거나 신규 등록하지 않는다.

## 3. 파생어 변환 규칙

아래 패턴은 정규화 후보로 사용한다.

- `{단어}별` -> `{단어}`
- `{단어}기준` -> `{단어}`
- `{단어}단위` -> `{단어}`
- `{단어}정보` -> `{단어}`
- `{단어}내역` -> `{단어}`
- `{단어}현황` -> `{단어}`

### 적용 원칙
- raw value exact hit가 있으면 raw를 우선한다.
- raw exact hit가 없을 때 정규화 후보를 시도한다.
- 정규화 결과가 둘 이상이면 pending decision으로 돌린다.

## 4. 복합어 분해 규칙

예시:

- `일별통계` -> `일 통계`
- `월별집계` -> `월 집계`

### 적용 원칙
- 용어 exact hit가 있으면 복합어 분해를 하지 않는다.
- 용어 exact miss 시 용어 synonym을 먼저 확인한다.
- 용어 exact / synonym 모두 miss일 때 복합어 분해 후보를 적용한다.
- 복합어 분해 후 단어 수 제한을 다시 검증한다.

## 5. synonym / 금칙어 처리

### 5.1 용어 synonym

term exact가 없으면 `tb_db_com_std_trm.synm_list_expln`을 검색한다.

결과가 있으면:
- 최종 한글 컬럼명은 원 입력이 아니라 매칭된 canonical `trm_nm`
- 영문 컬럼명은 매칭된 canonical term의 `trm_eng_abbr_nm`
- 도메인은 매칭된 canonical term의 `dmn_nm`
- 단어 분해를 수행하지 않는다.

### 5.2 단어 synonym / 금칙어

exact word가 없으면 아래를 검색한다.

- `synm_list_expln`
- `phwrd_lis_expln`

결과가 있으면:
- 최종 한글명은 원 입력이 아니라 매칭된 canonical `word_nm`
- 영문 약어는 매칭된 canonical word의 `word_eng_abbr_nm`

### 주의
- LIKE 기반 검색은 오검출 가능성이 있다.
- 2건 이상 매칭되면 임의 확정하지 않는다.
- 가능하면 delimiter-aware matching을 사용한다.
- term synonym과 word synonym 모두 자동 재사용 전 delimiter 기준 토큰 분리, trim, 공백 제거 등 동일 정규화 후 전체 토큰 일치를 확인한다.

## 6. 최종 한글명 확정 규칙

- term synonym 매칭 -> canonical `trm_nm`
- word synonym 매칭 -> canonical `word_nm`
- prohibited-word 매칭 -> canonical `word_nm`
- 파생어 정규화 -> 정규화 후 canonical `word_nm`
- 복합어 분해 -> 분해 후 각 단어의 canonical `word_nm`

## 7. 테이블 / 컬럼 공통 적용

테이블명과 컬럼명 모두 위 규칙을 적용한다.
단, 컬럼은 다음 차이를 가진다.

- term exact lookup을 먼저 한다.
- term exact miss 시 term synonym lookup을 수행한다.
- 마지막 단어만 도메인 판단 대상이다.
- 단어 수는 4를 초과할 수 없다.

## 8. 예시

### 예시 1
입력: `사용자 정보`

- `사용자`, `정보` exact 조회
- canonical words 확정
- 물리명 조합: `USER_INFO`

### 예시 2
입력: `월별집계`

- raw term miss
- 복합어 분해: `월 집계`
- 각 단어 조회 후 조합

### 예시 3
입력: 용어 이음동의어

- raw term exact miss
- term synonym lookup hit
- canonical `trm_nm`, `trm_eng_abbr_nm`, `dmn_nm` 재사용
- 단어 분해 생략

### 예시 4
입력: 금칙어 또는 이음동의어

- raw word miss
- synonym / prohibited lookup hit
- canonical `word_nm` 으로 치환
- 최종 한글명과 COMMENT는 canonical 기준 사용
