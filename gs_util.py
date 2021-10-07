"""
utilities for Olympics project: Fx's for wrangling data, in particular:
analyze_xxxx - group, sort, select values, do starts on Olympic data tables
describe_xxxx - give characteristics of dataframe or list with one type of Olympic data
reconcile_xxxx or cleanup_xxxx - true-up one data set with another, fix errors or missings
"""

import csv
import json
import os
import pandas as pd
from pandas.api.types import CategoricalDtype

from gs_datadict import OUTDIR

def count_events(elist):
    """
    from list-list-dict with event results we read direct from source,
    count medal events per each Discipline.
    :param elist: list of list of dict, 2nd level list has all results for one event
    :return: dict with key=Discipline 'html' name, value=number of medal events
    """
    print("\ncounting medal events per discipline from source data")
    edct: dict = {}
    dis_cnt: int = 0
    for lstx in elist:
        if lstx[0]['discipline'] not in edct:
            dis_cnt += 1
            edct[lstx[0]['discipline']] = 1
        else:
            edct[lstx[0]['discipline']] += 1
    print("    found %d events in %d Disciplines \n" %(sum(edct.values()), dis_cnt))

    return edct

def get_uniques(lst):
    """
    simple Fx to return sorted and unique elements from a list
    :param lst:
    :return:
    """
    tmplst: list = []
    for item in lst:
        if item not in tmplst:
            tmplst.append(item)
    tmplst = sorted(tmplst)

    return tmplst

def save_df_tocsv(df: pd.DataFrame, savefile: str="eventdata.csv", wmode: str="w"):
    """
    writes out dataframes to csv file, give me most flexibility when re-importing,
    first write uses w, which overwrites an existing file of same name,
    subsequent writes use a, which appends to end of file, this allows me to
    add all event data together.
    :param df: pd.DataFrame
    :param savefile: name of archive to write
    :param wmode: write mode for file, either w for first, or a for append for additional
    :return: 0 if successful
    """
    outf = os.path.join(OUTDIR, savefile)
    df.to_csv(path_or_buf=outf, mode=wmode, header=False, index=False, date_format="%Y-%m-%d")

    return 0

def save_dcts_tocsv(lstdct, savefile: str = "eventdata.csv", wmode: str = "w"):
    """
    saves each dict in list of discipline or event results
    :param lstdct: list of dict, each dict an individual result in an event
    :param savefile: name of csv file for archive
    :param wmode: write mode for file, w for first item, a (append) for rest
    :return:
    """
    if isinstance(lstdct, list):
        fh = open(savefile, wmode)
        keys = lstdct[0].keys()
        dict_writer = csv.DictWriter(fh, fieldnames=keys, dialect='unix', quoting=csv.QUOTE_MINIMAL)
        if wmode == "w":
            dict_writer.writeheader()
        for dct in lstdct:
            dict_writer.writerow(dct)
        fh.close()

    return

def save_tojson(tweets: list, savefil: str):
    """
    called by save_recs to save a large batch of tweets to file.
    easy to chunk any junk and serialize to json
    :param tweets: list of dict, each dict a set of fields for one tweet
    :param savefil: str with name of file
    :return: 0 if success
    """
    fh_j = open(savefil, mode='a+', encoding='utf-8', newline='')
    json.dump(tweets, fh_j, separators=(',', ':'))
    return fh_j.close()

def save_events_df(edf: pd.DataFrame, savef: str):
    """
    saves the core event dataframe which has one row for each medal event with sport, event,
    gender, html text for scraping, date, participants and NOCs, and medalists and country

    I've found most reliable way to backup dataframe is save as list of dict and then use
    csv.dictwriter on it!
    :param edf: events_df dataframe, 339 rows, one for each medal event
    :param savef: fully qualified path + filename
    :return: none
    """
    edata = edf.to_dict("records")
    save_dcts_tocsv(edata, savef)
    print("backup completed for %d Event Summary records \n" %len(edata))

    return

