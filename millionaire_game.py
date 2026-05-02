# "Who Wants to Be a Millionaire? — Interactive Python Quiz Game


import tkinter as tk
from tkinter import messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import importlib

#  MongoDB Setup
try:
    pymongo = importlib.import_module("pymongo")
except ModuleNotFoundError:
    pymongo = None

try:
    if pymongo is None:
        raise ModuleNotFoundError("pymongo is not installed")
    client = pymongo.MongoClient("mongodb://localhost:27017/", serverSelectionTimeoutMS=2000)
    client.server_info()
    db = client["millionaire_game"]
    players_col = db["players"]
    MONGO_CONNECTED = True
except Exception:
    MONGO_CONNECTED = False
    players_col = None

#  Game Constants
PRIZE_LADDER = [
    100, 200, 300, 500, 1000,
    2000, 4000, 8000, 16000, 32000,
    64000, 125000, 250000, 500000, 1000000
]
SAFE_HAVENS = {4, 9}   # indices → ₹1K and ₹32K
#  Colour Palette
BG         = "#EE1A3D"
CARD       = "#12122a"
GOLD       = "#FFD700"
TEAL       = "#00e5cc"
WHITE      = "#ffffff"
GRAY       = "#555577"
GREEN      = "#00cc66"
RED        = "#ff4444"
OPTBG      = "#1a1a3e"
OPTHOV     = "#2a2a5e"
PURPLE     = "#aa88ff"
ORANGE     = "#ff8844"
LBLUE      = "#44aaff"

