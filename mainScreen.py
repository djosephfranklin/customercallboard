import base64
import json
import os
from textwrap import dedent

import dash
import dash_html_components as html
import dash_core_components as dcc
import dash_bootstrap_components as dbc
import materialdashboard as md
import dash_ag_grid as dag
from dash import callback, ctx
from dash.dependencies import Input, Output, State, ALL
import openai
import plotly.graph_objects as go


@callback(
    Output("livetracker", "children"),
    [Input("analyse", "n_clicks"), Input("od", "n_clicks")]
)
def livetrackerupdate(n_clicks):
    if ctx.triggered_id == "analyse":
        print("Catch")
        transcript = '''json {
  "uuid": "17013f35-8693-487b-a88a-020e48d67825",
  "transcripted": "Speaker 1: Good morning, Sarah. How can I assist you today? Hey \nSpeaker 2: Samantha. I'm interested in exploring investment options, but I'm more comfortable with bonds. \nSpeaker 1: I understand bonds are a safe choice, but have you considered diversifying your \nSpeaker 2: portfolio with a mutual \nSpeaker 1: fund? We have a solid mutual fund low-volatility Equity portfolio that offers High returns and quarterly dividends. It has a 70% spread in the US Equity market and 30% in fixed-income. It has been performing well in the market for a long time and it's a good fun to start investing. I'm not \nSpeaker 2: sure about mutual funds. I've always preferred bonds because they feel safer to me while \nSpeaker 1: bonds are safe. Your portfolio is already heavily invested in them diversifying with this mutual fund could balance your Investments and potentially yield higher Returns the US market portion provides growth potential while the fixed-income part offers stability. I \nSpeaker 2: see the point But I'll have to think about it Mom's just feel more secure to me. \nSpeaker 1: I understand it's important to feel secure in your Investments take your time. But remember that diversifying can protect your portfolio from Market volatility and enhance overall returns if you have any questions or need more information, I'm here to help.",
  "score": "20%",
  "scoreReason": "The banker uses suggestive words like 'consider' and 'could' instead of stronger verbs like 'should' or 'must', indicating a softer approach focused on recommendations rather than forceful directives.",
  "actionable": "Potential Lead",
  "clientRequested": "BND:Bonds:BUY:",
  "orderarray": [
    {
      "productType": "MF",
      "productName": "low-volatility Equity portfolio",
      "amount":""}]
}'''
        transcript = transcript.replace("json", "")
        transcript = json.loads(transcript, strict=False)
        return livetracker(transcript)
    else:
        return None


@callback(
    Output("popup", "open"),
    Input("od", "n_clicks")
)
def openPopUp(n_clicks):
    if ctx.triggered_id == "od":
        return True
    elif ctx.triggered_id == "close":
        return False
    else:
        return False


