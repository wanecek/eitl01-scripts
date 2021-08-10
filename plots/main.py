#!/usr/bin/env python

import argparse
import os
import sys

from cycler import cycler
import matplotlib.pyplot as plt
import pandas as pd

DEFAULT_OUTPUT_DIR = "./figures"

PATHS = {
    "POWER_READINGS": "data/cpu-ram.csv",
    "NETWORK_TRAFFIC_DAILY": "data/network-traffic.csv",
    "NETWORK_TRAFFIC_FIVEMINUTE": "data/network-traffic-5m.csv",
    "TOP_STATS": "data/top-stats.csv",
    "LEDGER_ACTIVITY": "data/ledger/ledger-activity.csv",
}

"""
Load CSV-file as dataframe, with the first column (timestamps) as index
"""
def read_csv(filepath):
    return pd.read_csv(filepath, index_col=0, parse_dates=["timestamp"])


def gbToW(gb, hours):
    GB_TO_KWH = 0.06
    return gb * GB_TO_KWH * 1000 / hours


"""
Plot network traffic as x=time vs y=(GB, W) (double axes)
"""
def plot_network_traffic(network_df, output_dir, enddate="2021-06-01"):
    startdate = "2021-05-14"

    fig, ax1 = plt.subplots()
    df = network_df.loc[startdate:enddate] * 1e-9

    # Duplicate axis for power consumption on the right
    ax2 = ax1.twinx()

    ax1.set_title("Network traffic to and from node per day")
    ax1.set_ylabel("Data (GB)")
    ax2.set_ylabel("Power (W)")

    df.plot(kind="line", ax=ax1, xlabel="")
    fig.tight_layout()

    ax1.set_ylim([0, None])

    mn, mx = ax1.get_ylim()
    ax2.set_ylim(gbToW(mn, 24), gbToW(mx, 24))

    ax1.set_xlim([startdate, enddate])

    fig.savefig(os.path.join(output_dir, "network-traffic.pdf"))


"""
Plot RAPL readings
"""
def plot_rapl_readings(df, output_dir):
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(6, 6))

    df.drop(columns=["RAM"]).plot(kind="line", ax=ax2, xlabel="")
    df = df.resample("1h").mean()
    df.plot(kind="line", ax=ax1, xlabel="")

    ax1.set_title("Power consumption from RAPL measurements")
    ax1.set_ylabel("Power, hourly average (W)")
    ax2.set_ylabel("Power (W)")

    for ax in [ax1, ax2]:
        ax.set_ylim([0, None])
        ax.set_xlim(["2021-05-14", "2021-06-01"])

    fig.tight_layout()
    fig.savefig(os.path.join(output_dir, "rapl-readings.pdf"))


"""
Print LaTeX table for RAPL measurements
"""
def print_rapl_table(df):
    mu = df.mean()
    q = df.quantile([0.1, 0.9])
    thead = " " * 14 + " & CPU     & RAM\\\\\\toprule\n"
    tbody = ""
    tbody += "10~\\%% quantile & %.3f W & %.3f W \\\\\n" % (q.at[0.1, "CPU"], q.at[0.1, "RAM"])
    tbody += "Mean           & %.3f W & %.3f W \\\\\n" % (mu["CPU"], mu["RAM"])
    tbody += "90~\\%% quantile & %.3f W & %.3f W \\\\\\bottomrule\n" % (
        q.at[0.9, "CPU"],
        q.at[0.9, "RAM"],
    )

    print("\n" + thead + tbody + "\n")


