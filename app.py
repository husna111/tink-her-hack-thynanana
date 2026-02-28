# ╔══════════════════════════════════════════════════════════════╗
# ║  BROKE.EXE — Backend  (Flask)                               ║
# ║                                                              ║
# ║  SETUP:                                                      ║
# ║    pip install flask flask-cors requests                     ║
# ║    set ANTHROPIC_API_KEY=sk-ant-...   (Windows CMD)         ║
# ║    $env:ANTHROPIC_API_KEY="sk-ant-..."  (PowerShell)        ║
# ║    export ANTHROPIC_API_KEY=sk-ant-...  (Mac/Linux)         ║
# ║    python app.py                                             ║
# ║                                                              ║
# ║  WHAT THIS DOES:                                             ║
# ║  • Serves the frontend (index.html)                          ║
# ║  • Stores expenses in a local JSON file                      ║
# ║  • Proxies AI calls to Anthropic (no CORS issues)           ║
# ║  • Parses UPI/SMS messages server-side                       ║
# ║  • Generates reminders, roasts, tips via Claude             ║
# ╚══════════════════════════════════════════════════════════════╝

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_cors import CORS
import json, os, datetime, requests as http

app = Flask(__name__, template_folder='.', static_folder='.')
CORS(app)  # allow requests from any origin (useful if running frontend separately)

# ── Config ────────────────────────────────────────────────────────────────────
ANTHROPIC_API_KEY = os.environ.get('ANTHROPIC_API_KEY', '')
DATA_FILE         = 'broke_data.json'
ANTHROPIC_URL     = 'https://api.anthropic.com/v1/messages'
DEFAULT_BUDGET    = 5000.0

# ── Data layer ────────────────────────────────────────────────────────────────
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE) as f:
                return json.load(f)
        except Exception:
            pass
    return {'expenses': [], 'budget': DEFAULT_BUDGET, 'profile': {}}

def save_data(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f, indent=2)

db = load_data()

# ── Utilities ─────────────────────────────────────────────────────────────────
def next_id():
    exps = db.get('expenses', [])
    return max((e.get('id', 0) for e in exps), default=0) + 1

def period_expenses(period='month', offset=0):
    today = datetime.date.today()
    if period == 'day':
        d = today + datetime.timedelta(days=offset)
        start = end = d
    elif period == 'week':
        d     = today + datetime.timedelta(weeks=offset)
        start = d - datetime.timedelta(days=d.weekday())
        end   = start + datetime.timedelta(days=6)
    elif period == 'year':
        yr    = today.year + offset
        start = datetime.date(yr, 1, 1)
        end   = datetime.date(yr, 12, 31)
    else:  # month (default)
        y, m = today.year, today.month + offset
        while m < 1:  m += 12; y -= 1
        while m > 12: m -= 12; y += 1
        start = datetime.date(y, m, 1)
        end   = datetime.date(y, m, calendar_days(y, m))
    return [e for e in db['expenses'] if start.isoformat() <= e.get('date','') <= end.isoformat()]

def calendar_days(year, month):
    import calendar
    return calendar.monthrange(year, month)[1]

def calc_stats(expenses, budget):
    if not expenses:
        return {
            'total': 0, 'count': 0, 'by_cat': {}, 'by_pm': {'cash':0,'card':0,'upi':0,'other':0},
            'needs': 0, 'wants': 0, 'remaining': budget, 'status': 'safe',
            'daily_avg': 0, 'budget': budget, 'top_cat': None, 'top_cat_amt': 0,
            'wants_pct': 0, 'days_elapsed': datetime.date.today().day
        }
    total     = sum(e['amount'] for e in expenses)
    by_cat    = {}
    by_pm     = {'cash': 0, 'card': 0, 'upi': 0, 'other': 0}
    for e in expenses:
        by_cat[e['category']] = by_cat.get(e['category'], 0) + e['amount']
        pm = e.get('pay_method', 'cash')
        by_pm[pm] = by_pm.get(pm, 0) + e['amount']
    needs     = sum(e['amount'] for e in expenses if e.get('is_necessary', True))
    wants     = total - needs
    remaining = budget - total
    days      = datetime.date.today().day
    status    = 'over_budget' if remaining < 0 else 'warning' if remaining < budget * .2 else 'safe'
    top_cat   = max(by_cat, key=by_cat.get) if by_cat else None
    sorted_cat = dict(sorted(by_cat.items(), key=lambda x: -x[1]))
    return {
        'total':      round(total, 2),
        'count':      len(expenses),
        'by_cat':     {k: round(v, 2) for k, v in sorted_cat.items()},
        'by_pm':      {k: round(v, 2) for k, v in by_pm.items()},
        'needs':      round(needs, 2),
        'wants':      round(wants, 2),
        'remaining':  round(remaining, 2),
        'status':     status,
        'daily_avg':  round(total / days, 2),
        'budget':     budget,
        'top_cat':    top_cat,
        'top_cat_amt': round(by_cat.get(top_cat, 0), 2) if top_cat else 0,
        'wants_pct':  round(wants / total * 100, 1) if total else 0,
        'days_elapsed': days,
    }

