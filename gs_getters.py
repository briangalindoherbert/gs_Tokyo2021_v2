"""
the  module in gs_Olympics app involving data acquisition via HTML page reads (scraping)
TODO: move IO Fx's in gs_util to here, move general util Fx's from here to gs_util.
"""
import csv
import pandas as pd
import numpy as np
import requests
from urllib.error import HTTPError
from bs4 import BeautifulSoup
import html5lib
from gs_datadict import EVT_URL, NOC_URL, MDLST_URL

# 4 disciplines use different URL folder struct from others
evtrnk_lst: list = ["3x3-basketball", "surfing", "beach-volleyball", "karate"]
headers = {'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Methods': 'GET',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Max-Age': '3600',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0'
}

def get_olympic_data(fil, typ: str=""):
    """
    1. read raw Olympic event data into pandas DataFrames
    2. read file with final standings for Olympic medal events
    3. reads file with Olympic athlete age, height and weight data
    :param fil: string with path and name of .csv file
    :param typ: which olympic dataset to import
    :return: pd.DataFrame
    """
    if typ.startswith("timeline"):
        df = pd.read_csv(fil, skipinitialspace=True)
    elif typ.startswith("athletes"):
        types = {"age": np.float32, "ht_in": float, "ht_lbs": float}
        df = pd.read_csv(fil, dtype=types, skipinitialspace=True)
        df['dob'] = pd.to_datetime(df['dob'], errors="coerce", format="%Y-%m-%d")
    elif typ.startswith("events"):
        df = pd.read_csv(fil)
    else:
        print("unknown type of Olympic data requested: %s" %typ)
        return 1

    return df

def get_list_file(discfil):
    """
    this is a generic getter for several Olympic files used in this app,
    possible to add separate processing paths as i've done for the countries file
    :param discfil: fq filename for discplines.csv
    :return: list of dict
    """
    with open(discfil, mode='r') as infile:
        csrdr = csv.DictReader(infile)
        if 'country_name' in csrdr.fieldnames:
            tmp: dict = {}
            for row in csrdr:
                tmp.update({row["NOC"]:row["country_name"]})
        else:
            tmp: list = []
            for row in csrdr:
                tmp.append(row)
    return tmp

def get_events_from_bak(disc):
    """
    build events table from backup that was read
    :param disc:
    :return:
    """
    evt_list: list = []
    evttmp: list = []
    lim = len(disc) - 1
    for x in range(len(disc)):
        if x == 0:
            thisevt: str = disc[x]['event']
        evttmp.append(disc[x])
        if x +1 <= lim:
            if disc[x+1]['event'] != disc[x]['event']:
                evt_list.append(evttmp)
                evttmp: list = []
        elif x == lim:
            evt_list.append(evttmp)

    return evt_list

def get_noc_medalct(mdf):
    """
    1.  build dict for each of three medal types
        keys=3-letter NOC (country) codes, values are medal counts
    2: correct counts where multiple medals were awarded for single event:
        two bronze in most combat events, and a dual gold in one athletic event

    :param mdf: DataFrame with medal winners for each Olympic event
    :return: list with 3 dicts for Gold, Silver, and Bronze counts
    """
    def get_medals(edf, typ: str='G'):
        """
        inner function to correct medal counts
        :param edf: pd.DataFrame
        :param typ: str of Gold, Silver, or Bronze
        :return:
        """
        mdldct: dict = mdf[typ + "_NOC"].value_counts().to_dict()
        if typ in ['G', 'B']:
            dup_mdl: str = typ + "2_NOC"
            tmpdct: dict = mdf[dup_mdl].value_counts().to_dict()

            for k, v in tmpdct.items():
                if k in mdldct:
                    mdldct[k] = mdldct[k] + v
                else:
                    mdldct[k] = v
            # sort dict by descending values (medal counts)
        mdldct = {k: mdldct[k] for k in sorted(mdldct, key=lambda x: mdldct.get(x), reverse=True)}

        return mdldct

    mdls: list = [['Gold', None], ['Silver', None], ['Bronze', None]]
    for prize in ['G', 'S', 'B']:
        dctnm: dict = get_medals(mdf, typ=prize)
        if prize.startswith('G'):
            mdls[0][1] = dctnm
        elif prize.startswith('S'):
            mdls[1][1] = dctnm
        else:
            mdls[2][1] = dctnm

    return mdls

