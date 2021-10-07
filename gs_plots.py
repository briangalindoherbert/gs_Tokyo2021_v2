"""
plotly chart fx's for Olympic data
"""
import sys

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.io as pio

from gs_datadict import GS_COLOR, TRACE_COLRS, HT_NORM

pio.renderers.default = 'browser'
# pio.templates.default = "plotly"
pd.options.plotting.backend = "plotly"
pltly_cfg = {"displayModeBar": False, "showTips": False}

def create_layout():
    """
    creates a plotly graph_objects Layout object instance, with styles which can be
    leveraged by all plots in this app
    :return: go.Figure instance
    """

    gs_lyt: go.Layout = go.Layout(
        height=900,
        width=1200,
        title={'text': "Tokyo Olympics Analysis",
               'font': {'size': 36, 'family': 'Helvetica Neue UltraLight', 'color': GS_COLOR["offblk"]
                        }},
        paper_bgcolor=GS_COLOR["ltgry"],
        font={'size': 18, 'family': 'Helvetica Neue UltraLight', 'color': GS_COLOR["drkblue"]},
        hovermode="closest",
        hoverlabel={'font': {'family': 'Copperplate Light', 'size': 16}},
        hoverdistance=10,
        legend={
            'title': {'text': "Marker Legend",
                      'font': {
                          'size': 18, 'family': 'Helvetica Neue UltraLight',
                          'color': GS_COLOR["offblk"]}},
            'font': {'size': 14, 'family': 'Copperplate Light', 'color': GS_COLOR["drkblue"]},
            'bordercolor': GS_COLOR["offblk"],
            'borderwidth': 2
            },
        xaxis={'title': {'text': "Countries and Athletes",
                         'font': {'size': 28,
                                  'family': 'Helvetica Neue UltraLight',
                                  'color': GS_COLOR["brown"]}},
               'linecolor': GS_COLOR["drkgrn"],
               'rangemode': "normal"
               },
        yaxis={'title': {'text': "Olympic Medals",
                         'font': {'size': 28,
                                  'family': 'Helvetica Neue UltraLight',
                                  'color': GS_COLOR["brown"]}},
               'linecolor': GS_COLOR["drkgrn"]
               }
        )

    gs_lyt.template.data.scatter = [
        go.Scatter(marker=dict(symbol="diamond", size=10)),
        go.Scatter(marker=dict(symbol="triangle-up", size=10))
        ]

    return gs_lyt

def plot_global(odf):
    """
    update_geos controlled via projections and scope.
    projections for update_geos:  orthographic, natural_earth,
    scope: north_america, usa.  Also- show_countries=True/False
    :param odf:
    :return:
    """
    fig = go.Figure(go.Scattergeo(odf, locations="iso_alpha",
                                  color="continent",  # column to set color of markers
                                  hover_name="country",  # column added to hover information
                                  size="pop",  # size of markers
                                  projection="natural earth"))
    fig.update_geos(projection_type="natural_earth",
        visible=False, resolution=50,
        showcountries=True, countrycolor=GS_COLOR["drkgrn"]
    )
    fig.update_layout(width=800, height=800, margin={"r": 20, "t": 20, "l": 0, "b": 0})
    fig.show()

    return fig

def sort_noc_mdls(mdl: list):
    """
    get total medal count for NOCs, sort by descending order
    :param mdl: list of dict, one for each of Gold, Silver, Bronze
    :return: dict of medal count keyed on NOC
    """
    mdlct: dict = {}
    for x in range(3):
        tmpl = mdl[x][1]
        if isinstance(tmpl, dict):
            for k, v in tmpl.items():
                if k not in mdlct:
                    mdlct[k] = v
                else:
                    mdlct[k] = mdlct[k] + v

    mdlct = {k: mdlct[k] for k in sorted(mdlct, key=lambda x: mdlct.get(x), reverse=True)}

    return mdlct

