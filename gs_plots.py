"""
plotly chart fx's for Olympic data
"""

import pandas as pd
import plotly.io as pio
import plotly.graph_objects as go
import datetime as dt
import sys
from gs_datadict import GS_COLOR

pio.renderers.default = 'browser'
pio.templates.default = "plotly"
pd.options.plotting.backend = "plotly"
pltly_cfg = {"displayModeBar": False, "showTips": False}

def create_layout():
    """
    creates a plotly graph_objects Layout object instance, with styles which can be
    leveraged by all plots in this app
    :return: go.Figure instance
    """
    gs_lyt = go.Layout(height=800, width=1600,
                       title={'text': "Tokyo Olympics Analysis",
                              'font': {'size': 36, 'family': 'Helvetica Neue UltraLight', 'color': GS_COLOR["offblk"]}
                              },
                       paper_bgcolor=GS_COLOR["ltgry"],
                       font={'size': 18, 'family': 'Helvetica Neue UltraLight', 'color': GS_COLOR["drkblue"]},
                       hovermode="closest",
                       hoverlabel={'font': {'family': 'Copperplate Light', 'size': 16}},
                       hoverdistance=10,
                       legend={'title': {'text': "Marker Legend",
                                         'font': {'size': 18, 'family': 'Helvetica Neue UltraLight',
                                                  'color': GS_COLOR["offblk"]}
                                         },
                               'font': {'size': 14, 'family': 'Copperplate Light', 'color': GS_COLOR["drkblue"]},
                               'bordercolor': GS_COLOR["offblk"],
                               'borderwidth': 2
                               },
                       xaxis={'title': {'text': "Countries and Athletes",
                                        'font': {'size': 28, 'family': 'Helvetica Neue UltraLight',
                                                 'color': GS_COLOR["brown"]}},
                              'linecolor': GS_COLOR["drkgrn"],
                              'rangemode': "normal"
                              },
                       yaxis={'title': {'text': "Olympic Medals",
                                        'font': {'size': 28, 'family': 'Helvetica Neue UltraLight',
                                                 'color': GS_COLOR["brown"]}},
                              'linecolor': GS_COLOR["drkgrn"]
                              },
                       margin=go.layout.Margin(autoexpand=True)
                       )
    gs_lyt.template.data.scatter = [
        go.Scatter(marker=dict(symbol="diamond", size=10)),
        go.Scatter(marker=dict(symbol="circle", size=10)),
        go.Scatter(marker=dict(symbol="triangle-up", size=10)),
        go.Scatter(marker=dict(symbol="hexagon", size=10))
    ]

    gs_lyt.template.data.bar = [
        go.Bar(marker=dict(color=GS_COLOR["bronze"])),
        go.Bar(marker=dict(color=GS_COLOR["silver"])),
        go.Bar(marker=dict(color=GS_COLOR["gold"]))
    ]

    return gs_lyt

def us_medalists(odf):
    """
    show a plot of US medalists
    :param odf: pd.DataFrame with events, medalists, and NOCs
    :return:
    """
    fig = go.Figure(go.Scattergeo())
    fig.update_geos(
        visible=False, resolution=110, scope="usa",
        showcountries=True, countrycolor="Black",
        showsubunits=True, subunitcolor="Blue"
    )
    fig.update_layout(height=300, margin={"r": 0, "t": 0, "l": 0, "b": 0})
    fig.show()

    return

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
    nocs: dict = sort_noc_mdls(mdllst)

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

def plot_groups(cats: list, sprts: list, mdls: list):
    """
    plot top medalist countries by alternative sports groups
    :param cats: list of categories for grouping of sports
    :param sprts: list of Olympic disciplines for each primary group
    :param mdls: list of NOC gold, silver, and bronze for each primary group
    :return:
    """
    # from plotly.subplots import make_subplots
    lay = create_layout()
    lay.title.text = "Results by Primary Sports Groupings, Tokyo Olympics"
    lay.xaxis.title.text = "Primary Groups"
    lay.yaxis.title.text = "Medal Events for Sports in Group"

    # x-axis will be primary sports groups, bars will be sports in each group
    # y-axis will be medals awarded in each sport in the group
    plot_size: int = len(cats)
    pcols: int = 3
    prows: int = int(plot_size / pcols)
    grp_mdlct: list = []
    for grp in mdls:
        grp_mdlct.append(len(grp[0]))

    fig = go.Figure(layout=lay)
    # fig = make_subplots(rows=prows, cols=pcols)

    fig.add_trace(go.Bar(
        x=cats,
        y=grp_mdlct,
        name='Medal Events for Group',
        marker_color='indianred'
    ))

    fig.show(config=pltly_cfg)

    return

def plot_athlete_avg(adf: pd.DataFrame):
    """
    plots the team or sport height and weight averages versus US adult avg, by gender
    :param adf: athlete_df
    :return:
    """
    trk_fld = ["Athletics"]
    ballteam = ["TeamSports"]
    gry_poupn = ["RacquetSports", "Fencing","Sailing"]
    individ = ["MTBCycling", "Skateboarding", "Climbing"]
    the_public = ["GeneralPublic"]
    trc0 = adf[adf["category"].isin(ballteam)]
    trc1 = adf[adf["category"].isin(trk_fld)]
    trc2 = adf[adf["category"].isin(gry_poupn)]
    trc3 = adf[adf["category"].isin(individ)]
    trc4 = adf[adf["category"].isin(the_public)]

    adf = adf[adf["event"] != "Average Adult"]
    frames = [trc0, trc1, trc2, trc3, trc4]
    lay = create_layout()
    lay.title = "Tokyo Olympic Medalist Averages versus US Adults"
    lay.xaxis.title = "Average Weight in Pounds"
    lay.yaxis.title = "Average Height in Inches"
    fig = go.Figure(lay)

    # Add traces
    for trx in frames:
        fig.add_trace(go.Scatter(x=trx["wt_lbs"], y=trx["ht_in"],
                             mode='lines+markers',
                             name='athletes'))

    fig.show(config=pltly_cfg)

    return