def score(scoreValue):
    score = int(scoreValue.strip('%'))
    scoreValue = score
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=scoreValue,
        mode="gauge+number+delta",
        title={'text': "Enforcement Score"},
        gauge={'axis': {'range': [None, 100]},
               'steps': [
                   {'range': [0, 40], 'color': "green"},
                   {'range': [40, 60], 'color': "yellow"},
                   {'range': [60, 100], 'color': "red"}],
               'threshold': {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': scoreValue}}))
    return fig


def livetracker(transcript):
    encoded_image = base64.b64encode(open('assets/mic.svg', 'rb').read()).decode()
    # transcript['transcripted'].replace( /(?:\r\n|\r|\n)/g, '<br>')

    conversations = str(transcript['transcripted']).split("\n")

    transcript_ = md.Paper(elevation=3, style={"position": "relative", "width": "auto", "height": "280px"}, children=[
        # {"uuid":"", "transcripted" : "", "score":"", "actionable" :"", "orderarray" : ""},

        md.Typography("UUID: " + transcript['uuid'], style={"padding": "20px"}),

        md.Card(children=[md.Typography(conversation) for conversation in conversations],
                style={"padding-top": "10px", "padding-bottom": "10px", 'maxHeight': '60%', 'overflow': 'auto'}),
        md.Icon(className="bi bi-mic-fill"),

        # md.TableContainer(children=[
        #     md.TableHead(transcript['uuid'], style={"padding":"2px"}),
        #     md.TableBody(children=[md.TableRow(transcript['transcripted'], style={"padding":"2px", 'maxHeight': '40px', 'overflow': 'auto'}),
        #                            ]),
        #     md.TableFooter(
        #         html.Img(src="data:image/png;base64,{}".format(encoded_image), height="2rem", width="auto"))
        # ])
    ])
    # logo = md.TableContainer(children=[md.TableRow(children=[md.TableCell(style={"background-color": "green"}, height="10px", width="20px"), md.TableCell(children=[md.Icon(className="bi bi-record2", style={"color":"black"})],style={"background-color": "yellow"}, height="10px", width="20px"), md.TableCell(style={"background-color": "red"}, height="10px", width="20px")])])
    return dbc.Row([dbc.Col(md.Paper(dcc.Graph(style={"position": "relative", "width": "280px", "height": "280px"},
                                               figure=score(transcript['score'])), elevation=3), md=3),
                    dbc.Col(transcript_, md=9)])


def Header(name, app, id):
    title = html.H4(name, style={"margin-top": 5, "padding-top": "10px"})
    if id == "1":
        logo = html.H4("RM Logged In: RM09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    if id == "3":
        logo = html.H4("Customer: CUS09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    if id == "2":
        return dbc.Row([dbc.Col(
            children=[title, md.Button(children=[md.Icon(className="bi bi-headset"), "Call Live"], id="callrecord")],
            md=8)])
    else:
        return dbc.Row([dbc.Col(title, md=8)])


def EarlierConversations(name, app):
    title = html.H5(name, style={"margin-top": 5, "padding-top": "10px"})
    columnDefs = [
        {"field": "UUID", "checkboxSelection": True},
        {"field": "CustomerID"},
        {"field": "Date"},
        {"field": "Quick Hint"},
        {"field": "Actionable",
         "cellRenderer": "Button",
         "cellRendererParams": {"className": "btn btn-success"}, },
        {"field": "Score"},
    ]

    rowData = [
        # {"UUID": "CUS01234-30-001",
        #  "CustomerID": "CUS01234",
        #  "Date": "30-July-2024",
        #  "Playback": "PLAYBACK-001.wav",
        #  "Orders": "4",
        #  "Quick Hint" : "Switch-2",
        #  "Status" : "Inprogress",
        #  "Actionable" : "Initiate,#119dff",
        #  "Score": "Recommanded"
        #  },
        {"UUID": "CUS01234-30-003",
         "CustomerID": "CUS01234",
         "Date": "30-July-2024",
         "PLAYBACK": "PLAYBACK-001.wav",
         "Orders": "4",
         "Quick Hint": "Buy-1",
         "Actionable": "Miss Lead,1",
         "Score": "Recommanded"
         },
        {"UUID": "CUS01234-30-003",
         "CustomerID": "CUS01234",
         "Date": "30-July-2024",
         "PLAYBACK": "PLAYBACK-001.wav",
         "Orders": "4",
         "Quick Hint": "Buy-8",
         "Actionable": "Potential Lead,2",
         "Score": "Recommanded"
         },
        {"UUID": "CUS01234-30-002",
         "CustomerID": "CUS01234",
         "Date": "30-July-2024",
         "PLAYBACK": "PLAYBACK-001.wav",
         "Orders": "4",
         "Quick Hint": "Sell-1",
         "Actionable": "Completed,3",
         "Score": "Recommanded"
         },
    ]

    tableData = dag.AgGrid(
        id="styling-selections",
        className="ag-theme-alpine selection",
        columnSize="sizeToFit",
        columnDefs=columnDefs,
        rowData=rowData,
        dashGridOptions={"animateRows": False},
    ),
    return dbc.Row([dbc.Col(tableData)])


def textbox(text, box="AI", name="Philippe"):
    text = text.replace(f"{name}:", "").replace("You:", "")
    style = {
        "max-width": "60%",
        "width": "max-content",
        "padding": "5px 10px",
        "border-radius": 25,
        "margin-bottom": 20,
    }

    if box == "user":
        style["margin-left"] = "auto"
        style["margin-right"] = 0

        return dbc.Card(text, style=style, body=True, color="primary", inverse=True)

    elif box == "AI":
        style["margin-left"] = 0
        style["margin-right"] = "auto"

        thumbnail = html.Img(
            src=app.get_asset_url("Philippe.jpg"),
            style={
                "border-radius": 50,
                "height": 36,
                "margin-right": 5,
                "float": "left",
            },
        )
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)

        return html.Div([thumbnail, textbox])

    else:
        raise ValueError("Incorrect option for `box`.")


description = """
Philippe is the principal architect at a condo-development firm in Paris. He lives with his girlfriend of five years in a 2-bedroom condo, with a small dog named Coco. Since the pandemic, his firm has seen a  significant drop in condo requests. As such, he’s been spending less time designing and more time on cooking,  his favorite hobby. He loves to cook international foods, venturing beyond French cuisine. But, he is eager  to get back to architecture and combine his hobby with his occupation. That’s why he’s looking to create a  new design for the kitchens in the company’s current inventory. Can you give him advice on how to do that?
"""

# Authentication
openai.api_key = os.getenv("OPENAI_KEY")

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP, md.external_stylesheets, dbc.icons.BOOTSTRAP,
                                                dbc.icons.FONT_AWESOME, dbc.themes.PULSE],
                suppress_callback_exceptions=True)
server = app.server

# Load images
IMAGES = {"Philippe": app.get_asset_url("Philippe.jpg")}

# Define Layout
conversation = html.Div(
    html.Div(id="display-conversation"),
    style={
        "overflow-y": "auto",
        "display": "flex",
        "height": "calc(90vh - 132px)",
        "flex-direction": "column-reverse",
    },
)

controls = dbc.InputGroup(
    children=[
        md.IconButton(),
        dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),

        md.Icon(className="bi bi-mic-fill", id="record"),
        dbc.Button("Submit", id="submit"),
    ]
)