def medals_barplot(mdllst: list, allnoc: list, slctnoc: list=None):
    """
    build a stacked bar chart of medals for NOCs
    :param mdllst: 3 lists for count of Gold, Silver, and Bronze by NOC
    :param allnoc: list of dict {NOC:country_name} for all countries in Olympics
    :param slctnoc: subset list of NOCs to plot, 8 or less to avoid crowding
    :return:
    """

    # use list of NOCs from parm 'select', else just get top 5
    if slctnoc:
        glst: list = []
        slst: list = []
        blst: list = []
        totlst: list = []
        for ctry in slctnoc:
            glst.append(mdllst[0][1].get(ctry))
            slst.append(mdllst[1][1].get(ctry))
            blst.append(mdllst[2][1].get(ctry))
        for lstx in [glst, slst, blst]:
            if None in lstx:
                mlen = len(lstx)
                for idx in range(mlen):
                    if lstx[idx] is None:
                        lstx[idx] = 0
        for x in range(len(glst)):
            totlst.append(glst[x] + slst[x] + blst[x])
        longnames: list = [allnoc[x] for x in slctnoc]

    else:
        sys.exit(0)

    lyt: go.Layout = create_layout()

    lyt.template.data.bar = [
        go.Bar(marker=dict(color=GS_COLOR["bronze"])),
        go.Bar(marker=dict(color=GS_COLOR["silver"])),
        go.Bar(marker=dict(color=GS_COLOR["gold"]))
    ]

    fig = go.Figure(data=[go.Bar(name='Bronze', x=slctnoc, y=blst, meta=longnames,
                                 hovertemplate='<b>%{meta}</b> %{y}'),
        go.Bar(name='Silver', x=slctnoc, y=slst, meta=longnames,
               hovertemplate='<b>%{meta}</b> %{y}'),
        go.Bar(name='Gold', x=slctnoc, y=glst, meta=longnames,
               customdata=totlst,
               hovertemplate='<b>%{meta}</b> %{y}' +
                             '<br>total: %{customdata}'
               ),
    ], layout=lyt)

    # Change the bar mode
    fig.update_layout(title_text='Total Medals won by NOC, Tokyo Olympics', barmode='stack',
                      colorscale=None)
    fig.show(config=pltly_cfg)

    return

def plot_groups(p_d: dict, d_e: dict):
    """
    plot top medalist countries by alternative sports groups
    :param p-d: dict of key=primary group, val=list of disciplines
    :param d_e: dict of key=discipline, val=events
    :return:
    """

    # catlst= x-axis categories, sprtlst=stacked bars, sprtcnt= y-axis bar size
    catlst: list = []
    sprtlst: list = []
    sprtcnt: list = []
    for k, v in p_d.items():
        catlst.append(k)
        sprtlst.append(v)
        tmp: list = []
        for sp in v:
            tmp.append(d_e[sp])
        sprtcnt.append(tmp)

    cat_rpt: list = []
    for x in range(len(catlst)):
        cat_rpt.append([catlst[x] for y in range(len(sprtlst[x]))])

    df_dct: list = []
    for catr, bars, bary in zip(cat_rpt, sprtlst, sprtcnt):
        for x in range(len(catr)):
            df_dct.append({'categ': catr[x], 'sport': bars[x], 'medalct': bary[x]})

    primarydf = pd.DataFrame.from_records(df_dct)
    grpsrt_df = primarydf.groupby(by="categ").sum().sort_values("medalct", ascending=False)
    grpsrtd: list = grpsrt_df.index.values.tolist()

    lay = create_layout()
    lay.xaxis.title.text = "Primary Groups"
    lay.yaxis.title.text = "Medal Events for Sports in Group"
    lay.width = 1500
    lay.legend.title = "Sports Groupings"
    fig = go.Figure(layout=lay)

    grp_rank: int = 2000
    grpidx: int = 0
    for catx in grpsrtd:
        grpdf: pd.DataFrame = primarydf.loc[primarydf.categ == catx, ]
        fig.add_trace(go.Bar(name=catx, x=grpdf["categ"], y=grpdf["medalct"],
                             meta=grpdf["sport"],
                             hovertemplate='Sport: %{meta}<br>' +
                                           'Medal Events: %{y}',
                             legendrank=grp_rank,
                             text=grpdf["sport"],
                             marker=dict(color=grpidx, colorscale="viridis"),
                             ))
        grp_rank = grp_rank - 100
        grpidx += 1

    fig.add_annotation(text="Most of my groups are self-explanatory, a few aren't :-)<br>" +
                            "  just a fun way to group the 339 medal events<br>" +
                            "freeride= sports with external locomotion<br>" +
                            "swim=triathlon is more than this, but it fits<br>" +
                            "balance and spinflip= what is most elemental skill?<br>" +
                            "and modern pentathlon just doesn't group ;-)",
                       xref="paper", yref="paper",
                       x=0.8, y=0.9,
                       borderwidth=1, bordercolor=GS_COLOR["offblk"],
                       showarrow=False)

    fig.update_layout(title_text='Total Medals per Primary Group', barmode='stack',
                      colorscale=None)
    fig.show(config=pltly_cfg)

    return primarydf

def plot_group_nocs(g_n: list, slctd: str):
    """
    for a selected group, plot the medalist countries
    :param g_n: all medalists by group
    :param slctd: name of selected group
    :return:
    """

