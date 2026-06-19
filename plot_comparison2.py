"""
Compare openevolve run2 vs advisor (20260617) vs evox run5 — all opus-4-8 runs.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
import csv

# ── Advisor data (20260617_002859) ────────────────────────────────────────────
ADV_TSV = "/workspace/trimul-advisor/trimul/runs/20260617_002859_trimul_starting_point/results.tsv"
adv_iters, adv_times, adv_kinds = [], [], []
with open(ADV_TSV) as f:
    reader = csv.DictReader(f, delimiter="\t")
    for row in reader:
        adv_iters.append(int(row["agent_iteration"]))
        adv_times.append(float(row["time_us"]))
        adv_kinds.append(row["status"])

# ── OpenEvolve run2 data ──────────────────────────────────────────────────────
# Extracted from trimul_kernel/openevolve_runs/run2/logs/openevolve_20260617_002801.log
oe_raw = [
    (0,  10887.99),
    (1,  9254.15),
    (2,  None),
    (3,  None),
    (4,  None),
    (5,  None),
    (6,  10282.41),
    (7,  None),
    (8,  6798.24),
    (9,  6899.34),
    (10, 6791.43),
    (11, None),
    (12, 6914.04),
    (13, None),
    (14, 6825.52),
    (15, None),
    (16, 6912.42),
    (17, None),
    (18, 7617.89),
    (19, None),
    (20, 6791.82),
    (21, None),
    (22, 6791.73),
    (23, 9336.72),
    (24, 6790.62),
    (25, None),
]
oe_iters, oe_times, oe_kinds = [], [], []
best_so_far = float("inf")
for it, t in oe_raw:
    oe_iters.append(it)
    oe_times.append(t if t is not None else 0.0)
    if t is None:
        oe_kinds.append("crash")
    elif t < best_so_far:
        best_so_far = t
        oe_kinds.append("keep")
    else:
        oe_kinds.append("discard")

# ── EvoX run5 data ────────────────────────────────────────────────────────────
# Extracted from trimul/skydiscover_runs/run5/logs/evox_20260617_073111.log
evox_raw = [
    (0,  10920.60),
    (1,  10927.16),
    (2,  None),
    (3,  11066.71),
    (4,  11121.23),
    (5,  8606.63),
    (6,  9597.45),
    (7,  None),
    (8,  None),
    (9,  9331.88),
    (10, 8916.77),
    (11, None),
    (12, None),
    (13, 8846.16),
    (14, 8903.56),
    (15, 8879.06),
    (16, 8928.64),
    (17, 8908.22),
    (18, 8561.48),
    (19, 8889.31),
    (20, None),
    (21, 8915.99),
    (22, 8635.40),
    (23, None),
    (24, 9068.75),
    (25, 8921.93),
]
evox_iters, evox_times, evox_kinds = [], [], []
best_so_far = float("inf")
for it, t in evox_raw:
    evox_iters.append(it)
    evox_times.append(t if t is not None else 0.0)
    if t is None:
        evox_kinds.append("crash")
    elif t < best_so_far:
        best_so_far = t
        evox_kinds.append("keep")
    else:
        evox_kinds.append("discard")

# ── Best-over-time step lines ─────────────────────────────────────────────────
def best_step(iters, times, kinds):
    bx, by = [], []
    best = float("inf")
    for it, t, k in sorted(zip(iters, times, kinds)):
        if k == "keep" and t > 0:
            best = t
        if best < float("inf"):
            bx.append(it)
            by.append(best)
    return bx, by

adv_bx,  adv_by  = best_step(adv_iters,  adv_times,  adv_kinds)
oe_bx,   oe_by   = best_step(oe_iters,   oe_times,   oe_kinds)
evox_bx, evox_by = best_step(evox_iters, evox_times, evox_kinds)

adv_best  = min(t for t, k in zip(adv_times,  adv_kinds)  if k == "keep" and t > 0)
oe_best   = min(oe_by)   if oe_by   else float("inf")
evox_best = min(evox_by) if evox_by else float("inf")

# ── Y-axis (negative latency, clip outliers) ──────────────────────────────────
CLIP_US = 20000.0
all_valid = [t for t in adv_times + oe_times + evox_times if 0 < t <= CLIP_US]
y_hi = -(min(all_valid) * 0.82)
y_lo = -(CLIP_US * 1.08)

def ny(t):
    return max(-t, y_lo) if t > 0 else y_lo

# ── Plot ──────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(14, 8))
fig.subplots_adjust(top=0.75)

# OpenEvolve run2 — blue
oe_kx = [it for it, k in zip(oe_iters, oe_kinds) if k == "keep"]
oe_ky = [ny(oe_times[i]) for i, k in enumerate(oe_kinds) if k == "keep"]
oe_dx = [it for it, k in zip(oe_iters, oe_kinds) if k == "discard"]
oe_dy = [ny(oe_times[i]) for i, k in enumerate(oe_kinds) if k == "discard"]
oe_cx = [it for it, k in zip(oe_iters, oe_kinds) if k == "crash"]
if oe_kx:
    ax.scatter(oe_kx, oe_ky, c="#3b82f6", s=70, zorder=5, edgecolors="white", linewidths=0.5, label="openevolve keep")
if oe_dx:
    ax.scatter(oe_dx, oe_dy, c="#93c5fd", s=40, zorder=4, edgecolors="white", linewidths=0.3, alpha=0.8, label="openevolve discard")
if oe_bx:
    ax.step(oe_bx, [-t for t in oe_by], where="post", color="#3b82f6", linewidth=2, label="openevolve best", zorder=6)

# Advisor (20260617) — green
adv_kx = [it for it, k in zip(adv_iters, adv_kinds) if k == "keep"]
adv_ky = [ny(adv_times[i]) for i, k in enumerate(adv_kinds) if k == "keep"]
adv_dx = [it for it, k in zip(adv_iters, adv_kinds) if k == "discard"]
adv_dy = [ny(adv_times[i]) for i, k in enumerate(adv_kinds) if k == "discard"]
adv_cx = [it for it, k in zip(adv_iters, adv_kinds) if k == "crash"]
if adv_kx:
    ax.scatter(adv_kx, adv_ky, c="#22c55e", s=70, zorder=5, edgecolors="white", linewidths=0.5, label="advisor keep")
if adv_dx:
    ax.scatter(adv_dx, adv_dy, c="#ef4444", s=40, zorder=4, edgecolors="white", linewidths=0.3, alpha=0.7, label="advisor discard")
if adv_bx:
    ax.step(adv_bx, [-t for t in adv_by], where="post", color="#22c55e", linewidth=2, label="advisor best", zorder=6)

# EvoX run5 — orange
evox_kx = [it for it, k in zip(evox_iters, evox_kinds) if k == "keep"]
evox_ky = [ny(evox_times[i]) for i, k in enumerate(evox_kinds) if k == "keep"]
evox_dx = [it for it, k in zip(evox_iters, evox_kinds) if k == "discard"]
evox_dy = [ny(evox_times[i]) for i, k in enumerate(evox_kinds) if k == "discard"]
evox_cx = [it for it, k in zip(evox_iters, evox_kinds) if k == "crash"]
if evox_kx:
    ax.scatter(evox_kx, evox_ky, c="#f97316", s=70, zorder=5, edgecolors="white", linewidths=0.5, label="evox keep")
if evox_dx:
    ax.scatter(evox_dx, evox_dy, c="#fed7aa", s=40, zorder=4, edgecolors="white", linewidths=0.3, alpha=0.8, label="evox discard")
if evox_bx:
    ax.step(evox_bx, [-t for t in evox_by], where="post", color="#f97316", linewidth=2, label="evox best", zorder=6)

# Crashes (all series)
all_cx = oe_cx + adv_cx + evox_cx
if all_cx:
    ax.scatter(all_cx, [y_lo] * len(all_cx), c="#fbbf24", s=40, zorder=3,
               marker="x", linewidths=1.5, label=f"crash ({len(all_cx)})", alpha=0.8)

ax.set_ylim(y_lo * 1.05, y_hi)
ax.yaxis.set_major_formatter(ticker.FormatStrFormatter("%.0f"))
ax.set_xlabel("Iteration #", fontsize=12)
ax.set_ylabel("Negative Latency (-μs)", fontsize=12)
ax.grid(True, alpha=0.3)

# Legend above the plot
ax.legend(loc="lower center", bbox_to_anchor=(0.5, 1.01), ncol=4,
          framealpha=0.9, fontsize=10, borderaxespad=0)

# Best-time records above the plot
fig.text(0.5, 0.92,
         f"EvoX run5 best: {evox_best:.2f} μs    |    "
         f"OpenEvolve run2 best: {oe_best:.2f} μs    |    "
         f"Advisor best: {adv_best:.2f} μs",
         ha="center", va="top", fontsize=11, fontweight="bold", color="#1e3a5f",
         bbox=dict(boxstyle="round,pad=0.4", facecolor="white", edgecolor="#22c55e", alpha=0.9))

# Title
fig.text(0.5, 0.995, "evox run5 vs openevolve run2 vs advisor (20260617) — trimul — opus-4-8",
         ha="center", va="top", fontsize=14, fontweight="bold")

# Outlier note — bottom left
ax.annotate(
    f"(outliers > {CLIP_US:.0f} μs shown at floor)",
    xy=(0.01, 0.02), xycoords="axes fraction",
    ha="left", va="bottom", fontsize=9, color="#6b7280",
    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", edgecolor="#d1d5db", alpha=0.8),
)

out = "/workspace/trimul-advisor/comparison2.png"
fig.savefig(out, dpi=150)
plt.close(fig)
print(f"Saved {out}")