"""
Plot 4x1 subplots with rapl measurements and associated factors
"""
def plot_rapl_with_others(rapl_df, sysstat_df, activity_df, network_df, output_dir):
    fig, (ax1, ax2, ax3, ax4) = plt.subplots(4, 1, figsize=(5, 5))
    # fig.figsize = (4, 6)
    fig.tight_layout(h_pad=3)
    fig.subplots_adjust(left=0.12)

    startdate = "2021-05-23"
    enddate = "2021-06-01"

    df1 = rapl_df.resample("1h").mean().loc[startdate:enddate]
    df_sysstat = sysstat_df.resample("1h").mean().loc[startdate:enddate]

    df_sysstat["Stellar CPU%"] = df_sysstat["Stellar CPU%"] / 8
    df_sysstat["PGSQL CPU%"] = df_sysstat["PGSQL CPU%"] / 8

    ax1.set_title("RAPL power readings (W)")
    df1.plot(kind="line", ax=ax1, xlabel="")

    ax2.set_title("System resource usage (\\%)")
    df2 = df_sysstat[["CPU US", "CPU SY", "Stellar CPU%", "PGSQL CPU%"]]
    df2.columns = ["CPU, User", "CPU, System", "stellar-core CPU\\%", "postgres CPU\\%"]
    df2.plot(kind="line", ax=ax2, xlabel="")

    ax3.set_title("Payment network activity per consensus round")
    df3 = activity_df.resample("1h").mean().loc[startdate:enddate]
    df3.columns = ["Operations", "Successful txs", "Failed txs"]
    df3.plot(kind="line", ax=ax3, xlabel="")

    ax4.set_title("Network power consumption estimate (W)")
    df4 = gbToW(network_df.loc[startdate:enddate].copy() * 1e-9, 1)
    df4.plot(kind="line", ax=ax4, xlabel="")

    for ax in (ax1, ax2, ax3, ax4):
        ax.set_ylim([0, None])
        ax.set_xlim([startdate, enddate])
        ax.legend(bbox_to_anchor=(1, 1), loc="upper left", frameon=False, borderpad=0)

    fig.savefig(os.path.join(output_dir, "rapl-vs-sysstat.pdf"))


def plot_cpu_vs_ops(rapl_df, activity_df, pue, output_dir):
    fig, ax = plt.subplots()
    # fig.figsize = (4, 6)
    fig.tight_layout(h_pad=3)
    fig.subplots_adjust(left=0.12)

    startdate = "2021-05-26"
    enddate = "2021-06-01"

    rapl_df = rapl_df.loc[startdate:enddate].resample("1h").mean()

    activity_df = activity_df.loc[startdate:enddate].resample("1h").sum()
    activity_df["txs_tot"] = activity_df["txs"] + activity_df["ftxs"]

    # Add storage (6.5) and multply with PUE (1.67), and then add network
    activity_df["power"] = (rapl_df["CPU"]) * pue

    ax.scatter(
        activity_df["txs"],
        activity_df["power"],
        label="Successul transactions",
        edgecolors="k",
        alpha=0.75,
    )
    ax.scatter(
        activity_df["ftxs"],
        activity_df["power"],
        label="Failed transactions",
        edgecolors="k",
        alpha=0.75,
    )
    ax.scatter(
        activity_df["txs_tot"],
        activity_df["power"],
        label="Total number of transactions",
        marker="D",
        edgecolors="k",
        alpha=0.5,
    )
    ax.scatter(
        activity_df["ops"],
        activity_df["power"],
        label="Successful operations",
        edgecolors="k",
        marker="s",
        alpha=0.5,
    )
    ax.legend()
    ax.set_title(
        "Estimated CPU electricity consumption against hourly payment network activity"
    )
    ax.set_ylabel("Electricity (Wh)")
    ax.set_xlabel("Transactions or operations per hour")
    fig.tight_layout()

    fig.savefig(os.path.join(output_dir, "cpu-vs-transactions.pdf"))


def plot_power_per_transaction(rapl_df, activity_df, network_df, pue, output_dir):
    fig, ax = plt.subplots()
    # fig.figsize = (4, 6)
    fig.tight_layout(h_pad=3)
    fig.subplots_adjust(left=0.12)

    startdate = "2021-05-26"
    enddate = "2021-06-01"

    rapl_df["sum"] = rapl_df["CPU"] + rapl_df["RAM"]
    rapl_df = (
        rapl_df.loc[startdate:enddate]
        .drop(columns=["CPU", "RAM"])
        .resample("1h")
        .mean()
    )

    network_power_df = network_df
    network_power_df["avg"] = (network_power_df["tx"] + network_power_df["rx"]) / 2
    network_power_df = network_power_df.drop(columns=["tx", "rx"])
    network_power_df = gbToW(
        network_df.resample("1h").sum().loc[startdate:enddate] * 1e-9, 1
    )

    activity_df = activity_df.loc[startdate:enddate].resample("1h").sum()
    activity_df["txs_tot"] = activity_df["txs"] + activity_df["ftxs"]

    # Add storage (6.5) and multply with PUE (1.67), and then add network
    activity_df["power"] = (rapl_df["sum"] + 6.5) * pue + network_power_df["avg"]

    ax.scatter(
        activity_df["txs"],
        activity_df["power"],
        label="Successul transactions",
        edgecolors="k",
        alpha=0.75,
    )
    ax.scatter(
        activity_df["ftxs"],
        activity_df["power"],
        label="Failed transactions",
        edgecolors="k",
        alpha=0.75,
    )
    ax.scatter(
        activity_df["txs_tot"],
        activity_df["power"],
        label="Total number of transactions",
        edgecolors="k",
        marker="D",
        alpha=0.5,
    )
    ax.scatter(
        activity_df["ops"],
        activity_df["power"],
        label="Successful operations",
        marker="s",
        edgecolors="k",
        alpha=0.5,
    )
    ax.legend()
    ax.set_title(
        "Estimated electricity consumption against hourly payment network activity"
    )
    ax.set_ylabel("Electricity (Wh)")
    ax.set_xlabel("Transactions or operations per hour")
    fig.tight_layout()

    n_nodes = 132
    avgs = activity_df.copy()
    avgs["avg"] = activity_df["power"] / activity_df["txs_tot"]
    avgs["avg_op"] = activity_df["power"] / activity_df["ops"]
    avgs["avg_txs"] = activity_df["power"] / activity_df["txs"]
    print("\n")
    print("Average per node: %.5f W" % avgs.mean()["avg"])
    print("Average per node (ops): %.5f W" % avgs.mean()["avg_op"])
    print("Average per node (ops): %.5f W" % avgs.mean()["avg_txs"])
    print("Average total: %.3f W" % (n_nodes * avgs.mean()["avg"]))
    print("Average total (ops): %.3f W" % (n_nodes * avgs.mean()["avg_op"]))
    print("Average total (succ): %.3f W" % (n_nodes * avgs.mean()["avg_txs"]))

    fig.savefig(os.path.join(output_dir, "power-vs-transactions.pdf"))