def simple_event_entry(disc, event, debug: bool=False):
    """
      Names and NOCs entered for a specific medal event
      Beautiful Soup requires dealing with 4 types of objects:
          Tag, NavigableString, Beautiful Soup, Comment
              Tags have names and attributes
              NavigableStrings are text within a tag, cannot be
                  modified in place but can be replaced
              BeautifulSoup represents the html document as a whole, and
                  can be dealt with as a Tag


      :param disc: official name of Olympic discipline
      :param event: official name of medal_event
      :param debug: if True prints status of current disc and event being processed
      :return:
      """
    import re

    def chknum(y):
        """
        check if var is all numeric, else return 0
        :param y: field to check for numeric
        :return:
        """
        if re.search("[0-9]", y):
            return y
        else:
            return 0

    def get_splt(nam):
        """
        inner fx to find split position for name field scraped from web
        :param nam: str Name field from Dataframe of scraped olympic entries
        :return: position to use for splicing the field
        """
        splt = str(nam).partition(" ")[2]
        return splt[1:]

    # a few disciplines for Tokyo2020 use a different results screen url format...
    if disc in evtrnk_lst:
        sfx: str = "/event-ranking-"
    else:
        sfx: str = "/medals-and-ranking-"
    fqurl = EVT_URL + str(disc) + sfx + str(event) + ".htm"
    if debug:
        print("getting %s results for event: %s" %(disc,event))
    try:
        if disc in evtrnk_lst:
            pandas_resp = pd.read_html(fqurl, match="Event Ranking", flavor="html5lib")
        else:
            pandas_resp = pd.read_html(fqurl, match="Medals and Ranking", flavor="html5lib")
    except HTTPError as err:
        if err.code == 404:
            print("404 Error on url: %s" %fqurl)
            respdf = pd.DataFrame({'discipline': [],})
            return respdf
        else:
            raise

    if len(pandas_resp) == 1:
        respdf = pandas_resp[0].copy(deep=True)
        respdf.dropna(axis='columns', inplace=True, thresh=5)

        if 'Name' in respdf.columns:
            respdf['NOC'] = respdf['Name'].apply(lambda x: str(x)[0:3])
            respdf['Name'] = respdf['Name'].apply(lambda x: get_splt(x))
        elif 'Team' in respdf.columns:
            respdf['NOC'] = respdf['Team'].apply(lambda x: str(x)[0:3])
            respdf['Name'] = respdf['Team'].apply(lambda x: str(x)[3:])
            respdf.drop(columns=['Team'], inplace=True)
        elif 'Boat' in respdf.columns:
            respdf['NOC'] = respdf['Boat'].apply(lambda x: str(x)[0:3])
            respdf['Name'] = respdf['Boat'].apply(lambda x: str(x)[3:])
            respdf.drop(columns=['Boat'], inplace=True)

        respdf['event'] = event
        respdf['discipline'] = disc
        if 'Rank' in respdf.columns:
            respdf = respdf.rename(columns={"Rank":"final_place"})

        # housekeeping on standings: may contain "DNS", "DNF", etc strings...
        respdf['final_place'] = respdf['final_place'].astype(str)
        respdf['final_place'] = respdf['final_place'].apply(lambda x: chknum(x))
        respdf['final_place'] = respdf['final_place'].astype(float)
        respdf['final_place'] = respdf['final_place'].astype(int)
        respdf.fillna(0, inplace=True)

        respdf = respdf.reindex(["discipline","event","NOC","Name","final_place"], axis=1)
        respdf.set_index(['discipline','event','final_place'], drop=False, inplace=True)
        # respdf.dropna(how='all', axis=1, inplace=True)
    else:
        print("simple_event_entry: html parsing errors...\n")
        return None

    return respdf

