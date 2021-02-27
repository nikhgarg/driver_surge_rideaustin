import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import datetime
import scipy.stats as stats
from utilities import *
from generic.latexify import *
from payment.payment_functions import *


def platform_stability(runlabel, df):  # TODO fix date labels
    print("Plotting trips per day over time")
    df.loc[:, "day_rounded_for_count"] = df.start_hour // 24
    df.loc[:, "day_rounded_for_count"] = df.loc[:, "day_rounded_for_count"] - min(df.loc[:, "day_rounded_for_count"])
    dff = df.groupby("day_rounded_for_count")["dispatch_hour"].count().reset_index()
    sns.lineplot(x="day_rounded_for_count", y="dispatch_hour", data=dff)
    plt.xlabel("Day in analysis period", fontsize=20)
    plt.ylabel("Number of trips", fontsize=20)
    saveimage("tripsperday_{}".format(runlabel), extension="pdf")


def evaluate_reverseengineer(runlabel, df):
    print("Mean difference between reverse engineer fare and total fare: {}".format(df.eval("abs(mimic_fare - total_fare + 2.02)").mean()))

    df.eval("abs(mimic_fare - total_fare + 2.02)").hist(bins=np.logspace(-9, 1.1, 20))
    plt.yscale("log")
    plt.xscale("log")
    plt.xlabel("Difference in dollars between total fare and reverse engineered fare")
    plt.ylabel("Number of trips", fontsize=25)
    saveimage("difftotalfare_reverse_fare_{}".format(runlabel), extension="png")


def scatter_fares(
    runlabel, df, farex="mimic_fare", farey="pure_addsurge_bysurgefactor_fare", namex="Reverse engineered fare", namey="Additive Surge"
):
    plt.scatter(y=df[farey], x=df[farex])
    plt.plot(range(400), range(400))
    plt.xlabel(namex, fontsize=25)
    plt.ylabel(namey, fontsize=25)
    plt.xlim((0, 200))
    plt.ylim((0, 200))
    saveimage("{}_vs_{}_{}".format(namex.replace(" ", ""), namey.replace(" ", ""), runlabel), extension="png")


def evaluate_matching(runlabel, df, match_funcname):
    match_column = match_funcname.replace("_matched_index", "")
    df[match_column + "_matched_distance"].hist()  # TODO
    plt.yscale("log")
    plt.xlabel("Matching distance between matched trips", fontsize=15)
    plt.ylabel("Number of trips", fontsize=25)
    saveimage("matching_distance_{}_{}".format(match_column, runlabel), extension="png")


def surge_basic_facts(runlabel, df):
    print("Mean surge factor: ", df.surge_factor.mean())
    print("Fraction surge trips factor: ", df.surged_trip.mean())
    print("Fraction of surge trips less than 3x: ", (df[df.surge_factor > 1].surge_factor <= 3).mean())

    df.surge_factor.hist(bins=10)
    plt.yscale("log")
    plt.xlabel("Surge Factor", fontsize=25)
    plt.ylabel("Number of trips", fontsize=25)
    saveimage("surgehistogram_{}".format(runlabel), extension="png")

    df.loc[:, "minutes"] = (df.end_hour - df.start_hour) * 60
    df.loc[:, "surge_rounded"] = df.loc[:, "surge_factor"] * 4 // 2 / 2  # round down to nearest .5
    sns.lineplot(x="surge_rounded", y="minutes", data=df)
    plt.xlabel("Surge Factor", fontsize=25)
    plt.ylabel("Mean trip length in minutes", fontsize=15)
    saveimage("triplengthmeans_{}".format(runlabel), extension="png")