def plot_athlete_avg(padf: pd.DataFrame):
    """
    plots the team or sport height and weight averages versus US adult avg, by gender
    :param padf: precalculated subset from athlete_df
    :return:
    """

    ballteam = ["TeamSports"]
    trk_fld = ["Athletics"]
    individ = ["Fencing", "Sailing", "Cycling-MTB", "Skateboarding", "Climbing"]
    the_public = ["US_Public"]
    pltsym: dict = {"men": "triangle-up", "women": "circle"}

    trc0 = padf[(padf["category"].isin(ballteam)) & (padf["gender"] == "Women")]
    trc1 = padf[(padf["category"].isin(ballteam)) & (padf["gender"] == "Men")]
    trc2 = padf[(padf["category"].isin(trk_fld)) & (padf["gender"] == "Women")]
    trc3 = padf[(padf["category"].isin(trk_fld)) & (padf["gender"] == "Men")]
    trc4 = padf[padf["category"].isin(individ) & (padf["gender"] == "Women")]
    trc5 = padf[padf["category"].isin(individ) & (padf["gender"] == "Men")]

    # split and sort rows with general public height and weight by gender & age group
    trc6 = padf[padf["category"].isin(the_public) & (padf["gender"] == "Women")]
    trc6a = trc6[trc6["event"].isin(["Adult_25"])]
    trc6 = trc6[trc6["event"].isin(["Adult_All"])]
    trc7 = padf[padf["category"].isin(the_public) & (padf["gender"] == "Men")]
    trc7a = trc7[trc7["event"].isin(["Adult_25"])]
    trc7 = trc7[trc7["event"].isin(["Adult_All"])]

    for pubdf in [trc6, trc6a, trc7, trc7a]:
        pubdf = pubdf.sort_values(["wt_lbs"], ignore_index=True)

    frames = [
        [trc0, "Team sports women", TRACE_COLRS[0], pltsym["women"]],
        [trc1, "Team sports men", TRACE_COLRS[0], pltsym["men"]],
        [trc2, "Track-n-Field women", TRACE_COLRS[1], pltsym["women"]],
        [trc3, "Track-n-Field men", TRACE_COLRS[1], pltsym["men"]],
        [trc4, "Individual sports women", TRACE_COLRS[2], pltsym["women"]],
        [trc5, "Individual sports men", TRACE_COLRS[2], pltsym["men"]]
    ]
    frame2 = [
        [trc6, "US Adult Women", TRACE_COLRS[3], pltsym["women"]],
        [trc6a, "US Women 20-29", TRACE_COLRS[4], pltsym["women"]],
        [trc7, "US Adult Men", TRACE_COLRS[3], pltsym["men"]],
        [trc7a, "US Men 20-29", TRACE_COLRS[4], pltsym["men"]]
    ]

    lay = create_layout()
    lay.title = "Tokyo Olympic Medalist Averages versus US Adults"
    lay.xaxis.title = "Average Weight in Pounds"
    lay.yaxis.title = "Average Height in Inches"
    fig = go.Figure(layout=lay)

    # Add traces for Olympic athletes first, then avg adults, each split by gender:
    for tr in frames:
        fig.add_trace(go.Scattergl(x=tr[0]["wt_lbs"], y=tr[0]["ht_in"],
                                   meta=tr[0]["name"],
                                   fillcolor=tr[2], name=tr[1],
                                   customdata=tr[0]["gender"], mode='markers',
                                   hovertemplate="<b>%{meta} -%{customdata}</b>" +
                                                 "<br>Height: %{y:.1f}''</br>" +
                                                 "<br>Weight: %{x:.1f} lbs.</br>",
                                   marker=dict(color=tr[2], symbol=tr[3], size=12,
                                               line=dict(width=1, color=GS_COLOR["offblk"])
                                               )
                                   )
                      )

    for tr in frame2:
        fig.add_trace(go.Scattergl(x=tr[0]["wt_lbs"], y=tr[0]["ht_in"], meta=tr[0]["name"],
                                   fillcolor=tr[2], name=tr[1], customdata=tr[0]["gender"],
                                   mode='lines+markers',
                                   line=dict(width=1, dash='dash', color=tr[2]),
                                   hovertemplate="<b>%{meta} -%{customdata}</b>" +
                                                 "<br>Height: %{y:.1f}''</br>" +
                                                 "<br>Weight: %{x:.1f} lbs.</br>",
                                   marker=dict(color=tr[2], symbol=tr[3], size=12)
                                   ))

    fig.add_annotation(text="Plot of Tokyo Olympic Medalists in 45 medal events<br>" +
                            "connected points show US adult women and men, avg to 75th pctl<br>" +
                            "and 20-29 age group, avg to 75th pctl",
                       xref="x", yref="y",
                       x=250, y=60,
                       borderwidth=1, bordercolor=TRACE_COLRS[5],
                       showarrow=False)

    fig.update_traces(textfont_size=12)
    fig.show(config=pltly_cfg)

    return

