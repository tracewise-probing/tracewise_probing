
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd 

def effect_n():
    # ----------------- data -----------------
    n_labels = [1, 2, 4, 8, 16, 32, 64, 128]   # labels only
    x_pos    = list(range(len(n_labels)))      # equally spaced positions: 0..7
    
    wo       = [40.27, 43.56, 52.60, 53.97, 58.08, 61.64, 66.03, 64.66]
    exe      = [38.08, 49.04, 49.32, 56.71, 57.81, 63.01, 63.01, 65.75]
    concise  = [39.45, 47.12, 52.33, 57.26, 58.08, 59.45, 64.38, 64.38]
    next_    = [39.18, 44.66, 51.78, 55.89, 60.27, 61.10, 68.22, 65.48]
    semc     = [37.81, 46.03, 51.78, 55.34, 59.45, 61.37, 63.84]          # shorter series (up to index 6)
    
    # ----------------- palette ---------------
    COLORS = {
        "wo"     : "#003C8F",
        "exe"    : "#E1AD01",
        "concise": "#004B3C",
        "next"   : "#808080",
        "semc"   : "#74258C",
    }
    
    plt.figure(figsize=(6.2, 5.2), dpi=150)
    
    
    plt.plot(x_pos, wo,       color=COLORS["wo"],      marker="o", lw=1.5, ms=5, label="w/o trace")
    plt.plot(x_pos, exe,      color=COLORS["exe"],     marker="o", lw=1.5, ms=5, label="CodeExecutor")
    plt.plot(x_pos, concise,  color=COLORS["concise"], marker="o", lw=1.5, ms=5, label="Concise")
    plt.plot(x_pos, next_,    color=COLORS["next"],    marker="o", lw=1.5, ms=5, label="NExT")
    plt.plot(x_pos[:len(semc)], semc,
             color=COLORS["semc"], marker="o", lw=1.5, ms=5, label="SemCoder")
    
    # ----------------- style -----------------
    plt.title("Effect of n", fontsize=22)
    plt.xlabel("n (number of sampled completions)", fontsize=16)
    plt.ylabel("Pass@1", fontsize=16)
    
    # equally spaced ticks with numeric labels
    plt.xticks(x_pos, n_labels)
    plt.grid(color="lightgray", linestyle="--", linewidth=0.7, alpha=0.6)
    plt.tick_params(labelsize=13)
    plt.legend(frameon=True, framealpha=1, edgecolor="black", fontsize=11)
    
    plt.tight_layout()
    
    
    
    plt.savefig("effect_of_n.pdf", format="pdf", bbox_inches="tight")
    
    
    plt.show()
    
    
def effect_temp():
    
    
    # ---------- temperature values ----------
    temps = [0.2, 0.5, 0.7, 0.9]
    
    # # ---------- accuracy data ---------------
    # wo      = [53.70, 61.37, 58.08, 59.73]  # baseline (no trace)
    # exe     = [55.34, 59.45, 57.81, 58.08]  # CODEEXECUTOR
    # concise = [57.81, 58.08, 58.08, 58.36]  # CONCISETRACE
    # next_   = [56.44, 56.16, 60.27, 56.71]  # NEXT
    # semc    = [56.44, 56.44, 59.45, 60.27]  # OUR01
    #

    # ---------- accuracy data ---------------
    wo      = [60.00, 61.37, 58.08, 59.73]  # baseline (no trace)
    concise = [56.44, 58.08, 58.08, 58.36]  # CONCISETRACE
    next_   = [57.26, 56.16, 60.27, 56.71]  # NEXT
    semc    = [57.53, 56.44, 59.45, 60.27]  # OUR01
    exe     = [55.34, 59.45, 57.81, 58.08]  # CODEEXECUTOR
    
    # ---------- palette ---------------------
    COLORS = {
        "wo"     : "#003C8F",
        "exe"    : "#E1AD01",
        "concise": "#004B3C",
        "next"   : "#808080",
        "semc"   : "#74258C",
    }
    
    plt.figure(figsize=(6.4, 5.2), dpi=150)
    
    plt.plot(temps, wo,      color=COLORS["wo"],      marker="o", lw=1.5, ms=5, label="w/o trace")
    plt.plot(temps, exe,     color=COLORS["exe"],     marker="o", lw=1.5, ms=5, label="CodeExecutor")
    plt.plot(temps, concise, color=COLORS["concise"], marker="o", lw=1.5, ms=5, label="Concise")
    plt.plot(temps, next_,   color=COLORS["next"],    marker="o", lw=1.5, ms=5, label="NExT")
    plt.plot(temps, semc,    color=COLORS["semc"],    marker="o", lw=1.5, ms=5, label="SemCoder")
    
    # ---------- styling ---------------------
    plt.title("Effect of Temperature (n = 16)", fontsize=22)
    plt.xlabel("Temperature", fontsize=16)
    plt.ylabel("Pass@1", fontsize=16)
    
    plt.xticks(temps, temps)
    plt.grid(color="lightgray", linestyle="--", linewidth=0.7, alpha=0.6)
    plt.tick_params(labelsize=13)
    plt.legend(frameon=True, framealpha=1, edgecolor="black", fontsize=11)
    
    plt.tight_layout()

    plt.savefig("effect_of_temp.pdf", format="pdf", bbox_inches="tight")

    plt.show()