def plot_piegraph(network_traffic, rapl, storage, output_dir):
    network_power = gbToW(network_traffic * 1e-9, 24)
    network_avg_power = (network_power["tx"] + network_power["rx"]) / 2
    network_power_mean = network_avg_power.mean()

    rapl_power_mean = rapl.mean()

    data = {
        "average power": [
            network_power_mean,
            storage,
            rapl_power_mean["CPU"],
            rapl_power_mean["RAM"],
        ],
    }

    total = sum(data["average power"])
    pct = lambda x: 100 * x / total

    fig, ax = plt.subplots()
    ax.set_title("Distribution of mean power consumption between factors")
    columns = [
        ("Network: %1.1f" % pct(network_power_mean)),
        "Storage: %1.1f" % pct(storage),
        "CPU: %1.1f" % pct(rapl_power_mean["CPU"]),
        "RAM: %1.1f" % pct(rapl_power_mean["RAM"]),
    ]

    columns = list(map(lambda s: s + " \\" + "%", columns))
    df = pd.DataFrame(data, index=columns)
    df.plot(
        kind="pie", y="average power", ax=ax, textprops={"color": "w"}, pctdistance=2.8
    )
    ax.set_ylabel("")

    fig.savefig(os.path.join(output_dir, "comparison-pie.pdf"))


def print_summary_table(rapl_df, network_df_raw, storage):
    network_df = gbToW(network_df_raw * 1e-9, 24)
    network_avg = (network_df["rx"] + network_df["tx"]) / 2

    rq = rapl_df.quantile([0.1, 0.9])
    nq = network_avg.quantile([0.1, 0.9])
    rmu = rapl_df.mean()
    nmu = network_avg.mean()
    total = {
        "q10": rq.at[0.1, "CPU"] + rq.at[0.1, "RAM"] + nq.at[0.1] + storage,
        "mean": rmu["CPU"] + rmu["RAM"] + nmu + storage,
        "q90": rq.at[0.9, "CPU"] + rq.at[0.9, "RAM"] + nq.at[0.9] + storage,
    }

    cols = [" " * 14, "CPU    ", "RAM", "Network", "Storage", "Total"]
    rows = [
        "10~\\%% quantile & %.3f W & %.3f W & %.3f W & ---     & %.3f W"
        % (rq.at[0.1, "CPU"], rq.at[0.1, "RAM"], nq.at[0.1], total["q10"]),
        "Mean           & %.3f W & %.3f W & %.3f W & %.3f W & %.3f W"
        % (rmu["CPU"], rmu["RAM"], nmu, storage, total["mean"]),
        "90~\\%% quantile & %.3f W & %.3f W & %.3f W & ---     & %.3f W"
        % (rq.at[0.9, "CPU"], rq.at[0.9, "RAM"], nq.at[0.9], total["q90"]),
    ]

    header = " & ".join(cols) + "\\\\\\toprule\n"
    body = "\\\\\n".join(rows) + "\\\\\\bottomrule\n"

    print(header + body)

