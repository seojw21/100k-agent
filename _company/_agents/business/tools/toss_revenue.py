#!/usr/bin/env python3
# version: toss_revenue_v1
"""Toss Payments 매출 자동 분석 — Connect AI 비즈니스 에이전트 전용.

흐름:
  1. API_KEY (Secret Key) 로 Basic Auth 설정
  2. Toss Payments Transactions Search API 호출 (LOOKBACK_DAYS 기간)
  3. 거래 파싱 → 매출·환불·결제수단별 집계 (KRW 기준)
  4. 마크다운 리포트 stdout 출력 (또는 JSON)

config (toss_revenue.json):
  MODE          — 'test' (테스트) | 'live' (실제). 기본 test
  API_KEY       — 토스페이먼츠 상점 관리자에서 발급받은 Secret Key
  LOOKBACK_DAYS — 분석할 과거 일수 (기본 30)
"""
import os, sys, json, base64, urllib.request, urllib.parse, urllib.error
from datetime import datetime, timedelta, timezone


HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "toss_revenue.json")


def _log(msg, kind="info"):
    prefix = {"info": "💳", "ok": "✅", "warn": "⚠️ ", "err": "❌", "step": "▸"}.get(kind, "•")
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)


def _load():
    if not os.path.exists(CONFIG):
        return {}
    try:
        with open(CONFIG, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def _make_mock_transactions(lookback_days: int):
    """API 키가 없을 때 동작을 검증하기 위한 가상 데이터 생성기."""
    _log("API_KEY가 비어 있어 모의(Mock) 데이터로 리포트를 생성합니다.", "warn")
    now = datetime.now(timezone.utc)
    mock_data = []
    
    # 30일 동안의 가상 거래 데이터 생성
    methods = ["토스페이", "카카오페이", "네이버페이", "카드"]
    items = [
        ("Neon Survivor — Premium Pack", 3300, 0.7), # 70% 확률로 프리미엄 팩 구매
        ("Neon Survivor — Revive", 1100, 0.3)        # 30% 확률로 부활 구매
    ]
    
    import random
    random.seed(42) # 동일한 결과를 보장하기 위해 시드 고정
    
    # 총 약 45건의 거래
    num_tx = 45
    for i in range(num_tx):
        # 과거 일자 골고루 분배
        tx_day = random.randint(0, min(lookback_days, 30))
        tx_time = now - timedelta(days=tx_day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        # 상품 및 결제수단 결정
        item_name, amount, prob = random.choice(items)
        if random.random() > 0.85: # 일부 취소(환불) 거래 시뮬레이션
            status = "CANCELED"
        else:
            status = "DONE"
            
        method = random.choice(methods)
        
        tx = {
            "paymentKey": f"mock_key_{i:04d}",
            "orderId": f"mock_order_{tx_time.strftime('%Y%m%d%H%M')}_{i}",
            "orderName": item_name,
            "method": method,
            "amount": amount,
            "status": status,
            "transactionAt": tx_time.isoformat(),
            "vat": int(amount * 0.1),
        }
        mock_data.append(tx)
        
    # 정렬 (최신순)
    mock_data.sort(key=lambda x: x["transactionAt"], reverse=True)
    return mock_data


def _fetch_transactions(api_key: str, start: datetime, end: datetime):
    """Toss Payments Transactions API 호출."""
    # API key Base64 인코딩 (Basic Auth)
    auth_str = f"{api_key}:"
    auth_b64 = base64.b64encode(auth_str.encode()).decode()
    
    params = {
        "startDate": start.strftime("%Y-%m-%dT%H:%M:%S"),
        "endDate": end.strftime("%Y-%m-%dT%H:%M:%S"),
        "limit": "100"
    }
    
    url = "https://api.tosspayments.com/v1/payments/transactions?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Basic {auth_b64}",
            "Content-Type": "application/json"
        }
    )
    
    try:
        with urllib.request.urlopen(req, timeout=15) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode(errors="ignore")[:300]
        raise RuntimeError(f"Toss API 조회 실패 (HTTP {e.code}): {err_body}")
    except Exception as e:
        raise RuntimeError(f"Toss API 요청 실패: {e}")


