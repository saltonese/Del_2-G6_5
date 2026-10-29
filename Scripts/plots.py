
import matplotlib.pyplot as plt #used to plot graphs
from Task_5 import results

#Before and after glitches and NOK correction
fig, axes = plt.subplots(1, 2, figsize=(13, 4), sharex=True)
colors = {"EUR": "tab:blue", "NOK": "tab:red", "USD": "tab:green"}

for ax, frame, title in [(axes[0], results["raw_df"], "Raw prices (with glitches)"),
                         (axes[1], results["clean_df"], "After outlier removal + NOK correction")]:
    for currency, group in frame.groupby("currency"):
        ax.scatter(group.index, group["price"], s=12, alpha=0.6, label=currency, color=colors[currency])
    ax.set_title(title)
    ax.set_xlabel("time")
    ax.legend(title="currency")
axes[0].set_ylabel("price")
fig.autofmt_xdate()
plt.tight_layout()
plt.show()



# revenue overview and refund ratio
fig, axes = plt.subplots(1, 2, figsize=(13, 4))

results["pivot"].plot(kind="bar", ax=axes[0], width=0.8)
axes[0].set_title("Revenue per item by status")
axes[0].set_ylabel("revenue (mixed currencies)")
axes[0].tick_params(axis="x", rotation=30)

results["ratios"]["refund_ratio"].plot(kind="bar", ax=axes[1], color="tab:orange")
axes[1].axhline(0.25, color="black", linestyle="--", linewidth=1, label="expected 0.25")
axes[1].set_title("Refund ratio per item")
axes[1].set_ylabel("refunds / (sales + ε)")
axes[1].tick_params(axis="x", rotation=30)
axes[1].legend()

plt.tight_layout()
plt.show()