def print_total_power_table(rapl_df, network_df_raw, pue, nodes, storage):
    network_df = gbToW(network_df_raw * 1e-9, 24)
    network_avg = (network_df["rx"] + network_df["tx"]) / 2

    rq = rapl_df.quantile([0.1, 0.9]) * pue
    nq = network_avg.quantile([0.1, 0.9])
    rmu = rapl_df.mean() * pue
    nmu = network_avg.mean()
    total = {
        "q10":  pue * (rq.at[0.1, "CPU"] + rq.at[0.1, "RAM"] + storage) + nq.at[0.1],
        "mean": pue * (rmu["CPU"] + rmu["RAM"]) + nmu + 6.5,
        "q90":  pue * (rq.at[0.9, "CPU"] + rq.at[0.9, "RAM"] + storage) + nq.at[0.9],
    }

    create_tuple = lambda x: (x, x * nodes / 1000)

    cols = [" " * 14, "Power per node", "Total power"]
    rows = [
        "10~\\%% quantile & %.3f W & %.3f kW"
        % create_tuple(total["q10"]),
        "Mean           & %.3f W & %.3f kW"
        % create_tuple(total["mean"]),
        "90~\\%% quantile & %.3f W & %.3f kW"
        % create_tuple(total["q90"]),
    ]

    header = " & ".join(cols) + "\\\\\\toprule\n"
    body = "\\\\\n".join(rows) + "\\\\\\bottomrule\n"

    print(header + body)


def patched_network_data(network_d_df, network_t_df):
    network_d_df = network_d_df.loc["2021-05-23":"2021-05-25"] / 24
    network_t_df = network_t_df.loc["2021-05-26":"2021-06-01"].resample("1h").sum()
    return pd.concat([network_d_df, network_t_df])


def get_output_dir(dirpath):
    if not dirpath:
        return DEFAULT_OUTPUT_DIR
    if not os.path.isdir(dirpath):
        return DEFAULT_OUTPUT_DIR
    return dirpath


def setup_mathplotlib():
    plt.style.use(["science", "grid"])
    plt.rcParams["figure.figsize"] = (6, 4)
    colors = [
        "#3E1BDB",
        "#FFB200",
        "#A28FFF",
        "#20BF6B",
        "#FF414A",
        "#BF2175",
        "#474747",
        "#9E9E9E",
    ]
    plt.rcParams.update({"axes.prop_cycle": cycler("color", colors)})


if __name__ == "__main__":
    setup_mathplotlib()

    pue = 1.67

    parser = argparse.ArgumentParser(
        "Main plotting script. Make sure to configure the paths of \
        input-files inside the source-code."
    )

    rapl_readings = read_csv(PATHS["POWER_READINGS"]).drop(columns=["CORE"])
    rapl_readings.columns = ["CPU", "RAM"]
    rapl_readings = rapl_readings.loc["2021-05-13":"2021-06-01"]

    network_traffic_readings = read_csv(PATHS["NETWORK_TRAFFIC_DAILY"])
    network_traffic_5m_readings = read_csv(PATHS["NETWORK_TRAFFIC_FIVEMINUTE"])

    sysstat_readings = read_csv(PATHS["TOP_STATS"])
    ledger_readings = read_csv(PATHS["LEDGER_ACTIVITY"])

    output_dir = get_output_dir(sys.argv[1])

    # Printing rapl table
    print_rapl_table(rapl_readings.copy())
    print_summary_table(rapl_readings.copy(), network_traffic_readings.copy(), 6.5)

    print_total_power_table(
        rapl_df=rapl_readings.copy(),
        network_df_raw=network_traffic_readings.copy(),
        pue=1.67,
        nodes=132,
        storage=6.5)

    plot_cpu_vs_ops(rapl_readings.copy(), ledger_readings.copy(), pue, output_dir)
    plot_power_per_transaction(
        rapl_readings.copy(),
        ledger_readings.copy(),
        network_traffic_5m_readings.copy(),
        pue,
        output_dir,
    )
    plot_rapl_readings(rapl_readings.copy(), output_dir)
    plot_network_traffic(
        network_traffic_readings.copy(), output_dir, enddate="2021-06-01"
    )
    plot_piegraph(
        network_traffic_readings.copy(), rapl_readings.copy(), 6.5, output_dir
    )

    plot_rapl_with_others(
        rapl_readings.copy(),
        sysstat_readings.copy(),
        ledger_readings.copy(),
        patched_network_data(network_traffic_readings, network_traffic_5m_readings),
        output_dir,
    )