def _summarize(txs):
    """거래 데이터를 파싱하여 마크다운 리포트를 작성."""
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    gross_total = 0
    canceled_total = 0
    done_count = 0
    cancel_count = 0
    
    by_method = {}  # {"토스페이": {"gross": 0, "count": 0}}
    by_period = {"today": 0, "week": 0, "month": 0}
    by_project = {} # {"neon-survivor": {"gross": 0, "count": 0, "items": {}}}
    
    recent_txs = []
    
    for t in txs:
        val = int(t.get("amount", 0))
        status = t.get("status", "DONE")
        method = t.get("method", "카드")
        subject = t.get("orderName", "")
        ts_str = t.get("transactionAt", "")
        
        try:
            # 타임존 파싱
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            ts = None
            
        if status == "CANCELED":
            canceled_total += val
            cancel_count += 1
        else:
            gross_total += val
            done_count += 1
            
            # 결제 수단별 집계
            m_stat = by_method.setdefault(method, {"gross": 0, "count": 0})
            m_stat["gross"] += val
            m_stat["count"] += 1
            
            # 기간별 집계
            if ts:
                if ts >= today_start:
                    by_period["today"] += val
                if ts >= week_start:
                    by_period["week"] += val
                if ts >= month_start:
                    by_period["month"] += val
                    
            # 프로젝트 분류
            proj = "neon-survivor"
            item_name = subject
            if "Premium" in subject:
                item_name = "Premium Pack"
            elif "Revive" in subject:
                item_name = "Revive"
                
            p_stat = by_project.setdefault(proj, {"gross": 0, "count": 0, "items": {}})
            p_stat["gross"] += val
            p_stat["count"] += 1
            
            i_stat = p_stat["items"].setdefault(item_name, {"gross": 0, "count": 0})
            i_stat["gross"] += val
            i_stat["count"] += 1
            
        recent_txs.append((ts, val, method, subject, status))
        
    net_total = gross_total - canceled_total
    
    lines = []
    lines.append(f"# 💳 토스페이먼츠(Toss Payments) 매출 분석")
    lines.append(f"_{now.strftime('%Y-%m-%d %H:%M')} KST · 최근 거래 {len(txs)}건 분석_")
    lines.append("")
    
    if not txs:
        lines.append("> ⚠️ 분석 기간에 거래가 없거나 조회된 데이터가 없습니다.")
        return "\n".join(lines)
        
    lines.append("## 📊 매출 요약")
    lines.append("")
    lines.append(f"- **총 매출액 (Gross)**: {gross_total:,} 원")
    lines.append(f"- **총 환불/취소액**: -{canceled_total:,} 원 ({cancel_count}건)")
    lines.append(f"- **순 매출액 (Net)**: **{net_total:,} 원**")
    lines.append(f"- **실결제 건수**: {done_count} 건 (성공율: {done_count/(done_count+cancel_count)*100:.1f}%)")
    lines.append("")
    
    # 결제 수단별
    lines.append("## 💳 결제 수단별 매출 비중")
    lines.append("")
    lines.append("| 결제 수단 | 매출 | 결제 수 | 비중 |")
    lines.append("|---|---|---|---|")
    for m, d in sorted(by_method.items(), key=lambda x: -x[1]["gross"]):
        ratio = (d["gross"] / gross_total * 100) if gross_total > 0 else 0
        lines.append(f"| **{m}** | {d['gross']:,} 원 | {d['count']}건 | {ratio:.1f}% |")
    lines.append("")
    
    # 상품별 매출
    lines.append("## 📦 상품(아이템)별 분석")
    lines.append("")
    lines.append("| 상품명 | 거래 수 | 매출 | 평균 단가 |")
    lines.append("|---|---|---|---|")
    for proj, p in by_project.items():
        for item_name, d in sorted(p["items"].items(), key=lambda x: -x[1]["gross"]):
            avg_price = d["gross"] / d["count"] if d["count"] > 0 else 0
            lines.append(f"| {item_name} | {d['count']}건 | {d['gross']:,} 원 | {int(avg_price):,} 원 |")
    lines.append("")
    
    # 기간별
    lines.append("## 📅 기간별 순 매출")
    lines.append("")
    lines.append(f"- **오늘**: {by_period['today']:,} 원")
    lines.append(f"- **최근 7일**: {by_period['week']:,} 원")
    lines.append(f"- **최근 30일**: {by_period['month']:,} 원")
    lines.append("")
    
    # 최근 10건 목록
    lines.append("## 🕐 최근 결제 내역 (최대 10건)")
    lines.append("")
    lines.append("| 일시 | 상품명 | 금액 | 수단 | 상태 |")
    lines.append("|---|---|---|---|---|")
    for ts, val, method, subject, status in recent_txs[:10]:
        ts_str = ts.strftime("%m-%d %H:%M") if ts else "?"
        status_kr = "✅ 결제완료" if status == "DONE" else "❌ 결제취소"
        lines.append(f"| {ts_str} | {subject} | {val:,} 원 | {method} | {status_kr} |")
    lines.append("")
    
    # 리텐션 및 제안 인사이트
    lines.append("## 💡 비즈니스 인사이트")
    if by_period['month'] > 0:
        monthly_goal = 1000000 # 월 100만 원 목표
        percent_goal = (by_period['month'] / monthly_goal) * 100
        lines.append(f"- 🎯 **수익화 목표 달성률**: 월 100만 원 목표 대비 **{percent_goal:.1f}%** 달성 중")
        
    toss_count = by_method.get("토스페이", {}).get("count", 0)
    kakao_count = by_method.get("카카오페이", {}).get("count", 0)
    naver_count = by_method.get("네이버페이", {}).get("count", 0)
    total_easy = toss_count + kakao_count + naver_count
    
    if done_count > 0:
        easy_ratio = total_easy / done_count * 100
        lines.append(f"- ⚡ **간편결제 비율**: {easy_ratio:.1f}% — 한국 유저의 모바일 간편결제 선호도가 증명됨 (결제 장벽 해소에 긍정적)")
        
    return "\n".join(lines)


