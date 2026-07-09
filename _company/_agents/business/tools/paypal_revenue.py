#!/usr/bin/env python3
# version: paypal_revenue_v4 · sentinel: paypal_revenue_v3
"""PayPal 매출 자동 분석 — Connect AI 비즈니스 에이전트 전용 (v4 multi-cred).

흐름:
  1. CLIENT_ID + CLIENT_SECRET 으로 OAuth2 access token 발급
  2. Transaction Search API 호출 (LOOKBACK_DAYS 기간)
  3. 거래 파싱 → 매출·환불·평균액·통화별 집계
  4. 마크다운 리포트 stdout 출력

config (paypal_revenue.json):
  MODE          — 'sandbox' (테스트) | 'live' (실제). 기본 sandbox
  CLIENT_ID     — PayPal Developer Dashboard 에서 발급
  CLIENT_SECRET — 같은 곳, 비밀로 보관 (password 필드)
  LOOKBACK_DAYS — 분석할 과거 일수 (기본 30)
  CURRENCY      — 기본 통화 (USD/KRW 등). 비우면 모든 통화 표시

발급: https://developer.paypal.com/dashboard/applications → Apps & Credentials
샌드박스 테스트: sandbox.paypal.com 계정 무료 생성 가능
"""
import os, sys, json, base64, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone
import ssl
try:
    ssl._create_default_https_context = ssl._create_unverified_context
except Exception:
    pass


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "paypal_revenue.json")


def _log(msg, kind="info"):
    prefix = {"info": "💰", "ok": "✅", "warn": "⚠️ ", "err": "❌", "step": "▸"}.get(kind, "•")
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)



def _parse_config_md(path: str) -> dict:
    """Connect external panel also writes PAYPAL_* into business/config.md."""
    out = {}
    if not os.path.exists(path):
        return out
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                for sep in (":", "：", "="):
                    if sep in line:
                        k, v = line.split(sep, 1)
                        k, v = k.strip(), v.strip()
                        if k.startswith("PAYPAL_"):
                            out[k] = v
                        break
    except Exception:
        pass
    return out


def _clean_secret(v: str) -> str:
    if not v:
        return ""
    v = v.strip().strip('"').strip("'")
    # strip accidental key prefixes pasted from UI
    for prefix in ("PAYPAL_CLIENT_ID:", "PAYPAL_CLIENT_SECRET:", "CLIENT_ID:", "CLIENT_SECRET:"):
        if v.startswith(prefix):
            v = v[len(prefix):].strip()
    return v.replace("\n", "").replace("\r", "").strip()


def _credential_candidates(cfg: dict, mode: str):
    """Ordered (label, client_id, client_secret, force_mode_or_None)."""
    md = _parse_config_md(os.path.join(os.path.dirname(HERE), "..", "config.md"))
    # env first (operator override)
    env_id = _clean_secret(os.environ.get("PAYPAL_CLIENT_ID") or os.environ.get("CLIENT_ID") or "")
    env_sec = _clean_secret(os.environ.get("PAYPAL_CLIENT_SECRET") or os.environ.get("CLIENT_SECRET") or "")
    env_mode = _clean_secret(os.environ.get("PAYPAL_MODE") or os.environ.get("MODE") or "") or None

    pairs = []
    if env_id and env_sec:
        pairs.append(("env", env_id, env_sec, env_mode.lower() if env_mode else None))

    def add(label, cid, sec, force_mode=None):
        cid, sec = _clean_secret(cid), _clean_secret(sec)
        if cid and sec:
            pairs.append((label, cid, sec, force_mode))

    add("json.CLIENT", cfg.get("CLIENT_ID"), cfg.get("CLIENT_SECRET"))
    add("json.LIVE", cfg.get("LIVE_CLIENT_ID"), cfg.get("LIVE_CLIENT_SECRET"), "live")
    add("json.SANDBOX", cfg.get("SANDBOX_CLIENT_ID"), cfg.get("SANDBOX_CLIENT_SECRET"), "sandbox")
    add("config.md", md.get("PAYPAL_CLIENT_ID"), md.get("PAYPAL_CLIENT_SECRET"),
        (md.get("PAYPAL_MODE") or "").lower() or None)

    # de-dupe by id+secret
    seen = set()
    out = []
    for item in pairs:
        key = (item[1], item[2])
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def _oauth_try_modes(client_id: str, client_secret: str, preferred_mode: str):
    """Try preferred mode first, then the other. Returns (mode, token_resp)."""
    order = [preferred_mode] if preferred_mode in ("live", "sandbox") else ["live", "sandbox"]
    if "live" not in order:
        order.append("live")
    if "sandbox" not in order:
        order.append("sandbox")
    errors = []
    for m in order:
        base = _base_url(m)
        try:
            resp = _get_access_token_full(base, client_id, client_secret)
            if resp.get("access_token"):
                return m, resp, base
        except Exception as e:
            errors.append(f"{m}: {e}")
    raise RuntimeError(" | ".join(errors))