# ── Anthropic helper ──────────────────────────────────────────────────────────
def ask_claude(system, user, max_tokens=280, model='claude-haiku-4-5-20251001'):
    """Call Claude API server-side. Returns text or None on any failure."""
    if not ANTHROPIC_API_KEY:
        return None
    try:
        resp = http.post(
            ANTHROPIC_URL,
            headers={
                'x-api-key':          ANTHROPIC_API_KEY,
                'anthropic-version':  '2023-06-01',
                'content-type':       'application/json',
            },
            json={
                'model':      model,
                'max_tokens': max_tokens,
                'system':     system,
                'messages':   [{'role': 'user', 'content': user}],
            },
            timeout=25
        )
        data = resp.json()
        if resp.status_code != 200:
            return None
        return (data.get('content') or [{}])[0].get('text', '').strip() or None
    except Exception:
        return None

# ══════════════════════════════════════════════════════════════
# ROUTES — Serve frontend
# ══════════════════════════════════════════════════════════════
@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

# ══════════════════════════════════════════════════════════════
# ROUTES — Expenses
# ══════════════════════════════════════════════════════════════
@app.route('/api/expenses', methods=['GET'])
def get_expenses():
    period = request.args.get('period', 'month')
    offset = int(request.args.get('offset', 0))
    exps   = period_expenses(period, offset)
    exps   = sorted(exps, key=lambda e: (e.get('date',''), e.get('id',0)), reverse=True)
    return jsonify({'success': True, 'expenses': exps})

@app.route('/api/expenses', methods=['POST'])
def add_expense():
    d = request.get_json(force=True) or {}
    required = ['description', 'amount', 'category']
    if not all(d.get(k) for k in required):
        return jsonify({'success': False, 'message': 'Missing required fields'}), 400
    expense = {
        'id':           next_id(),
        'date':         d.get('date') or datetime.date.today().isoformat(),
        'description':  str(d['description'])[:100],
        'amount':       round(float(d['amount']), 2),
        'category':     str(d['category']),
        'is_necessary': bool(d.get('is_necessary', True)),
        'pay_method':   d.get('pay_method', 'cash'),
        'note':         str(d.get('note', ''))[:80],
    }
    db.setdefault('expenses', []).append(expense)
    save_data(db)
    return jsonify({'success': True, 'expense': expense}), 201

@app.route('/api/expenses/<int:expense_id>', methods=['DELETE'])
def delete_expense(expense_id):
    before = len(db.get('expenses', []))
    db['expenses'] = [e for e in db.get('expenses', []) if e.get('id') != expense_id]
    if len(db['expenses']) < before:
        save_data(db)
        return jsonify({'success': True})
    return jsonify({'success': False, 'message': 'Not found'}), 404

@app.route('/api/expenses/<int:expense_id>', methods=['PUT'])
def edit_expense(expense_id):
    d    = request.get_json(force=True) or {}
    exps = db.get('expenses', [])
    for i, e in enumerate(exps):
        if e.get('id') == expense_id:
            exps[i].update({
                k: d[k] for k in
                ['description','amount','category','date','is_necessary','pay_method','note']
                if k in d
            })
            save_data(db)
            return jsonify({'success': True, 'expense': exps[i]})
    return jsonify({'success': False, 'message': 'Not found'}), 404

# ══════════════════════════════════════════════════════════════
# ROUTES — Stats
# ══════════════════════════════════════════════════════════════
@app.route('/api/stats')
def get_stats():
    period = request.args.get('period', 'month')
    offset = int(request.args.get('offset', 0))
    exps   = period_expenses(period, offset)
    budget = db.get('budget', DEFAULT_BUDGET)
    return jsonify({'success': True, 'stats': calc_stats(exps, budget)})

# ══════════════════════════════════════════════════════════════
# ROUTES — Budget & Profile
# ══════════════════════════════════════════════════════════════
@app.route('/api/budget', methods=['GET'])
def get_budget():
    return jsonify({'success': True, 'budget': db.get('budget', DEFAULT_BUDGET)})

