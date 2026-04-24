import tkinter as tk
from pymongo import MongoClient
from datetime import datetime, timedelta
import random, string

client = MongoClient("mongodb://localhost:27017/")
db = client["restaurants"]
collection = db["data"]

state = {}

BG      = "#E0F7FA"
PRIMARY = "#00838F"
WHITE   = "#FFFFFF"
DARK    = "#004D5A"
FONT    = "Helvetica"

def clear(root):
    for w in root.winfo_children():
        w.destroy()

def window1(root):
    clear(root)
    root.title("Dine & Reserve")
    root.config(bg=BG)

    tk.Label(root, text="🍽", font=(FONT, 32), bg=BG).pack(pady=(28, 0))
    tk.Label(root, text="Dine & Reserve", font=(FONT, 20, "bold"), bg=BG, fg=DARK).pack(pady=(4, 0))
    tk.Label(root, text="Discover restaurants, book tables — all in one place",
             font=(FONT, 10), bg=BG, fg="#607D8B", wraplength=360, justify="center").pack(pady=(4, 24))
    tk.Frame(root, bg="#B2EBF2", height=1, width=320).pack(pady=(0, 16))

    for city in ["Mumbai", "Delhi", "Bangalore", "Chennai"]:
        tk.Button(root, text=city, font=(FONT, 13), width=22, pady=9,
                  bg=PRIMARY, fg=WHITE, relief="flat", cursor="hand2",
                  activebackground="#006978", activeforeground=WHITE,
                  command=lambda c=city: [state.update({"city": c}), window2(root)]
                  ).pack(pady=5)

def window2(root):
    clear(root)
    root.title("Step 2 - Choose Restaurant")
    root.config(bg=BG)

    city = state["city"]
    restaurants = list(collection.find({"city": city}))

    tk.Label(root, text=f" Top Restaurants in {city}", font=(FONT, 16, "bold"),
             bg=BG, fg=DARK, pady=10).pack()

    frame = tk.Frame(root, bg=BG)
    frame.pack(fill="both", expand=True, padx=20)

    for r in restaurants:
        seats = r.get("available_seats", 0)
        label = f"{r['name']}  |  Seats: {seats}"
        tk.Button(frame, text=label, font=(FONT, 11), width=55, pady=5,
                  bg=PRIMARY if seats > 0 else "#B2EBF2",
                  fg=WHITE if seats > 0 else "#607D8B",
                  relief="flat", cursor="hand2" if seats > 0 else "arrow",
                  state="normal" if seats > 0 else "disabled",
                  command=lambda res=r: [state.update({"restaurant": res}), window_table(root)]
                  ).pack(pady=4)

    tk.Frame(frame, bg="#B2EBF2", height=1).pack(fill="x", pady=(14, 6))
    tk.Button(frame, text=f"📋  Show Previous Bookings in {city}",
              font=(FONT, 11), width=55, pady=6,
              bg="#004D5A", fg=WHITE, relief="flat", cursor="hand2",
              activebackground="#003540", activeforeground=WHITE,
              command=lambda: window_bookings(root)).pack(pady=4)

    tk.Button(root, text="← Back", font=(FONT, 10), bg=BG, fg=DARK,
              relief="flat", command=lambda: window1(root)).pack(pady=10)