def _make_grid_item(size) -> md.Grid:
    return md.Grid(
        # Children components should have the `item=True` attribute.
        item=True,
        # The size (in number of columns) of the item can be set depending on the screen size (xs, sm, md, lg, xl).
        # The size for each screen size can be set, or some can be left unspecified.
        # In this case, only `xs` is used, which means that the layout will always be the same, independently of the
        # screen size (hence will be unresponsive).
        xs=3,
        children=[_make_paper_item(f"{size[0]}", size[1])],
    )


def _customer_view(text: str) -> md.Paper:
    return md.Paper(
        children=[md.Icon(), md.Typography("Customer 1"), md.Typography("Last Activity"), md.Typography("Status"),
                  md.Typography("Button")],
        style={
            "padding": "20px",
            "height": "50px",
            "position": "relative",
            "backgroundColor": "#eeeeee",
        },
    )


def _make_paper_item(text: str, img) -> md.Paper:
    print(text)
    if True:
        '''
        <Box sx={{ position: 'relative', display: 'inline-flex' }}>
      <CircularProgress variant="determinate" {...props} />
      <Box
        sx={{
          top: 0,
          left: 0,
          bottom: 0,
          right: 0,
          position: 'absolute',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
        }}
      >
        <Typography variant="caption" component="div" color="text.secondary">
          {`${Math.round(props.value)}%`}
        </Typography>
      </Box>
    </Box>
        '''
        return md.Paper(
            children=[md.Box(style={'position': 'relative', 'display': 'inline-flex'},
                             children=[
                                 md.Typography(text.split(":")[0], variant="h6"),
                                 #md.CircularProgress(variant="determinate", size="8rem", value=80, color="primary"),

                                 ],
                             ),
                      md.Typography(text.split(":")[1], variant="h4"),
                      md.Box(style={'position': 'relative', 'display': 'inline-flex', 'height':'30%', 'width':'30%'},
                             children=[img])

                      ],
            style={

            "padding-top": "10px",
            "padding": "10px",
                "height": "200px",
                "textAlign": "center",
                # "backgroundColor": "#eeeeee",
            },
        )
    return md.Paper(
        children=[text],
        style={
            "padding-top": "10px",
            "padding": "10px",
            "height": "200px",
            "textAlign": "center",
            "backgroundColor": "#eeeeee",
        },
    )

total_customer_img = dash.html.Img(src=app.get_asset_url("total-number-of-users.png"))
potential_leads_img = dash.html.Img(src=app.get_asset_url("leads.png"))
missed_leads_img = dash.html.Img(src=app.get_asset_url("missed.svg"))
fullfiled_img = dash.html.Img(src=app.get_asset_url("fulfill.png"))