#  Built-in Questions  (fallback if no CSV)
BUILTIN_QS = [
    {"question":"What is the time complexity of building a heap from an unsorted array?","A":"O(n log n)","B":"O(n)","C":"O(log n)","D":"O(n²)","answer":"B","category":"CS","difficulty":"Medium"},

{"question":"In Python, what does `sys.intern()` do?","A":"Garbage-collects a string","B":"Returns the byte size of a string","C":"Forces two strings to share memory if equal","D":"Encrypts a string in-place","answer":"C","category":"Python","difficulty":"Medium"},

{"question":"Which isolation level prevents phantom reads?","A":"Read Uncommitted","B":"Read Committed","C":"Repeatable Read","D":"Serializable","answer":"D","category":"DBMS","difficulty":"Medium"},

{"question":"What does the `volatile` keyword guarantee in Java/C?","A":"Atomic read-modify-write","B":"Visibility of changes across threads","C":"Mutual exclusion","D":"Stack allocation","answer":"B","category":"Systems","difficulty":"Medium"},

{"question":"In REST, which HTTP method is idempotent but NOT safe?","A":"GET","B":"DELETE","C":"POST","D":"PATCH","answer":"B","category":"Web","difficulty":"Medium"},

{"question":"Which data structure is optimal for finding the k-th smallest element repeatedly?","A":"Sorted array","B":"BST","C":"Min-heap of size k","D":"Hash map","answer":"C","category":"CS","difficulty":"Medium"},

{"question":"What is the output of: `print(0.1 + 0.2 == 0.3)` in Python?","A":"True","B":"False","C":"Error","D":"None","answer":"B","category":"Python","difficulty":"Medium"},

{"question":"In a B-tree of order m, what is the minimum number of keys in a non-root node?","A":"⌈m/2⌉","B":"⌈m/2⌉ − 1","C":"m − 1","D":"m/2","answer":"B","category":"DBMS","difficulty":"Medium"},

{"question":"What scheduling algorithm can cause starvation?","A":"Round Robin","B":"FCFS","C":"Priority Scheduling","D":"Shortest Job Next","answer":"C","category":"OS","difficulty":"Medium"},

{"question":"What is the amortized time complexity of a single push on a dynamic array?","A":"O(n)","B":"O(log n)","C":"O(1)","D":"O(n log n)","answer":"C","category":"CS","difficulty":"Medium"},

{"question":"What problem does the ABA issue describe in lock-free programming?","A":"Stack overflow due to recursion","B":"A value changed from A→B→A making CAS incorrectly succeed","C":"Deadlock between two atomic operations","D":"Memory alignment fault on 64-bit systems","answer":"B","category":"Systems","difficulty":"Hard"},

{"question":"In Python's GIL, which operation is NOT protected?","A":"List append","B":"Dictionary lookup","C":"File I/O operations","D":"Object reference counting","answer":"C","category":"Python","difficulty":"Hard"},

{"question":"What is the output of `[*{1,2,3}]` compared to `[1,2,3]` in Python?","A":"Always identical","B":"Same elements, possibly different order","C":"Raises TypeError","D":"Returns set object","answer":"B","category":"Python","difficulty":"Hard"},

{"question":"In Postgres, what does MVCC stand for and what does it eliminate?","A":"Multi-Version Concurrency Control; eliminates read-write conflicts without locks","B":"Multiple Value Caching Control; eliminates cache misses","C":"Memory-Version Cache Control; eliminates dirty reads only","D":"Multi-Value Conflict Control; eliminates all deadlocks","answer":"A","category":"DBMS","difficulty":"Hard"},

{"question":"Which of these correctly describes the Liskov Substitution Principle?","A":"A subclass must override all parent methods","B":"An interface should have only one method","C":"Objects of a subclass must be usable wherever the parent class is expected without altering correctness","D":"Every class should depend on abstractions, not concretions","answer":"C","category":"OOP","difficulty":"Hard"},

{"question":"What is the worst-case time to find an element in a hash table with chaining?","A":"O(1)","B":"O(log n)","C":"O(n)","D":"O(n²)","answer":"C","category":"CS","difficulty":"Hard"},

{"question":"What does `__slots__` do in a Python class?","A":"Prevents subclassing","B":"Makes all attributes read-only","C":"Replaces the per-instance __dict__ with a fixed-size array","D":"Generates __init__ automatically","answer":"C","category":"Python","difficulty":"Hard"},

{"question":"In TCP, what does the TIME_WAIT state prevent?","A":"SYN flooding attacks","B":"Delayed packets from an old connection being accepted by a new one on the same port","C":"Duplicate ACKs from triggering retransmission","D":"RST packets during half-close","answer":"B","category":"Networking","difficulty":"Hard"},

{"question":"What distinguishes a process from a thread in terms of memory?","A":"Threads have separate heap; processes share heap","B":"Processes have isolated virtual address space; threads share it","C":"Threads have their own page tables","D":"Processes share stack memory","answer":"B","category":"OS","difficulty":"Hard"},

{"question":"In consistent hashing, adding a node requires remapping approximately how many keys?","A":"All keys","B":"n/m keys (n=keys, m=nodes)","C":"O(log n) keys","D":"Zero keys","answer":"B","category":"Systems","difficulty":"Hard"},

{"question":"What is the time complexity of Tarjan's strongly connected components algorithm?","A":"O(V²)","B":"O(V + E)","C":"O(E log V)","D":"O(VE)","answer":"B","category":"CS","difficulty":"Impossible"},

{"question":"In Python, what is the MRO resolution order for: `class D(B, C)` where `B(A)` and `C(A)`?","A":"D → B → A → C","B":"D → B → C → A","C":"D → C → B → A","D":"D → A → B → C","answer":"B","category":"Python","difficulty":"Impossible"},

{"question":"Which theorem states that no distributed system can simultaneously guarantee consistency, availability, AND partition tolerance?","A":"ACID theorem","B":"Brewer's CAP theorem","C":"FLP impossibility theorem","D":"BASE theorem","answer":"B","category":"DBMS","difficulty":"Impossible"},

{"question":"What is the key insight behind the Raft consensus algorithm vs. Paxos?","A":"Raft uses randomized leader election; Paxos uses quorum intersection","B":"Raft decomposes consensus into independent subproblems with a single strong leader for understandability","C":"Raft guarantees liveness under asynchrony; Paxos does not","D":"Raft uses multi-cast; Paxos uses unicast only","answer":"B","category":"Systems","difficulty":"Impossible"},

{"question":"In Python, `id(256) == id(256)` is True but `id(257) == id(257)` may be False. Why?","A":"256 is cached as a singleton; 257 is not","B":"256 uses 8 bits; 257 overflows to heap","C":"Python interns all even numbers only","D":"257 triggers garbage collection","answer":"A","category":"Python","difficulty":"Impossible"},

{"question":"What is the false sharing problem in multi-core CPUs?","A":"Two threads incorrectly share a mutex","B":"Two threads on different cores write to different variables that share a cache line, causing unnecessary invalidation","C":"Shared memory mapped to wrong physical page","D":"CPU branch predictor sharing state across cores","answer":"B","category":"Systems","difficulty":"Impossible"},

{"question":"Which normal form does BCNF improve upon, and what does it fix?","A":"Fixes 2NF by removing partial dependencies","B":"Fixes 3NF by removing all functional dependencies not based on superkeys","C":"Fixes 1NF by allowing multivalued dependencies","D":"Fixes 4NF by removing join dependencies","answer":"B","category":"DBMS","difficulty":"Impossible"},

{"question":"In Python's asyncio, what is the difference between `asyncio.gather` and `asyncio.wait`?","A":"gather cancels all on first failure; wait returns sets of done/pending tasks for manual control","B":"gather is synchronous; wait is asynchronous","C":"They are identical","D":"wait creates new event loops; gather reuses existing","answer":"A","category":"Python","difficulty":"Impossible"},

{"question":"What is the difference between linearizability and serializability?","A":"Linearizability applies to single-object operations with real-time ordering; serializability applies to multi-object transactions","B":"Serializability is stronger than linearizability","C":"They are the same concept in different literature","D":"Linearizability only applies to reads; serializability to writes","answer":"A","category":"DBMS","difficulty":"Impossible"},

{"question":"In CPython, what triggers the GIL to be released voluntarily by a running thread?","A":"Every function call","B":"Every 100 bytecode instructions (pre-3.2) or after a configurable interval via sys.setswitchinterval","C":"Only when a thread calls time.sleep()","D":"Only on I/O and C extension calls","answer":"B","category":"Python","difficulty":"Impossible"}
]
#  Load & prepare questions
def load_questions() -> list[dict]:
    try:
        df = pd.read_csv("questions.csv")
        qs = df.to_dict("records")
    except Exception:
        qs = BUILTIN_QS.copy()

    df = pd.DataFrame(qs)
    order = {"Easy": 0, "Medium": 1, "Hard": 2}
    df["_ord"] = df["difficulty"].map(order).fillna(1)

    rng = np.random.default_rng()
    parts = []
    for diff, need in [("Easy", 5), ("Medium", 5), ("Hard", 5)]:
        pool = df[df["difficulty"] == diff]
        n = min(need, len(pool))
        idx = rng.choice(len(pool), size=n, replace=False)
        parts.append(pool.iloc[idx])

    selected = pd.concat(parts).reset_index(drop=True)
    return selected.to_dict("records")