def surge_evolution(runlabel, df):
    # Surge lag by driver session's first trip
    df = df.sort_values(by="dispatch_hour")
    df.loc[:, "Surge Bin"], retbins = pd.cut(
        df["surge_factor"], bins=[1, 1.5, 2, 2.5, 3, 5], retbins=True, precision=1, include_lowest=True, right=False
    )
    grouped = df[["active_driver_id", "Surge Bin", "surge_factor", "mimic_fare"]].dropna().groupby("active_driver_id").agg(list)
    grouped.loc[:, "len"] = grouped["surge_factor"].apply(len)
    minlen = 5
    groupedminlen = grouped.query("len >= @minlen")
    groupedminlen.loc[:, "Surge Bin"] = groupedminlen["Surge Bin"].apply(lambda x: x[0])
    uniques = list(set(groupedminlen["Surge Bin"].tolist()))
    lags_by_surge = {k: [] for k in uniques}
    for k in uniques:
        dfs = groupedminlen[groupedminlen["Surge Bin"] == k]
        lags_by_surge[k] = [np.mean([x[i] for x in dfs.surge_factor if not np.isnan(x[i])]) for i in range(minlen)]
    for x in sorted(lags_by_surge):
        label = "First trip's surge in {}".format(x)
        plt.plot(lags_by_surge[x], label=label)
    plt.legend(frameon=False)
    plt.xlabel("Trip in session", fontsize=20)
    plt.ylabel("Average Surge Factor", fontsize=25)
    saveimage("tripsurgeautocorrelation_{}".format(runlabel), extension="png")

    # Surge lag in period
    df.loc[:, "rounded_time_to_10_minutes"] = df["dispatch_hour"] * 60 // 6 * 10  # rounded every 10 minutes
    dflocrounded = df.groupby("rounded_time_to_10_minutes").surge_factor.agg("mean").reset_index()
    for lagg in range(1, 13):
        dflocrounded.loc[:, "lag{}".format(lagg)] = dflocrounded.surge_factor.shift(periods=-lagg)
    dflocrounded.loc[:, "Surge Bin"], retbins = pd.cut(
        dflocrounded["surge_factor"], bins=[1, 1.5, 2, 2.5, 3, 5], retbins=True, precision=1, include_lowest=True, right=False
    )
    lags_by_surge = {k: [] for k in dflocrounded["Surge Bin"].unique().tolist()}
    for k in dflocrounded["Surge Bin"].unique().tolist():
        dfs = dflocrounded[dflocrounded["Surge Bin"] == k]
        lags_by_surge[k] = [dfs.surge_factor.mean(skipna=True)]
        lags_by_surge[k].extend([dfs["lag{}".format(x)].mean(skipna=True) for x in range(1, 13)])
    labels = (
        "Current surge in [1, 1.5)",
        "Current surge in [1.5, 2)",
        "Current surge in [2, 2.5)",
        "Current surge in [2.5, 3)",
        "Current surge in [3, 5)",
    )
    for en, x in enumerate(lags_by_surge):
        plt.plot([yy / 6 for yy in range(len(lags_by_surge[x]))], lags_by_surge[x], label=labels[en])
    plt.legend(frameon=False)
    plt.xlabel("Hours in the future", fontsize=20)
    plt.ylabel("Average Surge Factor", fontsize=25)
    saveimage("surgeautocorrelation_{}".format(runlabel), extension="png")

    dtindex = pd.to_datetime(df.started_on, format="%Y-%m-%d %H:%M:%S")
    df.loc[:, "Hour in week"] = (dtindex.apply(lambda x: x.hour)) + 24 * (dtindex.apply(lambda x: x.weekday()))
    # df.loc[:, 'Hour in day'] = dtindex.apply(lambda x: x.hour + (x.minute//30)/2) #rounded every 30 minutes
    df.loc[:, "Hour in day"] = dtindex.apply(lambda x: x.hour)  # rounded every hour
    df.loc[:, "Day in week"] = dtindex.apply(lambda x: x.weekday())
    df.loc[df["Day in week"] <= 4, "Day type"] = "Weekday"
    df.loc[df["Day in week"] > 4, "Day type"] = "Weekend"
    df.loc[:, "date"] = dtindex.apply(lambda x: x.date())
    sns.lineplot(x="Hour in day", y="surge_factor", data=df, hue="Day type")
    plt.ylabel("Average Surge Factor", fontsize=25)
    plt.xlabel("Hour in day", fontsize=25)
    plt.legend(frameon=False)
    saveimage("surgefactorbydayhour_{}".format(runlabel), extension="png")

    trips_by_hourinday = df.groupby(["Hour in day", "Day type"])["driver_id"].count().reset_index()
    trips_by_hourinday.loc[trips_by_hourinday["Day type"] == "Weekday", "driver_id"] /= 5 * 2
    trips_by_hourinday.loc[trips_by_hourinday["Day type"] == "Weekend", "driver_id"] /= 2 * 2
    sns.lineplot(data=trips_by_hourinday, x="Hour in day", y="driver_id", hue="Day type")
    plt.ylabel("Avg number of trips per hour", fontsize=15)
    plt.xlabel("Hour in day", fontsize=25)
    plt.legend(frameon=False)
    saveimage("avgnumtrips_{}".format(runlabel), extension="png")