def read_df_from_file(archf):
    """
    read in the csv file archived by save_to_csv
    :param archf: a csv file with all event or athlete data
    :return: pd.DataFrame
    """
    df = pd.read_csv(archf, dtype={'final_place': int})

    return df

def do_event_bak(bakfil, elst):
    """
    little fx to write event result detail to file
    :param bakfil:
    :param elst:
    :return:
    """
    print("\n    saving final standings for each event as %s" % bakfil)
    first: bool = True
    for evtx in elst:
        if first:
            save_dcts_tocsv(evtx, savefile=bakfil)
            first = False
        else:
            save_dcts_tocsv(evtx, savefile=bakfil, wmode="a")

    return

def show_metadata(meta: dict):
    """
    simple function to print metadata created with athlete analysis
    :param meta: dict created in athletes_groupby fx
    :return:
    """
    print("------ Metadata for athletes ------")
    for k, v in meta.items():
        print(" Meta: %s = %d" %(k, v))
    print("")

    return

def describe_basics(dis: list, edf: pd.DataFrame):
    """
    provide overview stats on Olympic sports and events
    :param dis: discplines list, this has primary and secondary groupings for sports
    :param edf: the events_df DataFrame with one row per event summary
    :return: list of dict with group-discipline hierarchy, to assist with plotting
    """
    print("\n------ General Information on Tokyo Olympic Events: ------")
    evtgender_dct: dict = edf["Gender"].value_counts().to_dict()
    for k, v in evtgender_dct.items():
        if str(k).startswith("Men") or str(k).startswith("Women"):
            print("%s events were restricted to %s " % (v, k))
        else:
            print("%s events were %s format\n" % (v, k))

    sprt_mdls: dict = edf["Sport"].value_counts().to_dict()
    print("%d Disciplines had medal events at the Tokyo Olympics..." %len(sprt_mdls))
    for k, v in sprt_mdls.items():
        print("    %d medal events in %s" % (v, k))

    primes: list = [d['primary'] for d in dis]
    primes = get_uniques(primes)

    print("\nI designated a higher level 'Primary group' for each discipline")
    print("    %d primary groups..." %len(primes))
    primdct: dict = {}
    for p in primes:
        p_dis: list = []
        for d in dis:
            if str(d['primary']).startswith(p):
                p_dis.append(d['htmlq'])
        primdct.update({p: p_dis})

    for k, v in primdct.items():
        print("%s group includes %s" %(k, v))
    print("")

    return primdct

def analyze_groups(dis: list, edf: pd.DataFrame):
    """
    get info on primary and secondary level sports groups I created
    :param dis: list of disciplines with primary and secondary groups
    :param edf: events dataframe
    :return:
    """
    primes: list = [disx['primary'] for disx in dis]
    primes: list = get_uniques(primes)
    # append grp_sports and grp_medals for each Sport in a primary group
    grp_sports: dict = {}
    grp_mdls: list = []
    for p in primes:
        #  for each sport in group, collect results for events
        p_sports = [x['htmlq'] for x in dis if x['primary']==p]
        evt_count: int = 0
        sprt_mdls: list = []
        for spx in p_sports:
            # .loc with columns list in brackets SHOULD return a df, buggy though...
            tmp_df: pd.DataFrame = edf.loc[edf["disc_html"]== spx, ["G_NOC", "S_NOC", "B_NOC", "G2_NOC", "B2_NOC"]]
            evt_count += len(tmp_df)
            prime_g: list = tmp_df.G_NOC.to_list()
            prime_s: list = tmp_df.S_NOC.to_list()
            prime_b: list = tmp_df.B_NOC.to_list()

            for altmdl in ["G2_NOC", "B2_NOC"]:
                nocmdl  = tmp_df.loc[tmp_df[altmdl].notna(), [altmdl]]
                if len(nocmdl) >= 1:
                    altm_lst = nocmdl[altmdl].to_list()
                    prime_g.extend(altm_lst)
            sprt_mdls.append([spx, prime_g, prime_s, prime_b])

        grp_mdls.append(sprt_mdls)
        grp_sports.update({p: evt_count})

    for k, v in grp_sports.items():
        print("primary group %s had %d medal events" %(k, v))

    return grp_sports, grp_mdls

