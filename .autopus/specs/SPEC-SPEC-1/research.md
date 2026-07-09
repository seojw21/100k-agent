# SPEC-SPEC-1 Research: AI Agent Custom Action Marketplace

## Codebase Analysis

대상 코드 영역의 구조, 의존성, 패턴을 분석합니다.

### Target Files

| 파일 | 역할 | 변경 필요 |
|------|------|-----------|

### Dependencies

기존 코드와의 의존 관계를 매핑합니다.

## Lore Decisions

`auto lore context`로 조회한 과거 의사결정 기록입니다.

## Architecture Compliance

`auto arch enforce`로 확인한 아키텍처 정합성 결과입니다.

## Reference Discipline

| Reference | Type | Verification |
|-----------|------|--------------|
| [path or symbol] | existing / [NEW] planned addition | existing refs verified with rg/read; [NEW] excluded from existing-reference checks |

## Reviewer Brief

- Intended scope: [이 SPEC가 닫는 결과]
- Explicit non-goals: [리뷰어가 새 scope로 확장하지 말아야 할 항목]
- Self-verified: Traceability Matrix, Semantic Invariant Inventory, oracle acceptance, existing/[NEW] reference discipline
- Reviewer should focus on: correctness, convergence safety, regression risk

## Semantic Invariant Inventory

| ID | source clause | invariant type | affected outputs | acceptance IDs |
|----|---------------|----------------|------------------|----------------|
| INV-001 | [sanitized user request evidence] | [ordering / parser / formula / state transition] | [stdout/API field/file content] | S1 |

## Key Findings

리서치 과정에서 발견된 주요 사항을 정리합니다.

## Recommendations

구현 시 참고할 권고사항을 나열합니다.

## Self-Verify Summary

- Q-CORR-04 | status: PASS | attempt: 1 | files: research.md | reason: existing/[NEW] reference discipline recorded
- Q-COMP-06 | status: PASS | attempt: 1 | files: spec.md, research.md | reason: Reviewer Brief and Traceability Matrix present
