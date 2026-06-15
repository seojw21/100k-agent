#!/usr/bin/env python3
# version: transfer_revenue_v1
"""계좌이체/무통장 입금 대장 자동 분석 — Connect AI 비즈니스 에이전트 전용.

흐름:
  1. transfer_revenue.json (수동 입력 장부) 로드
  2. 거래 내역 파싱 및 매출 집계 (KRW 기준)
  3. 마크다운 리포트 stdout 출력 (또는 JSON)

config (transfer_revenue.json):
  대장 데이터 리스트 형태로 보관.
"""
import os, sys, json
from datetime import datetime, timedelta, timezone


HERE = os.path.dirname(os.path.abspath(__file__))
LEDGER = os.path.join(HERE, "transfer_revenue.json")


def _log(msg, kind="info"):
    prefix = {"info": "🏦", "ok": "✅", "warn": "⚠️ ", "err": "❌", "step": "▸"}.get(kind, "•")
    print(f"{prefix} {msg}", file=sys.stderr, flush=True)


def _load_ledger():
    if not os.path.exists(LEDGER):
        return []
    try:
        with open(LEDGER, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def _make_mock_ledger():
    """장부 파일이 없거나 비어 있을 때 사용할 시뮬레이션 입금 내역 데이터."""
    _log("입금 장부 파일이 비어 있어 모의(Mock) 입금 대장 데이터로 분석을 실행합니다.", "warn")
    now = datetime.now(timezone.utc)
    mock_data = []
    
    senders = ["김민수", "이영희", "박철수", "정다은", "최지우", "강태현", "윤도현", "송혜교"]
    items = [
        ("Premium Pack", 3300, 0.7),
        ("Revive", 1100, 0.3)
    ]
    
    import random
    random.seed(100)
    
    num_tx = 35
    for i in range(num_tx):
        tx_day = random.randint(0, 30)
        tx_time = now - timedelta(days=tx_day, hours=random.randint(0, 23), minutes=random.randint(0, 59))
        
        item_name, amount, prob = random.choice(items)
        sender = random.choice(senders)
        # 입금 미완료(대기) 상태 시뮬레이션
        if random.random() > 0.9:
            status = "PENDING"
        elif random.random() > 0.95:
            status = "CANCELED"
        else:
            status = "COMPLETED"
            
        tx = {
            "date": tx_time.isoformat(),
            "sender": sender,
            "amount": amount,
            "itemName": item_name,
            "status": status,
            "note": "토스송금" if random.random() > 0.4 else "일반계좌이체"
        }
        mock_data.append(tx)
        
    mock_data.sort(key=lambda x: x["date"], reverse=True)
    return mock_data


def _summarize(txs):
    now = datetime.now(timezone.utc)
    today_start = datetime(now.year, now.month, now.day, tzinfo=timezone.utc)
    week_start = today_start - timedelta(days=7)
    month_start = today_start - timedelta(days=30)
    
    gross_total = 0
    pending_total = 0
    canceled_total = 0
    completed_count = 0
    pending_count = 0
    canceled_count = 0
    
    by_item = {}
    by_period = {"today": 0, "week": 0, "month": 0}
    by_note = {} # 결제수단 통계 (토스앱 송금 vs 일반 계좌이체)
    
    recent_txs = []
    
    for t in txs:
        val = int(t.get("amount", 0))
        status = t.get("status", "COMPLETED")
        sender = t.get("sender", "무명")
        item_name = t.get("itemName", "Premium Pack")
        ts_str = t.get("date", "")
        note = t.get("note", "계좌이체")
        
        try:
            ts = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        except Exception:
            ts = None
            
        if status == "COMPLETED":
            gross_total += val
            completed_count += 1
            
            # 아이템별
            i_stat = by_item.setdefault(item_name, {"gross": 0, "count": 0})
            i_stat["gross"] += val
            i_stat["count"] += 1
            
            # 결제 노트 수단별
            n_stat = by_note.setdefault(note, {"gross": 0, "count": 0})
            n_stat["gross"] += val
            n_stat["count"] += 1
            
            # 기간별
            if ts:
                if ts >= today_start: by_period["today"] += val
                if ts >= week_start: by_period["week"] += val
                if ts >= month_start: by_period["month"] += val
        elif status == "PENDING":
            pending_total += val
            pending_count += 1
        elif status == "CANCELED":
            canceled_total += val
            canceled_count += 1
            
        recent_txs.append((ts, val, sender, item_name, status, note))
        
    lines = []
    lines.append(f"# 🏦 계좌이체/무통장 수동 입금 대장 분석 보고서")
    lines.append(f"_{now.strftime('%Y-%m-%d %H:%M')} KST 기준_")
    lines.append("")
    
    lines.append("## 📊 입금 정산 요약 (확정 금액 기준)")
    lines.append("")
    lines.append(f"- **총 입금 확정액 (Completed)**: **{gross_total:,} 원** ({completed_count}건)")
    lines.append(f"- **입금 확인 대기액 (Pending)**: {pending_total:,} 원 ({pending_count}건)")
    lines.append(f"- **취소/미입금액 (Canceled)**: {canceled_total:,} 원 ({canceled_count}건)")
    lines.append("")
    
    # 송금 수단별
    lines.append("## 📲 송금 유형별 통계")
    lines.append("")
    lines.append("| 송금 유형 | 누적 매출 | 승인 건수 |")
    lines.append("|---|---|---|")
    for n, d in sorted(by_note.items(), key=lambda x: -x[1]["gross"]):
        lines.append(f"| **{n}** | {d['gross']:,} 원 | {d['count']}건 |")
    lines.append("")
    
    # 아이템별
    lines.append("## 📦 상품별 매출 기여")
    lines.append("")
    lines.append("| 상품명 | 판매 건수 | 매출 합계 | 평균 단가 |")
    lines.append("|---|---|---|---|")
    for name, d in sorted(by_item.items(), key=lambda x: -x[1]["gross"]):
        avg = d["gross"] / d["count"] if d["count"] > 0 else 0
        lines.append(f"| {name} | {d['count']}건 | {d['gross']:,} 원 | {int(avg):,} 원 |")
    lines.append("")
    
    # 기간별
    lines.append("## 📅 기간별 순 매출 (Completed 기준)")
    lines.append("")
    lines.append(f"- **오늘**: {by_period['today']:,} 원")
    lines.append(f"- **최근 7일**: {by_period['week']:,} 원")
    lines.append(f"- **최근 30일**: {by_period['month']:,} 원")
    lines.append("")
    
    # 최근 10건 목록
    lines.append("## 🕐 최근 입금 처리 내역 (최대 10건)")
    lines.append("")
    lines.append("| 일시 | 예금주 | 상품명 | 금액 | 상태 | 유형 |")
    lines.append("|---|---|---|---|---|---|")
    for ts, val, sender, item_name, status, note in recent_txs[:10]:
        ts_str = ts.strftime("%m-%d %H:%M") if ts else "?"
        status_kr = "✅ 입금완료" if status == "COMPLETED" else "⏳ 확인대기" if status == "PENDING" else "❌ 취소됨"
        lines.append(f"| {ts_str} | {sender} | {item_name} | {val:,} 원 | {status_kr} | {note} |")
    lines.append("")
    
    # 비즈니스 가이드라인
    lines.append("## 💡 시장 검증 가이드")
    lines.append("- 🎯 **초기 검증 목표**: 월 100만 원 달성을 위해 약 300명의 프리미엄 팩 유저 확보가 필요합니다.")
    lines.append("- 💸 **무비용의 장점**: PG사 등록비(22만 원) 및 월 유지비 0원 상태로 리스크가 없습니다.")
    lines.append("- 💡 **추천 업무**: 구글 설문지에 '입금자명'과 '송금 완료 캡처'를 수집하여 하루 1회 수동 매칭 후 기능을 지급하면 추가 시스템 리소스 없이 100% 검증이 가능합니다.")
    
    return "\n".join(lines)


def _json_dump(txs):
    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "totals": {
            "completed": sum(int(t["amount"]) for t in txs if t["status"] == "COMPLETED"),
            "pending": sum(int(t["amount"]) for t in txs if t["status"] == "PENDING"),
            "canceled": sum(int(t["amount"]) for t in txs if t["status"] == "CANCELED")
        },
        "transactions": txs[:100]
    }


def main():
    txs = _load_ledger()
    if not txs:
        txs = _make_mock_ledger()
        
    output_mode = (os.environ.get("OUTPUT") or "markdown").strip().lower()
    
    if output_mode == "json":
        print(json.dumps(_json_dump(txs), ensure_ascii=False, indent=2))
    else:
        print(_summarize(txs))


if __name__ == "__main__":
    main()