def count_grp_nocs(g_m: list, g_s: dict):
    """
    aggregate medals by NOC for each primary group
    :param g_m: list of n(groups) length with list for each sport with noc medals
    :param g_s: dict with key=group name, val=num of medal events
    :return:
    """
    grp_noc_ct: list = []
    for gnam, mdls in zip(g_s.keys(), g_m):
        noc_dct: dict = {}
        slen: int = len(mdls)
        for x in range(slen):
            for y in [1, 2, 3]:
                nocs: list = mdls[x][y]
                for z in nocs:
                    if z in noc_dct:
                        noc_dct[z] += 1
                    else:
                        noc_dct[z] = 1
        grp_noc_ct.append(noc_dct)

    return grp_noc_ct

def analyze_events(dis: list, edf: pd.DataFrame):
    """
    entry point for analyzing sports groups and events at Olympic games
    :param dis: list of disciplines with common groups and other meta-attributes
    :param edf: events dataframe with core info on the 339 medal events
    :return:
    """

    eg_df = edf.copy(deep=True)         # df copy we can modify and leave original OK
    meta_dct: dict = {}

    sports: list = [disx['discipline'] for disx in dis]
    sports = get_uniques(sports)
    meta_dct["Sports"] = len(sports)
    eg_df["Sport"] = eg_df["Sport"].astype(CategoricalDtype(sports))

    mdls_bysport: dict = eg_df["Sport"].value_counts().to_dict()
    meta_dct["Events_by_Sport"] = mdls_bysport.items()

    evt_gender_dct: dict = eg_df["Gender"].value_counts().to_dict()
    gend_cat = list(evt_gender_dct.keys())
    meta_dct["Events_by_Gender"] = evt_gender_dct.items()
    eg_df["Gender"] = eg_df["Gender"].astype(CategoricalDtype(gend_cat))

    # one event awarded two gold, several awarded two bronze, the rest just gold, silver, bronze
    gNOCs: list = eg_df["G_NOC"].value_counts().keys().to_list()
    gNOCs.extend(eg_df["G2_NOC"].value_counts().keys().to_list())
    gNOCs = get_uniques(gNOCs)
    eg_df["G_NOC"] = eg_df["G_NOC"].astype(CategoricalDtype(gNOCs))

    sNOCs: list = eg_df["S_NOC"].value_counts().keys().to_list()
    sNOCs = get_uniques(sNOCs)
    eg_df["S_NOC"] = eg_df["S_NOC"].astype(CategoricalDtype(sNOCs))

    bNOCs: list = eg_df["B_NOC"].value_counts().keys().to_list()
    bNOCs.extend(eg_df["B2_NOC"].value_counts().keys().to_list())
    bNOCs = get_uniques(bNOCs)
    eg_df["B_NOC"] = eg_df["B_NOC"].astype(CategoricalDtype(bNOCs))

    all_NOCs = gNOCs + sNOCs + bNOCs
    all_NOCs = get_uniques(all_NOCs)
    meta_dct["Gold_medal_NOCs"] = len(gNOCs)
    meta_dct["Silver_medal_NOCs"] = len(sNOCs)
    meta_dct["Bronze_Unique_Countries"] = len(bNOCs)
    meta_dct["Countries_with_Medals"] = len(all_NOCs)

    return eg_df, meta_dct