# ── NEW: Table Selection Window ──────────────────────────────────────────────
def window_table(root):
    clear(root)
    r = state["restaurant"]
    root.title("Step 3 - Choose Your Table")
    root.config(bg=BG)

    # ── Header ──
    tk.Label(root, text="🪑 Choose Your Table", font=(FONT, 16, "bold"),
             bg=BG, fg=DARK, pady=8).pack()
    tk.Label(root, text=r["name"], font=(FONT, 11), bg=BG, fg=PRIMARY).pack()
    tk.Frame(root, bg="#B2EBF2", height=1, width=480).pack(pady=(8, 4))

    # ── Legend ──
    legend = tk.Frame(root, bg=BG)
    legend.pack(pady=(4, 8))
    for color, label in [("#A5D6A7", "Available"), ("#CFD8DC", "Occupied"), (PRIMARY, "Selected")]:
        dot = tk.Label(legend, bg=color, width=2, relief="flat")
        dot.pack(side="left", padx=(8, 2))
        tk.Label(legend, text=label, font=(FONT, 9), bg=BG, fg=DARK).pack(side="left", padx=(0, 8))

    selected_table = tk.StringVar(value="")

    info_label = tk.Label(root, text="No table selected", font=(FONT, 10, "italic"),
                          bg=BG, fg="#607D8B")
    info_label.pack(pady=(0, 6))

    # ── Table data: (table_id, seats, section, occupied) ──
    tables = [
        ("T1", 2, "Indoor"), ("T2", 4, "Indoor"), ("T3", 2, "Indoor"),
        ("T4", 6, "Indoor"), ("T5", 4, "Indoor"), ("T6", 2, "Indoor"),
        ("T7", 2, "Outdoor"), ("T8", 4, "Outdoor"),
        ("T9", 2, "Outdoor"), ("T10", 6, "Outdoor"),
    ]

    # Simulate some occupied tables randomly (or you can store this in MongoDB)
    occupied = {"T2", "T5", "T9"}

    btn_refs = {}

    def select_table(tid, seats, section):
        selected_table.set(tid)
        for key, (btn, _) in btn_refs.items():
            if key in occupied:
                btn.config(bg="#CFD8DC", fg="#90A4AE")
            elif key == tid:
                btn.config(bg=PRIMARY, fg=WHITE)
            else:
                btn.config(bg="#A5D6A7", fg=DARK)
        info_label.config(
            text=f"Table {tid} selected — {section}, {seats} seats",
            fg=PRIMARY, font=(FONT, 10, "bold")
        )
        confirm_btn.config(state="normal", bg=PRIMARY)

    # ── Section frames ──
    for section_name in ["Indoor", "Outdoor"]:
        sec_frame = tk.LabelFrame(root, text=f"  {section_name}  ",
                                   font=(FONT, 10, "bold"), bg=BG, fg=DARK,
                                   padx=10, pady=8, relief="groove", bd=1)
        sec_frame.pack(fill="x", padx=20, pady=6)

        row_frame = tk.Frame(sec_frame, bg=BG)
        row_frame.pack()

        col = 0
        for (tid, seats, sec, *_) in [(t[0], t[1], t[2]) for t in tables if t[2] == section_name]:
            is_occ = tid in occupied
            bg_color = "#CFD8DC" if is_occ else "#A5D6A7"
            fg_color = "#90A4AE" if is_occ else DARK
            cursor = "arrow" if is_occ else "hand2"

            cell = tk.Frame(row_frame, bg=BG, padx=4, pady=4)
            cell.grid(row=0, column=col)

            btn = tk.Button(
                cell,
                text=f"{tid}\n{seats} seats",
                font=(FONT, 9, "bold"),
                width=7, height=3,
                bg=bg_color, fg=fg_color,
                relief="flat", cursor=cursor,
                state="disabled" if is_occ else "normal",
                command=lambda t=tid, s=seats, sec=section_name: select_table(t, s, sec)
            )
            btn.pack()

            status = tk.Label(cell, text="Occupied" if is_occ else "Free",
                              font=(FONT, 7), bg=BG,
                              fg="#90A4AE" if is_occ else "#388E3C")
            status.pack()

            btn_refs[tid] = (btn, seats)
            col += 1

    # ── Confirm button ──
    confirm_btn = tk.Button(
        root, text="Continue to Booking →",
        font=(FONT, 12, "bold"), bg="#B2EBF2", fg="#607D8B",
        relief="flat", pady=8, width=22, cursor="hand2", state="disabled",
        command=lambda: [
            state.update({"table": selected_table.get()}),
            window3(root)
        ]
    )
    confirm_btn.pack(pady=(10, 4))

    tk.Button(root, text="← Back", font=(FONT, 10), bg=BG, fg=DARK,
              relief="flat", command=lambda: window2(root)).pack()