app.layout = dbc.Container(
    fluid=True,
    style={"--bs-gutter-x": "0rem"},
    children=[
        md.Paper(square=True,
                 children=[
                     md.Grid(style={"flexGrow": "2"}, container=True, xs=12, children=[
                         md.Grid(item=True, xs=1, children=[
                             md.Icon(className="bi bi-c-square-fill"),
                             # md.Typography("RM Conversation Dashbord", variant="h4", style={"width": "90%","color": "#3338FF"})
                         ]),
                         md.Grid(item=True, xs=6, children=[
                             md.Typography("RM Conversation Dashbord", variant="h4",
                                           style={"width": "90%", "color": "#FFFFFF"})
                         ]),
                         md.Grid(item=True, xs=3, children=[

                         ]),
                         md.Grid(item=True, xs=1, children=[
                             md.Avatar(children="SM", style={"bgcolor": "#3368FF", "float": "right", }),
                             md.Icon(className="bi bi-bell-fill", style={"color": "white", "height": "2em"})
                         ]),
                         md.Grid(item=True, xs=1, children=[
                             md.Icon(className="bi bi-box-arrow-right",
                                     style={"color": "white", "float": "right", "height": "2em"}),

                         ]),
                     ])], style={"background-color": "#1a3347", "padding": "10px", "height": "60px"}),
        md.Container(
            # The max width is specified as a screen size.
            maxWidth="xl",
            style={"backgroundColor": "#eeeeee"},
            children=[
                md.Grid(

                    style={"padding-top": "10px", "padding-bottom": "10px"},
                    # The container component should have the `container=True` attribute.
                    container=True,
                    # The number of columns determines the maximum sum of sizes of items in a single row.
                    # 12 is the default and doesn't need to be specified.
                    columns=12,
                    # Row and column spacing can be set independently, or the `spacing` attribute can be used to set both.
                    rowSpacing=2,
                    columnSpacing=2,
                    children=[_make_grid_item(s) for s in [("Total Customers:210",total_customer_img), ("Potential Leads:30",potential_leads_img), ("Missed Leads:10",missed_leads_img), ("Fulfilled:10",fullfiled_img)]]

                ),
                md.Paper(
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "position": "relative",
                        "backgroundColor": "#ffffff",
                    },
                    children=[
                        md.Typography("Customer Base", variant="h5"),
                        md.List(
                            dense=True,
                            children=[
                                md.ListItem(
                                    children=[
                                        md.ListItemAvatar(children="SW", ),
                                        md.ListItemText(primary="Sarah Willie", secondary="Citi Gold - Last Spoke Today 10:20 AM"),

md.ListItemText(primary="Recommended", secondary="Citi Gold"),
md.ListItemText(primary="Preferred", secondary="Citi Gold"),
md.ListItemText(primary="Converted Investment", secondary="BUY"),
                                        md.Button("View Details")]),
                                md.ListItem(
                                    children=[
                                        md.ListItemAvatar(children="BI", ),
                                        md.ListItemText(primary="BRUCE IVAN", secondary="Citi Gold"),

                                        md.ListSubheader(children=[
                                            md.Typography("Last Spoke by 12:10PM, Today", align="left",
                                                          style={"backgroundColor": "#eeeeee"}, variant="h6")]),

                                        # md.ListSubheader(children=[md.Typography("Potential Lead", align="left", variant="h6")]),
                                        md.Button("Potential Lead")]),
                                md.ListItem(
                                    children=[
                                        md.ListItemAvatar(children="KK", ),
                                        md.ListItemText(primary="KARUP KUSMAN",
                                                        secondary="Last Spoke by 11:23AM, Today"),
                                        # md.ListSubheader(children=[md.Typography("Potential Lead", align="left", variant="h6")]),
                                        md.Button("Missed Lead")]),
                                md.ListItem(
                                    children=[
                                        md.ListItemAvatar(children="PE", ),
                                        md.ListItemText(primary="PETER EPIC", secondary="Last Spoke by 10:00AM, Today"),
                                        # md.ListSubheader(children=[md.Typography("Potential Lead", align="left", variant="h6")]),
                                        md.Button("Potential Lead", style={"align": "left"})])
                                # md.ListItemButton(placeholder="View Details")])
                            ]
                        )
                    ]
                )
            ],
        )

        # Header("RM Conversation Tracker", app, "1"),
        # html.Hr(),
        # Header("Customer in Live : CUS02012", app, "2"),
        # html.Div(id="livetracker"),
        # html.Hr(),
        # Header("Conversation History", app, "4"),
        # html.Div(children=[md.Button("Analyse", id="analyse"), md.Button("Order Details", id="od")]),
        # EarlierConversations("Conversation History", app),
        # dcc.Store(id="store-conversation", data=""),
        #
        # conversation,
        # controls,
        # dbc.Spinner(html.Div(id="loading-component")),
    ],
)


@app.callback(
    Output("display-conversation", "children"), [Input("store-conversation", "data")]
)
def update_display(chat_history):
    return [
        textbox(x, box="user") if i % 2 == 0 else textbox(x, box="AI")
        for i, x in enumerate(chat_history.split("<split>")[:-1])
    ]


@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""


@app.callback(
    [Output("store-conversation", "data"), Output("loading-component", "children")],
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
    [State("user-input", "value"), State("store-conversation", "data")],
)
def run_chatbot(n_clicks, n_submit, user_input, chat_history):
    if n_clicks == 0 and n_submit is None:
        return "", None

    if user_input is None or user_input == "":
        return chat_history, None

    name = "Philippe"

    prompt = dedent(
        f"""
    {description}

    You: Hello {name}!
    {name}: Hello! Glad to be talking to you today.
    """
    )

    # First add the user input to the chat history
    chat_history += f"You: {user_input}<split>{name}:"

    model_input = prompt + chat_history.replace("<split>", "\n")

    # response = openai.Completion.create(
    #     engine="davinci",
    #     prompt=model_input,
    #     max_tokens=250,
    #     stop=["You:"],
    #     temperature=0.9,
    # )
    # model_output = response.choices[0].text.strip()

    chat_history += f"{user_input}<split>"

    return chat_history, None


if __name__ == "__main__":
    app.run_server(debug=True)