def _load():
    if not os.path.exists(CONFIG):
        return {}
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _base_url(mode: str) -> str:
    return "https://api-m.paypal.com" if mode.lower() == "live" else "https://api-m.sandbox.paypal.com"


def _has_reporting_scope(token_response: dict) -> bool:
    """v2: OAuth 응답의 scope 필드에 Reporting (Transaction Search) 권한 있는지 검사.
       PayPal Dashboard 앱 설정 → Features → Transaction Search 체크 + Save 안 했으면 False.
       사용자에게 친절한 안내 띄우는 용도."""
    scopes = (token_response.get("scope") or "").split()
    return any("reporting" in s for s in scopes)


def _get_access_token_full(base_url: str, client_id: str, client_secret: str) -> dict:
    """v2: OAuth2 client_credentials grant — token + scope 둘 다 반환.
       scope 검사로 사용자 안내 (Transaction Search 권한 부재 사전 감지)."""
    auth = base64.b64encode(f"{client_id}:{client_secret}".encode()).decode()
    req = urllib.request.Request(
        f"{base_url}/v1/oauth2/token",
        data=b"grant_type=client_credentials",
        headers={
            "Authorization": f"Basic {auth}",
            "Content-Type": "application/x-www-form-urlencoded",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="ignore")[:200]
        raise RuntimeError(f"OAuth 실패 (HTTP {e.code}): {err_body}")
    except Exception as e:
        raise RuntimeError(f"OAuth 요청 실패: {e}")


def _get_access_token(base_url: str, client_id: str, client_secret: str) -> str:
    """레거시 호환 — token 만 반환."""
    return _get_access_token_full(base_url, client_id, client_secret)["access_token"]


def _fetch_transactions(base_url: str, token: str, start: datetime, end: datetime, currency_filter: str = ""):
    """Transaction Search API — 페이지네이션 자동 처리.
    공식 API 는 한 번에 최대 31일·500건 → 여러 페이지로 나눠 호출."""
    all_txs = []
    cur = start
    while cur < end:
        page_end = min(cur + timedelta(days=31), end)
        params = {
            # v3: PayPal Transaction Search 는 마이크로초 포함 ISO 형식 거부.
            #     초 단위까지만 + Z timezone 으로 강제. strftime 으로 안전 포맷.
            "start_date": cur.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "end_date": page_end.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "fields": "all",
            "page_size": "500",
            "page": "1",
        }
        if currency_filter:
            params["transaction_currency"] = currency_filter
        url = f"{base_url}/v1/reporting/transactions?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}", "Content-Type": "application/json"})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                data = json.loads(r.read().decode())
                txs = data.get("transaction_details", [])
                all_txs.extend(txs)
                _log(f"{cur.date()} ~ {page_end.date()}: {len(txs)}건 수신", "step")
                total_pages = int(data.get("total_pages", 1))
                if total_pages > 1:
                    for p in range(2, total_pages + 1):
                        params["page"] = str(p)
                        url2 = f"{base_url}/v1/reporting/transactions?" + urllib.parse.urlencode(params)
                        req2 = urllib.request.Request(url2, headers={"Authorization": f"Bearer {token}"})
                        with urllib.request.urlopen(req2, timeout=20) as r2:
                            d2 = json.loads(r2.read().decode())
                            all_txs.extend(d2.get("transaction_details", []))
        except urllib.error.HTTPError as e:
            body = e.read().decode(errors="ignore")[:300]
            _log(f"거래 조회 실패 ({cur.date()}~{page_end.date()}): HTTP {e.code} {body}", "warn")
        except Exception as e:
            _log(f"거래 조회 예외: {e}", "warn")
        cur = page_end
    return all_txs


