"""
Tiffin Connect Lite — Design Thinking prototype
------------------------------------------------
A lightweight Streamlit demo showing how customers and home tiffin providers
could coordinate menus, orders, skips and deliveries in one place.

Run with:  streamlit run app.py

All data is illustrative sample data held in Streamlit session state
(in memory). Nothing is sent anywhere and no payments are processed.
"""

from __future__ import annotations

import html as _html
import random
from datetime import date, datetime, timedelta

import pandas as pd
import streamlit as st

st.set_page_config(
    page_title="Tiffin Connect Lite",
    page_icon="🍱",
    layout="wide",
    initial_sidebar_state="auto",
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CUSTOMER_ID = "C1"  # the demo customer (Riya)
SLOTS = ["Lunch", "Dinner"]
SLOT_ICON = {"Lunch": "☀️", "Dinner": "🌙"}

FLOW = ["Confirmed", "Preparing", "Out for Delivery", "Delivered"]
COUNTED = ("Confirmed", "Preparing", "Out for Delivery", "Delivered")  # count as real meals
IN_PROGRESS = ("Confirmed", "Preparing", "Out for Delivery")          # still need delivery
NEXT_STEP = {
    "Confirmed": ("Preparing", "👩‍🍳 Start preparing"),
    "Preparing": ("Out for Delivery", "🛵 Out for delivery"),
    "Out for Delivery": ("Delivered", "✅ Mark delivered"),
}
STATUS_STYLE = {  # background, text
    "Confirmed": ("#E2EDE5", "#1F4D3A"),
    "Preparing": ("#FBEBD8", "#94480F"),
    "Out for Delivery": ("#E3EAF4", "#2A4F78"),
    "Delivered": ("#D9EAD9", "#205A33"),
    "Skipped": ("#EEEBE4", "#655F55"),
    "Cancelled": ("#F5E2DF", "#8A2E24"),
}

PROVIDERS = [
    {
        "id": "P1", "name": "Aaji's Kitchen", "owner": "Sunanda Kale", "icon": "🍛",
        "locality": "Kothrud", "price": 90, "diet": "Veg", "rating": 4.7, "reviews": 212,
        "desc": "Simple Maharashtrian ghar-ka-khana cooked by a grandmother-and-daughter team. "
                "Less oil, fresh phulkas and a different bhaji every day.",
        "timings": "Lunch 12:30–2:00 pm · Dinner 8:00–9:30 pm",
        "slots": ["Lunch", "Dinner"], "capacity": 30, "since": 2019,
    },
    {
        "id": "P2", "name": "Annapurna Dabba Co.", "owner": "Hetal Shah", "icon": "🥘",
        "locality": "Baner", "price": 110, "diet": "Veg", "rating": 4.5, "reviews": 168,
        "desc": "Gujarati-style dal, bhaat, shaak and rotli with a sweet on Sundays. "
                "Popular with working professionals around Baner and Balewadi.",
        "timings": "Lunch 12:00–1:30 pm · Dinner 7:30–9:00 pm",
        "slots": ["Lunch", "Dinner"], "capacity": 25, "since": 2021,
    },
    {
        "id": "P3", "name": "Konkan Coast Home Meals", "owner": "Vaishali Sawant", "icon": "🐟",
        "locality": "Viman Nagar", "price": 140, "diet": "Non-Veg", "rating": 4.4, "reviews": 131,
        "desc": "Malvani-style home cooking — fish thalis, chicken rassa and egg curries with "
                "solkadhi. A veg option is always available.",
        "timings": "Lunch 1:00–2:30 pm · Dinner 8:00–9:30 pm",
        "slots": ["Lunch", "Dinner"], "capacity": 20, "since": 2020,
    },
    {
        "id": "P4", "name": "Green Bowl Tiffins", "owner": "Ritu Malhotra", "icon": "🥗",
        "locality": "Hinjewadi", "price": 120, "diet": "Veg", "rating": 4.6, "reviews": 97,
        "desc": "Light, high-protein North Indian lunches for IT-park professionals — "
                "millets, sprouts, paneer and seasonal sabzi. Lunch only.",
        "timings": "Lunch 12:30–2:00 pm",
        "slots": ["Lunch"], "capacity": 40, "since": 2022,
    },
    {
        "id": "P5", "name": "Ghar Ki Rasoi", "owner": "Manpreet Gill", "icon": "🍲",
        "locality": "Shivajinagar", "price": 100, "diet": "Veg & Non-Veg", "rating": 4.3, "reviews": 156,
        "desc": "Hearty Punjabi home food near the colleges in Shivajinagar — rajma chawal, "
                "chole and chicken curry twice a week. Student-friendly portions.",
        "timings": "Lunch 12:30–2:30 pm · Dinner 7:30–9:30 pm",
        "slots": ["Lunch", "Dinner"], "capacity": 35, "since": 2018,
    },
]

MENU_POOL = {
    "P1": [
        [("Varan Bhaat", "Toor dal varan, steamed rice and a spoon of ghee"),
         ("Batata Bhaji", "Dry potato sabzi with curry leaves"),
         ("Poli", "3 soft wheat chapatis"),
         ("Koshimbir", "Cucumber and peanut salad")],
        [("Matki Usal", "Sprouted moth bean curry"),
         ("Jeera Rice", "Cumin-tempered rice"),
         ("Jowar Bhakri", "2 bhakris with butter"),
         ("Thecha", "Green chilli-garlic relish")],
        [("Pithla", "Besan pithla with coriander"),
         ("Bharli Vangi", "Stuffed baby brinjal"),
         ("Poli", "3 soft wheat chapatis"),
         ("Masale Bhaat", "Spiced Maharashtrian rice")],
    ],
    "P2": [
        [("Gujarati Dal", "Sweet-tangy toor dal"),
         ("Bhaat", "Steamed rice"),
         ("Sev Tameta Shaak", "Tomato curry with sev"),
         ("Rotli", "4 thin rotlis"),
         ("Chaas", "Spiced buttermilk")],
        [("Kadhi Khichdi", "Gujarati kadhi with moong khichdi"),
         ("Bhindi Shaak", "Okra stir-fry"),
         ("Thepla", "2 methi theplas"),
         ("Papad", "Roasted")],
    ],
    "P3": [
        [("Bangda Fry Thali", "Rava-fried mackerel"),
         ("Malvani Fish Curry", "Coconut-kokum gravy"),
         ("Ukadiche Tandul", "Parboiled red rice"),
         ("Solkadhi", "Kokum-coconut drink")],
        [("Chicken Rassa", "Malvani chicken curry"),
         ("Vade", "2 Malvani vade"),
         ("Rice", "Steamed rice"),
         ("Veg option", "Kala vatana usal")],
    ],
    "P4": [
        [("Rajma Bowl", "Rajma with brown rice"),
         ("Paneer Tikka Salad", "Grilled paneer, greens, mint dressing"),
         ("Multigrain Roti", "2 rotis"),
         ("Curd", "Low-fat dahi")],
        [("Moong Dal Khichdi", "With ghee and papad"),
         ("Lauki Chana", "Bottle gourd with chana dal"),
         ("Millet Roti", "2 bajra rotis"),
         ("Sprouts Chaat", "Lemon and chaat masala")],
    ],
    "P5": [
        [("Rajma Chawal", "Slow-cooked rajma with jeera rice"),
         ("Aloo Gobhi", "Dry sabzi"),
         ("Tandoori Roti", "3 rotis"),
         ("Salad & Pickle", "Onion, cucumber, mango pickle")],
        [("Chole", "Amritsari-style chole"),
         ("Chicken Curry", "Home-style, Wed & Sun only"),
         ("Jeera Rice", "Cumin rice"),
         ("Phulka", "3 phulkas")],
    ],
}

MENU_NOTES = {
    "P1": "Extra poli available on request.",
    "P2": "Jain option available — mention in delivery note.",
    "P3": "Fish depends on the morning catch.",
    "P4": "Approx. 550 kcal per bowl.",
    "P5": "Spice level: medium. Ask for mild.",
}

CUSTOMERS = {
    "C1": {"name": "Riya Kulkarni", "phone": "+91 98220 11223", "locality": "Kothrud",
           "address": "Flat 302, Shanti Apartments, Karve Road", "diet": "Vegetarian",
           "menu_alerts": True, "skip_reminder": True},
    "C2": {"name": "Amit Joshi", "phone": "+91 98901 22334", "locality": "Kothrud",
           "address": "Room 14, Dahanukar Colony PG"},
    "C3": {"name": "Sneha Patil", "phone": "+91 97654 33445", "locality": "Kothrud",
           "address": "B-6, Ideal Colony"},
    "C4": {"name": "Rahul Deshmukh", "phone": "+91 99230 44556", "locality": "Kothrud",
           "address": "Paud Road, Shastrinagar"},
    "C5": {"name": "Kavya Iyer", "phone": "+91 98500 55667", "locality": "Kothrud",
           "address": "Mayur Colony, Lane 3"},
    "C6": {"name": "Omkar Bhosale", "phone": "+91 90110 66778", "locality": "Kothrud",
           "address": "Erandwane, near Mhatre Bridge"},
    "C7": {"name": "Neha Shah", "phone": "+91 98810 77889", "locality": "Kothrud",
           "address": "Bhusari Colony, Wing C"},
}


def plans_for(p: dict) -> list[dict]:
    """Illustrative monthly packages for a provider."""
    plans = []
    for slot in p["slots"]:
        plans.append({
            "name": f"Everyday {slot}", "slots": [slot], "meals": 26,
            "price": int(round(p["price"] * 26 * 0.9, -1)),
            "blurb": f"26 {slot.lower()}s · ~10% off",
        })
    if len(p["slots"]) == 2:
        plans.append({
            "name": "Full Day", "slots": ["Lunch", "Dinner"], "meals": 52,
            "price": int(round(p["price"] * 52 * 0.85, -1)),
            "blurb": "26 lunches + 26 dinners · ~15% off",
        })
    return plans


# ---------------------------------------------------------------------------
# Sample data (seeded relative to today so the demo always looks "live")
# ---------------------------------------------------------------------------

def menu_key(pid: str, day_iso: str) -> str:
    return f"{pid}|{day_iso}"


def build_seed_data() -> dict:
    today = date.today()

    def iso(offset: int) -> str:
        return (today + timedelta(days=offset)).isoformat()

    providers = {p["id"]: dict(p) for p in PROVIDERS}

    menus: dict[str, dict] = {}
    for p in PROVIDERS:
        pool = MENU_POOL[p["id"]]
        for off in (0, 1):
            if p["id"] == "P5" and off == 1:
                continue  # one kitchen hasn't published tomorrow yet
            items = pool[(today.toordinal() + off) % len(pool)]
            menus[menu_key(p["id"], iso(off))] = {
                "items": [{"dish": d, "detail": x} for d, x in items],
                "price": p["price"],
                "slots": list(p["slots"]),
                "capacity": p["capacity"],
                "note": MENU_NOTES[p["id"]],
                "published": True,
                "updated_at": "Sample data",
            }

    orders: list[dict] = []
    taken: set[tuple] = set()
    counter = [1000]

    def add(cid, pid, off, slot, status, source="One-day", qty=1, sub_id=None, note=""):
        if (cid, pid, off, slot) in taken:
            return
        taken.add((cid, pid, off, slot))
        counter[0] += 1
        orders.append({
            "id": f"TC-{counter[0]}", "customer_id": cid, "provider_id": pid,
            "date": iso(off), "slot": slot, "qty": qty,
            "amount": 0 if source == "Subscription" else providers[pid]["price"] * qty,
            "status": status, "source": source, "sub_id": sub_id, "note": note,
            "created_at": f"{iso(min(off, 0) - 1)} 19:30",
        })

    p1 = providers["P1"]
    subscriptions = [
        {"id": "SUB-201", "customer_id": "C1", "provider_id": "P1", "package": "Everyday Lunch",
         "slots": ["Lunch"], "meals_total": 26, "price": plans_for(p1)[0]["price"],
         "start": iso(-4), "end": iso(25), "status": "Active"},
        {"id": "SUB-202", "customer_id": "C2", "provider_id": "P1", "package": "Everyday Lunch",
         "slots": ["Lunch"], "meals_total": 26, "price": plans_for(p1)[0]["price"],
         "start": iso(-6), "end": iso(23), "status": "Active"},
    ]
    # Subscription meals
    for off in range(-4, 2):
        add("C1", "P1", off, "Lunch", "Delivered" if off < 0 else "Confirmed", "Subscription", sub_id="SUB-201")
    for off in range(-6, 2):
        add("C2", "P1", off, "Lunch", "Delivered" if off < 0 else "Confirmed", "Subscription", sub_id="SUB-202")

    # Today and tomorrow at Aaji's Kitchen
    add("C3", "P1", 0, "Lunch", "Preparing")
    add("C4", "P1", 0, "Dinner", "Confirmed", qty=2, note="Please send extra chutney")
    add("C5", "P1", 0, "Lunch", "Skipped")
    add("C6", "P1", 0, "Lunch", "Out for Delivery")
    add("C7", "P1", 0, "Dinner", "Confirmed")
    add("C3", "P1", 1, "Dinner", "Confirmed")
    add("C5", "P1", 1, "Lunch", "Confirmed")

    # Riya's past one-day orders elsewhere
    add("C1", "P1", -1, "Dinner", "Delivered")
    add("C1", "P2", -3, "Dinner", "Delivered")
    add("C1", "P4", -2, "Lunch", "Skipped")
    add("C1", "P3", -6, "Dinner", "Delivered")

    # A little activity at the other kitchens
    add("C4", "P2", 0, "Lunch", "Delivered")
    add("C6", "P2", 0, "Dinner", "Confirmed")
    add("C7", "P3", 0, "Lunch", "Preparing")
    add("C5", "P4", 0, "Lunch", "Confirmed")
    add("C2", "P5", 0, "Dinner", "Confirmed")

    # Past week history for Aaji's Kitchen (for records & earnings)
    rng = random.Random(42)
    for off in range(-6, 0):
        combos = [(c, s) for c in ("C3", "C4", "C5", "C6", "C7") for s in SLOTS]
        for cid, slot in rng.sample(combos, rng.randint(3, 6)):
            add(cid, "P1", off, slot, "Skipped" if rng.random() < 0.2 else "Delivered")

    orders.sort(key=lambda o: o["id"])

    now = datetime.now().strftime("%H:%M")
    activity = [
        {"pid": "P1", "date": iso(0), "time": "07:05", "icon": "📝", "text": "Today's menu published"},
        {"pid": "P1", "date": iso(0), "time": "08:40", "icon": "⏭️", "text": "Kavya Iyer skipped today's lunch"},
        {"pid": "P1", "date": iso(0), "time": "09:15", "icon": "🛒", "text": "Rahul Deshmukh ordered 2 dinners"},
        {"pid": "P1", "date": iso(0), "time": now, "icon": "👩‍🍳", "text": "Sneha Patil's lunch is being prepared"},
    ]

    return {
        "providers": providers,
        "menus": menus,
        "customers": {k: dict(v) for k, v in CUSTOMERS.items()},
        "orders": orders,
        "subscriptions": subscriptions,
        "activity": activity,
        "counters": {"order": counter[0], "sub": 202},
    }


# ---------------------------------------------------------------------------
# State helpers
# ---------------------------------------------------------------------------

def init_state() -> None:
    if "db" not in st.session_state:
        st.session_state.db = build_seed_data()
    defaults = {
        "role": None,
        "cust_page": "Discover",
        "owner_page": "Overview",
        "selected_provider": None,
        "owner_pid": "P1",
        "skip_pending": None,
        "flash": [],
        "menu_ver": 0,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def db() -> dict:
    return st.session_state.db


def today_iso() -> str:
    return date.today().isoformat()


def day_offset_iso(offset: int) -> str:
    return (date.today() + timedelta(days=offset)).isoformat()


def fmt_day(day_iso: str, relative: bool = True) -> str:
    d = date.fromisoformat(day_iso)
    label = f"{d.strftime('%a')} {d.day} {d.strftime('%b')}"
    if relative:
        delta = (d - date.today()).days
        if delta == 0:
            return f"Today · {label}"
        if delta == 1:
            return f"Tomorrow · {label}"
        if delta == -1:
            return f"Yesterday · {label}"
    return label


def rupees(x: float) -> str:
    return f"₹{int(round(x)):,}"


def esc(text) -> str:
    return _html.escape(str(text if text is not None else ""))


def provider(pid: str) -> dict:
    return db()["providers"][pid]


def customer(cid: str) -> dict:
    return db()["customers"].get(cid, {"name": "Unknown customer", "address": "", "phone": ""})


def get_menu(pid: str, day_iso: str, published_only: bool = True) -> dict | None:
    m = db()["menus"].get(menu_key(pid, day_iso))
    if m is None or (published_only and not m.get("published")):
        return None
    return m


def booked_meals(pid: str, day_iso: str, slot: str | None = None) -> int:
    return sum(
        o["qty"] for o in db()["orders"]
        if o["provider_id"] == pid and o["date"] == day_iso
        and (slot is None or o["slot"] == slot) and o["status"] in COUNTED
    )


def active_order_for(cid: str, pid: str, day_iso: str, slot: str) -> dict | None:
    for o in db()["orders"]:
        if (o["customer_id"] == cid and o["provider_id"] == pid and o["date"] == day_iso
                and o["slot"] == slot and o["status"] in COUNTED):
            return o
    return None


def sub_used(sub: dict) -> int:
    return sum(1 for o in db()["orders"] if o.get("sub_id") == sub["id"] and o["status"] in COUNTED)


def sub_remaining(sub: dict) -> int:
    return max(sub["meals_total"] - sub_used(sub), 0)


def active_subs(cid: str | None = None, pid: str | None = None) -> list[dict]:
    t = today_iso()
    return [
        s for s in db()["subscriptions"]
        if s["status"] == "Active" and s["end"] >= t
        and (cid is None or s["customer_id"] == cid) and (pid is None or s["provider_id"] == pid)
    ]


def next_order_id() -> str:
    db()["counters"]["order"] += 1
    return f"TC-{db()['counters']['order']}"


def log(pid: str, icon: str, text: str) -> None:
    db()["activity"].append({
        "pid": pid, "date": today_iso(), "time": datetime.now().strftime("%H:%M"),
        "icon": icon, "text": text,
    })


def flash(kind: str, title: str, body: str = "") -> None:
    st.session_state.flash.append((kind, title, body))


def ensure_valid(key: str, options: list) -> None:
    """Drop a stored widget value that is no longer one of the options."""
    if key in st.session_state and st.session_state[key] not in options:
        del st.session_state[key]


def choice(key: str, default):
    val = st.session_state.get(key)
    return default if val is None else val


def create_order(cid, pid, day_iso, slot, qty=1, source="One-day", sub_id=None, note="") -> dict:
    p = provider(pid)
    menu = get_menu(pid, day_iso, published_only=False)
    unit = menu["price"] if menu else p["price"]
    order = {
        "id": next_order_id(), "customer_id": cid, "provider_id": pid, "date": day_iso,
        "slot": slot, "qty": qty, "amount": 0 if source == "Subscription" else unit * qty,
        "status": "Confirmed", "source": source, "sub_id": sub_id, "note": note.strip(),
        "created_at": datetime.now().strftime("%Y-%m-%d %H:%M"),
    }
    db()["orders"].append(order)
    return order


# ---------------------------------------------------------------------------
# Callbacks (run before the rerun, so the new state is shown immediately)
# ---------------------------------------------------------------------------

def cb_choose_role(role: str) -> None:
    st.session_state.role = role
    st.session_state.skip_pending = None


def cb_cust_nav(page: str) -> None:
    st.session_state.cust_page = page
    st.session_state.skip_pending = None
    st.session_state.pop("order_confirm", None)


def cb_owner_nav(page: str) -> None:
    st.session_state.owner_page = page


def cb_open_provider(pid: str) -> None:
    st.session_state.selected_provider = pid
    st.session_state.cust_page = "Provider"


def cb_owner_kitchen() -> None:
    st.session_state.owner_pid = st.session_state.owner_pid_widget


def cb_place_order(pid: str) -> None:
    day = choice(f"day_{pid}", today_iso())
    menu = get_menu(pid, day)
    if menu is None:
        flash("error", "Menu not available", "This kitchen hasn't published a menu for that day yet.")
        return
    slot = choice(f"slot_{pid}_{day}", menu["slots"][0])
    if slot not in menu["slots"]:
        flash("error", "Slot not available", f"{provider(pid)['name']} isn't serving {slot.lower()} that day.")
        return
    qty = int(st.session_state.get(f"qty_{pid}", 1) or 1)
    note = st.session_state.get(f"note_{pid}", "") or ""
    existing = active_order_for(CUSTOMER_ID, pid, day, slot)
    if existing:
        flash("warning", "You already have this meal booked",
              f"{slot} on {fmt_day(day)} from {provider(pid)['name']} is already on your list "
              f"({existing['id']}, {existing['status']}). No duplicate order was created.")
        return
    left = menu["capacity"] - booked_meals(pid, day, slot)
    if qty > left:
        flash("error", "Not enough tiffins left", f"Only {max(left, 0)} {slot.lower()} tiffin(s) left for that day.")
        return
    order = create_order(CUSTOMER_ID, pid, day, slot, qty=qty, note=note)
    st.session_state[f"note_{pid}"] = ""
    name = customer(CUSTOMER_ID)["name"]
    log(pid, "🛒", f"{name} ordered {qty} {slot.lower()}{'s' if qty > 1 else ''} for {fmt_day(day, False)}")
    st.session_state.order_confirm = (pid, f"<b>{order['id']}</b> · {qty} × {slot} · {fmt_day(day)} · {esc(provider(pid)['name'])} · "
          f"{rupees(order['amount'])} payable on delivery")


def cb_activate_sub(prefix: str, fixed_pid: str | None = None) -> None:
    pid = fixed_pid or st.session_state.get(f"{prefix}_pid")
    if not pid:
        flash("error", "Choose a tiffin service first")
        return
    p = provider(pid)
    plans = plans_for(p)
    plan_name = choice(f"{prefix}_plan_{pid}", plans[0]["name"])
    plan = next((x for x in plans if x["name"] == plan_name), plans[0])
    start = choice(f"{prefix}_start", today_iso())
    if active_subs(CUSTOMER_ID, pid):
        flash("warning", "You already have an active plan here",
              f"Your plan with {esc(p['name'])} is still running. See it under Subscription.")
        return
    db()["counters"]["sub"] += 1
    sub = {
        "id": f"SUB-{db()['counters']['sub']}", "customer_id": CUSTOMER_ID, "provider_id": pid,
        "package": plan["name"], "slots": list(plan["slots"]), "meals_total": plan["meals"],
        "price": plan["price"], "start": start,
        "end": (date.fromisoformat(start) + timedelta(days=29)).isoformat(), "status": "Active",
    }
    db()["subscriptions"].append(sub)
    # Schedule the first two days of meals so they show up for the owner right away
    scheduled = 0
    for off in range(2):
        day = (date.fromisoformat(start) + timedelta(days=off)).isoformat()
        for slot in plan["slots"]:
            if active_order_for(CUSTOMER_ID, pid, day, slot) is None and sub_remaining(sub) > 0:
                create_order(CUSTOMER_ID, pid, day, slot, source="Subscription", sub_id=sub["id"])
                scheduled += 1
    log(pid, "🔁", f"{customer(CUSTOMER_ID)['name']} subscribed to {plan['name']} ({plan['meals']} meals)")
    flash("success", "Subscription activated",
          f"<b>{esc(plan['name'])}</b> with {esc(p['name'])} · {fmt_day(start, False)} → "
          f"{fmt_day(sub['end'], False)} · {scheduled} upcoming meal(s) scheduled. "
          f"Demo only — no payment was taken.")


def cb_request_skip(order_id: str) -> None:
    st.session_state.skip_pending = order_id


def cb_cancel_skip() -> None:
    st.session_state.skip_pending = None


def cb_confirm_skip(order_id: str) -> None:
    st.session_state.skip_pending = None
    order = next((o for o in db()["orders"] if o["id"] == order_id), None)
    if order is None:
        flash("error", "Order not found")
        return
    if order["status"] != "Confirmed" or order["date"] < today_iso():
        flash("error", "This meal can no longer be skipped",
              f"The kitchen has already marked it <b>{esc(order['status'])}</b>.")
        return
    order["status"] = "Skipped"
    p = provider(order["provider_id"])
    log(p["id"], "⏭️", f"{customer(order['customer_id'])['name']} skipped {order['slot'].lower()} "
                       f"for {fmt_day(order['date'], False)}")
    extra = " One meal has been credited back to your plan." if order["source"] == "Subscription" else \
        " You won't be charged for it."
    flash("success", "Meal skipped",
          f"{order['slot']} on {fmt_day(order['date'])} from {esc(p['name'])} is now "
          f"<b>Skipped</b>. {esc(p['owner'].split()[0])} won't cook it.{extra}")


def cb_set_status(order_id: str, status: str) -> None:
    order = next((o for o in db()["orders"] if o["id"] == order_id), None)
    if order is None:
        return
    if order["status"] not in IN_PROGRESS:
        flash("warning", "Order can't be updated", f"{order_id} is already {order['status']}.")
        return
    order["status"] = status
    who = customer(order["customer_id"])["name"]
    log(order["provider_id"], {"Preparing": "👩‍🍳", "Out for Delivery": "🛵", "Delivered": "✅"}.get(status, "•"),
        f"{who}'s {order['slot'].lower()} → {status}")
    st.toast(f"{order_id} marked {status}", icon="✅")


def cb_save_profile() -> None:
    name = (st.session_state.get("pf_name") or "").strip()
    phone = (st.session_state.get("pf_phone") or "").strip()
    address = (st.session_state.get("pf_address") or "").strip()
    if not name or not phone or not address:
        flash("error", "Please fill in your name, phone number and delivery address")
        return
    c = db()["customers"][CUSTOMER_ID]
    c.update({
        "name": name, "phone": phone, "address": address,
        "locality": st.session_state.get("pf_locality", c.get("locality")),
        "diet": st.session_state.get("pf_diet", c.get("diet")),
        "menu_alerts": bool(st.session_state.get("pf_alerts")),
        "skip_reminder": bool(st.session_state.get("pf_reminder")),
    })
    flash("success", "Profile saved", "Kitchens will use these details for your deliveries.")


def cb_reset_demo() -> None:
    st.session_state.db = build_seed_data()
    st.session_state.skip_pending = None
    st.session_state.menu_ver += 1
    for k in list(st.session_state.keys()):
        if k.startswith(("pf_", "note_", "qty_")):
            del st.session_state[k]
    flash("success", "Demo data reset", "All sample orders, menus and subscriptions are back to the starting state.")


# ---------------------------------------------------------------------------
# Styling
# ---------------------------------------------------------------------------

CSS = """
<style>
:root{
  --ivory:#FBF8F1; --card:#FFFFFF; --sage:#EEF2EA; --sage-2:#DCE6D6; --sage-3:#C6D5BF;
  --forest:#1F4D3A; --forest-2:#2B6A4F; --orange:#D4772C; --orange-2:#BD6620; --orange-soft:#FBEEDF;
  --ink:#1D2A23; --muted:#5F6B64; --line:#E7E2D6;
  --shadow:0 1px 2px rgba(31,77,58,.05), 0 8px 24px rgba(31,77,58,.07);
  --serif: "Iowan Old Style","Palatino Linotype",Palatino,"Book Antiqua",Georgia,serif;
  --sans: ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI",Roboto,"Helvetica Neue",Arial,sans-serif;
}
html, body, .stApp, .stMarkdown, button, input, textarea, select { font-family: var(--sans); }
.stApp { background: var(--ivory); color: var(--ink); }
#MainMenu, footer, .stDeployButton, [data-testid="stToolbarActions"], [data-testid="stDecoration"],
[data-testid="stAppDeployButton"] { display:none !important; }
header[data-testid="stHeader"] { background: transparent; }
.block-container { padding-top: 2.2rem; padding-bottom: 3rem; max-width: 1180px; }
h1, h2, h3 { color: var(--ink); letter-spacing: -0.01em; }
a { color: var(--forest-2); }

/* ---------- sidebar ---------- */
[data-testid="stSidebar"] { background: var(--forest); }
[data-testid="stSidebar"] * { color: #EEF2EA; }
[data-testid="stSidebar"] [data-baseweb="select"] * { color: var(--ink) !important; }
[data-testid="stSidebar"] [data-baseweb="select"] > div { background:#FBF8F1; border-color: transparent; }
[data-testid="stSidebar"] [data-baseweb="select"] input,
[data-testid="stSidebar"] [data-testid="stSelectbox"] input,
[data-testid="stSidebar"] [data-testid="stSelectbox"] button,
[data-testid="stSidebar"] [data-testid="stSelectbox"] svg {
  color: var(--ink) !important; -webkit-text-fill-color: var(--ink) !important; fill: var(--ink) !important; opacity:1 !important;
}
[data-testid="stSidebar"] [data-testid="stSelectbox"] [role="group"] { background:#FBF8F1 !important; }
[data-testid="stSidebar"] .stButton button {
  width:100%; justify-content:flex-start; text-align:left; border-radius:12px;
  background: transparent; border: 1px solid transparent; color:#E8EFE5; font-weight:500;
  padding: .55rem .85rem; box-shadow:none;
}
[data-testid="stSidebar"] .stButton button > div { justify-content:flex-start; width:100%; }
[data-testid="stSidebar"] .stButton button p { text-align:left; }
[data-testid="stSidebar"] [data-testid="stPopover"] button {
  background: transparent; border: 1px solid rgba(255,255,255,.18); border-radius:12px; color:#E8EFE5;
}
[data-testid="stSidebar"] [data-testid="stPopover"] button:hover { background: rgba(255,255,255,.08); }
[data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,.08); border-color: rgba(255,255,255,.12); }
[data-testid="stSidebar"] .stButton button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] {
  background: var(--sage); color: var(--forest); font-weight:700; border-color: var(--sage);
}
[data-testid="stSidebar"] .stButton button[kind="primary"] *,
[data-testid="stSidebar"] [data-testid="stBaseButton-primary"] * { color: var(--forest); }
[data-testid="stSidebar"] hr { border-color: rgba(255,255,255,.15); }
.sb-brand { display:flex; align-items:center; gap:.6rem; margin:.2rem 0 1rem; }
.sb-brand .logo { width:40px; height:40px; border-radius:12px; background:var(--sage); display:grid; place-items:center; font-size:1.3rem; }
.sb-brand .name { font-family: var(--serif); font-size:1.15rem; font-weight:700; line-height:1.1; }
.sb-brand .sub { font-size:.72rem; opacity:.75; letter-spacing:.06em; text-transform:uppercase; }
.sb-user { background: rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12); border-radius:14px; padding:.7rem .85rem; margin-bottom:1rem; font-size:.85rem; }
.sb-user b { font-size:.95rem; }
.sb-label { font-size:.7rem; letter-spacing:.09em; text-transform:uppercase; opacity:.65; margin:.4rem 0 .3rem .2rem; }

/* ---------- buttons ---------- */
.stButton button, .stFormSubmitButton button, .stDownloadButton button {
  border-radius: 12px; font-weight: 600; padding: .55rem 1.05rem; transition: all .15s ease;
}
.main .stButton button[kind="secondary"], .stFormSubmitButton button[kind="secondary"], .stDownloadButton button {
  background: #fff; border: 1px solid var(--line); color: var(--ink);
}
.stButton button[kind="secondary"]:hover, .stDownloadButton button:hover { border-color: var(--forest-2); color: var(--forest); }
[class*="st-key-cta_"] button {
  background: var(--orange) !important; border-color: var(--orange) !important; color:#fff !important;
  font-size: 1rem; padding: .75rem 1rem; box-shadow: 0 6px 16px rgba(212,119,44,.25);
}
[class*="st-key-cta_"] button:hover { background: var(--orange-2) !important; }
[class*="st-key-cta_"] button:disabled { background: #EFE4D6 !important; border-color: #EFE4D6 !important; box-shadow:none; cursor:not-allowed; }
[class*="st-key-cta_"] button:disabled p { color: #9C8A76 !important; }
[class*="st-key-cta_"] button p { color:#fff !important; font-weight:700; }

/* ---------- card shells (keyed containers) ---------- */
[class*="st-key-pcard_"], [class*="st-key-panel_"], [class*="st-key-role_"], [class*="st-key-ocard_"],
[class*="st-key-mcard_"], [class*="st-key-plan_"] {
  background: var(--card); border: 1px solid var(--line); border-radius: 20px;
  padding: 1.15rem 1.2rem 1.2rem; box-shadow: var(--shadow);
}
[class*="st-key-pcard_"]:hover, [class*="st-key-role_"]:hover { border-color: var(--sage-3); }
[class*="st-key-role_"] { padding: 1.6rem 1.6rem 1.5rem; }
[class*="st-key-ocard_"] { padding: .9rem 1.1rem 1.05rem; border-radius: 16px; }
[class*="st-key-mcard_"] { padding: .95rem 1.1rem 1.2rem; border-radius: 16px; }
[class*="st-key-plan_"] { background: var(--sage); border-color: var(--sage-2); box-shadow:none; }
[class*="st-key-confirm_"] {
  background: var(--orange-soft); border: 1px solid #F0CFA9; border-radius: 18px; padding: 1.1rem 1.2rem;
}

/* ---------- generic components ---------- */
.tc-eyebrow { font-size:.74rem; font-weight:700; letter-spacing:.1em; text-transform:uppercase; color: var(--orange-2); margin-bottom:.25rem; }
h1.tc-title, .tc-title { font-family: var(--serif) !important; font-size: clamp(1.6rem, 2.4vw, 2.1rem) !important; font-weight:700 !important; color: var(--ink); line-height:1.15 !important; margin:0 !important; padding:0 !important; }
.tc-sub, p.tc-sub { color: var(--muted); margin:.35rem 0 1.2rem; font-size:.98rem !important; }
.tc-muted, p.tc-muted { color: var(--muted); font-size:.88rem !important; }
.tc-small, p.tc-small { font-size:.8rem !important; color: var(--muted); line-height:1.45; }
.pc-desc, p.pc-desc { font-size:.9rem; }
.badge { display:inline-flex; align-items:center; gap:.3rem; padding:.18rem .6rem; border-radius:999px; font-size:.76rem; font-weight:650; white-space:nowrap; }
.chip { display:inline-flex; align-items:center; gap:.3rem; padding:.2rem .6rem; border-radius:999px; font-size:.78rem; background: var(--sage); color: var(--forest); font-weight:600; margin: 0 .25rem .25rem 0; }
.chip.orange { background: var(--orange-soft); color: var(--orange-2); }
.chip.grey { background:#F1EEE8; color:#6B655B; }
.veg-dot { width:.7rem; height:.7rem; border:1.5px solid currentColor; border-radius:2px; display:inline-grid; place-items:center; }
.veg-dot::after { content:""; width:.32rem; height:.32rem; border-radius:50%; background: currentColor; }

.pc-head { display:flex; gap:.9rem; align-items:flex-start; }
.pc-icon { flex:0 0 auto; width:56px; height:56px; border-radius:16px; background: var(--sage); display:grid; place-items:center; font-size:1.7rem; }
.pc-name { font-family: var(--serif); font-size:1.2rem; font-weight:700; line-height:1.2; color: var(--ink); }
.pc-meta { font-size:.84rem; color: var(--muted); margin-top:.15rem; }
.pc-price { margin-left:auto; text-align:right; white-space:nowrap; }
.pc-price b { font-size:1.15rem; color: var(--forest); }
.pc-price span { display:block; font-size:.72rem; color: var(--muted); }
.pc-desc { color:#3E4A43; font-size:.9rem; margin:.7rem 0 .55rem; line-height:1.45; }
.pc-menu { font-size:.82rem; background: var(--ivory); border:1px dashed var(--line); border-radius:12px; padding:.5rem .7rem; margin-bottom:.7rem; color:#4A554E; }

.stat { background: var(--card); border:1px solid var(--line); border-radius:18px; padding: 1rem 1.1rem; box-shadow: var(--shadow); height:100%; }
.stat .lbl { font-size:.78rem; color: var(--muted); font-weight:600; text-transform:uppercase; letter-spacing:.05em; }
.stat .val { font-family: var(--serif); font-size: 2rem; font-weight:700; color: var(--forest); line-height:1.15; margin-top:.15rem; }
.stat .hint { font-size:.8rem; color: var(--muted); margin-top:.15rem; }
.stat.accent .val { color: var(--orange-2); }
.stat .ic { float:right; font-size:1.25rem; opacity:.85; }

.callout { border-radius:16px; padding: .85rem 1.05rem; margin-bottom: 1rem; border:1px solid; display:flex; gap:.75rem; align-items:flex-start; }
.callout .ci { font-size:1.2rem; line-height:1.3; }
.callout .ct { font-weight:700; margin-bottom:.1rem; }
.callout .cb { font-size:.9rem; }
.callout.success { background:#E9F2EA; border-color:#BFD8C3; color:#1D4A31; }
.callout.warning { background: var(--orange-soft); border-color:#F0CFA9; color:#7A3E0E; }
.callout.error { background:#F9E6E3; border-color:#EBC0BA; color:#7D2A20; }
.callout.info { background: var(--sage); border-color: var(--sage-2); color: var(--forest); }

.menu-list { list-style:none; padding:0; margin:.4rem 0 0; }
.menu-list li { display:flex; gap:.7rem; padding:.6rem 0; border-bottom:1px solid #F0ECE3; }
.menu-list li:last-child { border-bottom:none; }
.menu-list .dish { font-weight:650; color: var(--ink); }
.menu-list .det { font-size:.84rem; color: var(--muted); }
.menu-list .bul { color: var(--orange); font-size:1rem; line-height:1.4; }

.empty { text-align:center; padding: 2.2rem 1rem; border:1.5px dashed var(--sage-3); border-radius:20px; background: #FDFCF8; color: var(--muted); }
.empty .ei { font-size:2.2rem; }
.empty .et { font-family: var(--serif); font-size:1.15rem; color: var(--ink); font-weight:700; margin:.3rem 0 .2rem; }

.track { display:flex; align-items:center; gap:0; margin:.6rem 0 .2rem; }
.track .st { display:flex; flex-direction:column; align-items:center; flex:1; font-size:.68rem; color: var(--muted); text-align:center; position:relative; }
.track .dot { width:14px; height:14px; border-radius:50%; background:#E5E1D7; border:2px solid #fff; box-shadow:0 0 0 1px #E5E1D7; margin-bottom:.25rem; z-index:1; }
.track .st.done .dot { background: var(--forest-2); box-shadow:0 0 0 1px var(--forest-2); }
.track .st.done { color: var(--forest); font-weight:650; }
.track .st:not(:first-child)::before { content:""; position:absolute; top:6px; right:50%; width:100%; height:2px; background:#E5E1D7; }
.track .st.done:not(:first-child)::before { background: var(--forest-2); }

.feed-item { display:flex; gap:.7rem; padding:.55rem 0; border-bottom:1px solid #F0ECE3; font-size:.9rem; }
.feed-item:last-child { border-bottom:none; }
.feed-item .t { color: var(--muted); font-size:.78rem; min-width:3rem; padding-top:.1rem; }

.hero { text-align:center; padding: 1.5rem 0 1.2rem; }
.hero .logo { width:76px; height:76px; margin: 0 auto .9rem; border-radius:24px; background: var(--forest); display:grid; place-items:center; font-size:2.3rem; box-shadow: 0 10px 30px rgba(31,77,58,.25); }
.hero h1 { font-family: var(--serif); font-size: clamp(2.2rem, 5vw, 3.3rem); margin:0; color: var(--forest); font-weight:700; letter-spacing:-.02em; }
.hero .tag { font-family: var(--serif); font-size: clamp(1.1rem, 2.2vw, 1.45rem); color: var(--orange-2); font-style: italic; margin:.35rem 0 .8rem; }
.hero .desc { max-width: 620px; margin: 0 auto; color: var(--muted); font-size:1.02rem; line-height:1.55; }
.proto { display:inline-block; background: var(--orange-soft); color: var(--orange-2); border:1px solid #F0CFA9; border-radius:999px; padding:.22rem .75rem; font-size:.72rem; font-weight:700; letter-spacing:.08em; text-transform:uppercase; margin-bottom:1rem; }
.role-ic { width:58px; height:58px; border-radius:18px; display:grid; place-items:center; font-size:1.8rem; background: var(--sage); margin-bottom:.8rem; }
.role-t { font-family: var(--serif); font-size:1.45rem; font-weight:700; color: var(--ink); }
.role-d { color: var(--muted); font-size:.93rem; margin:.3rem 0 .8rem; line-height:1.5; }
.role-list { list-style:none; padding:0; margin:0 0 1rem; font-size:.88rem; color:#3E4A43; }
.role-list li { padding:.22rem 0; }
.role-list li::before { content:"✓"; color: var(--forest-2); font-weight:800; margin-right:.5rem; }
.problem { display:flex; gap:.6rem; justify-content:center; flex-wrap:wrap; margin: 1.6rem 0 .4rem; }

.stTabs [data-baseweb="tab-list"] { gap: .4rem; }
.stTabs [data-baseweb="tab"] { font-weight:600; }
[data-testid="stDataFrame"] { border-radius: 14px; overflow:hidden; border:1px solid var(--line); }
[data-testid="stForm"] { background: var(--card); border:1px solid var(--line); border-radius:20px; padding: 1.2rem 1.3rem; box-shadow: var(--shadow); }
[data-testid="stExpander"] { background: var(--card); border-radius:16px; }

@media (max-width: 640px){
  .block-container { padding-left: 1rem; padding-right: 1rem; padding-top: 1.2rem; }
  .pc-price b { font-size:1rem; }
  .stat .val { font-size:1.6rem; }
  [class*="st-key-role_"] { padding: 1.2rem; }
}
</style>
"""


def inject_css() -> None:
    st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------------------
# Reusable UI pieces
# ---------------------------------------------------------------------------

def html(markup: str) -> None:
    """Render HTML; lines are stripped so Markdown never treats them as code blocks."""
    st.markdown(" ".join(line.strip() for line in markup.splitlines()), unsafe_allow_html=True)


def page_header(eyebrow: str, title: str, subtitle: str = "") -> None:
    html(f"""
        <div class="tc-eyebrow">{esc(eyebrow)}</div>
        <h1 class="tc-title">{esc(title)}</h1>
        {f'<p class="tc-sub">{esc(subtitle)}</p>' if subtitle else '<div style="height:1rem"></div>'}
    """)


def callout(kind: str, title: str, body: str = "") -> None:
    icon = {"success": "✅", "warning": "⚠️", "error": "⛔", "info": "💡"}.get(kind, "•")
    html(f"""
        <div class="callout {kind}"><div class="ci">{icon}</div>
        <div><div class="ct">{esc(title)}</div>{f'<div class="cb">{body}</div>' if body else ''}</div></div>
    """)


def show_flash() -> None:
    msgs = st.session_state.flash
    st.session_state.flash = []
    for kind, title, body in msgs:
        callout(kind, title, body)


def badge(status: str) -> str:
    bg, fg = STATUS_STYLE.get(status, ("#EEE", "#333"))
    return f'<span class="badge" style="background:{bg};color:{fg}">● {esc(status)}</span>'


def diet_chip(diet: str) -> str:
    if diet == "Veg":
        return '<span class="chip" style="color:#2E7D32;background:#E7F2E7"><span class="veg-dot"></span>Veg</span>'
    if diet == "Non-Veg":
        return '<span class="chip" style="color:#A3341F;background:#F8E5E1"><span class="veg-dot"></span>Non-Veg</span>'
    return '<span class="chip orange"><span class="veg-dot"></span>Veg &amp; Non-Veg</span>'


def stat_card(label: str, value, hint: str = "", icon: str = "", accent: bool = False) -> None:
    html(f"""
        <div class="stat{' accent' if accent else ''}"><span class="ic">{icon}</span>
        <div class="lbl">{esc(label)}</div><div class="val">{esc(value)}</div>
        <div class="hint">{esc(hint)}</div></div>
    """)


def empty_state(icon: str, title: str, body: str) -> None:
    html(f'<div class="empty"><div class="ei">{icon}</div><div class="et">{esc(title)}</div><div>{esc(body)}</div></div>')


def tracker(status: str) -> str:
    if status not in FLOW:
        return ""
    idx = FLOW.index(status)
    steps = "".join(
        f'<div class="st{" done" if i <= idx else ""}"><div class="dot"></div>{esc(s)}</div>'
        for i, s in enumerate(FLOW)
    )
    return f'<div class="track">{steps}</div>'


def menu_html(menu: dict) -> str:
    parts = []
    for item in menu["items"]:
        detail = f'<div class="det">{esc(item["detail"])}</div>' if item.get("detail") else ""
        parts.append(f'<li><span class="bul">◆</span><div><div class="dish">{esc(item["dish"])}</div>{detail}</div></li>')
    return f'<ul class="menu-list">{"".join(parts)}</ul>'


def orders_frame(orders: list[dict], for_owner: bool = False) -> pd.DataFrame:
    rows = []
    for o in orders:
        p = provider(o["provider_id"])
        rows.append({
            "Order ID": o["id"],
            "Date": date.fromisoformat(o["date"]),
            "Slot": o["slot"],
            ("Customer" if for_owner else "Kitchen"): customer(o["customer_id"])["name"] if for_owner else p["name"],
            "Qty": o["qty"],
            "Type": o["source"],
            "Amount (₹)": o["amount"],
            "Status": o["status"],
        })
    df = pd.DataFrame(rows)
    if not df.empty:
        df = df.sort_values(["Date", "Slot", "Order ID"], ascending=[False, True, True]).reset_index(drop=True)
    return df


def sidebar_shell(role_label: str, user_line: str, sub_line: str) -> None:
    with st.sidebar:
        html(f"""
            <div class="sb-brand"><div class="logo">🍱</div>
            <div><div class="name">Tiffin Connect Lite</div><div class="sub">{esc(role_label)}</div></div></div>
            <div class="sb-user"><b>{esc(user_line)}</b><br><span style="opacity:.75">{esc(sub_line)}</span></div>
        """)


def sidebar_footer() -> None:
    with st.sidebar:
        st.divider()
        st.button("↩  Switch role", key="sb_switch", on_click=cb_choose_role, args=(None,), width="stretch")
        with st.popover("⟲  Reset demo data", width="stretch"):
            st.write("Restore all sample orders, menus and subscriptions?")
            st.button("Yes, reset", key="sb_reset_yes", type="primary", on_click=cb_reset_demo)
        html('<div class="tc-small" style="margin-top:.8rem;opacity:.7;color:#DCE6D6">Prototype demo · sample data only</div>')


# ---------------------------------------------------------------------------
# Landing page
# ---------------------------------------------------------------------------

def render_landing() -> None:
    show_flash()
    html("""
        <div class="hero">
          <div class="proto">Prototype Demo</div>
          <div class="logo">🍱</div>
          <h1>Tiffin Connect Lite</h1>
          <div class="tag">Homely meals. Hassle-free living.</div>
          <p class="desc">One shared place for home tiffin kitchens and the students and professionals they feed —
          daily menus, orders, skips and deliveries, without the endless WhatsApp back-and-forth.</p>
          <div class="problem">
            <span class="chip">📋 Menus published daily</span>
            <span class="chip">⏭️ Skip a meal in two taps</span>
            <span class="chip">🧮 Owners see exact counts</span>
            <span class="chip orange">♻️ Less food wasted</span>
          </div>
        </div>
    """)
    st.write("")
    _, c1, c2, _ = st.columns([0.4, 3, 3, 0.4], gap="large")
    with c1:
        with st.container(key="role_customer"):
            html("""
                <div class="role-ic">🧑‍🎓</div>
                <div class="role-t">I'm a Customer</div>
                <div class="role-d">Living alone, studying or working in Pune and looking for reliable home food.</div>
                <ul class="role-list"><li>Browse kitchens near you</li><li>See today's menu before ordering</li>
                <li>Subscribe monthly or skip a meal</li></ul>
            """)
            st.button("Continue as Customer  →", key="go_customer", type="primary",
                      on_click=cb_choose_role, args=("customer",), width="stretch")
    with c2:
        with st.container(key="role_owner"):
            html("""
                <div class="role-ic" style="background:var(--orange-soft)">👩‍🍳</div>
                <div class="role-t">I run a Tiffin Service</div>
                <div class="role-d">A home kitchen that cooks lunch and dinner tiffins for regular customers.</div>
                <ul class="role-list"><li>Publish the day's menu once</li><li>Know exactly how many to cook</li>
                <li>Track deliveries and earnings</li></ul>
            """)
            st.button("Continue as Tiffin Owner  →", key="go_owner", type="primary",
                      on_click=cb_choose_role, args=("owner",), width="stretch")
    html('<p class="tc-small" style="text-align:center;margin-top:1.6rem">All kitchens, people and prices are '
         'fictional sample data for a Design Thinking prototype. No payments are processed.</p>')


# ---------------------------------------------------------------------------
# Customer mode
# ---------------------------------------------------------------------------

CUSTOMER_NAV = [
    ("Discover", "🔍  Discover tiffins"),
    ("Subscription", "🔁  Subscription"),
    ("Skip", "⏭️  Skip a meal"),
    ("My Tiffin", "🍱  My Tiffin"),
]


def render_customer() -> None:
    me = customer(CUSTOMER_ID)
    sidebar_shell("Customer", me["name"], f"📍 {me.get('locality', '')}, Pune")
    current = st.session_state.cust_page
    with st.sidebar:
        html('<div class="sb-label">Menu</div>')
        for page, label in CUSTOMER_NAV:
            is_active = current == page or (current == "Provider" and page == "Discover")
            st.button(label, key=f"cnav_{page}", type="primary" if is_active else "secondary",
                      on_click=cb_cust_nav, args=(page,), width="stretch")
    sidebar_footer()

    show_flash()
    {
        "Discover": page_discover,
        "Provider": page_provider,
        "Subscription": page_subscription,
        "Skip": page_skip,
        "My Tiffin": page_my_tiffin,
    }.get(current, page_discover)()


def provider_card(p: dict) -> None:
    menu = get_menu(p["id"], today_iso())
    if menu:
        dishes = ", ".join(i["dish"] for i in menu["items"][:3])
        menu_line = f'<div class="pc-menu">🍽️ <b>Today:</b> {esc(dishes)}{"…" if len(menu["items"]) > 3 else ""}</div>'
    else:
        menu_line = '<div class="pc-menu">🕒 Today\'s menu not published yet</div>'
    slots = " ".join(f'<span class="chip grey">{SLOT_ICON[s]} {s}</span>' for s in p["slots"])
    with st.container(key=f"pcard_{p['id']}"):
        html(f"""
            <div class="pc-head"><div class="pc-icon">{p['icon']}</div>
            <div><div class="pc-name">{esc(p['name'])}</div>
            <div class="pc-meta">📍 {esc(p['locality'])} · ⭐ {p['rating']} ({p['reviews']})</div></div>
            <div class="pc-price"><b>{rupees(p['price'])}</b><span>per meal</span></div></div>
            <div class="pc-desc">{esc(p['desc'])}</div>
            <div>{diet_chip(p['diet'])}{slots}</div>
            {menu_line}
        """)
        st.button("View menu & order  →", key=f"open_{p['id']}", on_click=cb_open_provider,
                  args=(p["id"],), width="stretch")


def page_discover() -> None:
    me = customer(CUSTOMER_ID)
    hour = datetime.now().hour
    greet = "Good morning" if hour < 12 else "Good afternoon" if hour < 17 else "Good evening"
    page_header(f"{greet}, {me['name'].split()[0]}", "Discover home tiffin services",
                "Compare kitchens near you and check today's menu before you order — no need to message anyone.")

    providers = list(db()["providers"].values())
    localities = ["All localities"] + sorted({p["locality"] for p in providers})
    c1, c2, c3 = st.columns([2.2, 1.4, 1])
    with c1:
        query = st.text_input("Search", placeholder="Search by kitchen, dish or cuisine…", key="disc_q")
    with c2:
        loc = st.selectbox("Locality", localities, key="disc_loc")
    with c3:
        st.write("")
        veg_only = st.toggle("Veg only", key="disc_veg")

    q = (query or "").strip().lower()
    results = []
    for p in providers:
        menu = get_menu(p["id"], today_iso())
        haystack = " ".join([p["name"], p["desc"], p["locality"], p["diet"]] +
                            ([i["dish"] for i in menu["items"]] if menu else [])).lower()
        if q and q not in haystack:
            continue
        if loc != "All localities" and p["locality"] != loc:
            continue
        if veg_only and p["diet"] != "Veg":
            continue
        results.append(p)

    html(f'<p class="tc-muted" style="margin:.2rem 0 .8rem">{len(results)} kitchen{"s" if len(results) != 1 else ""} found</p>')
    if not results:
        empty_state("🔎", "No kitchens match your search", "Try a different dish, locality or turn off 'Veg only'.")
        return
    for i in range(0, len(results), 2):
        cols = st.columns(2, gap="medium")
        for col, p in zip(cols, results[i:i + 2]):
            with col:
                provider_card(p)
        st.write("")


def page_provider() -> None:
    pid = st.session_state.selected_provider
    if pid not in db()["providers"]:
        callout("info", "Pick a kitchen first")
        st.button("← Back to all tiffin services", on_click=cb_cust_nav, args=("Discover",))
        return
    p = provider(pid)
    st.button("←  All tiffin services", key="back_disc", on_click=cb_cust_nav, args=("Discover",))

    html(f"""
        <div style="display:flex;gap:1.1rem;align-items:center;margin:.6rem 0 .4rem;flex-wrap:wrap">
          <div class="pc-icon" style="width:72px;height:72px;font-size:2.2rem;border-radius:20px">{p['icon']}</div>
          <div style="flex:1;min-width:220px">
            <div class="tc-eyebrow">Home kitchen · since {p['since']}</div>
            <h1 class="tc-title">{esc(p['name'])}</h1>
            <div class="pc-meta" style="font-size:.92rem">📍 {esc(p['locality'])}, Pune · ⭐ {p['rating']} ({p['reviews']} reviews) ·
            run by {esc(p['owner'])}</div>
          </div>
          <div class="pc-price"><b style="font-size:1.6rem">{rupees(p['price'])}</b><span>per meal (typical)</span></div>
        </div>
        <p class="pc-desc" style="font-size:.98rem;max-width:820px">{esc(p['desc'])}</p>
        <div style="margin-bottom:1rem">{diet_chip(p['diet'])}<span class="chip grey">🕒 {esc(p['timings'])}</span></div>
    """)

    day_options = [day_offset_iso(o) for o in range(3)]
    ensure_valid(f"day_{pid}", day_options)
    day = st.segmented_control("Choose a day", day_options, default=day_options[0],
                               format_func=lambda d: fmt_day(d), key=f"day_{pid}")
    day = day or day_options[0]
    menu = get_menu(pid, day)

    left, right = st.columns([1.45, 1], gap="large")
    with left:
        with st.container(key=f"panel_menu_{pid}"):
            if menu:
                slots = " ".join(f'<span class="chip">{SLOT_ICON[s]} {s} available</span>' for s in menu["slots"])
                html(f"""
                    <div class="tc-eyebrow">Menu · {esc(fmt_day(day))}</div>
                    <div class="pc-name" style="font-size:1.35rem">What's cooking</div>
                    {menu_html(menu)}
                    <div style="margin-top:.6rem">{slots}</div>
                    {f'<p class="tc-small" style="margin-top:.4rem">📝 {esc(menu["note"])}</p>' if menu.get("note") else ""}
                """)
            else:
                html(f"""
                    <div class="tc-eyebrow">Menu · {esc(fmt_day(day))}</div>
                    <div class="empty" style="margin-top:.5rem"><div class="ei">🕒</div>
                    <div class="et">Menu not published yet</div>
                    <div>{esc(p['owner'].split()[0])} usually publishes the menu the evening before.
                    Check back later or pick another day.</div></div>
                """)
    with right:
        with st.container(key=f"panel_order_{pid}"):
            render_order_panel(p, day, menu)

    st.write("")
    render_subscription_offer(p)


def render_order_panel(p: dict, day: str, menu: dict | None) -> None:
    pid = p["id"]
    is_today = day == today_iso()
    html(f'<div class="tc-eyebrow">One-day order</div><div class="pc-name" style="font-size:1.25rem">'
         f'{"Order today&#39;s meal" if is_today else "Order for " + esc(fmt_day(day, False))}</div>')
    if not menu:
        callout("info", "Ordering opens once the menu is published")
        return

    slot_key = f"slot_{pid}_{day}"
    ensure_valid(slot_key, menu["slots"])
    slot = st.segmented_control("Meal", menu["slots"], default=menu["slots"][0],
                                format_func=lambda s: f"{SLOT_ICON[s]} {s}", key=slot_key)
    slot = slot or menu["slots"][0]

    left = menu["capacity"] - booked_meals(pid, day, slot)
    qty = st.number_input("Number of tiffins", min_value=1, max_value=3, value=1, step=1, key=f"qty_{pid}")
    st.text_input("Delivery note (optional)", placeholder="e.g. Less spicy, leave at the gate",
                  key=f"note_{pid}", max_chars=80)

    existing = active_order_for(CUSTOMER_ID, pid, day, slot)
    me = customer(CUSTOMER_ID)
    confirm = st.session_state.pop("order_confirm", None)
    just_ordered = bool(confirm and confirm[0] == pid)
    html(f"""
        <div style="display:flex;justify-content:space-between;margin:.3rem 0 .2rem;font-size:.9rem">
          <span class="tc-muted">{qty} × {rupees(menu['price'])}</span><b>{rupees(menu['price'] * qty)}</b></div>
        <div class="tc-small" style="margin-bottom:.7rem">
          {'🟢' if left > 5 else '🟠' if left > 0 else '🔴'} {max(left, 0)} of {menu['capacity']} {slot.lower()} tiffins left ·
          Deliver to {esc(me.get('address', ''))} · Pay on delivery</div>
    """)
    if just_ordered:
        callout("success", "Order placed — the kitchen has been notified", confirm[1])
    elif existing:
        callout("warning", f"You already have {slot.lower()} booked here",
                f"{existing['id']} · {existing['status']}"
                f"{' (subscription)' if existing['source'] == 'Subscription' else ''}. "
                f"Choose the other meal or another day.")
    disabled = existing is not None or left <= 0
    label = "🍱  Order Today's Meal" if is_today else f"🍱  Order for {fmt_day(day, False)}"
    with st.container(key=f"cta_{pid}"):
        st.button(label, key=f"order_btn_{pid}", on_click=cb_place_order, args=(pid,),
                  disabled=disabled, width="stretch")
    if left <= 0 and not existing:
        html('<p class="tc-small">Sold out for this meal — try the other slot or another day.</p>')
    html('<p class="tc-small" style="margin-top:.5rem">Changed your plans? You can skip any order until the kitchen starts preparing it.</p>')


def render_subscription_offer(p: dict) -> None:
    pid = p["id"]
    html('<div class="tc-eyebrow" style="margin-top:.6rem">Monthly subscription</div>'
         f'<div class="pc-name" style="font-size:1.3rem;margin-bottom:.6rem">Get {esc(p["name"])} every day with a monthly plan</div>')
    existing = active_subs(CUSTOMER_ID, pid)
    plans = plans_for(p)
    cols = st.columns(len(plans), gap="medium")
    for col, plan in zip(cols, plans):
        with col:
            with st.container(key=f"plan_{pid}_{plan['name'].replace(' ', '_')}"):
                html(f"""
                    <div style="font-weight:700;font-size:1.02rem">{esc(plan['name'])}</div>
                    <div class="tc-small">{esc(plan['blurb'])}</div>
                    <div style="font-family:var(--serif);font-size:1.5rem;font-weight:700;color:var(--forest);margin-top:.3rem">
                    {rupees(plan['price'])}<span class="tc-small" style="font-family:var(--sans)"> / 30 days</span></div>
                """)
    st.write("")
    if existing:
        s = existing[0]
        callout("success", f"You're subscribed — {s['package']}",
                f"{sub_remaining(s)} of {s['meals_total']} meals remaining · ends {fmt_day(s['end'], False)}")
        st.button("Manage in Subscription  →", key=f"to_sub_{pid}", on_click=cb_cust_nav, args=("Subscription",))
        return
    c1, c2, c3 = st.columns([1.4, 1.2, 1.2])
    with c1:
        st.selectbox("Package", [x["name"] for x in plans], key=f"pd_plan_{pid}")
    with c2:
        starts = [day_offset_iso(0), day_offset_iso(1)]
        st.selectbox("Start date", starts, format_func=lambda d: fmt_day(d), key="pd_start")
    with c3:
        st.write("")
        st.button("Activate subscription", key=f"pd_activate_{pid}", type="primary",
                  on_click=cb_activate_sub, args=("pd", pid), width="stretch")
    html('<p class="tc-small">Illustrative prices · demo only, no payment is taken. Skipped plan meals are credited back.</p>')


def subscription_card(s: dict) -> None:
    p = provider(s["provider_id"])
    used = sub_used(s)
    remaining = sub_remaining(s)
    pct = int(100 * used / s["meals_total"]) if s["meals_total"] else 0
    skipped = sum(1 for o in db()["orders"] if o.get("sub_id") == s["id"] and o["status"] == "Skipped")
    with st.container(key=f"mcard_sub_{s['id']}"):
        html(f"""
            <div class="pc-head"><div class="pc-icon">{p['icon']}</div>
            <div style="flex:1"><div class="pc-name">{esc(s['package'])}</div>
            <div class="pc-meta">{esc(p['name'])} · {esc(' + '.join(s['slots']))} · {rupees(s['price'])}</div></div>
            <span class="badge" style="background:#E2EDE5;color:#1F4D3A">● {esc(s['status'])}</span></div>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:.6rem;margin:.9rem 0 .6rem">
              <div><div class="tc-small">Start date</div><b>{fmt_day(s['start'], False)}</b></div>
              <div><div class="tc-small">End date</div><b>{fmt_day(s['end'], False)}</b></div>
              <div><div class="tc-small">Meals remaining</div><b style="color:var(--orange-2);font-size:1.15rem">{remaining}</b>
              <span class="tc-small"> / {s['meals_total']}</span></div>
            </div>
            <div style="background:var(--sage);border-radius:99px;height:8px;overflow:hidden">
              <div style="width:{pct}%;background:var(--forest-2);height:8px"></div></div>
            <div class="tc-small" style="margin-top:.35rem">{used} used or scheduled · {skipped} skipped (credited back)</div>
        """)


def page_subscription() -> None:
    page_header("Subscription", "Your monthly tiffin plans",
                "Subscribe once and your meals arrive every day. Skip any day and the meal is credited back.")
    subs = active_subs(CUSTOMER_ID)
    if subs:
        for s in subs:
            subscription_card(s)
            st.write("")
    else:
        empty_state("🔁", "No active subscription", "Activate a plan below to get a tiffin every day.")
        st.write("")

    html('<div class="tc-eyebrow" style="margin-top:.8rem">New plan</div>'
         '<div class="pc-name" style="font-size:1.3rem;margin-bottom:.4rem">Activate a subscription</div>')
    taken = {s["provider_id"] for s in subs}
    available = [p for p in db()["providers"].values() if p["id"] not in taken]
    if not available:
        callout("info", "You're subscribed to every kitchen in this demo")
        return
    with st.container(key="panel_newsub"):
        ids = [p["id"] for p in available]
        ensure_valid("sp_pid", ids)
        c1, c2, c3 = st.columns([1.4, 1.4, 1])
        with c1:
            pid = st.selectbox("Tiffin service", ids, key="sp_pid",
                               format_func=lambda x: f"{provider(x)['icon']}  {provider(x)['name']} — {provider(x)['locality']}")
        p = provider(pid)
        plans = plans_for(p)
        with c2:
            plan_name = st.selectbox("Package", [x["name"] for x in plans], key=f"sp_plan_{pid}",
                                     format_func=lambda n: f"{n} · {rupees(next(x['price'] for x in plans if x['name'] == n))}")
        with c3:
            starts = [day_offset_iso(0), day_offset_iso(1)]
            st.selectbox("Start date", starts, format_func=lambda d: fmt_day(d), key="sp_start")
        plan = next(x for x in plans if x["name"] == plan_name)
        start = choice("sp_start", day_offset_iso(0))
        end = (date.fromisoformat(start) + timedelta(days=29)).isoformat()
        html(f"""
            <div style="display:flex;flex-wrap:wrap;gap:.4rem;margin:.2rem 0 .8rem">
              <span class="chip">📦 {plan['meals']} meals</span>
              <span class="chip">{esc(' + '.join(SLOT_ICON[s] + ' ' + s for s in plan['slots']))}</span>
              <span class="chip">📅 {fmt_day(start, False)} → {fmt_day(end, False)}</span>
              <span class="chip orange">{rupees(plan['price'])} · illustrative</span>
            </div>
        """)
        st.button("Activate subscription", key="sp_activate", type="primary",
                  on_click=cb_activate_sub, args=("sp",))
        html('<p class="tc-small" style="margin-top:.4rem">Demo only — no payment is processed. '
             'The first two days of meals are scheduled immediately so the kitchen can plan.</p>')


def page_skip() -> None:
    page_header("Skip a meal", "Not eating in today?",
                "Let your kitchen know in advance so they don't cook a meal that goes to waste.")
    html("""
        <div class="callout info"><div class="ci">⏱️</div><div>
        <div class="ct">Skip cutoff rule</div>
        <div class="cb">You can skip any upcoming meal that is still <b>Confirmed</b>. Once the kitchen marks it
        <b>Preparing</b>, it can no longer be skipped. Skipped subscription meals are credited back to your plan;
        skipped one-day orders are not charged.</div></div></div>
    """)
    t = today_iso()
    upcoming = sorted(
        [o for o in db()["orders"] if o["customer_id"] == CUSTOMER_ID and o["date"] >= t and o["status"] in IN_PROGRESS],
        key=lambda o: (o["date"], SLOTS.index(o["slot"])),
    )
    if not upcoming:
        empty_state("🍽️", "No upcoming meals to skip", "When you order or subscribe, your upcoming meals will appear here.")
        st.button("Discover tiffin services  →", key="skip_to_disc", on_click=cb_cust_nav, args=("Discover",))
        return

    pending = st.session_state.skip_pending
    for o in upcoming:
        p = provider(o["provider_id"])
        eligible = o["status"] == "Confirmed"
        if pending == o["id"] and eligible:
            with st.container(key=f"confirm_{o['id']}"):
                html(f"""
                    <div class="ct" style="font-weight:700;font-size:1.05rem">Skip {o['slot'].lower()} on {esc(fmt_day(o['date']))}?</div>
                    <div class="cb" style="font-size:.92rem;margin:.25rem 0 .8rem">{esc(p['name'])} will be told not to cook this meal
                    ({o['qty']} tiffin{'s' if o['qty'] > 1 else ''}, {esc(o['id'])}).
                    {'1 meal will be credited back to your plan.' if o['source'] == 'Subscription' else 'You will not be charged.'}
                    This can't be undone in the demo.</div>
                """)
                c1, c2, _ = st.columns([1.2, 1, 1.6])
                c1.button("Yes, skip this meal", key=f"skip_yes_{o['id']}", type="primary",
                          on_click=cb_confirm_skip, args=(o["id"],), width="stretch")
                c2.button("Keep my meal", key=f"skip_no_{o['id']}", on_click=cb_cancel_skip, width="stretch")
            st.write("")
            continue
        with st.container(key=f"mcard_skip_{o['id']}"):
            c1, c2 = st.columns([3, 1.1], vertical_alignment="center")
            with c1:
                html(f"""
                    <div style="display:flex;gap:.8rem;align-items:center">
                      <div class="pc-icon" style="width:46px;height:46px;font-size:1.3rem">{SLOT_ICON[o['slot']]}</div>
                      <div><div style="font-weight:700">{o['slot']} · {esc(fmt_day(o['date']))}</div>
                      <div class="tc-small">{esc(p['name'])} · {o['qty']} tiffin{'s' if o['qty'] > 1 else ''} ·
                      {esc(o['source'])} · {esc(o['id'])}</div></div>
                      <div style="margin-left:auto">{badge(o['status'])}</div>
                    </div>
                """)
            with c2:
                if eligible:
                    st.button("Skip meal", key=f"skip_{o['id']}", on_click=cb_request_skip, args=(o["id"],),
                              width="stretch")
                else:
                    html('<div class="tc-small" style="text-align:center">🔒 Kitchen is already on it — can\'t skip</div>')
        st.write("")


def page_my_tiffin() -> None:
    me = customer(CUSTOMER_ID)
    page_header("My Tiffin", f"Hi {me['name'].split()[0]}, here's everything in one place",
                "Your plan, upcoming meals with live status, order history and profile.")
    my_orders = [o for o in db()["orders"] if o["customer_id"] == CUSTOMER_ID]
    t = today_iso()
    upcoming = sorted([o for o in my_orders if o["date"] >= t and o["status"] in IN_PROGRESS],
                      key=lambda o: (o["date"], SLOTS.index(o["slot"])))
    subs = active_subs(CUSTOMER_ID)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Upcoming meals", len(upcoming), "Confirmed or on the way", "🍱")
    with c2:
        stat_card("Active plans", len(subs), "Monthly subscriptions", "🔁")
    with c3:
        stat_card("Meals delivered", sum(1 for o in my_orders if o["status"] == "Delivered"), "All time (demo)", "✅")
    with c4:
        stat_card("Meals skipped", sum(1 for o in my_orders if o["status"] == "Skipped"), "Food not wasted", "♻️", accent=True)
    st.write("")

    tab1, tab2, tab3 = st.tabs(["Upcoming & plan", "Order history", "Profile & settings"])
    with tab1:
        if not my_orders and not subs:
            empty_state("🍽️", "No orders yet", "Find a kitchen you like and place your first order.")
            st.button("Discover tiffin services  →", key="mt_disc", on_click=cb_cust_nav, args=("Discover",))
        else:
            left, right = st.columns([1.35, 1], gap="large")
            with left:
                html('<div class="tc-eyebrow" style="margin-bottom:.5rem">Upcoming meals</div>')
                if not upcoming:
                    empty_state("🗓️", "Nothing scheduled", "Order a meal or activate a plan to see it here.")
                for o in upcoming:
                    p = provider(o["provider_id"])
                    with st.container(key=f"mcard_up_{o['id']}"):
                        html(f"""
                            <div style="display:flex;justify-content:space-between;gap:.6rem;align-items:flex-start">
                              <div><div style="font-weight:700">{SLOT_ICON[o['slot']]} {o['slot']} · {esc(fmt_day(o['date']))}</div>
                              <div class="tc-small">{esc(p['name'])} · {o['qty']} tiffin{'s' if o['qty'] > 1 else ''} · {esc(o['source'])}</div></div>
                              {badge(o['status'])}</div>
                            {tracker(o['status'])}
                        """)
                    st.write("")
                if any(o["status"] == "Confirmed" for o in upcoming):
                    st.button("⏭️  Skip an upcoming meal", key="mt_to_skip", on_click=cb_cust_nav, args=("Skip",))
            with right:
                html('<div class="tc-eyebrow" style="margin-bottom:.5rem">Active subscription</div>')
                if subs:
                    for s in subs:
                        subscription_card(s)
                        st.write("")
                else:
                    empty_state("🔁", "No active plan", "Subscribe for a meal every day at a lower price.")
                    st.button("Explore plans  →", key="mt_to_sub", on_click=cb_cust_nav, args=("Subscription",))

    with tab2:
        if not my_orders:
            empty_state("🧾", "No orders yet", "Your past and current orders will appear here.")
        else:
            df = orders_frame(my_orders)
            statuses = [s for s in STATUS_STYLE if s in set(df["Status"])]
            pick = st.multiselect("Filter by status", statuses, default=statuses, key="mt_status")
            view = df[df["Status"].isin(pick)]
            if view.empty:
                empty_state("🧾", "No orders with that status", "Change the filter to see more.")
            else:
                st.dataframe(view, hide_index=True, width="stretch",
                             column_config={
                                 "Date": st.column_config.DateColumn(format="ddd D MMM"),
                                 "Amount (₹)": st.column_config.NumberColumn(format="₹%d", help="₹0 = covered by plan"),
                             })
                html('<p class="tc-small">Subscription meals show ₹0 because they are prepaid in the plan.</p>')

    with tab3:
        with st.container(key="panel_profile"):
            c1, c2 = st.columns(2)
            with c1:
                st.text_input("Full name", value=me["name"], key="pf_name")
                st.text_input("Phone", value=me["phone"], key="pf_phone")
                locs = sorted({p["locality"] for p in db()["providers"].values()})
                st.selectbox("Locality", locs, index=locs.index(me["locality"]) if me.get("locality") in locs else 0,
                             key="pf_locality")
            with c2:
                st.text_area("Delivery address", value=me["address"], key="pf_address", height=108)
                diets = ["Vegetarian", "Non-vegetarian", "Eggetarian"]
                st.selectbox("Food preference", diets,
                             index=diets.index(me.get("diet", "Vegetarian")) if me.get("diet") in diets else 0,
                             key="pf_diet")
            st.toggle("Send me each day's menu on WhatsApp", value=me.get("menu_alerts", True), key="pf_alerts")
            st.toggle("Remind me before the skip cutoff", value=me.get("skip_reminder", True), key="pf_reminder")
            st.button("Save profile", key="pf_save", type="primary", on_click=cb_save_profile)


# ---------------------------------------------------------------------------
# Owner mode
# ---------------------------------------------------------------------------

OWNER_NAV = [
    ("Overview", "📊  Overview"),
    ("Menu", "📝  Daily menu"),
    ("Orders", "🧾  Today's orders"),
    ("Records", "📁  Records & earnings"),
]


def render_owner() -> None:
    pid = st.session_state.owner_pid
    p = provider(pid)
    sidebar_shell("Tiffin owner", p["owner"], f"{p['icon']} {p['name']}")
    with st.sidebar:
        ids = list(db()["providers"].keys())
        st.session_state.owner_pid_widget = pid
        st.selectbox("Demo: switch kitchen", ids, key="owner_pid_widget", on_change=cb_owner_kitchen,
                     format_func=lambda x: provider(x)["name"])
        html('<div class="sb-label">Manage</div>')
        for page, label in OWNER_NAV:
            st.button(label, key=f"onav_{page}", type="primary" if st.session_state.owner_page == page else "secondary",
                      on_click=cb_owner_nav, args=(page,), width="stretch")
    sidebar_footer()

    show_flash()
    {
        "Overview": owner_overview,
        "Menu": owner_menu,
        "Orders": owner_orders,
        "Records": owner_records,
    }.get(st.session_state.owner_page, owner_overview)(p)


def month_earnings(pid: str) -> tuple[int, int]:
    month = date.today().strftime("%Y-%m")
    one_day = sum(o["amount"] for o in db()["orders"]
                  if o["provider_id"] == pid and o["date"].startswith(month)
                  and o["source"] == "One-day" and o["status"] in COUNTED)
    subs = sum(s["price"] for s in db()["subscriptions"]
               if s["provider_id"] == pid and s["start"].startswith(month))
    return one_day, subs


def owner_overview(p: dict) -> None:
    pid = p["id"]
    t = today_iso()
    page_header(f"Good to see you, {p['owner'].split()[0]}", f"{p['name']} — today at a glance",
                f"{fmt_day(t)} · everything below updates the moment a customer orders or skips.")
    todays = [o for o in db()["orders"] if o["provider_id"] == pid and o["date"] == t]
    confirmed = sum(o["qty"] for o in todays if o["status"] in COUNTED)
    skipped = sum(o["qty"] for o in todays if o["status"] == "Skipped")
    to_deliver = sum(1 for o in todays if o["status"] in IN_PROGRESS)
    one_day, sub_rev = month_earnings(pid)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Meals to cook today", confirmed, f"Lunch {booked_meals(pid, t, 'Lunch')} · Dinner {booked_meals(pid, t, 'Dinner')}", "🍱")
    with c2:
        stat_card("Skipped today", skipped, "Not cooked — no waste", "⏭️", accent=True)
    with c3:
        stat_card("Awaiting delivery", to_deliver, "Orders not yet delivered", "🛵")
    with c4:
        stat_card("Earnings this month", rupees(one_day + sub_rev), "Illustrative · one-day + plans", "💰")
    st.write("")

    left, right = st.columns([1.2, 1], gap="large")
    with left:
        with st.container(key="panel_ov_prep"):
            html('<div class="tc-eyebrow">Preparation plan</div><div class="pc-name" style="margin-bottom:.6rem">What to cook today</div>')
            menu_t = get_menu(pid, t, published_only=False)
            rows = []
            for slot in p["slots"]:
                booked = booked_meals(pid, t, slot)
                skip_n = sum(o["qty"] for o in todays if o["slot"] == slot and o["status"] == "Skipped")
                pending = sum(o["qty"] for o in todays if o["slot"] == slot and o["status"] in IN_PROGRESS)
                rows.append(f"""
                    <div style="display:flex;align-items:center;gap:.8rem;padding:.65rem 0;border-bottom:1px solid #F0ECE3">
                      <div class="pc-icon" style="width:44px;height:44px;font-size:1.2rem">{SLOT_ICON[slot]}</div>
                      <div style="flex:1"><b>{slot}</b><div class="tc-small">{pending} still to deliver · {skip_n} skipped</div></div>
                      <div style="font-family:var(--serif);font-size:1.6rem;font-weight:700;color:var(--forest)">{booked}</div>
                      <div class="tc-small">tiffins</div></div>
                """)
            html("".join(rows))
            if menu_t and menu_t.get("published"):
                html(f'<p class="tc-small" style="margin-top:.7rem">✅ Today\'s menu is live: '
                     f'{esc(", ".join(i["dish"] for i in menu_t["items"]))}</p>')
            else:
                callout("warning", "Today's menu isn't published", "Customers can't order until you publish it.")
            c1, c2 = st.columns(2)
            c1.button("Open today's orders  →", key="ov_orders", on_click=cb_owner_nav, args=("Orders",),
                      width="stretch")
            c2.button("Edit menu", key="ov_menu", on_click=cb_owner_nav, args=("Menu",), width="stretch")
    with right:
        with st.container(key="panel_ov_feed"):
            html('<div class="tc-eyebrow">Live activity</div><div class="pc-name" style="margin-bottom:.4rem">Recent updates</div>')
            feed = [a for a in db()["activity"] if a["pid"] == pid and a["date"] == t][-7:][::-1]
            if not feed:
                html('<p class="tc-muted">No activity yet today.</p>')
            else:
                html("".join(
                    f'<div class="feed-item"><div class="t">{esc(a["time"])}</div><div>{a["icon"]}</div>'
                    f'<div>{esc(a["text"])}</div></div>' for a in feed))
            subs = active_subs(pid=pid)
            html(f'<p class="tc-small" style="margin-top:.8rem">🔁 {len(subs)} active subscriber{"s" if len(subs) != 1 else ""} · '
                 f'Tomorrow: {booked_meals(pid, day_offset_iso(1))} meals booked so far</p>')


def owner_menu(p: dict) -> None:
    pid = p["id"]
    page_header("Daily menu", "Publish your menu once — every customer sees it",
                "No more answering 'aaj kya hai?' on WhatsApp. Published menus appear instantly in the customer app.")
    c1, c2 = st.columns([1, 2])
    with c1:
        d = st.date_input("Menu date", value=date.today(), min_value=date.today() - timedelta(days=1),
                          max_value=date.today() + timedelta(days=14), key=f"menu_date_{pid}", format="DD/MM/YYYY")
    day = d.isoformat() if isinstance(d, date) else today_iso()
    existing = get_menu(pid, day, published_only=False)
    with c2:
        st.write("")
        if existing and existing.get("published"):
            callout("success", f"Published for {fmt_day(day)}", f"Last updated: {esc(existing.get('updated_at', ''))}")
        elif existing:
            callout("warning", f"Draft for {fmt_day(day)}", "Saved but not visible to customers yet.")
        else:
            callout("info", f"No menu yet for {fmt_day(day)}",
                    "We've pre-filled your last menu — change the dishes and publish when ready.")

    if existing:
        base = existing
    else:
        # Start from the kitchen's most recent menu so the owner only edits what changed
        recent = sorted((k for k in db()["menus"] if k.startswith(f"{pid}|")), reverse=True)
        template = db()["menus"][recent[0]] if recent else None
        base = {
            "items": [dict(i) for i in template["items"]] if template else [{"dish": "", "detail": ""}],
            "price": template["price"] if template else p["price"],
            "slots": list(template["slots"]) if template else list(p["slots"]),
            "capacity": template["capacity"] if template else p["capacity"],
            "note": "", "published": False,
        }
    ver = st.session_state.menu_ver
    left, right = st.columns([1.5, 1], gap="large")
    with left:
        with st.form(f"menu_form_{pid}_{day}_{ver}", border=False):
            html('<div class="tc-eyebrow">Dishes</div>')
            items_df = pd.DataFrame(base["items"], columns=["dish", "detail"])
            edited = st.data_editor(
                items_df, num_rows="dynamic", width="stretch", hide_index=True,
                key=f"menu_items_{pid}_{day}_{ver}",
                column_config={
                    "dish": st.column_config.TextColumn("Dish", required=True, max_chars=40, width=190),
                    "detail": st.column_config.TextColumn("Description", max_chars=80, width=280),
                },
            )
            html('<p class="tc-small" style="margin:-.3rem 0 .6rem">Click a cell to edit · use the + row at the bottom to add a dish · select a row and press Delete to remove it.</p>')
            f1, f2 = st.columns(2)
            with f1:
                price = st.number_input("Price per meal (₹)", min_value=0, max_value=1000, step=5,
                                        value=int(base["price"]), key=f"m_price_{pid}_{day}_{ver}")
            with f2:
                capacity = st.number_input("Tiffins per slot (capacity)", min_value=1, max_value=200, step=1,
                                           value=int(base["capacity"]), key=f"m_cap_{pid}_{day}_{ver}")
            slots = st.multiselect("Serving", SLOTS, default=[s for s in base["slots"] if s in SLOTS],
                                   key=f"m_slots_{pid}_{day}_{ver}")
            note = st.text_input("Note for customers (optional)", value=base.get("note", ""), max_chars=90,
                                 key=f"m_note_{pid}_{day}_{ver}", placeholder="e.g. Sweet dish on Sunday")
            b1, b2 = st.columns(2)
            publish = b1.form_submit_button("✅  Publish menu", type="primary", width="stretch")
            draft = b2.form_submit_button("Save as draft", width="stretch")

        if publish or draft:
            items = []
            for _, row in edited.iterrows():
                dish = str(row.get("dish") or "").strip()
                detail = str(row.get("detail") or "").strip()
                if dish and dish.lower() != "nan":
                    items.append({"dish": dish, "detail": "" if detail.lower() in ("nan", "none") else detail})
            errors = []
            if not items:
                errors.append("Add at least one dish.")
            if price <= 0:
                errors.append("Enter a price per meal above ₹0.")
            if not slots:
                errors.append("Choose whether you're serving lunch, dinner or both.")
            if errors:
                callout("error", "Menu not saved", "<br>".join(esc(e) for e in errors))
            else:
                db()["menus"][menu_key(pid, day)] = {
                    "items": items, "price": int(price), "slots": [s for s in SLOTS if s in slots],
                    "capacity": int(capacity), "note": note.strip(), "published": bool(publish),
                    "updated_at": datetime.now().strftime("%d %b, %H:%M"),
                }
                if publish:
                    log(pid, "📝", f"Menu published for {fmt_day(day, False)} ({len(items)} dishes)")
                    flash("success", f"Menu published for {fmt_day(day)}",
                          "Customers can see it and order right away — switch to the customer view to check.")
                else:
                    flash("success", f"Draft saved for {fmt_day(day)}", "Customers won't see it until you publish.")
                st.session_state.menu_ver += 1
                st.rerun()

    with right:
        with st.container(key="panel_menu_preview"):
            html('<div class="tc-eyebrow">Customer preview</div>')
            live = get_menu(pid, day)
            if live:
                html(f'<div class="pc-name">{esc(p["name"])}</div>'
                     f'<div class="tc-small">{esc(fmt_day(day))} · {rupees(live["price"])} per meal · '
                     f'{esc(" & ".join(live["slots"]))}</div>{menu_html(live)}')
                bookings = " · ".join(f"{s}: {booked_meals(pid, day, s)}/{live['capacity']}" for s in live["slots"])
                html(f'<p class="tc-small" style="margin-top:.5rem">📦 Booked so far — {bookings}</p>')
            else:
                html('<div class="empty"><div class="ei">👀</div><div class="et">Not visible yet</div>'
                     '<div>Customers will see the menu here once you publish it.</div></div>')


def owner_order_card(o: dict) -> None:
    c = customer(o["customer_id"])
    with st.container(key=f"ocard_{o['id']}"):
        c1, c2 = st.columns([3, 1.25], vertical_alignment="center")
        with c1:
            note = f'<div class="tc-small">📝 {esc(o["note"])}</div>' if o.get("note") else ""
            html(f"""
                <div style="display:flex;gap:.6rem;align-items:center;flex-wrap:wrap">
                  <b style="font-size:1rem">{esc(c['name'])}</b>{badge(o['status'])}
                  <span class="chip grey">{SLOT_ICON[o['slot']]} {o['slot']} × {o['qty']}</span>
                  <span class="chip{' orange' if o['source'] == 'Subscription' else ''}">{esc(o['source'])}</span>
                </div>
                <div class="tc-small" style="margin-top:.25rem">{esc(o['id'])} · 📍 {esc(c.get('address', ''))} · 📞 {esc(c.get('phone', ''))}</div>
                {note}
            """)
        with c2:
            if o["status"] in NEXT_STEP:
                nxt, label = NEXT_STEP[o["status"]]
                st.button(label, key=f"adv_{o['id']}", type="primary", on_click=cb_set_status,
                          args=(o["id"], nxt), width="stretch")
            else:
                html('<div class="tc-small" style="text-align:center">Done ✓</div>')


def owner_orders(p: dict) -> None:
    pid = p["id"]
    page_header("Orders", "Today's orders",
                "Move each tiffin along as you cook and dispatch it — customers see the status live.")
    opts = [day_offset_iso(0), day_offset_iso(1)]
    ensure_valid("oo_day", opts)
    day = st.segmented_control("Day", opts, default=opts[0], key="oo_day", format_func=lambda d: fmt_day(d))
    day = day or opts[0]
    orders = sorted([o for o in db()["orders"] if o["provider_id"] == pid and o["date"] == day],
                    key=lambda o: (SLOTS.index(o["slot"]), FLOW.index(o["status"]) if o["status"] in FLOW else 9, o["id"]))
    active = [o for o in orders if o["status"] in IN_PROGRESS]
    delivered = [o for o in orders if o["status"] == "Delivered"]
    skipped = [o for o in orders if o["status"] in ("Skipped", "Cancelled")]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("Lunch to prepare", booked_meals(pid, day, "Lunch"), "Confirmed tiffins (excl. skipped)", "☀️")
    with c2:
        stat_card("Dinner to prepare", booked_meals(pid, day, "Dinner"), "Confirmed tiffins (excl. skipped)", "🌙")
    with c3:
        stat_card("Still to deliver", len(active), "Confirmed / preparing / on the way", "🛵")
    with c4:
        stat_card("Skipped", sum(o["qty"] for o in skipped), "Removed from cooking count", "⏭️", accent=True)
    st.write("")

    if not orders:
        empty_state("🧾", f"No orders for {fmt_day(day)} yet", "New customer orders will appear here automatically.")
        return

    html(f'<div class="tc-eyebrow" style="margin:.4rem 0 .6rem">In progress · {len(active)}</div>')
    if not active:
        html('<p class="tc-muted">Everything is delivered or skipped. 🎉</p>')
    for slot in SLOTS:
        slot_orders = [o for o in active if o["slot"] == slot]
        if not slot_orders:
            continue
        html(f'<div style="font-weight:700;margin:.4rem 0 .4rem">{SLOT_ICON[slot]} {slot} '
             f'<span class="tc-small">({sum(o["qty"] for o in slot_orders)} tiffins)</span></div>')
        for o in slot_orders:
            owner_order_card(o)
            html('<div style="height:.5rem"></div>')

    c1, c2 = st.columns(2, gap="large")
    with c1:
        with st.expander(f"✅ Delivered · {len(delivered)}", expanded=False):
            if delivered:
                for o in delivered:
                    html(f'<div class="feed-item"><div>{SLOT_ICON[o["slot"]]}</div><div style="flex:1">'
                         f'<b>{esc(customer(o["customer_id"])["name"])}</b> · {o["slot"]} × {o["qty"]}'
                         f'<div class="tc-small">{esc(o["id"])}</div></div>{badge(o["status"])}</div>')
            else:
                html('<p class="tc-muted">No deliveries yet.</p>')
    with c2:
        with st.expander(f"⏭️ Skipped · {len(skipped)} — not counted for cooking", expanded=True):
            if skipped:
                for o in skipped:
                    html(f'<div class="feed-item"><div>{SLOT_ICON[o["slot"]]}</div><div style="flex:1">'
                         f'<b>{esc(customer(o["customer_id"])["name"])}</b> · {o["slot"]} × {o["qty"]}'
                         f'<div class="tc-small">{esc(o["id"])} · {esc(o["source"])}</div></div>{badge(o["status"])}</div>')
            else:
                html('<p class="tc-muted">No skips. Every booked meal is going out.</p>')


def owner_records(p: dict) -> None:
    pid = p["id"]
    page_header("Records", "Orders & earnings",
                "A simple record of every order — no more tallying from chat history at the end of the month.")
    orders = [o for o in db()["orders"] if o["provider_id"] == pid]
    one_day, sub_rev = month_earnings(pid)
    skipped_month = sum(o["qty"] for o in orders if o["status"] == "Skipped"
                        and o["date"].startswith(date.today().strftime("%Y-%m")))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        stat_card("One-day orders", rupees(one_day), "This month (illustrative)", "🧾")
    with c2:
        stat_card("Plan sales", rupees(sub_rev), "Subscriptions started this month", "🔁")
    with c3:
        stat_card("Total earnings", rupees(one_day + sub_rev), "Illustrative, before costs", "💰")
    with c4:
        stat_card("Meals not wasted", skipped_month, "Skipped before cooking", "♻️", accent=True)
    st.write("")

    if not orders:
        empty_state("📁", "No records yet", "Orders will be recorded here automatically.")
        return

    # Daily chart: last 7 days + tomorrow
    days = [day_offset_iso(o) for o in range(-6, 2)]
    chart = pd.DataFrame({
        "Day": [fmt_day(d, False) for d in days],
        "Meals served / booked": [sum(o["qty"] for o in orders if o["date"] == d and o["status"] in COUNTED) for d in days],
        "Skipped": [sum(o["qty"] for o in orders if o["date"] == d and o["status"] == "Skipped") for d in days],
    })
    with st.container(key="panel_rec_chart"):
        html('<div class="tc-eyebrow">Last 7 days</div><div class="pc-name" style="margin-bottom:.4rem">Meals per day</div>')
        st.bar_chart(chart, x="Day", y=["Meals served / booked", "Skipped"], color=["#2B6A4F", "#E0A26A"],
                     stack=True, height=260, x_label="", y_label="Tiffins", sort=False)
    st.write("")

    df = orders_frame(orders, for_owner=True)
    c1, c2, c3 = st.columns([2, 1.2, 1])
    with c1:
        statuses = [s for s in STATUS_STYLE if s in set(df["Status"])]
        pick = st.multiselect("Status", statuses, default=statuses, key="rec_status")
    with c2:
        typ = st.selectbox("Order type", ["All", "One-day", "Subscription"], key="rec_type")
    view = df[df["Status"].isin(pick)]
    if typ != "All":
        view = view[view["Type"] == typ]
    with c3:
        st.write("")
        st.download_button("⬇  Download CSV", view.to_csv(index=False).encode("utf-8"),
                           file_name=f"{pid}_orders.csv", mime="text/csv", width="stretch")
    if view.empty:
        empty_state("🧾", "No orders match these filters", "Adjust the filters above.")
    else:
        st.dataframe(view, hide_index=True, width="stretch", height=380,
                     column_config={
                         "Date": st.column_config.DateColumn(format="ddd D MMM"),
                         "Amount (₹)": st.column_config.NumberColumn(format="₹%d"),
                     })
        html(f'<p class="tc-small">{len(view)} orders shown · subscription meals show ₹0 because the plan is paid upfront.</p>')

    subs = [s for s in db()["subscriptions"] if s["provider_id"] == pid]
    if subs:
        html('<div class="tc-eyebrow" style="margin-top:1rem">Subscribers</div>')
        st.dataframe(pd.DataFrame([{
            "Plan ID": s["id"], "Customer": customer(s["customer_id"])["name"], "Package": s["package"],
            "Start": date.fromisoformat(s["start"]), "End": date.fromisoformat(s["end"]),
            "Meals left": sub_remaining(s), "Price (₹)": s["price"], "Status": s["status"],
        } for s in subs]), hide_index=True, width="stretch",
            column_config={"Start": st.column_config.DateColumn(format="D MMM"),
                           "End": st.column_config.DateColumn(format="D MMM"),
                           "Price (₹)": st.column_config.NumberColumn(format="₹%d")})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    init_state()
    inject_css()
    role = st.session_state.role
    if role == "customer":
        render_customer()
    elif role == "owner":
        render_owner()
    else:
        render_landing()


main()