# ─────────────────────────────────────────────────────────────────────────────


def window_bookings(root):
    clear(root)
    city = state["city"]
    root.title(f"Previous Bookings - {city}")
    root.config(bg=BG)

    tk.Label(root, text="📋 Previous Bookings", font=(FONT, 16, "bold"),
             bg=BG, fg=DARK, pady=6).pack()
    tk.Label(root, text=city, font=(FONT, 12), bg=BG, fg=PRIMARY).pack()
    tk.Frame(root, bg="#B2EBF2", height=1, width=480).pack(pady=(8, 0))

    container = tk.Frame(root, bg=BG)
    container.pack(fill="both", expand=True, padx=16, pady=(6, 0))

    canvas = tk.Canvas(container, bg=BG, highlightthickness=0)
    scrollbar = tk.Scrollbar(container, orient="vertical", command=canvas.yview)
    scroll_frame = tk.Frame(canvas, bg=BG)

    scroll_frame.bind("<Configure>",
        lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.pack(side="left", fill="both", expand=True)
    scrollbar.pack(side="right", fill="y")

    bookings = list(db["bookings"].find({"city": city}).sort("booked_at", -1))

    if not bookings:
        tk.Label(scroll_frame, text="No bookings found for this city.",
                 font=(FONT, 12), bg=BG, fg="#607D8B", pady=30).pack()
    else:
        for b in bookings:
            raw_phone = str(b.get("guest_phone", ""))
            masked_phone = ("●" * (len(raw_phone) - 3) + raw_phone[-3:]) if len(raw_phone) >= 3 else "●●●"

            card = tk.Frame(scroll_frame, bg="#B2EBF2", padx=14, pady=10)
            card.pack(fill="x", padx=6, pady=5)

            top = tk.Frame(card, bg="#B2EBF2")
            top.pack(fill="x")
            tk.Label(top, text=f"🎫 {b['booking_id']}", font=(FONT, 11, "bold"),
                     bg="#B2EBF2", fg=DARK).pack(side="left")
            tk.Label(top, text=b.get("date", ""), font=(FONT, 9),
                     bg="#B2EBF2", fg="#607D8B").pack(side="right")

            for lbl, val in [
                ("Restaurant", b.get("restaurant", "N/A")),
                ("Table",      b.get("table", "N/A")),
                ("Guest",      b.get("guest_name", "N/A")),
                ("Phone",      masked_phone),
                ("Meal",       b.get("meal", "N/A")),
                ("Guests",     str(b.get("guests", "N/A"))),
                ("Total Cost", f"₹{b.get('cost', 'N/A')}"),
            ]:
                row = tk.Frame(card, bg="#B2EBF2")
                row.pack(fill="x", pady=1)
                tk.Label(row, text=f"{lbl}:", font=(FONT, 10, "bold"),
                         width=12, anchor="w", bg="#B2EBF2", fg=DARK).pack(side="left")
                tk.Label(row, text=val, font=(FONT, 10),
                         anchor="w", bg="#B2EBF2", fg="#333333").pack(side="left")

    tk.Frame(root, bg="#B2EBF2", height=1, width=480).pack(pady=(6, 0))
    tk.Button(root, text="← Back", font=(FONT, 10), bg=BG, fg=DARK,
              relief="flat", command=lambda: window2(root)).pack(pady=8)


def window3(root):
    clear(root)
    root.title("Step 4 - Booking Details")
    root.config(bg=BG)

    r = state["restaurant"]

    card = tk.Frame(root, bg="#B2EBF2", padx=16, pady=10)
    card.pack(fill="x", padx=24, pady=(14, 0))

    tk.Label(card, text=r["name"], font=(FONT, 14, "bold"),
             bg="#B2EBF2", fg=DARK).pack(anchor="w")

    info_row = tk.Frame(card, bg="#B2EBF2")
    info_row.pack(anchor="w", pady=(2, 0))
    tk.Label(info_row, text=f"₹{r['price_per_person']} per person",
             font=(FONT, 10), bg="#B2EBF2", fg="#00838F").pack(side="left")
    tk.Label(info_row, text="  •", font=(FONT, 10), bg="#B2EBF2", fg="#607D8B").pack(side="left")
    tk.Label(info_row, text=f"  {r.get('available_seats', 0)} seats available",
             font=(FONT, 10), bg="#B2EBF2", fg="#607D8B").pack(side="left")
    tk.Label(info_row, text=f"  •  Table: {state.get('table', 'N/A')}",
             font=(FONT, 10), bg="#B2EBF2", fg="#607D8B").pack(side="left")

    if r.get("address"):
        tk.Label(card, text=f"📍 {r['address']}", font=(FONT, 10),
                 bg="#B2EBF2", fg="#607D8B", anchor="w",
                 wraplength=460, justify="left").pack(anchor="w", pady=(4, 0))

    tk.Label(root, text="Your Name:", font=(FONT, 11), bg=BG, fg=DARK).pack(anchor="w", padx=24, pady=(14, 2))
    name_var = tk.StringVar()
    tk.Entry(root, textvariable=name_var, font=(FONT, 12), width=30,
             bg=WHITE, fg=DARK, relief="solid", bd=1).pack(padx=24, anchor="w")

    tk.Label(root, text="Phone Number:", font=(FONT, 11), bg=BG, fg=DARK).pack(anchor="w", padx=24, pady=(10, 2))
    phone_var = tk.StringVar()
    tk.Entry(root, textvariable=phone_var, font=(FONT, 12), width=30,
             bg=WHITE, fg=DARK, relief="solid", bd=1).pack(padx=24, anchor="w")

    tk.Label(root, text="Number of Guests:", font=(FONT, 11), bg=BG, fg=DARK).pack(anchor="w", padx=24, pady=(10, 2))
    guests_var = tk.IntVar(value=1)

    guest_frame = tk.Frame(root, bg=BG)
    guest_frame.pack(anchor="w", padx=24)
    tk.Spinbox(guest_frame, from_=1, to=r["available_seats"], textvariable=guests_var,
               font=(FONT, 12), width=5, bg=WHITE, fg=DARK).pack(side="left")

    cost_label = tk.Label(guest_frame, text=f"  = ₹{r['price_per_person']}",
                          font=(FONT, 11), bg=BG, fg="#00838F")
    cost_label.pack(side="left", padx=(10, 0))

    def update_cost(*_):
        try:
            total = guests_var.get() * r["price_per_person"]
            cost_label.config(text=f"  = ₹{total}")
        except Exception:
            pass

    guests_var.trace_add("write", update_cost)

    tk.Label(root, text="Select Date:", font=(FONT, 11), bg=BG, fg=DARK).pack(anchor="w", padx=24, pady=(10, 2))
    date_var = tk.StringVar(value="Today")
    date_row = tk.Frame(root, bg=BG)
    date_row.pack(anchor="w", padx=24)
    for d in ["Today", "Tomorrow"]:
        tk.Radiobutton(date_row, text=d, variable=date_var, value=d,
                       font=(FONT, 11), bg=BG, fg=DARK,
                       selectcolor="#B2EBF2").pack(side="left", padx=(0, 10))

    tk.Label(root, text="Select Meal Time:", font=(FONT, 11), bg=BG, fg=DARK).pack(anchor="w", padx=24, pady=(10, 2))
    meal_var = tk.StringVar(value="Dinner")
    meal_row = tk.Frame(root, bg=BG)
    meal_row.pack(anchor="w", padx=24)
    for m in ["Breakfast", "Lunch", "Dinner"]:
        tk.Radiobutton(meal_row, text=m, variable=meal_var, value=m,
                       font=(FONT, 11), bg=BG, fg=DARK,
                       selectcolor="#B2EBF2").pack(side="left", padx=(0, 10))

    def confirm():
        name = name_var.get().strip()
        phone = phone_var.get().strip()

        if not name:
            tk.Label(root, text="⚠ Please enter your name.", font=(FONT, 10),
                     bg=BG, fg="#D32F2F").pack()
            return
        if not phone or not phone.isdigit() or len(phone) < 10:
            tk.Label(root, text="⚠ Please enter a valid 10-digit phone number.", font=(FONT, 10),
                     bg=BG, fg="#D32F2F").pack()
            return

        guests = guests_var.get()
        date = datetime.now() if date_var.get() == "Today" else datetime.now() + timedelta(days=1)
        bid = "RSV-" + "".join(random.choices(string.ascii_uppercase + string.digits, k=6))

        collection.update_one({"_id": r["_id"]}, {"$inc": {"available_seats": -guests}})
        db["bookings"].insert_one({
            "booking_id": bid, "restaurant": r["name"], "city": r["city"],
            "table": state.get("table", "N/A"),
            "guest_name": name, "guest_phone": phone,
            "guests": guests, "date": date.strftime("%A, %d %b %Y"),
            "meal": meal_var.get(), "cost": guests * r["price_per_person"],
            "booked_at": datetime.now()
        })
        state.update({
            "guests": guests, "date": date.strftime("%A, %d %b %Y"),
            "meal": meal_var.get(), "booking_id": bid,
            "cost": guests * r["price_per_person"],
            "guest_name": name, "guest_phone": phone
        })
        window4(root)

    tk.Button(root, text="Confirm Booking", font=(FONT, 12, "bold"),
              bg=PRIMARY, fg=WHITE, relief="flat", pady=8, width=20,
              cursor="hand2", command=confirm).pack(pady=(16, 4))
    tk.Button(root, text="← Back", font=(FONT, 10), bg=BG, fg=DARK,
              relief="flat", command=lambda: window_table(root)).pack()


def window4(root):
    clear(root)
    root.title("Step 5 - Confirmed!")
    root.config(bg=BG)

    r = state["restaurant"]
    tk.Label(root, text="✅ Seat Confirmed!", font=(FONT, 22, "bold"),
             fg=PRIMARY, bg=BG, pady=20).pack()

    details = [
        ("Booking ID",  state["booking_id"]),
        ("Name",        state["guest_name"]),
        ("Phone",       state["guest_phone"]),
        ("Restaurant",  r["name"]),
        ("Table",       state.get("table", "N/A")),
        ("City",        r["city"]),
        ("Date",        state["date"]),
        ("Meal",        state["meal"]),
        ("Guests",      str(state["guests"])),
        ("Total Cost",  f"₹{state['cost']}"),
        ("Rest. Phone", r.get("phone", "N/A")),
    ]

    for label, value in details:
        row = tk.Frame(root, bg=BG)
        row.pack(fill="x", padx=40, pady=2)
        tk.Label(row, text=f"{label}:", font=(FONT, 11, "bold"),
                 width=14, anchor="w", bg=BG, fg=DARK).pack(side="left")
        tk.Label(row, text=value, font=(FONT, 11),
                 anchor="w", bg=BG, fg=DARK).pack(side="left")

    tk.Button(root, text="🏠 New Booking", font=(FONT, 12),
              bg=PRIMARY, fg=WHITE, relief="flat", pady=6, width=18,
              cursor="hand2", command=lambda: window1(root)).pack(pady=20)


root = tk.Tk()
root.geometry("550x560")
root.resizable(False, False)
window1(root)
root.mainloop()