#  MAIN GAME CLASS
class MillionaireGame:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Who Wants to Be a Millionaire?")
        self.root.geometry("1100x680")
        self.root.configure(bg=BG)
        self.root.resizable(False, False)

        # ── session state ──
        self.player_name    = ""
        self.questions      : list[dict] = []
        self.current_q      = 0
        self.current_prize  = 0
        self.lifelines      = {"50-50": True, "Phone": True,
                               "Audience": True, "Switch": True}
        self.timer_job      = None
        self.timer_val      = 30
        self.session_data   : list[dict] = []
        self.lifeline_usage = {"50-50": 0, "Phone": 0,
                               "Audience": 0, "Switch": 0}
        self.disabled_opts  : list[str] = []

        # ── Lock Prize feature ──
        self.lock_prize_used : bool = False   # one-time use per game
        self.locked_prize    : int  = 0       # amount locked in

        self.show_login()
    # ── helpers ──────────────────────────────
    def clear(self):
        for w in self.root.winfo_children():
            w.destroy()

    def _btn(self, parent, text, cmd, bg=CARD, fg=WHITE,
             font_size=11, bold=False, px=15, py=8):
        f = ("Courier", font_size, "bold") if bold else ("Courier", font_size)
        return tk.Button(parent, text=text, command=cmd,
                         font=f, bg=bg, fg=fg, relief="flat",
                         padx=px, pady=py, cursor="hand2",
                         activebackground=bg, activeforeground=fg)
    #  LOGIN SCREEN
    def show_login(self):
        self.clear()
        f = tk.Frame(self.root, bg=BG)
        f.place(relx=.5, rely=.5, anchor="center")

        tk.Label(f, text="💰", font=("Arial", 64), bg=BG).pack()
        tk.Label(f, text="WHO WANTS TO BE",
                 font=("Courier", 20, "bold"), fg=GOLD, bg=BG).pack()
        tk.Label(f, text="A MILLIONAIRE?",
                 font=("Courier", 26, "bold"), fg=GOLD, bg=BG).pack()
        tk.Label(f, text="Interactive Python Quiz  ·  UPES B.Tech CSE",
                 font=("Courier", 10), fg=TEAL, bg=BG).pack(pady=(6, 28))

        tk.Label(f, text="Enter Your Name:", font=("Courier", 12),
                 fg=WHITE, bg=BG).pack()
        self.name_var = tk.StringVar()
        entry = tk.Entry(f, textvariable=self.name_var,
                         font=("Courier", 13), bg=CARD, fg=WHITE,
                         insertbackground=WHITE, relief="flat",
                         width=24, highlightthickness=2,
                         highlightcolor=GOLD, highlightbackground=GRAY)
        entry.pack(pady=10, ipady=8)
        entry.focus()

        self._btn(f, "▶  START GAME", self.start_game,
                  bg=GOLD, fg=BG, font_size=13, bold=True,
                  px=30, py=10).pack(pady=10)
        self._btn(f, "🏆  Leaderboard", self.show_leaderboard,
                  bg=CARD, fg=TEAL, font_size=11,
                  px=20, py=8).pack()

        self.root.bind("<Return>", lambda _: self.start_game())

    def start_game(self):
        name = self.name_var.get().strip()
        if not name:
            messagebox.showwarning("Name Required", "Please enter your name!")
            return
        self.player_name    = name
        self.questions      = load_questions()
        self.current_q      = 0
        self.current_prize  = 0
        self.lifelines      = {"50-50": True, "Phone": True,
                               "Audience": True, "Switch": True}
        self.session_data    = []
        self.lifeline_usage  = {"50-50": 0, "Phone": 0,
                                "Audience": 0, "Switch": 0}
        self.lock_prize_used = False
        self.locked_prize    = 0
        self.show_game()
    #  GAME SCREEN
    def show_game(self):
        self.clear()
        self.disabled_opts = []

        # ── Right: Prize Ladder ──────────────
        right = tk.Frame(self.root, bg=CARD, width=195)
        right.pack(side="right", fill="y")
        right.pack_propagate(False)

        tk.Label(right, text="PRIZE LADDER",
                 font=("Courier", 9, "bold"), fg=GOLD, bg=CARD).pack(pady=(12, 4))

        self.prize_labels: list[tuple[int, tk.Label]] = []
        for i in range(14, -1, -1):
            safe = i in SAFE_HAVENS
            lbl = tk.Label(right,
                           text=f"{'🛡 ' if safe else '   '}₹{PRIZE_LADDER[i]:,}",
                           font=("Courier", 8, "bold" if safe else "normal"),
                           fg=GOLD if safe else GRAY, bg=CARD, anchor="w", pady=1)
            lbl.pack(fill="x", padx=12)
            self.prize_labels.append((i, lbl))

        # ── Left: Main area ──────────────────
        main = tk.Frame(self.root, bg=BG)
        main.pack(side="left", fill="both", expand=True, padx=18, pady=14)

        # top bar
        top = tk.Frame(main, bg=BG)
        top.pack(fill="x")
        tk.Label(top, text=f"👤 {self.player_name}",
                 font=("Courier", 11), fg=TEAL, bg=BG).pack(side="left")
        self.prize_lbl = tk.Label(top, text="₹0",
                                  font=("Courier", 12, "bold"), fg=GOLD, bg=BG)
        self.prize_lbl.pack(side="left", padx=20)
        self.timer_lbl = tk.Label(top, text="⏱ 30",
                                  font=("Courier", 13, "bold"), fg=WHITE, bg=BG)
        self.timer_lbl.pack(side="right")

        # question meta
        self.meta_lbl = tk.Label(main, text="",
                                 font=("Courier", 9), fg=GRAY, bg=BG)
        self.meta_lbl.pack(pady=(10, 2))

        # question box
        qbox = tk.Frame(main, bg=CARD)
        qbox.pack(fill="x", pady=8, ipady=14)
        self.q_lbl = tk.Label(qbox, text="",
                              font=("Courier", 13, "bold"),
                              fg=WHITE, bg=CARD,
                              wraplength=680, justify="center")
        self.q_lbl.pack(padx=18, pady=10)

        # options 2×2 grid
        grid = tk.Frame(main, bg=BG)
        grid.pack(fill="x", pady=4)
        self.opt_btns: dict[str, tk.Button] = {}
        for idx, opt in enumerate(["A", "B", "C", "D"]):
            row, col = divmod(idx, 2)
            b = tk.Button(grid, text="", font=("Courier", 11),
                          bg=OPTBG, fg=WHITE, relief="flat",
                          padx=14, pady=11, width=38,
                          wraplength=290, justify="left", cursor="hand2",
                          command=lambda o=opt: self.answer(o),
                          activebackground=OPTHOV, activeforeground=WHITE)
            b.grid(row=row, column=col, padx=7, pady=5, sticky="ew")
            b.bind("<Enter>", lambda e, x=b: x["state"] != "disabled"
                   and x.configure(bg=OPTHOV))
            b.bind("<Leave>", lambda e, x=b: x["state"] != "disabled"
                   and x.configure(bg=OPTBG))
            self.opt_btns[opt] = b
        grid.columnconfigure(0, weight=1)
        grid.columnconfigure(1, weight=1)

        # lifelines
        ll_row = tk.Frame(main, bg=BG)
        ll_row.pack(pady=8)
        ll_cfg = [("50-50","50:50",TEAL),("Phone","📞 Phone",PURPLE),
                  ("Audience","👥 Audience",ORANGE),("Switch","🔄 Switch",LBLUE)]
        self.ll_btns: dict[str, tk.Button] = {}
        for key, label, color in ll_cfg:
            b = tk.Button(ll_row, text=label,
                          font=("Courier", 10, "bold"),
                          bg=CARD, fg=color, relief="flat",
                          padx=11, pady=5, cursor="hand2",
                          command=lambda k=key: self.lifeline(k),
                          activebackground=CARD, activeforeground=color)
            b.pack(side="left", padx=7)
            self.ll_btns[key] = b

        # ── Lock Prize button + status label ──────────────────────────
        lock_row = tk.Frame(main, bg=BG)
        lock_row.pack()

        self.lock_btn = tk.Button(
            lock_row, text="🔒 Lock Prize",
            font=("Courier", 10, "bold"),
            bg="#1a2a1a", fg=GREEN, relief="flat",
            padx=14, pady=5, cursor="hand2",
            command=self.use_lock_prize,
            activebackground="#1a2a1a", activeforeground=GREEN)
        self.lock_btn.pack(side="left", padx=7)

        self.lock_status_lbl = tk.Label(
            lock_row, text="",
            font=("Courier", 9, "bold"), fg=GREEN, bg=BG)
        self.lock_status_lbl.pack(side="left", padx=4)

        self._btn(main, "🚪 Walk Away", self.walk_away,
                  bg=CARD, fg=RED, font_size=9, px=12, py=5).pack(pady=4)

        self._load_q()

    # ── prize ladder highlight ──────────────
    def _update_ladder(self):
        for i, lbl in self.prize_labels:
            safe = i in SAFE_HAVENS
            locked_here = (self.locked_prize == PRIZE_LADDER[i])
            prefix = "🔒 " if locked_here else ("🛡 " if safe else "   ")
            color_fg = GREEN if locked_here else (GOLD if safe else GRAY)

            if i == self.current_q:
                lbl.configure(text=f"{prefix}₹{PRIZE_LADDER[i]:,}",
                              fg="#000000", bg=GOLD,
                              font=("Courier", 8, "bold"))
            elif i < self.current_q:
                lbl.configure(text=f"{prefix}₹{PRIZE_LADDER[i]:,}",
                              fg=GREEN, bg=CARD,
                              font=("Courier", 8, "normal"))
            else:
                lbl.configure(text=f"{prefix}₹{PRIZE_LADDER[i]:,}",
                              fg=color_fg, bg=CARD,
                              font=("Courier", 8, "bold" if (safe or locked_here) else "normal"))

    # ── load current question ───────────────
    def _load_q(self):
        self.disabled_opts = []
        q = self.questions[self.current_q]
        self.meta_lbl.configure(
            text=f"Q{self.current_q+1}/15  ·  {q['difficulty']}  ·  {q['category']}")
        self.q_lbl.configure(text=q["question"])
        self.prize_lbl.configure(text=f"₹{PRIZE_LADDER[self.current_q]:,}")
        for opt in ["A","B","C","D"]:
            self.opt_btns[opt].configure(
                text=f"  {opt}.  {q[opt]}",
                bg=OPTBG, fg=WHITE, state="normal")
        self._update_ladder()
        self._start_timer()

    # ── timer ───────────────────────────────
    def _start_timer(self):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        self.timer_val = 30
        self._tick()

    def _tick(self):
        self.timer_lbl.configure(
            text=f"⏱ {self.timer_val:02d}",
            fg=RED if self.timer_val <= 10 else WHITE)
        if self.timer_val > 0:
            self.timer_val -= 1
            self.timer_job = self.root.after(1000, self._tick)
        else:
            messagebox.showinfo("⏱ Time's Up!", "You ran out of time!")
            self.end_game(won=False)

    # ── answer handler ──────────────────────
    def answer(self, chosen: str):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)
        q = self.questions[self.current_q]
        correct = q["answer"]

        for b in self.opt_btns.values():
            b.configure(state="disabled")
        self.opt_btns[chosen].configure(bg="#884400")
        self.root.update()
        self.root.after(600, lambda: None)

        ok = chosen == correct
        self.session_data.append({
            "question" : self.current_q + 1,
            "category" : q["category"],
            "difficulty": q["difficulty"],
            "correct"  : ok,
            "time_taken": 30 - self.timer_val,
        })

        if ok:
            self.opt_btns[chosen].configure(bg=GREEN)
            self.current_prize = PRIZE_LADDER[self.current_q]
            self.root.after(900, self._next)
        else:
            self.opt_btns[chosen].configure(bg=RED)
            self.opt_btns[correct].configure(bg=GREEN)
            self.root.after(1300, lambda: self.end_game(won=False))

    def _next(self):
        self.current_q += 1
        if self.current_q >= 15:
            self.end_game(won=True)
        else:
            self._load_q()

    #  LOCK PRIZE
    def use_lock_prize(self):
        if self.lock_prize_used:
            messagebox.showinfo("🔒 Already Used",
                                "You've already locked a prize this game!")
            return
        if self.current_prize == 0:
            messagebox.showwarning("🔒 Nothing to Lock",
                                   "Answer at least one question first\n"
                                   "to have a prize worth locking!")
            return

        self.lock_prize_used = True
        self.locked_prize    = self.current_prize

        # update button to show it's been used
        self.lock_btn.configure(
            text=f"🔒 Locked ₹{self.current_prize:,}",
            fg=GRAY, state="disabled", bg=CARD)
        self.lock_status_lbl.configure(
            text=f"✔ Guaranteed: ₹{self.current_prize:,}")

        self._update_ladder()   # show 🔒 icon on ladder
        messagebox.showinfo(
            "🔒 Prize Locked!",
            f"₹{self.current_prize:,} is now GUARANTEED!\n\n"
            "Even if you answer wrong, you'll take home\n"
            "at least this amount. Good luck! 🍀")

    #  LIFELINES
    def lifeline(self, key: str):
        if not self.lifelines[key]:
            return
        self.lifelines[key] = False
        self.ll_btns[key].configure(fg=GRAY, state="disabled")
        self.lifeline_usage[key] += 1

        q = self.questions[self.current_q]
        correct = q["answer"]
        wrongs = [o for o in "ABCD"
                  if o != correct and o not in self.disabled_opts]
        rng = np.random.default_rng()

        if key == "50-50":
            remove = rng.choice(wrongs, size=min(2, len(wrongs)), replace=False)
            for o in remove:
                self.opt_btns[o].configure(text="", state="disabled", bg=BG)
                self.disabled_opts.append(o)

        elif key == "Phone":
            correct_chance = rng.integers(65, 90)
            if rng.random() * 100 < correct_chance:
                hint = f"I'm about {correct_chance}% sure it's  '{correct}'"
            else:
                decoy = rng.choice(wrongs) if wrongs else correct
                hint = f"Hmm… I think it might be '{decoy}'? Not so sure!"
            messagebox.showinfo("📞 Phone a Friend", hint)

        elif key == "Audience":
            probs = np.zeros(4)
            ci = "ABCD".index(correct)
            probs[ci] = rng.integers(52, 72)
            rest = np.array(rng.dirichlet(np.ones(3)) * (100 - probs[ci]))
            j = 0
            for i in range(4):
                if i != ci:
                    probs[i] = rest[j]; j += 1
            msg = "📊 Audience Poll:\n\n"
            for i, o in enumerate("ABCD"):
                bar = "█" * int(probs[i] / 4)
                msg += f"  {o}: {bar:<25} {probs[i]:.1f}%\n"
            messagebox.showinfo("👥 Ask the Audience", msg)

        elif key == "Switch":
            remaining = [i for i in range(len(self.questions))
                         if i != self.current_q]
            if remaining:
                ni = int(rng.choice(remaining))
                self.questions[self.current_q] = self.questions[ni]
            if self.timer_job:
                self.root.after_cancel(self.timer_job)
            self._load_q()

    # ── walk away ───────────────────────────
    def walk_away(self):
        if messagebox.askyesno("Walk Away",
                               f"Take home ₹{self.current_prize:,} and quit?"):
            self.end_game(won=False, walked=True)
    #  END GAME
    def end_game(self, won=False, walked=False):
        if self.timer_job:
            self.root.after_cancel(self.timer_job)

        # safe-haven fallback on wrong answer
        if not won and not walked:
            safe_prize = 0
            for sh in sorted(SAFE_HAVENS):
                if self.current_q > sh:
                    safe_prize = PRIZE_LADDER[sh]
            # 🔒 locked prize overrides safe haven if it's higher
            self.current_prize = max(safe_prize, self.locked_prize)

        # ── MongoDB CREATE ──
        record = {
            "name"               : self.player_name,
            "score"              : self.current_prize,
            "questions_answered" : self.current_q,
            "won"                : won,
            "session_data"       : self.session_data,
            "lifeline_usage"     : self.lifeline_usage,
            "timestamp"          : datetime.now(),
        }
        if MONGO_CONNECTED and players_col is not None:
            players_col.insert_one(record)

        self.show_result(won, walked)

    #  RESULT SCREEN
    def show_result(self, won: bool, walked: bool):
        self.clear()
        f = tk.Frame(self.root, bg=BG)
        f.place(relx=.5, rely=.5, anchor="center")

        if won:
            emoji, title, col = "🎉", "CONGRATULATIONS!", GREEN
        elif walked:
            emoji, title, col = "🚶", "YOU WALKED AWAY!", TEAL
        else:
            emoji, title, col = "💔", "GAME  OVER", RED

        tk.Label(f, text=emoji, font=("Arial", 56), bg=BG).pack()
        tk.Label(f, text=title,
                 font=("Courier", 22, "bold"), fg=col, bg=BG).pack(pady=(4,0))
        tk.Label(f, text="You take home",
                 font=("Courier", 12), fg=GRAY, bg=BG).pack(pady=(14,0))
        tk.Label(f, text=f"₹{self.current_prize:,}",
                 font=("Courier", 34, "bold"), fg=GOLD, bg=BG).pack()
        tk.Label(f, text=f"Questions answered: {self.current_q} / 15",
                 font=("Courier", 10), fg=WHITE, bg=BG).pack(pady=6)

        # show lock prize info if it was used
        if self.lock_prize_used and not won:
            if self.current_prize == self.locked_prize:
                tk.Label(f, text=f"🔒 Lock Prize saved you  ₹{self.locked_prize:,}!",
                         font=("Courier", 10, "bold"), fg=GREEN, bg=BG).pack(pady=3)
            else:
                tk.Label(f, text=f"🔒 You had locked ₹{self.locked_prize:,}",
                         font=("Courier", 9), fg=GRAY, bg=BG).pack(pady=2)

        if not MONGO_CONNECTED:
            tk.Label(f, text="⚠ MongoDB not connected — score not saved",
                     font=("Courier", 9), fg=ORANGE, bg=BG).pack()

        row = tk.Frame(f, bg=BG)
        row.pack(pady=16)
        self._btn(row, "📊 Analytics", self.show_analytics,
                  bg=TEAL, fg=BG, bold=True, px=18, py=8).pack(side="left", padx=7)
        self._btn(row, "▶ Play Again", self.show_login,
                  bg=GOLD, fg=BG, bold=True, px=18, py=8).pack(side="left", padx=7)
        self._btn(row, "🏆 Leaderboard", self.show_leaderboard,
                  bg=CARD, fg=WHITE, px=15, py=8).pack(side="left", padx=7)

    #  ANALYTICS  (Matplotlib)
    def show_analytics(self):
        if not self.session_data:
            messagebox.showinfo("No Data", "Answer at least one question first.")
            return

        df = pd.DataFrame(self.session_data)

        fig, axes = plt.subplots(2, 2, figsize=(12, 8))
        fig.patch.set_facecolor("#0a0a1a")
        fig.suptitle(f"Game Analytics  —  {self.player_name}",
                     color="gold", fontsize=13, fontweight="bold")

        # ── 1. Bar chart: category-wise ──────
        ax = axes[0][0]
        ax.set_facecolor(CARD)
        grp = df.groupby("category")["correct"].agg(["sum","count"])
        grp["wrong"] = grp["count"] - grp["sum"]
        x = np.arange(len(grp))
        ax.bar(x - .2, grp["sum"],  .4, label="Correct", color=GREEN)
        ax.bar(x + .2, grp["wrong"],.4, label="Wrong",   color=RED)
        ax.set_xticks(x)
        ax.set_xticklabels(grp.index, color="white", rotation=15, fontsize=8)
        ax.set_title("Category-wise Performance", color="white")
        ax.legend(facecolor=CARD, labelcolor="white")
        ax.tick_params(colors="white")
        for s in ax.spines.values(): s.set_color("#333")

        # ── 2. Line chart: score trend ───────
        ax = axes[0][1]
        ax.set_facecolor(CARD)
        if MONGO_CONNECTED and players_col is not None:
            sessions = list(players_col.find(
                {"name": self.player_name}, {"score": 1}))
            scores = [s["score"] for s in sessions[-12:]]
            if len(scores) > 1:
                ax.plot(range(1, len(scores)+1), scores,
                        color=TEAL, marker="o", linewidth=2)
                ax.set_title("Score Trend (Last Sessions)", color="white")
                ax.set_xlabel("Session #", color="white")
                ax.set_ylabel("₹ Score", color="white")
            else:
                ax.text(.5, .5, "Play more sessions\nto see the trend!",
                        ha="center", va="center",
                        color="white", transform=ax.transAxes)
                ax.set_title("Performance Trend", color="white")
        else:
            ax.text(.5, .5, "MongoDB not connected",
                    ha="center", va="center",
                    color="white", transform=ax.transAxes)
            ax.set_title("Performance Trend", color="white")
        ax.tick_params(colors="white")
        for s in ax.spines.values(): s.set_color("#333")

        # ── 3. Pie chart: lifeline usage ─────
        ax = axes[1][0]
        ax.set_facecolor(CARD)
        used = {k: v for k, v in self.lifeline_usage.items() if v > 0}
        if used:
            ax.pie(used.values(), labels=used.keys(),
                   colors=[TEAL, PURPLE, ORANGE, LBLUE],
                   autopct="%1.0f%%",
                   textprops={"color": "white"})
        else:
            ax.text(.5, .5, "No lifelines used",
                    ha="center", va="center",
                    color="white", transform=ax.transAxes)
        ax.set_title("Lifeline Usage", color="white")

        # ── 4. Histogram: all-player scores ──
        ax = axes[1][1]
        ax.set_facecolor(CARD)
        if MONGO_CONNECTED and players_col is not None:
            all_scores = [s["score"] for s in players_col.find({}, {"score":1})]
            if all_scores:
                ax.hist(all_scores, bins=10,
                        color=LBLUE, edgecolor=BG)
                ax.set_title("Score Distribution (All Players)", color="white")
                ax.set_xlabel("₹ Score", color="white")
                ax.set_ylabel("Count",   color="white")
            else:
                ax.text(.5, .5, "No records yet",
                        ha="center", va="center",
                        color="white", transform=ax.transAxes)
        else:
            ax.text(.5, .5, "MongoDB not connected",
                    ha="center", va="center",
                    color="white", transform=ax.transAxes)
        ax.set_title("Score Distribution", color="white")
        ax.tick_params(colors="white")
        for s in ax.spines.values(): s.set_color("#333")

        plt.tight_layout()
        plt.show()

    #  LEADERBOARD
    def show_leaderboard(self):
        win = tk.Toplevel(self.root)
        win.title("🏆 Leaderboard")
        win.geometry("520x520")
        win.configure(bg=BG)

        tk.Label(win, text="🏆  LEADERBOARD",
                 font=("Courier", 15, "bold"), fg=GOLD, bg=BG).pack(pady=14)

        if not MONGO_CONNECTED or players_col is None:
            tk.Label(win, text="⚠ MongoDB not connected.\nStart MongoDB service to track scores.",
                     font=("Courier", 11), fg=GRAY, bg=BG).pack(pady=50)
            return

        players_collection = players_col

        # ── MongoDB READ ──
        top = list(players_collection.find({}).sort("score", -1).limit(10))

        hdr = tk.Frame(win, bg=CARD)
        hdr.pack(fill="x", padx=18)
        for txt, w in [("#",4),("Name",15),("Score (₹)",13),("Qs",5)]:
            tk.Label(hdr, text=txt, width=w,
                     font=("Courier", 9, "bold"),
                     fg=GOLD, bg=CARD).pack(side="left")

        medal = [GOLD, "#C0C0C0", "#CD7F32"]
        for rank, p in enumerate(top, 1):
            c = medal[rank-1] if rank <= 3 else WHITE
            row = tk.Frame(win, bg=BG)
            row.pack(fill="x", padx=18, pady=1)
            for txt, w in [(str(rank),4),
                           (str(p.get("name","?"))[:15],15),
                           (f"{p.get('score',0):,}",13),
                           (str(p.get("questions_answered",0)),5)]:
                tk.Label(row, text=txt, width=w,
                         font=("Courier", 9), fg=c, bg=BG).pack(side="left")

        def _delete_player():
            sel = win.focus_get()
            # ── MongoDB DELETE ──
            if messagebox.askyesno("Delete",
                                   "Delete ALL records from MongoDB?"):
                players_collection.delete_many({})
                messagebox.showinfo("Done","All records cleared.")
                win.destroy()

        # ── MongoDB UPDATE demo ──
        def _update_demo():
            if top:
                players_collection.update_one(
                    {"name": top[0]["name"]},
                    {"$set": {"verified": True}})
                messagebox.showinfo("MongoDB UPDATE",
                                    f"Marked '{top[0]['name']}' as verified.")

        btn_row = tk.Frame(win, bg=BG)
        btn_row.pack(pady=14)
        self._btn(btn_row, "✏ Mark #1 Verified", _update_demo,
                  bg=CARD, fg=TEAL, font_size=9, px=10, py=5).pack(
                  side="left", padx=6)
        self._btn(btn_row, "🗑 Clear All", _delete_player,
                  bg=CARD, fg=RED, font_size=9, px=10, py=5).pack(
                  side="left", padx=6)
        
#  Entry Point
if __name__ == "__main__":
    root = tk.Tk()
    MillionaireGame(root)
    root.mainloop()
