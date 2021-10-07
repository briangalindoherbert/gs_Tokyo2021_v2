"""
the main script for my olympics analysis.
My data schema for the 2020 Tokyo Olympics is:
    1.  Disciplines - 48
    types of competition, a specific form of a 'sport' - such as
    beach volleyball and (court) volleyball are two disciplines.
    2.  NOCs - Olympic Team representing a nation, has athletes, wins medals and
    qualifies for and competes in events.
    3. Athletes - represent an NOC, qualify to compete in specific events,
        My desired set of attributes for athletes:
            full Name, ID, NOC, gender, DoB, discipline, events, medals won,
            height, weight, hometown, other Olympics (year), past medals/finishes
    4. Medal Events - a competition in a discipline for which medals are awarded
    5. Team_roster - for team ball sports like basketball, football, handball,
    baseball-softball, volleyball, water polo, rugby, and field hockey.
        Data:   player name, ID, jersey, DoB, Height, Weight, position.
                head coach name, country, age, first Olympics.
"""

import os
import sys
from datetime import datetime as dt

import pandas as pd

# imports from my modules:
import gs_getters as gsg
import gs_plots as gsp
import gs_util as gsu
from gs_datadict import *

# variables to control what scripts are run:
source_results: bool = False
source_medalists: bool = False
analyze_basics: bool = True
analyze_athletes: bool = False
analyze_events: bool = True
save_entries: bool = False

if os.path.isfile(os.path.join(RAWDIR, evts_byrow_f)):
    # get list/dict of disciplines and country teams (NOCs) which attended Olympics
    check_fields: list = ["the_elements", "tallbias", "style", "fast_twitch",
                          "suffer", "greypoupon", "cool"]
    disciplines: list = gsg.get_list_file(RAWDIR + discf, chkcols=check_fields)
    countries: dict = gsg.get_list_file(RAWDIR + nocf)
    # file of medal events - core data for this app
    fqf = os.path.join(RAWDIR, evts_byrow_f)
    events_df: pd.DataFrame = gsg.get_olympic_data(fqf, "events")
    # timeline of medals by discipline
    fqf = os.path.join(RAWDIR, timelinef)
    timeline_df: pd.DataFrame = gsg.get_olympic_data(fqf, "timeline")
    # team rosters plus selected individual athletes: age, height and weight
    fqf = os.path.join(RAWDIR, athlete_f)
    athlete_df: pd.DataFrame = gsg.get_olympic_data(fqf, "athletes")
    print("finished reading in disciplines, countries, events, timeline, and athlete files\n")
else:
    print("problem locating events_byrow file, maybe move it to %s ?" %RAWDIR)
    sys.exit()

if source_results:
    # provide all or slice of 'disciplines' to control what event results this collects
    evt_rslts = gsg.process_disc_and_event(disciplines, events_df)
else:
    # get event results from backup, such as 'results_bak_2021-09-26.csv'
    bakf = os.path.join(OUTDIR, evtresults_f)
    evt_rslts = gsg.get_events_from_bak(bakf)

if source_medalists:
    # get all medalists for 'NOC'. defaults to country="united states"
    medalist_df, medalists = gsg.get_all_medalists()
else:
    # get medalist data from backup, medalists_2021_09_25.csv is latest
    bakf = os.path.join(OUTDIR, medalists_f)
    medalists = gsg.get_list_file(bakf)

if analyze_basics:
    # ---- verify event and medal counts, reconcile source files plot medals by NOC ----
    # reconcile was built to clean initial data- not needed once stable!
    # events_edf: pd.DataFrame = gsu.reconcile_eventdf_wsrc(evt_rslts, events_df)

    disc_evts: dict = gsu.count_events(evt_rslts)
    medals: list = gsg.get_noc_medalct(events_df)
    select_nocs = ['USA', 'CHN', 'JPN', 'GBR', 'ROC', 'AUS']
    # gsp.medals_barplot(medals, countries, select_nocs)

    if analyze_athletes:
        # look at athlete age, height, and weight by team and sport, compare to adult avg
        gsu.describe_athlete_data(athlete_df)
        precalcs = gsu.prep_precalcs(athlete_df)
        by_ht, by_wt = gsu.athletes_groupby(athlete_df)
        gsp.plot_athlete_avg(precalcs)
        gsp.height_vs_norm(precalcs)

    if analyze_events:
        # organize by primary and secondary groups
        prime_to_dis: dict = gsu.describe_basics(disciplines, events_df)
        # sportsg_df, meta_dict = gsu.analyze_events(disciplines, events_df)
        grp_sports, grp_medals = gsu.analyze_groups(disciplines, events_df)
        grp_nocs = gsu.count_grp_nocs(grp_medals, grp_sports)
        grps: list = list(grp_sports.keys())
        # primedf: pd.DataFrame = gsp.plot_groups(prime_to_dis, disc_evts)
        selected: str = "combat"
        slct_idx: int = grps.index(selected)
        slctd_noc: dict = grp_nocs[slct_idx]


if save_entries:
    # backup data that is 'expensive' to source or build
    # FOUR components: event_summary, results, athletes, medalists
    # do_event_bak for list of list of dict, save_dcts_tocsv for list of dict

    # TODO: add descriptive text fields for sport and event
    today_dt: str = dt.today().strftime("%Y-%m-%d")
    bak_name = OUTDIR + "resultsbak_" + today_dt + ".csv"
    gsu.do_event_bak(bak_name, evt_rslts)

    # TODO: add html discipline and event fields for better matching to other data
    medals_dct = athlete_df.to_dict("records")
    bak_name = OUTDIR + "medalists_" + today_dt + ".csv"
    gsu.save_dcts_tocsv(medalists, bak_name)

    # move a recent, clean copy of this to RAWDIR for use as input
    bak_name = OUTDIR + "medalevents_byrow_" + today_dt + ".csv"
    gsu.save_events_df(events_df, bak_name)

    # TODO: format date as %Y-%m-%d, age and ht_in as %.1f, add
    bak_name = OUTDIR + "athletes_" + today_dt + ".csv"
    ath_tolist = athlete_df.to_dict("records")
    gsu.save_dcts_tocsv(ath_tolist, bak_name)