def peft():


    # --------------------------------------------------------------------
    # ❶ Put your numbers here ------------------------------------------------
    #    Each entry:  {backbone: (Full, LoRA64, LoRA8)}
    scores = {
        "only NL2Code & Reasoning": {
            "DeepSeek-Coder": (72.9, 73.2, 73.3),
            "LLaMA":          (73.7, 58.9, 52.1),
            "Gemma2":         (61.4, 59.4, 66.9),
        },
        "w/o trace": {
            "DeepSeek-Coder": (75.9, 70.7, 71.2),
            "LLaMA":          (59.4, 61.7, 57.5),
            "Gemma2":         (66.9, 67.2, 59.4),
        },
        "Concise": {
            "DeepSeek-Coder": (74.4, 71.4, 71.4),
            "LLaMA":          (59.4, 60.4, 61.2),
            "Gemma2":         (66.9, 67.9, 60.2),
        },
        "NExT": {
            "DeepSeek-Coder": (76.7, 70.4, 71.4),
            "LLaMA":          (61.4, 62.2, 59.6),
            "Gemma2":         (58.1, 66.2, 67.2),
        },
        "CodeExecutor": {
            "DeepSeek-Coder": (77.2, 72.2, 70.4),
            "LLaMA":          (59.4, 60.4, 60.9),
            "Gemma2":         (64.7, 66.2, 59.4),
        },
        # "Semcoder" example (uncomment if you want six panels)
        # "Semcoder (GPT-4o)": {
        #     "DeepSeek-Coder": (75.7, 69.7, 70.4),
        #     "LLaMA":          (59.4, 59.9, 54.9),
        #     "Gemma2":         (62.9, 66.9, 67.7),
        # },
    }
    # --------------------------------------------------------------------
    
    backbones  = ["DeepSeek-Coder", "LLaMA", "Gemma2"]
    schemes    = ["Full", "LoRA64", "LoRA8"]
    colors     = ["#C0C0C0", "#86C366", "#E8899E"]   # grey, green, red-pink
    width      = 0.22                                # bar width
    
    n_panels   = len(scores)
    n_cols     = 3                                   # 2×3 grid
    n_rows     = int(np.ceil(n_panels / n_cols))
    
    fig, axes  = plt.subplots(n_rows, n_cols,
                              figsize=(12, 6.5),
                              sharey=True)           # same y-axis across panels
    axes       = axes.flatten()
    
    for idx, (title, tbl) in enumerate(scores.items()):
        ax = axes[idx]
    
        # X positions for three backbones
        x = np.arange(len(backbones))
        for i, scheme in enumerate(schemes):
            vals = [tbl[b][i] for b in backbones]
            ax.bar(x + (i-1)*width, vals,
                   width=width, color=colors[i], label=scheme)
    
        ax.set_xticks(x, backbones, fontsize=9)
        ax.set_ylim(0, 100)
        ax.set_title(f"({chr(97+idx)}) {title}", fontsize=12, pad=8)
    
        # “side line” separators between backbones
        for xc in (x[0]+0.5, x[1]+0.5):
            ax.axvline(xc, color="black", lw=0.5, alpha=.4)
    
        # Tiny error-bar style ticks on each bar top (optional)
        for bar in ax.patches:
            ax.plot([bar.get_x()+bar.get_width()/2]*2,
                    [bar.get_height()-0.3, bar.get_height()+0.3],
                    color="black", lw=0.5)
    
    # Hide any unused subplot slots
    for j in range(idx+1, len(axes)):
        axes[j].axis("off")
    
    # One shared legend
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", ncol=3, frameon=False, fontsize=11)
    
    fig.suptitle("Fine-tuning Accuracy under Different Training Regimes",
                 fontsize=14, y=0.96)
    
    fig.text(0.5, 0.04,
             "LLM Backbone",
             ha="center", fontsize=12)
    fig.text(0.04, 0.5,
             "Pass@k (%)",
             va="center", rotation="vertical", fontsize=12)
    
    fig.tight_layout(rect=[0.03, 0.08, 0.97, 0.90])
    plt.savefig("peft.pdf", format="pdf", bbox_inches="tight")
    plt.show()