def generate_norm_distributions(adult_avg: list, obsrvs: int= 30000):
    """
    gives info on the precalculated rows from the athlete dataframe
    :param adult_avg: list of dict: male and female mean and std dev for height
    :return:
    """
    print("\ngenerating pseudorandom samples based on NCHS 2018 Report on US Adults")
    print("    parameter set to %d observations per gender" %obsrvs)
    np.random.seed(48)
    norms: list = []
    for subj in adult_avg:
        if isinstance(subj, dict):
            gauss: np.ndarray = subj['stdev'] * np.random.randn(obsrvs) + subj['height']
            print('    %s: avg height=%.1f, std dev=%.1f'
                  % (subj['ptype'], round(gauss.mean(), ndigits=1), np.std(gauss)))
            norms.append({subj['ptype']: gauss})
        else:
            print("Generate_Norm_Distributions: Invalid Value for adult_avg parameter")
            return None

    print("    %d normal distributions returned" %len(norms))

    return norms

def height_vs_norm(adf: pd.DataFrame):
    """
    plot a normal distribution curve for US adult heights (one each for Women and Men)
    and show our sampled Olympic medalist and US team athlete heights in relation to it.
    :param adf: pd.DataFrame with select athlete heights to plot against adult avg.
    :return:
    """

    # might need this if I decide to put a secondary y axis for the scatter plots:
    from plotly.subplots import make_subplots
    lay = create_layout()
    lay.margin = {'l': 50, 'r': 50, 't': 50, 'b': 50}
    lay.title = "US Adults vs Olympic Medalists"
    lay.xaxis.title = "Height in Inches"
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    ht_lst: list = generate_norm_distributions(HT_NORM)
    clrs: list = [GS_COLOR["drkblue"], GS_COLOR["magenta"]]
    # this section plots histograms- one each for height of adult men and women
    for htd, c in zip(ht_lst, clrs):
        if isinstance(htd, dict) & (len(htd) == 1):
            (k, v), = htd.items()
            avg: float = round(np.mean(v), ndigits=1)
            stdv: float = round(np.std(v), ndigits=1)
            fig.add_trace(go.Histogram(
                name=k,
                x=v,
                xbins=dict(start=(avg - (3 * stdv)), end=(avg + (3 * stdv)), size=0.2),
                histnorm="probability",
                marker_color=c,
            ), secondary_y=False)
            # add vertical line for mean for both adult men and women:
            fig.add_shape(type="line", name=k,
                          xref="x", yref="y domain",
                          x0=avg, y0=0, x1=avg, y1=1.0,
                          line=dict(color=GS_COLOR["offblk"], width=2),
                          secondary_y=False
                          )
            # describe what each of the lines represents:
            fig.add_annotation(
                xref="x", yref="y domain",
                x=avg, y=0.95,
                text=str(k) + " avg: " + str(avg),
                ax=-30, ay=-20,
                showarrow=True,
                arrowhead=1,
                secondary_y=False
            )

    # convert dataframe, remove non-athlete rows, strip down to end values for height
    ath_only: list = adf[adf.category != "US_Public"].to_dict("records")
    ath_plt: list = ath_only[0:1] + ath_only[2:6] + ath_only[7:9] + ath_only[10:14]
    ath_plt = ath_plt + ath_only[17:21] + ath_only[23:27] + ath_only[29:31] + ath_only[35:]
    ath_plt = sorted(ath_plt, key=lambda x: x.get("ht_in"), reverse=True)
    # ath_plt = ath_only[-6:]

    # create lists for attributes of the olympic athlete plots to add with histogram
    pltsym: dict = {"men": "diamond", "women": "triangle-up"}
    ht_plt: list = []
    nam_plt: list = []
    y_sprt: list = []
    clr_plt: list = []
    sym_plt: list = []
    for ath in ath_plt:
        ht_plt.append(ath["ht_in"])
        nam_plt.append(ath["name"])
        y_sprt.append(ath["event"])
        if str(ath["gender"]).startswith("Men"):
            clr_plt.append(GS_COLOR["drkblue"])
            sym_plt.append(pltsym["men"])
        else:
            clr_plt.append(GS_COLOR["magenta"])
            sym_plt.append(pltsym["women"])

    fig.add_trace(go.Scatter(x=ht_plt, y=y_sprt, name="Olympic_Medalists",
                             text=nam_plt,
                             mode="markers",
                             marker=dict(color=clr_plt, symbol=sym_plt, size=12,
                                         line=dict(width=1, color=TRACE_COLRS[5])
                                         ),
                             textfont=dict(size=8)
                             ), secondary_y=True)

    fig.update_layout(lay, overwrite=False)
    fig.update_yaxes(title_text="Probability Distribution of US Adult Height", secondary_y=False)
    fig.update_yaxes(title_text="Olympic Medalists Avg Height, by Sport", secondary_y=True)
    fig.update_layout(barmode='overlay')
    fig.show(config=pltly_cfg)

    return