def describe_athlete_data(tdf: pd.DataFrame):
    """
    tell some things about the athlete and team data like number of groups, gender, etc.
    :param tdf: copy of teamsdf created as part of the main readfiles script
    :return:
    """

    len_all = len(tdf)
    wt_coverage = round((len_all - tdf.wt_lbs.isna().sum()) * 100 / len_all, ndigits=1)
    ht_coverage = round((len_all - tdf.ht_in.isna().sum()) * 100/len_all, ndigits=1)
    bygender = tdf.gender.value_counts().to_dict()
    male_female = bygender["Men"] / (bygender["Men"] + bygender["Women"])
    print("---- Athlete data has %d rows ----" %len_all)
    print("    %.1f percent of records have height info" %ht_coverage)
    print("    %.1f percent of records have weight info" %wt_coverage)
    print("    %2.1f percent are male\n" %(male_female * 100))

    return

def athletes_groupby(adf: pd.DataFrame):
    """
    use dataframe groupby to calculate stats for athletes by team and sport
    :param adf: the teamsdf DataFrame created as part of readfiles - getOlympicdata
    :return: ht_grp and wt_grp: 2 pd.DataFrames with athlete descriptive statistics
    """

    print("\n---- athletes_groupby prep athlete data for analysis ----")
    funcs = {"age": "mean", "ht_in": ["mean", "min", "max"], "wt_lbs": "mean"}
    newcols = ["avg_age", "avg_ht", "min_ht", "max_ht", "avg_wt"]

    print("    creating categorical dtypes for category, event, gender, and NOC")
    cat_cat = adf.category.unique().tolist()
    adf["category"] = adf["category"].astype(CategoricalDtype(cat_cat))
    evt_cat = adf.event.unique().tolist()
    adf["event"] = adf["event"].astype(CategoricalDtype(evt_cat))
    gend_cat = adf.gender.unique().tolist()
    adf["gender"] = adf["gender"].astype(CategoricalDtype(gend_cat))
    noc_cat = adf.NOC.unique().tolist()
    adf["NOC"] = adf["NOC"].astype(CategoricalDtype(noc_cat))
    adf["medal"] = adf.loc[adf["medal"].isna(), ["medal"]] = "No"
    mdl_cat = adf.medal.unique().tolist()
    adf["medal"] = adf["medal"].astype(CategoricalDtype(mdl_cat))

    print("    removing precalculated rows and rows with missing height or weight")
    tdf = adf[adf["NOC"] != "ALL"]
    ht_df = tdf[tdf['ht_in'].notna()]
    wt_df = tdf[tdf['wt_lbs'].notna()]
    print("    %d rows for athlete height, %d rows for athlete weight" %(len(ht_df), len(wt_df)))

    ht_grp = ht_df.groupby(["event", "gender"])
    ht_grp = ht_grp.agg(funcs)
    ht_grp.columns = newcols
    ht_grp = ht_grp.reset_index()

    # same grouping for weight data
    wt_grp = wt_df.groupby(["event", "gender"])
    wt_grp = wt_grp.agg(funcs)
    wt_grp.columns = newcols
    wt_grp = wt_grp.reset_index()

    return ht_grp, wt_grp

def prep_precalcs(adf: pd.DataFrame):
    """
    extract and prep for plotting: precalculated athlete and population means
    :param adf: the athlete_df
    :return: list of dict with prepped data
    """

    precalcs: pd.DataFrame = adf.loc[adf.NOC == "ALL"]

    print("\n----  Prep precalculated Athlete data for plotting ----")
    print("    dropping %d rows due to no weight data" % precalcs.wt_lbs.isna().sum())
    precalcs = precalcs.dropna(subset=["wt_lbs"])
    precalcs = precalcs.drop(["dob"], axis=1)
    precalcs = precalcs.reset_index(drop=True)
    gendct: dict = precalcs.gender.value_counts().to_dict()
    catevts: dict = precalcs.category.value_counts().to_dict()
    print("    weight-height averages in %d events" %sum(catevts.values()))
    print("    in %d groups of sports" %len(catevts))
    print("    %d for Women, %d for Men\n" %(gendct['Women'], gendct['Men']))

    return precalcs