def peft2():
    from matplotlib.patches import Patch
    
    # ---------------- data ------------------------------------------------
    scores = {
        "NL2Code\n+Reasoning": {
            "DeepSeek-Coder": (72.9, 73.2, 73.3),
            "LLaMA":          (73.7, 58.9, 52.1),
            "Gemma2":         (61.4, 59.4, 66.9),
        },
        "w/o\ntrace": {
            "DeepSeek-Coder": (75.9, 70.7, 71.2),
            "LLaMA":          (59.4, 61.7, 57.5),
            "Gemma2":         (66.9, 67.2, 59.4),
        },
        "Concise": {
            "DeepSeek-Coder": (74.4, 71.4, 71.4),
            "LLaMA":          (59.4, 60.4, 61.2),
            "Gemma2":         (66.9, 67.9, 60.2),
        },
        "NExT": {
            "DeepSeek-Coder": (76.7, 70.4, 71.4),
            "LLaMA":          (61.4, 62.2, 59.6),
            "Gemma2":         (58.1, 66.2, 67.2),
        },
        "Code\nExecutor": {
            "DeepSeek-Coder": (77.2, 72.2, 70.4),
            "LLaMA":          (59.4, 60.4, 60.9),
            "Gemma2":         (64.7, 66.2, 59.4),
        },
        "SemCoder": {
            "DeepSeek-Coder": (75.7, 69.7, 70.4),
            "LLaMA":          (59.4, 59.9, 54.9),
            "Gemma2":         (62.9, 66.9, 67.7),
        },
    }
    
    methods   = list(scores.keys())
    backbones = ["DeepSeek-Coder", "LLaMA", "Gemma2"]
    schemes   = ["Full", "LoRA64", "LoRA8"]
    
    # pastel colours for training schemes
    scheme_colors = {
        "Full"  : "#c6dbef",  # light blue
        "LoRA64": "#fdd9b5",  # light orange
        "LoRA8" : "#c6e9c6",  # light green
    }
    
    # scheme_colors = {
    #     "Full": "#cccccc",  # light orange
    #     "LoRA64"  : "#7ccd7c",  # light blue
    #     "LoRA8" : "#eea2ad",  # light green
    # }
    
    
    # hatches for backbones
    backbone_hatches = {
        "DeepSeek-Coder": "",
        "LLaMA":          "//",
        "Gemma2":         "xx",
    }
    
    width = 0.22
    gap   = 1.0
    
    fig, ax = plt.subplots(figsize=(9.5, 4))
    
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

    for m_idx, m in enumerate(methods):
        base_x = m_idx * (len(backbones) + gap)
        for b_idx, backbone in enumerate(backbones):
            vals = scores[m][backbone]
            best_idx = int(np.argmax(vals))
            for s_idx, scheme in enumerate(schemes):
                x = base_x + b_idx + (s_idx - 1) * width
                y = vals[s_idx]
                bar = ax.bar(
                    x, y, width,
                    color=scheme_colors[scheme],
                    edgecolor="black",
                    hatch=backbone_hatches[backbone],
                    linewidth=0.8
                )
                # label only the best bar
                # if s_idx == best_idx:
                #     ax.text(x, y + 0.5, f"{y:.1f}", ha='center', va='bottom', fontsize=8)
    
    # x‑ticks
    centres = [i*(len(backbones)+gap) + (len(backbones)-1)/2 for i in range(len(methods))]
    ax.set_xticks(centres, methods, fontsize=9)
    
    ax.set_ylabel("Pass@k (%)", fontsize=11)
    ax.set_ylim(40, 100)          # cut off below 40
    # ax.set_title("Fine‑tuning Pass@1 (>40%) with Best Scores Highlighted", fontsize=12, pad=6)
    
    # baseline and separators
    ax.axhline(40, color='grey', lw=0.8)
    for g in range(1, len(methods)):
        ax.axvline(g*(len(backbones)+gap)-0.5, color='grey', lw=0.4, alpha=0.3)
    
    # # legends
    # scheme_handles   = [Patch(facecolor=scheme_colors[s], edgecolor='black', label=s) for s in schemes]
    # backbone_handles = [Patch(facecolor='white', edgecolor='black',
    #                           hatch=backbone_hatches[b], label=b) for b in backbones]
    #
    # leg1 = ax.legend(handles=scheme_handles, title="Training scheme",
    #                  loc='upper left', bbox_to_anchor=(1.02, 1))
    # leg2 = ax.legend(handles=backbone_handles, title="Backbone",
    #                  loc='lower left', bbox_to_anchor=(1.02, 0))
    # ax.add_artist(leg1)
    #

    
    
    # legends –– more compact
    scheme_handles = [
        Patch(facecolor=scheme_colors[s], edgecolor='black', label=s) for s in schemes
    ]
    backbone_handles = [
        Patch(facecolor='white', edgecolor='black',
              hatch=backbone_hatches[b], label=b) for b in backbones
    ]
    
    # compact legend style parameters
    LEG_KW = dict(
        fontsize=8,          # smaller text
        title_fontsize=8,
        frameon=False,       # no border
        handlelength=1.2,    # shorter legend handles
        handletextpad=0.4,
        borderpad=0.3,
        labelspacing=0.3,
    )
    
    # place both legends *inside* the plot area (upper-left & lower-left corners)
    leg1 = ax.legend(
        handles=scheme_handles, title="Training scheme",
    bbox_to_anchor=(0.01, 0.85),  # Lowered from top

        loc="upper left", **LEG_KW
    )
    leg2 = ax.legend(
        handles=backbone_handles, title="Backbone",
    bbox_to_anchor=(0.99, 0.85),  # Lowered from top
        loc="upper right", **LEG_KW
    )
    ax.add_artist(leg1)  # keep both legends




    fig.tight_layout()
    plt.show()
    plt.savefig("peft2.pdf", format="pdf", bbox_inches="tight")
    plt.show()