def _parse_project_from_subject(subject: str):
    """v2: PayPal createOrder 의 description 에서 게임/프로젝트 + 아이템 추출.
       규약: "{Project Name} — {Item Name}"  (em-dash 또는 -- 또는 :).
       예시:
         "Neon Survivor — Premium Pack" → ("neon-survivor", "Premium Pack")
         "Neon Survivor — Revive"       → ("neon-survivor", "Revive")
         "Chick Game: Custom Skin"      → ("chick-game", "Custom Skin")
       구분자 못 찾으면 전체를 프로젝트로 취급 + item = "(unspecified)".
    """
    if not subject:
        return "(unknown)", "(unspecified)"
    s = subject.strip()
    for sep in [" — ", " -- ", " – ", ": "]:
        if sep in s:
            proj, item = s.split(sep, 1)
            slug = proj.strip().lower().replace(" ", "-")
            return slug or "(unknown)", item.strip() or "(unspecified)"
    slug = s.lower().replace(" ", "-")
    return slug or "(unknown)", "(unspecified)"


def _summarize(txs, default_currency: str = ""):
    """거래 리스트 → 마크다운 리포트."""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    by_currency = {}            # {USD: {"gross": float, "fees": float, "refunds": float, "count": int}}
    by_period = {"today": 0.0, "week": 0.0, "month": 0.0}
    by_project = {}             # v2: {"neon-survivor": {"gross": float, "count": int, "currency": "USD",
                                #                       "items": {"Premium Pack": {"gross": float, "count": int}}}}
    transactions_clean = []     # 정상 거래 (T0000 = 일반 결제)
    refunds = []

    for t in txs:
        info = t.get("transaction_info", {})
        amount = info.get("transaction_amount", {})
        currency = amount.get("currency_code", "USD")
        value = float(amount.get("value", "0") or 0)
        status = info.get("transaction_status", "")
        event_code = info.get("transaction_event_code", "")
        ts_str = info.get("transaction_initiation_date", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            ts = None

        if currency not in by_currency:
            by_currency[currency] = {"gross": 0.0, "fees": 0.0, "refunds": 0.0, "count": 0}
        c = by_currency[currency]

        is_refund = event_code.startswith("T1") or "REFUND" in event_code or value < 0
        if is_refund:
            c["refunds"] += abs(value)
            refunds.append((ts, value, currency))
        else:
            c["gross"] += value
            c["count"] += 1
            transactions_clean.append((ts, value, currency))
            if ts and currency == (default_currency or currency):
                if ts >= today_start:
                    by_period["today"] += value
                if ts >= week_start:
                    by_period["week"] += value
                if ts >= month_start:
                    by_period["month"] += value
            # v2: 프로젝트별 그룹화 (정상 거래만 집계 — 환불은 별도 통계)
            subject = info.get("transaction_subject", "") or info.get("transaction_note", "")
            proj, item = _parse_project_from_subject(subject)
            if proj not in by_project:
                by_project[proj] = {"gross": 0.0, "count": 0, "currency": currency, "items": {}}
            p = by_project[proj]
            p["gross"] += value
            p["count"] += 1
            if item not in p["items"]:
                p["items"][item] = {"gross": 0.0, "count": 0}
            p["items"][item]["gross"] += value
            p["items"][item]["count"] += 1
        fee = float(info.get("fee_amount", {}).get("value", "0") or 0)
        c["fees"] += abs(fee)

    # 마크다운 리포트
    lines = []
    lines.append(f"# 💰 PayPal 매출 분석")
    lines.append(f"_{now.isoformat(timespec='minutes')} · 최근 거래 {len(txs)}건_")
    lines.append("")

    if not txs:
        lines.append("> ⚠️ 분석 기간에 거래가 없어요. PayPal Developer Dashboard 에서 모드(sandbox/live)·기간·계정을 확인하세요.")
        lines.append("")
        lines.append("**가능한 원인:**")
        lines.append("- 샌드박스 모드인데 실제 결제 데이터가 없음 → sandbox.paypal.com 에서 거래 시뮬레이션")
        lines.append("- API 권한 부족 → Developer Dashboard 에서 'Transaction Search' 권한 활성화")
        lines.append("- 너무 짧은 기간 → LOOKBACK_DAYS 늘려보기")
        return "\n".join(lines)

    # 통화별 집계
    lines.append("## 📊 통화별 매출")
    lines.append("")
    lines.append("| 통화 | 매출 (Gross) | 환불 | 수수료 | 순매출 | 거래수 |")
    lines.append("|---|---|---|---|---|---|")
    for cur, d in sorted(by_currency.items()):
        net = d["gross"] - d["refunds"] - d["fees"]
        lines.append(f"| **{cur}** | {d['gross']:,.2f} | -{d['refunds']:,.2f} | -{d['fees']:,.2f} | **{net:,.2f}** | {d['count']}건 |")
    lines.append("")

    # v2: 프로젝트(게임) 별 매출 — 카탈로그에 있는 게임들이 description 으로 자동 분류됨
    if by_project:
        lines.append("## 🎮 프로젝트별 매출")
        lines.append("")
        lines.append("| 프로젝트 | 거래 수 | 매출 | 통화 | 상위 아이템 |")
        lines.append("|---|---|---|---|---|")
        sorted_projects = sorted(by_project.items(), key=lambda x: -x[1]["gross"])
        for proj, p in sorted_projects:
            top_items = sorted(p["items"].items(), key=lambda x: -x[1]["gross"])[:2]
            top_str = ", ".join(f"{name} ({d['count']}건)" for name, d in top_items)
            lines.append(f"| **{proj}** | {p['count']}건 | {p['gross']:,.2f} | {p['currency']} | {top_str} |")
        lines.append("")
        # 상세 아이템 분해 (각 프로젝트별)
        for proj, p in sorted_projects:
            if len(p["items"]) <= 1:
                continue
            lines.append(f"### 🎯 {proj} 아이템 분해")
            lines.append("")
            lines.append("| 아이템 | 거래 수 | 매출 | ARPU |")
            lines.append("|---|---|---|---|")
            for name, d in sorted(p["items"].items(), key=lambda x: -x[1]["gross"]):
                arpu = d["gross"] / d["count"] if d["count"] > 0 else 0
                lines.append(f"| {name} | {d['count']}건 | {d['gross']:,.2f} | {arpu:,.2f} |")
            lines.append("")

    # 기간별 (default_currency 기준)
    primary_cur = default_currency or (sorted(by_currency.items(), key=lambda x: -x[1]["gross"])[0][0] if by_currency else "USD")
    lines.append(f"## 📅 기간별 매출 ({primary_cur})")
    lines.append("")
    lines.append(f"- **오늘**: {by_period['today']:,.2f} {primary_cur}")
    lines.append(f"- **지난 7일**: {by_period['week']:,.2f} {primary_cur}")
    lines.append(f"- **지난 30일**: {by_period['month']:,.2f} {primary_cur}")
    lines.append("")
    # 평균 거래액
    if transactions_clean:
        primary_txs = [v for (_, v, c) in transactions_clean if c == primary_cur]
        if primary_txs:
            avg = sum(primary_txs) / len(primary_txs)
            lines.append(f"- 평균 거래액 ({primary_cur}): **{avg:,.2f}**")
            lines.append(f"- 최대 거래: {max(primary_txs):,.2f}")
            lines.append(f"- 최소 거래: {min(primary_txs):,.2f}")
    lines.append("")

    # 최근 거래 10건
    lines.append("## 🕐 최근 거래 10건")
    lines.append("")
    lines.append("| 일시 | 금액 | 통화 | 종류 |")
    lines.append("|---|---|---|---|")
    sorted_txs = sorted(
        [(ts, v, c, "결제") for ts, v, c in transactions_clean] +
        [(ts, -v, c, "환불") for ts, v, c in refunds],
        key=lambda x: x[0] or datetime.min.replace(tzinfo=timezone.utc),
        reverse=True
    )[:10]
    for ts, v, c, kind in sorted_txs:
        ts_str = ts.strftime("%Y-%m-%d %H:%M") if ts else "?"
        sign = "+" if kind == "결제" else "-"
        lines.append(f"| {ts_str} | {sign}{abs(v):,.2f} | {c} | {kind} |")
    lines.append("")

    # 환불 비율 경고
    total_count = sum(d["count"] for d in by_currency.values())
    if refunds and total_count > 0:
        refund_rate = len(refunds) / (total_count + len(refunds)) * 100
        if refund_rate > 10:
            lines.append(f"> 🚨 **환불율 경고**: {refund_rate:.1f}% — 평균(2~5%)보다 높음. 원인 분석 권장.")
            lines.append("")

    # 인사이트
    lines.append("## 💡 다음 액션")
    if by_period['month'] > 0:
        weekly_avg = by_period['month'] / 4
        if by_period['week'] > weekly_avg * 1.2:
            lines.append(f"- 🚀 이번 주 매출({by_period['week']:,.0f})이 월 평균({weekly_avg:,.0f})보다 20%↑ — 무엇이 잘됐는지 파악")
        elif by_period['week'] < weekly_avg * 0.7:
            lines.append(f"- ⚠️ 이번 주 매출({by_period['week']:,.0f})이 월 평균({weekly_avg:,.0f})보다 30%↓ — 원인 점검")
        else:
            lines.append(f"- 📈 이번 주 매출({by_period['week']:,.0f})은 월 평균 추세 유지")
    if len(by_currency) > 1:
        lines.append(f"- 💱 {len(by_currency)}개 통화로 매출 발생 — 환율 변동 위험 분산 또는 헤지 검토")

    return "\n".join(lines)


def _json_dump(txs, default_currency: str = ""):
    """v2: OUTPUT=json 모드에서 호출. 마크다운 대신 watcher / 대시보드가 파싱하기
       쉬운 구조화 JSON 출력. 새 결제 감지 + 대시보드 그래프 양쪽에서 사용."""
    out = {
        "generated_at": datetime.now(timezone.utc).isoformat(timespec='seconds'),
        "currency_filter": default_currency,
        "totals": {"by_currency": {}, "by_period": {"today": 0.0, "week": 0.0, "month": 0.0}},
        "by_project": {},
        "by_day": {},        # {"2026-05-12": {"USD": {"gross": float, "count": int}}}
        "transactions": [],  # 최근 100건만
    }
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)

    for t in txs:
        info = t.get("transaction_info", {})
        amount = info.get("transaction_amount", {})
        currency = amount.get("currency_code", "USD")
        value = float(amount.get("value", "0") or 0)
        event_code = info.get("transaction_event_code", "")
        tx_id = info.get("transaction_id", "")
        subject = info.get("transaction_subject", "") or info.get("transaction_note", "")
        ts_str = info.get("transaction_initiation_date", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            ts = None
        is_refund = event_code.startswith("T1") or "REFUND" in event_code or value < 0

        # totals
        cur_bucket = out["totals"]["by_currency"].setdefault(currency, {"gross": 0.0, "refunds": 0.0, "fees": 0.0, "count": 0})
        if is_refund:
            cur_bucket["refunds"] += abs(value)
        else:
            cur_bucket["gross"] += value
            cur_bucket["count"] += 1
            if ts and currency == (default_currency or currency):
                if ts >= today_start: out["totals"]["by_period"]["today"] += value
                if ts >= week_start: out["totals"]["by_period"]["week"] += value
                if ts >= month_start: out["totals"]["by_period"]["month"] += value
        cur_bucket["fees"] += abs(float(info.get("fee_amount", {}).get("value", "0") or 0))

        # by_project
        if not is_refund:
            proj, item = _parse_project_from_subject(subject)
            p = out["by_project"].setdefault(proj, {"gross": 0.0, "count": 0, "currency": currency, "items": {}})
            p["gross"] += value
            p["count"] += 1
            it = p["items"].setdefault(item, {"gross": 0.0, "count": 0})
            it["gross"] += value
            it["count"] += 1

        # by_day (last 30 days)
        if ts and ts >= month_start and not is_refund:
            day_key = ts.strftime("%Y-%m-%d")
            d = out["by_day"].setdefault(day_key, {})
            db = d.setdefault(currency, {"gross": 0.0, "count": 0})
            db["gross"] += value
            db["count"] += 1

        # transactions (recent first, cap 100)
        out["transactions"].append({
            "id": tx_id,
            "ts": ts.isoformat() if ts else "",
            "ts_epoch": int(ts.timestamp()) if ts else 0,
            "value": value,
            "currency": currency,
            "subject": subject,
            "event_code": event_code,
            "is_refund": is_refund,
        })

    out["transactions"].sort(key=lambda x: x["ts_epoch"], reverse=True)
    out["transactions"] = out["transactions"][:100]
    return out


def main():
    cfg = _load()
    mode = _clean_secret(cfg.get("MODE") or "sandbox").lower()
    if mode not in ("live", "sandbox"):
        mode = "sandbox"

    lookback = int(os.environ.get("LOOKBACK_DAYS", cfg.get("LOOKBACK_DAYS", 30)))
    currency = _clean_secret(cfg.get("CURRENCY") or "").upper()
    output_mode = _clean_secret(os.environ.get("OUTPUT") or "markdown").lower()

    candidates = _credential_candidates(cfg, mode)
    if not candidates:
        _log("CLIENT_ID 또는 CLIENT_SECRET 비어있음. PayPal Developer Dashboard 에서 발급:", "err")
        _log("  https://developer.paypal.com/dashboard/applications", "info")
        _log("  → Apps & Credentials → Live/Sandbox 토글 확인 → Client ID + Secret 복사", "info")
        _log("  Connect: 외부 연결 패널 또는 connectAiLab.apiConnections.open", "info")
        sys.exit(1)

    _log(f"PayPal 설정 모드={mode.upper()} · 최근 {lookback}일 분석 · 후보 {len(candidates)}쌍", "info")

    token_resp = None
    used_label = None
    used_mode = mode
    base = _base_url(mode)
    last_err = None
    for label, client_id, client_secret, force_mode in candidates:
        pref = force_mode or mode
        try:
            used_mode, token_resp, base = _oauth_try_modes(client_id, client_secret, pref)
            used_label = label
            _log(f"OAuth 인증 성공 ({label} · {used_mode})", "ok")
            break
        except Exception as e:
            last_err = e
            _log(f"OAuth 후보 실패 [{label}]: {e}", "warn")

    if not token_resp:
        _log(f"OAuth 실패: {last_err}", "err")
        _log("자주 있는 원인:", "info")
        _log("  1) Live 키를 Sandbox에(또는 반대) 넣음 — Dashboard 좌상단 Live/Sandbox 토글 확인", "info")
        _log("  2) Client ID와 Secret이 서로 다른 앱 것", "info")
        _log("  3) Secret 재발급 후 예전 Secret 사용 / 계정이 앱과 연결 안 됨 (Invalid account for relying party)", "info")
        _log("  4) 외부 연결 패널에 저장 후 json·config.md 가 다시 덮였는지 확인", "info")
        _log("  → https://developer.paypal.com/dashboard/applications", "info")
        sys.exit(1)

    token = token_resp["access_token"]

    # v2: scope 검사 → Reporting (Transaction Search) 권한 없으면 친절 안내 후 종료
    if not _has_reporting_scope(token_resp):
        _log("Transaction Search (Reporting) 권한이 토큰에 없음", "err")
        _log("  PayPal Developer Dashboard → 본인 앱 → Features → ", "info")
        _log("  ☑ Transaction search 체크 → Save Changes (반드시!)", "info")
        _log("  변경 후 1~3분 대기 → 다시 시도", "info")
        _log("", "info")
        _log("  💡 자주 놓치는 곳:", "info")
        _log("  - Default Application 사용 중이면 새 앱 만들기 (Features 잠금 가능)", "info")
        _log("  - 좌상단 Sandbox/Live 토글이 입력한 자격증명과 같은 환경인지", "info")
        _log("  - Live 환경은 PayPal 비즈니스 인증 + 별도 권한 신청 필요할 수 있음", "info")
        if output_mode == "json":
            print(json.dumps({
                "error": "reporting_scope_missing",
                "message": "OAuth 토큰에 Transaction Search 권한 없음",
                "scope": token_resp.get("scope", ""),
                "used": used_label,
                "mode": used_mode,
                "fix": "PayPal Dashboard 앱 Features 에서 Transaction search 체크 + Save"
            }, ensure_ascii=False, indent=2))
        else:
            print("# 💰 PayPal 매출 분석")
            print()
            print("> ❌ **Transaction Search 권한 없음** — PayPal Dashboard 에서 활성화 필요")
            print()
            print("**해결 단계:**")
            print("1. https://developer.paypal.com/dashboard/applications")
            print("2. 좌상단 Sandbox/Live 토글 확인 (현재 모드: `" + used_mode + "`)")
            print("3. 본인 앱 클릭")
            print("4. **Features** 섹션 → ☑ **Transaction search** 체크")
            print("5. 페이지 하단 **Save Changes** 클릭 (필수!)")
            print("6. 1~3분 대기 후 매출 대시보드 다시 새로고침")
        sys.exit(2)

    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback)
    txs = _fetch_transactions(base, token, start, end, currency)
    _log(f"총 {len(txs)}건 거래 수집 (cred={used_label})", "ok")

    if output_mode == "json":
        print(json.dumps(_json_dump(txs, currency), ensure_ascii=False, indent=2))
    else:
        report = _summarize(txs, currency)
        print(report)

if __name__ == "__main__":
    main()