def conv_checkmark_to_bool(strct, chk_cols: list):
    """
    handle ('x' | '') checkmark fields read from csv's: transform to boolean columns
    :param strct: data container with checkmarks- either list or DataFrame
    :param chk_cols: list of columns with checkmark "x" to convert to boolean True
    :return: strct with checkmark fields converted to boolean
    """
    if isinstance(strct, list):
        for item in strct:
            if isinstance(item, dict):
                for col in chk_cols:
                    if item.get(col):
                        if str(item[col]).startswith("x"):
                            item[col] = True
                        else:
                            item[col] = False
                    else:
                        item[col] = False
    elif isinstance(strct, pd.DataFrame):
        for col in chk_cols:
            if col in strct.columns:
                strct[col] = strct[col].apply(lambda y: True if str(y).startswith("x") else False)
                print("cleaned up dataframe column  %s" %col)
            else:
                print("event cleanup: did not find column %s" %col)
    else:
        print("convert checkmarks was not passed a usable container")

    return strct

def reconcile_eventdf_wsrc(evts: list, edf: pd.DataFrame):
    """
    a utility that compares event results from scraping the Olympic site with
    our event_df which I downloaded from Kaggle and in which I found errors, to my
    bad surprise, the count of medals for a few countries was WRONG!  so, I wrote this
    to true-up from the source data I got from scraping the Olympic site.
    :param evts: the event_res list with 339 events scraped from the web
    :param edf: events_df DataFrame which is a handy layout but has some errors
    :return: corrected DataFrame
    """
    edf.set_index(['disc_html', 'evt_html'], drop=False, inplace=True, verify_integrity=True)

    row_count: int = 0
    col_count: int = 0
    for evt in evts:
        evt_flag: bool = False
        if isinstance(evt[0], dict):
            srcdct: dict = {}
            for x in range(4):
                ds: str = evt[x].get('discipline')
                ev: str = evt[x].get('event')
                if str(evt[x]['final_place']).startswith("1"):
                    if x == 0:
                        srcdct['Gold'] = evt[x]['Name']
                        srcdct['G_NOC'] = evt[x]['NOC']
                    elif x == 1:
                        srcdct['Gold2'] = evt[x]['Name']
                        srcdct['G2_NOC'] = evt[x]['NOC']
                elif str(evt[x]['final_place']).startswith("2"):
                    srcdct['Silver'] = evt[x]['Name']
                    srcdct['S_NOC'] = evt[x]['NOC']
                elif str(evt[x]['final_place']).startswith("3"):
                    if x == 2:
                        srcdct['Bronze'] = evt[x]['Name']
                        srcdct['B_NOC'] = evt[x]['NOC']
                    elif x == 3:
                        srcdct['Bronze2'] = evt[x]['Name']
                        srcdct['B2_NOC']= evt[x]['NOC']
            if srcdct.get('G2_NOC'):
                rowval: dict = edf.loc[(ds, ev),
                                       ['Gold', 'G_NOC', 'Gold2', 'G2_NOC', 'Bronze', 'B_NOC']].to_dict()
            elif srcdct.get('B2_NOC'):
                rowval: dict = edf.loc[(ds, ev),
                                       ['Gold', 'G_NOC', 'Silver', 'S_NOC', 'Bronze',
                                        'B_NOC', 'Bronze2', 'B2_NOC']].to_dict()
            else:
                rowval: dict = edf.loc[(ds, ev),
                                   ['Gold', 'G_NOC', 'Silver', 'S_NOC', 'Bronze', 'B_NOC']].to_dict()

            for k, v in rowval.items():
                if srcdct[k] == v:
                    # print("%s-%s matches" %(ds,ev))
                    continue
                else:
                    edf.loc[(ds, ev), k] = srcdct[k]
                    col_count += 1
                    if not evt_flag:
                        row_count += 1
                        evt_flag = True

    edf.reset_index(drop=True, inplace=True)
    print(" corrected %d entries in %d rows for event DataFrame" %(col_count, row_count))
    return edf
