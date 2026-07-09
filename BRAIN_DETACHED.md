# Connect 두뇌 분리됨 (정합성 복구 2026-07-10)

| 역할 | 경로 | git |
|------|------|-----|
| **Connect 두뇌** | `/Users/seojeong-won/reaper-brain` | 있을 수 있음 (파괴 없이 유지). auto 메시지는 hook으로 차단 |
| **코딩 워크스페이스** | `/Users/seojeong-won/GEMMA 4` | rateparse origin (제품) |
| **의도적 백업** | `100k-agent` | 3일 스크립트 / 수동 sync |

## Canonical 설정 (양쪽 동일)

| 키 | 값 |
|----|-----|
| `localBrainPath` / `localBrainFolder` | `/Users/seojeong-won/reaper-brain` |
| `knowledgePath` / `knowledgeFolder` | `/Users/seojeong-won/reaper-brain/knowledge` |
| `secondBrainRepo` | **빈 문자열** (Connect auto-init/push 방지) |
| `autoCycleEnabled` | **false** |
| `productWorkspace` | `/Users/seojeong-won/GEMMA 4` |

적용 파일:

- `GEMMA 4/.connect-ai/config.json`
- `GEMMA 4/.vscode/settings.json`
- `reaper-brain/.connect-ai/config.json`
- `reaper-brain/.vscode/settings.json`

## monorepo 커밋 게이트 (완화됨)

- **이전:** `ALLOW_COMMIT=1` 없으면 모든 커밋 거부 → VS Code 커밋 불가
- **현재:** Connect/auto-sync **메시지 패턴만** 거부. 일반 커밋은 VS Code/CLI 모두 가능

막히는 예:

- `chore(corporate): session …`
- `Auto-Inject …` / `[P-Reinforce] …`
- `🧠 Auto knowledge update …`
- `chore(auto): brain backup …`

허용: `feat:`, `fix:`, `chore: …` (auto 접두 아님) 등 사람/IDE 메시지

훅 재설치:

```bash
bash "/Users/seojeong-won/GEMMA 4/scripts/install_block_connect_autosync_hook.sh"
# reaper-brain에도 동일 정책 (옵션)
bash "/Users/seojeong-won/GEMMA 4/scripts/install_block_connect_autosync_hook.sh" "/Users/seojeong-won/reaper-brain"
```

## 필수 (적용 후)

1. Antigravity **Reload Window**
2. Connect AI UI에서 두뇌 경로가 `reaper-brain` 인지 확인
3. 자율 사이클 OFF 유지
4. 에이전트 산출은 `reaper-brain/_company/sessions` 등

## 백업

```bash
bash "/Users/seojeong-won/GEMMA 4/scripts/auto_backup_100k_agent.sh" --force
# 또는
source "/Users/seojeong-won/GEMMA 4/scripts/.brain_env"
python3 "/Users/seojeong-won/GEMMA 4/scripts/sync_100k_agent.py" push --commit --push
```

## 롤백 (한곳으로 되돌리기)

Antigravity / workspace settings:

- `localBrainPath` = `/Users/seojeong-won/GEMMA 4`
- `knowledgePath` = `/Users/seojeong-won/GEMMA 4/knowledge`
- `secondBrainRepo` = `https://github.com/seojw21/100k-agent.git` (원할 때만)

## 비파괴 정책

- `reaper-brain/.git` **삭제하지 않음** (요청 시 별도 검토)
- 경로·훅만 맞춤. 데이터/히스토리 유지

## CEO 400 / context 8192 대응

Connect AI Lab이 `num_ctx: 8192`를 하드코딩함 → 긴 CEO 프롬프트가 400.

이미 적용된 조치:
- `num_ctx` → **32768**, `MAX_CONTEXT_SIZE` → **20e3**
- `decisions.md` 최근 18개만 유지 (나머지는 `decisions_archive.md`)

### 확장 업데이트 후 패치 재적용

```bash
bash "/Users/seojeong-won/GEMMA 4/scripts/patch_connect_num_ctx.sh" --check
bash "/Users/seojeong-won/GEMMA 4/scripts/patch_connect_num_ctx.sh"
# 필요 시
python3 "/Users/seojeong-won/GEMMA 4/scripts/slim_decisions_md.py" --keep 18
```

적용 후 **Antigravity 완전 종료 후 재실행** (Reload만으로는 예전 extension.js가 메모리에 남을 수 있음).

### num_ctx 프록시 (권장 · 재시작 무관하게 강제)

확장/메모리가 8192를내도 요청을 32k로 바꿔 줌.

```bash
# 터미널에서 켜 두기
python3 "/Users/seojeong-won/GEMMA 4/scripts/ollama_num_ctx_proxy.py"
```

- 리슨: `http://127.0.0.1:11435` → upstream `11434`
- 워크스페이스 설정: `connectAiLab.ollamaUrl` = `http://127.0.0.1:11435`
- 프록시 로그에 `num_ctx 8192 -> 32768` 이 보이면 정상