@app.route('/api/budget', methods=['POST'])
def set_budget():
    d = request.get_json(force=True) or {}
    val = float(d.get('budget', DEFAULT_BUDGET))
    if val <= 0:
        return jsonify({'success': False, 'message': 'Budget must be positive'}), 400
    db['budget'] = round(val, 2)
    save_data(db)
    return jsonify({'success': True, 'budget': db['budget']})

@app.route('/api/profile', methods=['GET'])
def get_profile():
    return jsonify({'success': True, 'profile': db.get('profile', {})})

@app.route('/api/profile', methods=['POST'])
def set_profile():
    d = request.get_json(force=True) or {}
    db['profile'] = d
    save_data(db)
    return jsonify({'success': True, 'profile': db['profile']})

# ══════════════════════════════════════════════════════════════
# ROUTES — AI Proxy  (all Claude calls go through here)
# ══════════════════════════════════════════════════════════════
@app.route('/api/ai/roast', methods=['POST'])
def ai_roast():
    """Personalised spending roast based on profile + current stats."""
    d       = request.get_json(force=True) or {}
    profile = d.get('profile', {})
    stats   = d.get('stats', {})
    vibe    = profile.get('vibe', 'engineering')
    name    = profile.get('name', 'Student')
    year    = profile.get('year', 'college')
    curr    = profile.get('currency', '₹')

    SYSTEM = (
        "You roast broke Indian college HOSTEL students about money. Rules: "
        "NEVER suggest cooking/meal prep — they live in hostels with no kitchen. "
        "DO reference: hostel mess, canteen, Swiggy/Zomato, chai tapri, auto-rickshaw, "
        "shared OTT, student discounts, UPI cashback. "
        "2-3 sentences max. Savage but warm. End with ONE actionable tip. No fluff."
    )

    if stats.get('count', 0) == 0:
        user = f"Welcome roast for a {year} {vibe} student named {name} who just started tracking expenses. Make it funny and specific to their college type."
    else:
        cats = ', '.join(f"{k}:{curr}{v}" for k, v in stats.get('by_cat', {}).items())
        user = (
            f"{name}, {year} {vibe} student. "
            f"Spent {curr}{stats.get('total',0)} of {curr}{stats.get('budget',0)} budget ({stats.get('status','safe')}). "
            f"Categories: {cats}. Biggest: {stats.get('top_cat','?')} ({curr}{stats.get('top_cat_amt',0)}). "
            f"Wants: {stats.get('wants_pct',0)}%. Day {stats.get('days_elapsed',1)} of month. Roast them."
        )

    text = ask_claude(SYSTEM, user)
    return jsonify({'success': bool(text), 'text': text})


@app.route('/api/ai/tip', methods=['POST'])
def ai_tip():
    """Hostel-specific money tip tailored to spending pattern."""
    d       = request.get_json(force=True) or {}
    profile = d.get('profile', {})
    stats   = d.get('stats', {})
    curr    = profile.get('currency', '₹')
    vibe    = profile.get('vibe', 'engineering')
    year    = profile.get('year', 'college')

    SYSTEM = (
        "Give HOSTEL-SPECIFIC money tips for Indian college students. "
        "NEVER suggest cooking — no kitchens in hostels. "
        "Reference: hostel mess, canteen, chai tapri, Swiggy One split, "
        "student discounts (Amazon Prime {curr}499/yr, GitHub Education, Adobe), "
        "UPI cashback, shared subscriptions, auto negotiation, campus facilities. "
        "1-2 sentences. Include real amounts. Casual tone. Actionable TODAY."
    )

    if stats.get('count', 0) > 0:
        user = f"One tip for: {year} {vibe} student, top spend: {stats.get('top_cat','?')} ({curr}{stats.get('top_cat_amt',0)}), {stats.get('wants_pct',0)}% wants, {curr}{stats.get('remaining',0)} left in budget."
    else:
        user = f"One general hostel life money tip for a {year} {vibe} student in India."

    text = ask_claude(SYSTEM, user)
    return jsonify({'success': bool(text), 'text': text})


@app.route('/api/ai/challenge', methods=['POST'])
def ai_challenge():
    """Weekly money challenge tailored to vibe + spending."""
    d       = request.get_json(force=True) or {}
    profile = d.get('profile', {})
    stats   = d.get('stats', {})
    curr    = profile.get('currency', '₹')
    vibe    = profile.get('vibe', 'engineering')

    SYSTEM = (
        "Generate ONE weekly money challenge for an Indian college hostel student. "
        "Format: first line = 'CHALLENGE: [catchy name]', then 2 sentences explaining it. "
        f"Include a {curr} savings goal. Make it fun, specific, achievable in 7 days. "
        "Examples: no-Swiggy week, split-everything challenge, cashback hunter, canteen-only lunches."
    )
    user = f"{vibe} student spending most on {stats.get('top_cat', 'food')}. Week {min(4,(datetime.date.today().day//7)+1)} of the month."

    text = ask_claude(SYSTEM, user)
    return jsonify({'success': bool(text), 'text': text})