def tripdistribution_nosurge(runlabel, df):
    vals = df[(~(df.mimic_fare.isna())) & df.surge_factor == 1].eval("(end_hour - start_hour)*60")

    fit = stats.exponweib.fit(vals, 1, 1, floc=vals.mean())
    loc = fit[2]
    scale = fit[0]
    print("No surge trip distribution mean: {:.3f}, weibull scale: {:.3f}".format(loc, scale))

    vals.hist(histtype="step", bins=40, density=True, label="Trip distribution")
    x = np.linspace(0, 60, 1000)
    plt.plot(x, weib(x, loc, scale), label="Weibull w/ shape {:.1f}, mean {:.1f}".format(scale, loc))
    plt.xlabel("Trip length in minutes", fontsize=25)
    plt.ylabel("Density", fontsize=25)
    plt.legend(frameon=False)
    saveimage("triplengthdist_nosurge_{}".format(runlabel), extension="png")


def surge_close_to_capitol_markovian(runlabel, df):
    lat_capitol = 30.274375
    long_capitol = -97.7408387
    minn = df.dispatch_hour.min()
    offset = 81 + 24 * 7 * 4 + 1 * 24
    lenn = 24 * 3
    df3days = df[(df.dispatch_hour < minn + offset + lenn) & (df.dispatch_hour >= minn + offset)]
    if df3days.shape[0] == 0:
        print("No rows in dataframe overlapping with 3 day period")
        return
    print(df3days.head())
    df3days["miles_from_capitol"] = df3days.apply(
        lambda x: haversine(lat_capitol, long_capitol, x["start_location_lat"], x["start_location_long"]), axis=1
    )
    df3days_closetocap = df3days.query("miles_from_capitol < 5")
    df3days_closetocap.loc[:, "rounded_time_to_10_minutes"] = df3days_closetocap.eval(
        "((dispatch_hour*60)//6)/10 - @minn - @offset"
    )  # rounded every 10 minutes
    sns.lineplot(x="rounded_time_to_10_minutes", y="surge_factor", data=df3days_closetocap)
    plt.xlabel("Time (hours from beginning of period)", fontsize=18)
    plt.ylabel("Average Surge Factor", fontsize=25)
    saveimage("surgeclosetocap_{}".format(runlabel), extension="png")


def dispatch_vs_trip(runlabel, df):
    df.loc[:, "Dispatch Time"] = df.eval("start_hour - dispatch_hour")
    df.loc[:, "Trip Time"] = df.eval("end_hour - start_hour")
    dfgood = df.dropna(subset=["mimic_fare"])
    (dfgood["Dispatch Time"] / (dfgood["Dispatch Time"] + dfgood["Trip Time"])).hist(bins=20)
    plt.xlabel("Fraction of trip time that is unpaid", fontsize=20)
    plt.ylabel("Number of trips", fontsize=25)
    saveimage("dispatchratio_{}".format(runlabel), extension="png")


def supplementary_pipeline(outputrunlabel, df, matching_functions, payment_functions_names, payment_functions_prettynames):
    scatter_fares(outputrunlabel, df)
    scatter_fares(outputrunlabel, df, farey="pure_mult_bysurgefactor_fare", namey="Multiplicative surge")

    for en2, fun2 in enumerate(payment_functions_names):
        for en, fun in enumerate(payment_functions_names[en2 + 1 :]):
            scatter_fares(
                outputrunlabel,
                df,
                farex=fun,
                farey=fun2,
                namex=payment_functions_prettynames[fun],
                namey=payment_functions_prettynames[fun2],
            )

    surge_basic_facts(outputrunlabel, df)
    surge_close_to_capitol_markovian(outputrunlabel, df)
    tripdistribution_nosurge(outputrunlabel, df)
    dispatch_vs_trip(outputrunlabel, df)
    surge_evolution(outputrunlabel, df)
    evaluate_reverseengineer(outputrunlabel, df)

    for matching_function in matching_functions:
        evaluate_matching(outputrunlabel, df, matching_function.name)