def show_gain_testcase_increase ():
    
    
    
    # --- Data -----------------------------------------------------------
    sizes = ["Two testcases", "Three testcases"]
    methods = ["CodeExecutor", "ConCise", "NExT", "SemCoder"]
    variants = ["base", "plus"]
    
    data = np.array([
        [ 0.6,  1.4, -1.1,  0.0,  0.0,  0.9, -0.3,  0.6],   # size 2
        [ 0.3,  0.6, -3.1, -1.0, -7.9, -4.0,  0.8,  1.4]    # size 3
    ])
    
    # --- Plot with smaller fonts -----------------------------------------------------------
    plt.rcParams.update({"font.size": 9})  # globally smaller
    
    fig, ax = plt.subplots(figsize=(9, 2.8))
    im = ax.imshow(data, aspect="auto", cmap="coolwarm")
    
    # Primary x-ticks (variant labels)
    xtick_positions = np.arange(data.shape[1])
    ax.set_xticks(xtick_positions, variants * len(methods))
    ax.tick_params(axis='x', labelsize=8)
    ax.tick_params(axis='y', labelsize=8)
    
    # y-ticks (sizes)
    ax.set_yticks(np.arange(len(sizes)), sizes)
    
    # Group boundaries
    for boundary in np.arange(2, data.shape[1], 2):
        ax.axvline(boundary - 0.5, color="black", linewidth=0.4)
    
    # Secondary x-axis for method names
    secax = ax.secondary_xaxis('top')
    group_centers = np.arange(0.5, data.shape[1], 2)
    secax.set_xticks(group_centers, methods)
    secax.tick_params(axis='x', labelsize=9)
    
    # Title and colorbar
    ax.set_title("Percentage-point Gain vs. Baseline (1 testcase)", fontsize=11)
    cbar = fig.colorbar(im, ax=ax, shrink=0.75, label="Gain (pp)")
    cbar.ax.tick_params(labelsize=8)
    cbar.set_label("Gain (pp)", fontsize=9)
    
    plt.tight_layout()


    plt.savefig("gain.pdf", format="pdf", bbox_inches="tight")
    plt.show()

    #
    # # --- Data -----------------------------------------------------------
    # sizes = ["two testcases", "three testcases"]
    # methods = ["CodeExecutor", "ConCise", "NExT", "SemCoder"]
    # variants = ["base", "plus"]
    #
    # # gains organized as [size, method*variant]
    # data = np.array([
    #     [ 0.6,  1.4, -1.1,  0.0,  0.0,  0.9, -0.3,  0.6],   # size 2
    #     [ 0.3,  0.6, -3.1, -1.0, -7.9, -4.0,  0.8,  1.4]    # size 3
    # ])
    #
    # # --- Plot -----------------------------------------------------------
    # fig, ax = plt.subplots(figsize=(9, 2.8))
    # im = ax.imshow(data, aspect="auto", cmap="coolwarm")
    #
    # # Primary x-ticks for variant labels
    # xtick_positions = np.arange(data.shape[1])
    # variant_labels = variants * len(methods)  # ['base','plus','base','plus',...]
    # ax.set_xticks(xtick_positions, variant_labels, rotation=0)
    #
    # # y-ticks for sizes
    # ax.set_yticks(np.arange(len(sizes)), sizes)
    #
    # # Optional grid-like separators between method groups
    # for boundary in np.arange(2, data.shape[1], 2):
    #     ax.axvline(boundary - 0.5, color="black", linewidth=0.5)
    #
    # # Secondary x-axis for grouped method names
    # secax = ax.secondary_xaxis('top')
    # group_centers = np.arange(0.5, data.shape[1], 2)
    # secax.set_xticks(group_centers, methods)
    #
    # # Titles & colorbar
    # ax.set_title("Percentage-point Gain vs. Baseline (trace on one testcase).")
    # fig.colorbar(im, ax=ax, shrink=0.75, label="Gain (pp)")
    #
    # plt.tight_layout()
    
