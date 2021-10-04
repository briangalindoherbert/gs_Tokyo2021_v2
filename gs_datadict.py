"""
constants used in Tokyo2021 Python app:
CORE folders for app input and output, and file names

some linked to plotly, for attributes like map projections
"""
RAWDIR: str = '/Users/bgh/dev/pydev/gs_Tokyo2021/rawdata/'
OUTDIR: str = '/Users/bgh/dev/pydev/gs_Tokyo2021/output/'

nocf: str = 'country_codes.csv'
discf: str = 'disciplines.csv'
evts_byrow_f: str = 'medalevents_byrow_2021-09-30.csv'
timelinef: str = 'medals_bydate.csv'
athlete_f: str = 'athletes_2021-09-30.csv'
evtresults_f: str = 'resultsbak_2021-09-30.csv'
medalists_f: str = 'medalists_2021-09-30.csv'

NOC_URL: str = "https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/"
EVT_URL: str = "https://olympics.com/tokyo-2020/olympic-games/en/results/"
MDLST_URL: str = "https://olympics.com/tokyo-2020/olympic-games/en/results/all-sports/"\
                     "noc-medalist-by-sport-"

GS_COLOR = {"green": "rgb(0, 204, 102)",
         "drkgrn": "rgb(0, 102, 0)",
         "brown": "rgb( 102, 51, 51)",
         "grey": "rgb( 153, 153, 153)",
         "ltgry": "rgb(204, 204, 204)",
         "drkblue": "rgb(0, 102, 153)",
         "ltblue": "rgb(0, 153, 255)",
         "orange": "rgb(255, 102, 51)",
         "gold": "rgb(204,153,51)",
         "bronze": "rgb(153,102,0)",
         "silver": "rgb(153,153,153)",
         "magenta": "rgb(255, 51, 255)",
         "purple": "rgb(102, 0, 153)",
         "offblk": "rgb(51, 51, 51)",
         "beige": "rgb(204, 204, 153)",
         "red": "rgb(255, 51, 51)"}

go_projection: list = ("airy", "aitoff", "albers", "albers usa", "august", "azimuthal equal area",
                       "azimuthal ", "equidistant", "baker", "bertin1953", "boggs",
                       "bromley", "conic conformal", "conic equal area",
                       "conic equidistant", "craig", "craster", "cylindrical equal area",
                       "cylindrical stereographic", "eckert1", "eckert5", "eckert6",
                       "eisenlohr", "equirectangular", "fahey", "foucaut", "foucaut sinusoidal",
                       "ginzburg5", "ginzburg8", "ginzburg9", "gnomonic", "hyperelliptical",
                       "kavrayskiy7", "lagrange", "larrivee", "laskowski", "mercator", "miller",
                       "mt flat polar parabolic", "mt flat polar quartic", "natural earth",
                       "natural earth1", "natural earth2", "nicolosi", "orthographic",
                       "patterson", "peirce quincuncial", "polyconic", "rectangular polyconic",
                       "robinson", "satellite", "sinusoidal", "stereographic", "times",
                       "transverse mercator", "van der grinten", "van der grinten4", "wagner6",
                       "wiechel", "winkel tripel", "winkel3")