@app.route('/api/ai/alert', methods=['POST'])
def ai_alert():
    """Context-aware money alert based on current budget status."""
    d     = request.get_json(force=True) or {}
    stats = d.get('stats', {})
    curr  = d.get('profile', {}).get('currency', '₹')

    # Server-side logic — no AI needed for alerts, they're data-driven
    if not stats or stats.get('count', 0) == 0:
        return jsonify({'success': True, 'text': '📊 No expenses logged yet. Start tracking so I can give you real alerts.'})

    budget    = stats.get('budget', 0)
    remaining = stats.get('remaining', 0)
    status    = stats.get('status', 'safe')
    today     = datetime.date.today()
    days_left = (datetime.date(today.year, today.month,
                  calendar_days(today.year, today.month)) - today).days + 1
    daily_left = round(remaining / max(days_left, 1), 0)
    wants_pct  = stats.get('wants_pct', 0)
    top_cat    = stats.get('top_cat', '')
    top_amt    = stats.get('top_cat_amt', 0)
    sub_amt    = stats.get('by_pm', {}).get('subscriptions', 0) if 'by_pm' in stats else (stats.get('by_cat',{}).get('subscriptions',0))

    if status == 'over_budget':
        msg = f"🚨 OVER BUDGET by {curr}{abs(remaining):.0f}. {days_left} days left. Canteen + transport only until month end."
    elif status == 'warning':
        msg = f"⚡ LOW: {curr}{remaining:.0f} left with {days_left} days to go. Max {curr}{daily_left:.0f}/day to survive the month."
    elif days_left <= 3:
        msg = f"🏁 LAST {days_left} DAYS of month. {curr}{remaining:.0f} remaining — don't blow it in the final stretch."
    elif wants_pct > 50:
        msg = f"✨ {wants_pct}% on wants — target is under 30%. Cut one want category this week."
    elif top_cat and top_amt > budget * 0.3:
        msg = f"📈 {top_cat.upper()} is {round(top_amt/budget*100)}% of your budget ({curr}{top_amt:.0f}). That's high — review it."
    elif sub_amt > budget * 0.08:
        msg = f"📱 Subscriptions = {curr}{sub_amt:.0f}. Split every one with hostel mates. Instant 50–75% saving."
    else:
        daily_avg = stats.get('daily_avg', 0)
        projected = round(daily_avg * 30, 0)
        color = "💚" if projected <= budget else "⚠️"
        msg = f"{color} On track! Daily avg {curr}{daily_avg:.0f}, projected {curr}{projected:.0f}/month vs budget {curr}{budget:.0f}."

    return jsonify({'success': True, 'text': msg})


