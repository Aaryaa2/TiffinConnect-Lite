# 🍱 Tiffin Connect Lite

**Homely meals. Hassle-free living.**

A working prototype for a Design Thinking project. Tiffin Connect Lite shows how people living alone (students and working professionals) and small home tiffin services could coordinate in one place, instead of over endless WhatsApp messages.

> This is a lightweight demonstration prototype, not a production app. All kitchens, people, prices and orders are fictional sample data. No payments are processed.

---

## What it demonstrates

| Problem today | What the prototype shows |
|---|---|
| Customers message providers every day to ask about the menu | Owners publish the day's menu once; customers see it instantly |
| Orders and cancellations get lost in chat | Every order has an ID, a meal slot and a live status |
| Owners cook meals customers no longer want | Customers skip a meal in two taps; the owner's cooking count drops right away |
| Small kitchens struggle to track orders and earnings | A simple records page with an order table, daily chart and earnings |

### Customer mode
- **Discover:** five sample Pune kitchens, with search, a locality filter and a Veg-only toggle
- **Kitchen details:** menu for today, tomorrow or the day after, tiffins left per slot, and the **Order Today's Meal** button
- **One-day order:** choose lunch or dinner and the number of tiffins. Duplicate orders for the same kitchen, date and meal are blocked.
- **Subscription:** activate a monthly plan and see the start date, end date and meals remaining
- **Skip a meal:** skip any meal that is still *Confirmed*, with a confirmation step. Skipped plan meals are credited back.
- **My Tiffin:** upcoming meals with a live delivery tracker, active plan, order history and profile/settings

### Owner mode
- **Overview:** meals to cook today, skipped meals, orders awaiting delivery, earnings this month and a live activity feed
- **Daily menu:** pick a date, edit dishes in a table, set price, capacity and slots, then publish or save as a draft
- **Today's orders:** move each order from Confirmed → Preparing → Out for Delivery → Delivered. Skipped orders are listed separately and removed from the cooking count.
- **Records & earnings:** filterable order table, a 7-day meals chart, subscriber list and CSV download

---

## Installation

You need **Python 3.10 or newer**.

```bash
# 1. Go into the project folder
cd tiffin-connect-lite

# 2. (Recommended) create a virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate

# 3. Install the dependencies
pip install -r requirements.txt
```

## Running

```bash
streamlit run app.py
```

The app opens at **http://localhost:8501**.

To view it on a phone on the same Wi-Fi, open the "Network URL" that Streamlit prints in the terminal.

---

## Suggested 3-minute demo script

1. **Landing page:** explain the two roles. Click **Continue as Customer**.
2. **Discover:** search "rajma" or filter by locality. Open **Aaji's Kitchen**.
3. **Order:** lunch is already booked (Riya has a lunch plan), so the button is disabled. That is the duplicate protection. Switch to **Dinner** and click **Order Today's Meal**. The confirmation appears.
4. **Skip a meal:** skip tomorrow's lunch. Confirm it. Note that one meal is credited back to the plan.
5. **Switch role → Tiffin Owner.** The Overview shows the new dinner order and the skip in the activity feed, and the cooking counts have updated.
6. **Today's orders:** move Riya's dinner to *Preparing → Out for Delivery → Delivered*.
7. **Daily menu:** pick the day after tomorrow. It is pre-filled from the last menu. Change a dish and click **Publish menu**.
8. **Switch back to Customer:** Riya's dinner shows *Delivered* in My Tiffin, and the new menu is orderable for that day.

Use **⟲ Reset demo data** in the sidebar to restore the starting state before presenting.

---

## How it works

- **One file:** all logic and UI live in `app.py`.
- **Shared state:** the customer and owner views read and write the same sample data held in `st.session_state`. Every change shows up on the other side immediately. Data lives in memory for one browser session; refreshing the page restores the sample data.
- **Skip rule (deterministic):** a meal can be skipped while its status is *Confirmed*. Once the owner marks it *Preparing*, it can no longer be skipped. Skipped and cancelled orders never count as confirmed meals.
- **Sample dates** are generated relative to today, so the demo always looks current.
- **Styling:** custom CSS (forest green, sage, ivory, orange accent). `.streamlit/config.toml` locks the light theme so the colours look right even if the laptop is in dark mode.

## Files

```
tiffin-connect-lite/
├── app.py                  # the whole app
├── requirements.txt        # streamlit, pandas
├── README.md
└── .streamlit/config.toml  # light theme + brand colours
```

## Troubleshooting

- **`streamlit: command not found`:** run `python -m streamlit run app.py`.
- **Colours look dark or wrong:** make sure the `.streamlit` folder sits next to `app.py`, then restart Streamlit.
- **Old Streamlit version errors** (for example, `segmented_control` not found): run `pip install -U streamlit`. Version 1.46 or newer is required.
