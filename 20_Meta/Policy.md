# 🧠 P-Reinforce RL Policy (Classification Policy)

## ⚖️ RL Weights
- **$w_1$ (Categorization Accuracy):** 0.4
- **$w_2$ (Graph Connectivity):** 0.4
- **$w_3$ (User Satisfaction):** 0.2

## 📋 행동 정책 (Action Policies)
1. **기존 분류 (Exploitation):** 의미적 유사도 85% 이상 시 기존 폴더에 지식을 배치한다.
2. **신규 생성 (Exploration):** 기존 카테고리에 맞지 않는 새로운 개념 등장 시 즉시 상위 개념을 도출하여 새 폴더를 생성한다.
3. **구조 재설계 (Refactoring):** 특정 폴더의 파일이 12개를 초과하면 하위 카테고리로 세분화(Refactoring)를 제안한다.

## 📝 사용자 피드백 로그 (RL Updates)
- [2026-05-03] P-Reinforce 엔진이 성공적으로 초기화되었습니다. 기본 가중치가 설정되었습니다.
