# Suggested MCP tool contract

이 파일은 실제 MCP 서버를 구현할 때 권장하는 도구 계약 예시다.

## 권장 tools

### lookup_word
입력:
- word_nm
- include_synonym
- include_prohibited

출력:
- canonical word
- word_eng_abbr_nm
- dmn_yn
- dmn_clsf_nm
- match_type (exact / synonym / prohibited)

### lookup_term
입력:
- trm_nm

출력:
- trm_eng_abbr_nm
- dmn_nm

### list_domain_groups
출력:
- dmn_group_nm[]

### list_domain_classes
입력:
- dmn_group_nm

출력:
- dmn_clsf_nm[]

### list_domains_by_class
입력:
- dmn_clsf_nm

출력:
- dmn_nm
- data_type_nm
- data_len
- data_dc_len

### get_domain_details
입력:
- dmn_nm

출력:
- prm_vl_expln
- strg_frm_expln
- exprs_frm_expln
- data_type_nm
- data_len
- data_dc_len

### execute_approved_sql
입력:
- sql_bundle
- approval_token
- project_id

출력:
- success / failure
- execution_log
- affected_objects

## 권장 원칙

- lookup tool과 write tool을 분리한다.
- write tool은 approval token 없이는 실행하지 않는다.
- MCP는 canonical data만 반환하고, workflow orchestration은 skill이 담당한다.