def scrape_noc_entries(nocfil):
    """
    TODO: as of sept28 2021- have not needed to use this Fx, it needs a bug shakeout!
    get entries for each Olympic discipline for NOCs in 'nocfil'
    uses bs4 (Beautiful Soup) html scraping.
    :param nocfil: file with list of NOCS and end text for html request
    :return:
    """
    entrylst: list = []
    with open(nocfil, mode='r') as infil:
        rows = csv.reader(infil)
    for r in rows:
        disc_dct: dict = {"NOC":r[0], "Name": r[1], "ent_url": r[2]}
        entrylst.append(disc_dct)

    entrydf: pd.DataFrame = pd.DataFrame(columns=["Discipline", "F", "M", "Total"])
    tmprecs: list = []
    for nocx in entrylst:
        noc_url: str = NOC_URL + str(nocx['ent_url'])
        nocdf = pd.read_html(noc_url)
        if len(nocdf) == 1:
            tmpdct: dict = nocdf[0].to_dict("records")
            for ent in tmpdct:
                ent["NOC"] = nocx["NOC"]
                ent["Name"] = nocx["Name"]
            tmprecs.extend(tmpdct)
    entrydf.from_records(tmprecs)

    return entrydf

def process_disc_and_event(dis, gdf: pd.DataFrame):
    """
    gets the final standings for all events for the list of disciplines passed in
    as dis. calls simple_event_entry with pandas read_html to scrape data
    and then processes to generate complete lists for sports at Olympics
    :param dis: list of dict, each entry an Olympic "discipline"
    :param gdf: pd.DataFrame with info on all Olympic events, such as event url ending
    :return:
    """
    event_lst: list = []
    for y in range(len(dis)):
        dis_url = dis[y]['htmlq']
        dis_name = dis[y]['discipline']
        tmpdf: pd.DataFrame = gdf.loc[gdf['Sport'] == dis_name]
        tmpdf.sort_values(by=['Gender','Event'], inplace=True)
        for x in range(len(tmpdf)):
            evt_url = tmpdf.iat[x, 5]
            edf: pd.DataFrame = simple_event_entry(dis_url, evt_url, debug=True)
            if not len(edf) == 0:
                evtrecs = edf.to_dict("records")
                event_lst.append(evtrecs)
    print("\n    sourcing event results complete, %d events scraped\n" %len(event_lst))

    return event_lst

def get_all_medalists(country: str="united-states"):
    """
    mixture of pandas and bs4 to scrape medalist info from Olympics site.
    uses requests as well- short brief on requests parms:
        url – URL for the new Request object.
        params – (optional) Dictionary of GET Parameters to send with the Request.
        headers – (optional) Dictionary of HTTP Headers to send with the Request.
        cookies – (optional) CookieJar object to send with the Request.
        auth – (optional) AuthObject to enable Basic HTTP Auth.
        timeout – (optional) Float describing the timeout of the request.
    - I learned to use the headers included as constant at top of this file, a hacker
    told me it can reduce the incidence of scrapes being rejected/messed with!!

    soup accepts these parsers:  "lxml", "lxml-xml", "html.parser", or "html5lib"

    medal column returned is causing issues, uses img tag and src is an icon file
    (gold,silver, or bronze), also has "alt" text 1,2, or 3 to indicate place.
    example: <img class="medal-icon" src="../medals/big/1.png" alt="1">
    :param country: defaults to united states, identifies which NOCs athletes to list
    :return: pd.DataFrame with all medalists for country plus what event and medal
    """

    def medl(x):
        """
        inner function to replace Medal 'ordinal' (1, 2, or 3) with medal type name
        :param x: str of '1', '2', or '3'
        :return: "gold", "silver" or "bronze"
        """
        return {'1': "gold", '2': "silver", "3": "bronze"}[x]

    full_url = MDLST_URL + country + ".htm"
    page = requests.get(full_url, headers=headers)
    soup = BeautifulSoup(page.text, 'html5lib')
    pd_res = pd.read_html(page.text)[0]

    places = []
    tablex = soup.find("table", {"id":"medal-standings-table"})
    for tr in tablex.findAll("tr"):
        tds = tr.findAll("td")
        for elem in tds:
            # page gives medal icons rather than just place or number, workaround:
            try:
                placetxt = elem.find('img')['alt']
                if str(placetxt) in ["1", "2", "3"]:
                    places.append(placetxt)
            except (HTTPError, TypeError) as err:
                print("exception caught while reading medalists...")
                pass

    pd_res['Medal'] = places
    pd_res['Medal'] = pd_res['Medal'].apply(lambda x: medl(x))
    evt_sum = pd_res.to_dict("records")
    print("sourced %d medalists for %s \n" %(len(evt_sum),country))

    return pd_res, evt_sum