import io
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

import numpy as np 

import pandas as pd
import matplotlib.pyplot as plt
import io
import numpy as np
from matplotlib.patches import Patch
from matplotlib.lines import Line2D



def effect_temp_n_in_one():
    csv_text="""
temp,trace,model,diff,n,acc
temp02,,qwen7b,easy,1,0.46153846153846156
temp02,,qwen7b,easy,16,0.7692307692307693
temp02,,qwen7b,easy,32,0.7307692307692307
temp02,,qwen7b,easy,8,0.5769230769230769
temp02,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,1,0.46153846153846156
temp02,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,16,0.6923076923076923
temp02,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,32,0.7692307692307693
temp02,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,8,0.7692307692307693
temp02,bug_trace_TPL_CONCISETRACE,qwen7b,easy,1,0.46153846153846156
temp02,bug_trace_TPL_CONCISETRACE,qwen7b,easy,16,0.6923076923076923
temp02,bug_trace_TPL_CONCISETRACE,qwen7b,easy,32,0.7307692307692307
temp02,bug_trace_TPL_CONCISETRACE,qwen7b,easy,8,0.6153846153846154
temp02,bug_trace_TPL_NEXT,qwen7b,easy,1,0.46153846153846156
temp02,bug_trace_TPL_NEXT,qwen7b,easy,16,0.7307692307692307
temp02,bug_trace_TPL_NEXT,qwen7b,easy,32,0.7692307692307693
temp02,bug_trace_TPL_NEXT,qwen7b,easy,8,0.7307692307692307
temp02,bug_trace_TPL_OUR01,qwen7b,easy,1,0.46153846153846156
temp02,bug_trace_TPL_OUR01,qwen7b,easy,16,0.6923076923076923
temp02,bug_trace_TPL_OUR01,qwen7b,easy,32,0.7307692307692307
temp02,bug_trace_TPL_OUR01,qwen7b,easy,8,0.6538461538461539
temp05,,qwen7b,easy,1,0.3076923076923077
temp05,,qwen7b,easy,16,0.7307692307692307
temp05,,qwen7b,easy,32,0.8076923076923077
temp05,,qwen7b,easy,8,0.6923076923076923
temp05,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,1,0.23076923076923078
temp05,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,16,0.7692307692307693
temp05,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,32,0.6538461538461539
temp05,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,8,0.7307692307692307
temp05,bug_trace_TPL_CONCISETRACE,qwen7b,easy,1,0.3076923076923077
temp05,bug_trace_TPL_CONCISETRACE,qwen7b,easy,16,0.6923076923076923
temp05,bug_trace_TPL_CONCISETRACE,qwen7b,easy,32,0.8461538461538461
temp05,bug_trace_TPL_CONCISETRACE,qwen7b,easy,8,0.8076923076923077
temp05,bug_trace_TPL_NEXT,qwen7b,easy,1,0.38461538461538464
temp05,bug_trace_TPL_NEXT,qwen7b,easy,16,0.7307692307692307
temp05,bug_trace_TPL_NEXT,qwen7b,easy,32,0.7307692307692307
temp05,bug_trace_TPL_NEXT,qwen7b,easy,8,0.6923076923076923
temp05,bug_trace_TPL_OUR01,qwen7b,easy,1,0.4230769230769231
temp05,bug_trace_TPL_OUR01,qwen7b,easy,16,0.7307692307692307
temp05,bug_trace_TPL_OUR01,qwen7b,easy,32,0.7692307692307693
temp05,bug_trace_TPL_OUR01,qwen7b,easy,8,0.7307692307692307
temp09,,qwen7b,easy,1,0.4230769230769231
temp09,,qwen7b,easy,16,0.8076923076923077
temp09,,qwen7b,easy,32,0.8076923076923077
temp09,,qwen7b,easy,8,0.6923076923076923
temp09,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,1,0.3076923076923077
temp09,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,16,0.7307692307692307
temp09,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,32,0.8846153846153846
temp09,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,8,0.6538461538461539
temp09,bug_trace_TPL_CONCISETRACE,qwen7b,easy,1,0.38461538461538464
temp09,bug_trace_TPL_CONCISETRACE,qwen7b,easy,16,0.8076923076923077
temp09,bug_trace_TPL_CONCISETRACE,qwen7b,easy,32,0.8461538461538461
temp09,bug_trace_TPL_CONCISETRACE,qwen7b,easy,8,0.7307692307692307
temp09,bug_trace_TPL_NEXT,qwen7b,easy,1,0.34615384615384615
temp09,bug_trace_TPL_NEXT,qwen7b,easy,16,0.7692307692307693
temp09,bug_trace_TPL_NEXT,qwen7b,easy,32,0.8846153846153846
temp09,bug_trace_TPL_NEXT,qwen7b,easy,8,0.7692307692307693
temp09,bug_trace_TPL_OUR01,qwen7b,easy,1,0.34615384615384615
temp09,bug_trace_TPL_OUR01,qwen7b,easy,16,0.8076923076923077
temp09,bug_trace_TPL_OUR01,qwen7b,easy,32,0.8461538461538461
temp09,bug_trace_TPL_OUR01,qwen7b,easy,8,0.6538461538461539
vanilla,,qwen7b,easy,1,0.38461538461538464
vanilla,,qwen7b,easy,16,0.7307692307692307
vanilla,,qwen7b,easy,32,0.7692307692307693
vanilla,,qwen7b,easy,8,0.7307692307692307
vanilla,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,1,0.5384615384615384
vanilla,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,16,0.8076923076923077
vanilla,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,32,0.8461538461538461
vanilla,bug_trace_TPL_CODEEXECUTOR,qwen7b,easy,8,0.7692307692307693
vanilla,bug_trace_TPL_CONCISETRACE,qwen7b,easy,1,0.4230769230769231
vanilla,bug_trace_TPL_CONCISETRACE,qwen7b,easy,16,0.7307692307692307
vanilla,bug_trace_TPL_CONCISETRACE,qwen7b,easy,32,0.7307692307692307
vanilla,bug_trace_TPL_CONCISETRACE,qwen7b,easy,8,0.6538461538461539
vanilla,bug_trace_TPL_NEXT,qwen7b,easy,1,0.38461538461538464
vanilla,bug_trace_TPL_NEXT,qwen7b,easy,16,0.8461538461538461
vanilla,bug_trace_TPL_NEXT,qwen7b,easy,32,0.7307692307692307
vanilla,bug_trace_TPL_NEXT,qwen7b,easy,8,0.7307692307692307
vanilla,bug_trace_TPL_OUR01,qwen7b,easy,1,0.46153846153846156
vanilla,bug_trace_TPL_OUR01,qwen7b,easy,16,0.6923076923076923
vanilla,bug_trace_TPL_OUR01,qwen7b,easy,32,0.8846153846153846
vanilla,bug_trace_TPL_OUR01,qwen7b,easy,8,0.6923076923076923
"""

    

    df = pd.read_csv(io.StringIO(csv_text))
    
    # normalise trace & temperature
    df['trace'] = (df['trace'].fillna('wo')
                   .str.replace('bug_trace_TPL_', '', regex=False))
    temp_map = {'temp02': 0.2, 'temp05': 0.5, 'temp09': 0.9, 'vanilla': 0.7}
    df['temp'] = df['temp'].map(temp_map)
    
    # nice labels
    nice = {'wo':'w/o trace', 'CONCISETRACE':'Concise',
            'NEXT':'NExT',    'CODEEXECUTOR':'CodeExec', 'OUR01':'Semcoder'}
    trace_order = [t for t in nice if t in df['trace'].unique()]
    
    # ── Scientific color scheme with light colors ───────────────────────────
    scheme_colors = {
        1:  "#c1e7ff",  # light blue
        8:  "#ffdac1",  # light peach
        16: "#d5f0c1",  # light green
        32: "#e6d6ff",  # light purple
    }
    
    # Line colors - using a professional scientific color palette
    line_colors = {
        0.2: "#1f77b4",  # blue
        0.5: "#ff7f0e",  # orange
        0.7: "#2ca02c",  # green
        0.9: "#9467bd",  # purple
    }
    
    # ── data pivots ──────────────────────────────────────────────────────
    bars  = (df[df['temp']==0.7]
             .pivot(index='trace', columns='n', values='acc')
             .reindex(trace_order))
    lines = (df[df['n']==16]
             .pivot(index='trace', columns='temp', values='acc')
             .reindex(trace_order))
    
    # ── plot with improved styling ─────────────────────────────────────────
    plt.style.use('seaborn-v0_8-whitegrid')  # Clean scientific style
    fig, ax = plt.subplots(figsize=(7, 4.5))
    
    x      = np.arange(len(trace_order))
    bar_w  = 0.18
    n_vals = sorted(bars.columns)         # [1, 8, 16, 32]
    t_vals = sorted(lines.columns)        # [0.2, 0.5, 0.7, 0.9]
    marker = {0.2:'o', 0.5:'s', 0.7:'^', 0.9:'D'}
    
    # coloured bars with better styling
    for i, n in enumerate(n_vals):
        xpos = x + (i-1.5)*bar_w
        ax.bar(
            xpos, bars[n]*100, bar_w,
            color=scheme_colors[n],
            edgecolor='dimgrey', linewidth=0.7,
            label=f"n={n}" if i==0 else None,
            alpha=0.9
        )
    
    # colored lines for temperatures instead of all black
    for t in t_vals:
        ax.plot(
            x, lines[t]*100,
            color=line_colors[t], lw=1.4, marker=marker[t], markersize=7,
            markeredgecolor='white', markeredgewidth=0.5,
            label=f"T={t}" if t==t_vals[0] else None
        )
    
    # axes & cosmetics
    ax.set_xticks(x)
    ax.set_xticklabels([nice[t] for t in trace_order], fontsize=10)
    ax.set_ylabel('Pass@1 (%)', fontsize=11)
    ax.set_ylim(20, 95)
    # ax.set_title('Accuracy vs Trace Method', fontsize=13, pad=10)
    ax.text(0.5, -0.15, '(bars = N-sampled completions, lines = temperature)', 
            transform=ax.transAxes, ha='center', fontsize=10, style='italic')
    
    # Grid styling
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    for spine in ('top', 'right'):
        ax.spines[spine].set_visible(False)
    
    # combined legend with better formatting
    bar_handles = [Patch(facecolor=scheme_colors[n], edgecolor='dimgrey', 
                        label=f"N={n}", alpha=0.9) for n in n_vals]
    line_handles = [Line2D([0],[0], color=line_colors[t], marker=marker[t], 
                          lw=1.4, label=f"T={t}", markeredgecolor='white', 
                          markeredgewidth=0.5) for t in t_vals]
    
    # Create two separate legends
    ax.legend(handles=bar_handles, loc='upper left', frameon=True, 
              fontsize=9, ncol=2, title="N-samples", 
              framealpha=0.7, title_fontsize=10)
    
    ax.legend(handles=line_handles, loc='upper right', frameon=True, 
              fontsize=9, ncol=2, title="Temperature", 
              framealpha=0.7, title_fontsize=10)
    
    # Add both legends
    first_legend = ax.legend(handles=bar_handles, loc='upper left', frameon=True, 
                            fontsize=9, ncol=2, title="N-samples", 
                            framealpha=0.7, title_fontsize=10)
    ax.add_artist(first_legend)
    ax.legend(handles=line_handles, loc='upper right', frameon=True, 
              fontsize=9, ncol=2, title="Temperature", 
              framealpha=0.7, title_fontsize=10)
    
    plt.tight_layout()
    plt.savefig('trace_temp_n_combined.pdf', bbox_inches='tight', dpi=300)
    plt.show()