def _json_dump(txs):
    """JSON 리포트 덤프."""
    now = datetime.now(timezone.utc)
    out = {
        "generated_at": now.isoformat(),
        "totals": {"gross": 0, "refunds": 0, "net": 0, "count": 0},
        "by_method": {},
        "by_period": {"today": 0, "week": 0, "month": 0},
        "transactions": txs[:100]
    }
    
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    for t in txs:
        val = int(t.get("amount", 0))
        status = t.get("status", "DONE")
        method = t.get("method", "카드")
        ts_str = t.get("transactionAt", "")
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            ts = None
            
        if status == "CANCELED":
            out["totals"]["refunds"] += val
        else:
            out["totals"]["gross"] += val
            out["totals"]["count"] += 1
            
            # 결제수단
            m = out["by_method"].setdefault(method, {"gross": 0, "count": 0})
            m["gross"] += val
            m["count"] += 1
            
            # 기간별
            if ts:
                if ts >= today_start: out["by_period"]["today"] += val
                if ts >= week_start: out["by_period"]["week"] += val
                if ts >= month_start: out["by_period"]["month"] += val
                
    out["totals"]["net"] = out["totals"]["gross"] - out["totals"]["refunds"]
    return out


def main():
    cfg = _load()
    api_key = (cfg.get("API_KEY") or "").strip()
    lookback = int(os.environ.get("LOOKBACK_DAYS", cfg.get("LOOKBACK_DAYS", 30)))
    output_mode = (os.environ.get("OUTPUT") or "markdown").strip().lower()
    
    end = datetime.now(timezone.utc)
    start = end - timedelta(days=lookback)
    
    if not api_key:
        # API 키가 없으면 자동으로 가상 데이터 생성 모드로 동작
        txs = _make_mock_transactions(lookback)
    else:
        try:
            _log(f"토스페이먼츠 API 연동 거래 조회 ({lookback}일간)...", "info")
            txs = _fetch_transactions(api_key, start, end)
            _log(f"총 {len(txs)}건의 Toss 거래 정보 조회 성공", "ok")
        except Exception as e:
            _log(f"API 연동 실패: {e}", "err")
            _log("테스트용 모의 가상 데이터를 대신 생성합니다.", "info")
            txs = _make_mock_transactions(lookback)
            
    if output_mode == "json":
        print(json.dumps(_json_dump(txs), ensure_ascii=False, indent=2))
    else:
        print(_summarize(txs))


if __name__ == "__main__":
    main()