@app.route('/api/ai/parse-upi', methods=['POST'])
def ai_parse_upi():
    """Parse a UPI/SMS/bank message and extract structured payment data."""
    d    = request.get_json(force=True) or {}
    text = d.get('text', '').strip()
    if not text:
        return jsonify({'success': False, 'message': 'No text provided'}), 400

    # Try AI parse
    if ANTHROPIC_API_KEY:
        SYSTEM = (
            "Extract payment info from a UPI/SMS/bank message. "
            "Return ONLY valid JSON — no explanation, no markdown, just JSON. "
            "Keys: amount (number), merchant (string), date (YYYY-MM-DD or null), "
            "category (one of: food, coffee, transport, entertainment, subscriptions, health, clothes, textbooks, other)."
        )
        raw = ask_claude(SYSTEM, f'Parse: "{text}"', max_tokens=120)
        if raw:
            try:
                import re
                clean = re.sub(r'```json|```', '', raw).strip()
                parsed = json.loads(clean)
                if parsed.get('amount'):
                    return jsonify({'success': True, 'parsed': parsed, 'method': 'ai'})
            except Exception:
                pass

    # Regex fallback
    import re
    amt_m = re.search(r'(?:rs\.?|inr|₹)\s*([\d,]+(?:\.\d{1,2})?)', text, re.I) or \
            re.search(r'([\d,]+(?:\.\d{1,2})?)\s*(?:rs\.?|inr|₹)', text, re.I)
    amount = float(amt_m.group(1).replace(',', '')) if amt_m else None

    date_m = re.search(r'(\d{1,2})[-/](\w{2,3})[-/](\d{2,4})', text, re.I) or \
             re.search(r'(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})', text)
    date = None
    if date_m:
        try:
            d_parsed = datetime.datetime.strptime(date_m.group(0), '%d-%b-%y') if len(date_m.group(3)) == 2 and not date_m.group(2).isdigit() else None
            if not d_parsed:
                d_parsed = datetime.datetime.strptime(date_m.group(0), '%d/%m/%Y') if '/' in date_m.group(0) else None
            if d_parsed:
                date = d_parsed.date().isoformat()
        except Exception:
            pass

    MERCHANTS = {
        'swiggy': 'food', 'zomato': 'food', 'mcdonalds': 'food', 'kfc': 'food',
        'dominos': 'food', 'subway': 'food', 'bigbasket': 'food', 'blinkit': 'food',
        'zepto': 'food', 'instamart': 'food', 'faasos': 'food', 'box8': 'food',
        'starbucks': 'coffee', 'cafe coffee day': 'coffee', 'ccd': 'coffee',
        'ola': 'transport', 'uber': 'transport', 'rapido': 'transport',
        'redbus': 'transport', 'irctc': 'transport', 'makemytrip': 'transport',
        'netflix': 'subscriptions', 'spotify': 'subscriptions', 'hotstar': 'subscriptions',
        'prime video': 'subscriptions', 'youtube': 'subscriptions', 'jiocinema': 'subscriptions',
        'amazon': 'other', 'flipkart': 'other', 'myntra': 'clothes', 'ajio': 'clothes',
        'nykaa': 'other', 'meesho': 'clothes',
    }
    lower = text.lower()
    merchant, category = None, 'other'
    for name, cat in MERCHANTS.items():
        if name in lower:
            merchant = name.title()
            category = cat
            break
    if not merchant:
        m = re.search(r'(?:to|paid to|payment to|transferred to|debit to)\s+([A-Za-z0-9 &]+?)(?:\s+(?:via|on|upi|ref|\.)|$)', text, re.I)
        if m:
            merchant = m.group(1).strip()

    if amount:
        return jsonify({'success': True, 'parsed': {'amount': amount, 'merchant': merchant, 'date': date, 'category': category}, 'method': 'regex'})

    return jsonify({'success': False, 'message': 'Could not extract amount from message'})


@app.route('/api/ai/chat', methods=['POST'])
def ai_chat():
    """General AI proxy — frontend can send any system+user prompt."""
    if not ANTHROPIC_API_KEY:
        return jsonify({'success': False, 'reason': 'no_key'}), 200
    d = request.get_json(force=True) or {}
    system = d.get('system', 'You are a helpful assistant.')
    user   = d.get('user', '')
    tokens = min(int(d.get('max_tokens', 280)), 800)
    if not user:
        return jsonify({'success': False, 'message': 'No user message'}), 400
    text = ask_claude(system, user, max_tokens=tokens)
    return jsonify({'success': bool(text), 'text': text})


# ══════════════════════════════════════════════════════════════
# ROUTES — Export / Backup
# ══════════════════════════════════════════════════════════════
@app.route('/api/export')
def export_data():
    """Download all data as JSON."""
    from flask import Response
    return Response(
        json.dumps(db, indent=2),
        mimetype='application/json',
        headers={'Content-Disposition': 'attachment;filename=broke_backup.json'}
    )

@app.route('/api/import', methods=['POST'])
def import_data():
    """Restore data from a JSON backup."""
    global db
    d = request.get_json(force=True) or {}
    if 'expenses' not in d:
        return jsonify({'success': False, 'message': 'Invalid backup file'}), 400
    db = d
    save_data(db)
    return jsonify({'success': True, 'message': f"Imported {len(db['expenses'])} expenses"})


# ══════════════════════════════════════════════════════════════
# RUN
# ══════════════════════════════════════════════════════════════
if __name__ == '__main__':
    expenses_count = len(db.get('expenses', []))
    print('\n' + '─' * 58)
    print('  💸  BROKE.EXE Backend')
    print('  🌐  http://localhost:5000')
    print(f'  📦  {expenses_count} expenses loaded')
    if ANTHROPIC_API_KEY:
        print('  ✅  ANTHROPIC_API_KEY found — AI fully enabled')
    else:
        print('  ⚠️   No API key — AI uses offline fallbacks')
        print('  →   PowerShell: $env:ANTHROPIC_API_KEY="sk-ant-..."')
        print('  →   CMD:        set ANTHROPIC_API_KEY=sk-ant-...')
        print('  →   Mac/Linux:  export ANTHROPIC_API_KEY=sk-ant-...')
    print('─' * 58 + '\n')
    app.run(debug=True, port=5000, host='127.0.0.1')
