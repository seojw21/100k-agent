# Connect AI Git Auto-Sync — 본질 분석 & 우회 설계

> 2026-07-10. 확장 `connect-ai-lab` 2.89.x `out/extension.js` 기준.

---

## 1. Connect가 실제로 하는 일

### `_safeGitAutoSync(brainDir, commitMsg)`

| 조건 | 동작 |
|------|------|
| git 미설치 | 로컬만 저장, return |
| **brainDir에 .git 없음** + `secondBrainRepo` 비어 있음 | **커밋 안 함** (로컬 저장 tip만) |
| brainDir에 .git 없음 + secondBrainRepo 있음 | `git init` → add → commit → origin 등록 → **push** |
| **brainDir에 .git 있음** | add → commit → 기존 **origin** 으로 push |

### `_safeGitAutoSyncCompany`

| 조건 | 동작 |
|------|------|
| companyDir가 brain **안**에 있음 (기본) | **즉시 return** (회사 단독 싱크 없음) |
| company가 brain 밖 + companyRepo 설정 | 별도 레포로 push |

세션 종료 시 대략:

```text
sessionMsg = "chore(corporate): session <dir>"
_safeGitAutoSync(brainDir, sessionMsg)
_safeGitAutoSyncCompany(sessionMsg)  // nested면 스킵
```

주입 시: `Auto-Inject Knowledge…`, `[P-Reinforce] Auto-synced…` 등.

### 결정적 사실 (현재 PC)

```text
localBrainPath = /Users/seojeong-won/GEMMA 4
GEMMA 4/.git origin = https://github.com/seojw21/rateparse.git
secondBrainRepo   = https://github.com/seojw21/100k-agent.git   ← auto-sync 때 거의 안 씀!
```

**origin이 이미 있으면 secondBrainRepo는 무시되고 rateparse로 push** 됩니다.  
그래서 “백업은 100k-agent” 설정만으로는 **제품 레포 스팸 커밋을 막을 수 없습니다.**

---

## 2. 우회 옵션 비교

| 옵션 | 방법 | auto-sync | 제품 레포 오염 | 난이도 | 추천 |
|------|------|-----------|----------------|--------|------|
| **A. commit-msg 훅** | Connect 자동 메시지 커밋 거부 | 로컬 커밋 실패→push 없음 | 차단 | 낮음 | **즉시 적용** |
| **B. 무git 두뇌 분리** | brain을 git 없는 폴더 + secondBrainRepo 비움 | 코드상 no-op | 원천 차단 | 중 | **중기 정석** |
| **C. 두뇌 전용 origin** | GEMMA 4 origin을 100k-agent로 | push는 100k로 | rateparse 깨끗 | 중·위험 | monorepo 정리 후 |
| **D. 확장 패치** | auto-sync 함수 무력화 | 완전 차단 | 차단 | 높음 | 업스트림 덮어씀 |

---

## 3. 권장 아키텍처 (정석 = B)

```text
[작업 워크스페이스]  GEMMA 4/          ← Antigravity Open Folder (코드·Study)
                     rateparse/        ← 제품 (이 레포 origin=rateparse 유지 가능)
                     whatsapp-.../

[Connect 두뇌]       ~/reaper-brain/   ← localBrainPath, **.git 없음**
                     _shared/ _agents/ _company/
                     00_Raw/ 10_Wiki/ business/ knowledge/…

[의도적 백업만]      100k-agent         ← scripts/sync + launchd 3일
                     secondBrainRepo = (비움)  ← Connect 자동 init/push 방지
```

### 왜 secondBrainRepo를 비우나?

무git 폴더 + secondBrainRepo 설정 시 Connect가 **`git init` 후 자동 push** 함.  
자동 싱크를 끄려면 **레포 URL을 비워야** 함. 백업은 우리 스크립트가 담당.

### 동기화 흐름 (사람/스케줄)

```text
Connect가 reaper-brain에 md 씀
        │
        │  (git auto-sync: no-op, .git 없음 + repo URL 없음)
        ▼
3일 launchd / 수동: sync_100k_agent.py
  reaper-brain(또는 GEMMA4 whitelist) → 100k-agent → push
```

---

## 4. 즉시 방어 (A) — monorepo 유지하면서 스팸 차단

`GEMMA 4/.git/hooks/commit-msg` 에서 Connect 자동 메시지 패턴이면 **exit 1**.

막는 예:

- `chore(corporate): session …`
- `Auto-Inject …`
- `[P-Reinforce] …`
- `Initial company backup`
- `🧠 Auto knowledge update` (로컬에서 흉내 낼 경우)

허용: 사람/의도적 `feat:`, `chore:`, `fix:` 등.

한계: 에이전트가 **임의의 feat: 메시지**로 `git commit` 하면 통과 가능.  
→ 자율 사이클 OFF + 훅 + (가능하면) B 분리가 세트.

---

## 5. 적용 체크리스트

### 지금 (A)

- [x] `scripts/install_block_connect_autosync_hook.sh` 로 훅 설치
- [ ] (선택) `git commit` 테스트: Connect 패턴 거부 확인

### 중기 (B) — `scripts/setup_detached_brain.sh`

1. `~/reaper-brain` 생성, Connect OS 파일 복사 (제품 코드 제외)
2. **git init 하지 않음**
3. Antigravity: `localBrainPath` = `~/reaper-brain`
4. `secondBrainRepo` = **빈 문자열**
5. `companyDir` 비움 (brain 안 `_company` nested → company sync 스킵)
6. `sync_100k_agent.py` 의 `--gemma`/`AGENT` 경로를 reaper-brain 기준으로
7. 워크스페이스는 GEMMA 4 유지 (코딩), Connect만 두뇌 경로 분리
8. Reload Window

### 하지 말 것

- monorepo origin을 함부로 100k로 바꾸기 (rateparse 배포 히스토리 꼬임)
- 무git 두뇌에 secondBrainRepo 채우기 (자동 init 부활)
- 자율 사이클 + 훅만으로 “완전 안전” 가정 (feat 우회 가능)

---

## 6. 한 줄 요약

> Connect auto-sync는 **“brain 폴더의 git + origin”** 을 그대로 민다.  
> 지금 구조에선 그게 **rateparse** 다.  
> **끄려면:** (1) 자동 커밋 메시지 훅으로 거부, 또는 (2) **git 없는 두뇌 폴더 + secondBrainRepo 비움** + 우리 백업 스크립트만 사용.