def show_gain_testcase_increase():
    # --- Data -----------------------------------------------------------
    sizes = ["Two testcases", "Three testcases"]
    methods = ["CodeExecutor", "ConCise", "NExT", "SemCoder"]
    variants = ["base", "plus"]
    
    # Original data
    original_data = np.array([
        [ 0.6,  1.4, -1.1,  0.0,  0.0,  0.9, -0.3,  0.6],   # size 2
        [ 0.3,  0.6, -3.1, -1.0, -7.9, -4.0,  0.8,  1.4]    # size 3
    ])
    
    # Transpose the data to swap rows and columns
    data = original_data.T  # Now method/variant pairs will be rows, sizes will be columns
    
    # --- Plot with transposed data -------------------
    plt.rcParams.update({"font.size": 12})
    
    # Wider figure to accommodate the transposed data
    fig, ax = plt.subplots(figsize=(6, 8))
    
    im = ax.imshow(data, aspect="auto", cmap="coolwarm", interpolation='nearest')
    
    # Now y-axis contains method+variant combinations
    method_variant_labels = []
    for method in methods:
        for variant in variants:
            method_variant_labels.append(f"{method} ({variant})")
    
    # Y-ticks for method+variant combinations
    ax.set_yticks(np.arange(data.shape[0]))
    ax.set_yticklabels(method_variant_labels, fontsize=11)
    
    # X-ticks for sizes (formerly rows, now columns)
    ax.set_xticks(np.arange(data.shape[1]))
    ax.set_xticklabels(sizes, fontsize=13)
    
    # Group boundaries for methods (every 2 rows)
    for boundary in np.arange(2, data.shape[0], 2):
        ax.axhline(boundary - 0.5, color="black", linewidth=0.8)
    
    # Add values in each cell
    for i in range(data.shape[0]):
        for j in range(data.shape[1]):
            value = data[i, j]
            # Choose text color based on background darkness
            text_color = 'white' if abs(value) > 3 else 'black'
            ax.text(j, i, f"{value:.1f}", ha="center", va="center", 
                   fontsize=11, color=text_color, fontweight='bold')
    
    # Title with larger font
    ax.set_title("Percentage-point Gain vs. Baseline (1 testcase)", fontsize=14, pad=10)
    
    # Colorbar with adjusted positioning for vertical layout
    cax = fig.add_axes([0.93, 0.15, 0.02, 0.7])
    cbar = fig.colorbar(im, cax=cax)
    cbar.ax.tick_params(labelsize=11)
    cbar.set_label("Gain (pp)", fontsize=12, labelpad=10)
    
    plt.tight_layout(rect=[0, 0, 0.91, 1])
    plt.savefig("gain.pdf", format="pdf", bbox_inches="tight", dpi=300)
    plt.show()
    
    
    
if __name__=="__main__":
    # effect_temp()
    
    # peft()    
    # peft2()
    show_gain_testcase_increase()
    
    # effect_temp_n_in_one()