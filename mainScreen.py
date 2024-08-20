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
import speech_recognition as sr
import vertexai
import vertexai.preview.generative_models as generative_models
from dash.dependencies import Input, Output
from google.cloud import speech_v1p1beta1 as speech
from vertexai.generative_models import GenerativeModel
from PIL import Image
import openai
import plotly.graph_objects as go

customers = [{'UUID': 'CUS68725-30-001', 'country': 'us', 'customerid': 'C42484', 'RelationshipID': 'R1251', 'Customername': 'Samantha Hanson', 'mail': 'hernandezlinda@example.net', 'phone': '529-512-9991x3564', 'age': 90, 'id': 1, 'activestatus': '4hrs ago', 'Quick Hint': 'Buy-1', 'infer': 'Follow-up:4', 'category': 'Citi Private Client', 'category-count': 9, 'Score': 'Not Recommended', 'rmAdvisoryScore': 60, 'customerUnderstandingScore': 60, 'rmUnderstandingScore': 30, 'customerAppreciationValue': 80, 'rmKnowledgeScore': 60, 'overallCallQualityScore': 40}, {'UUID': 'CUS33429-30-002', 'country': 'au', 'customerid': 'C39568', 'RelationshipID': 'R3868', 'Customername': 'Laura Gallagher', 'mail': 'bryan54@example.org', 'phone': '3564672629', 'age': 74, 'id': 2, 'activestatus': '4 days ago', 'Quick Hint': 'Sell-1', 'infer': 'Follow-up:4', 'category': 'Citi Gold', 'category-count': 0, 'Score': 'Recommended', 'rmAdvisoryScore': 80, 'customerUnderstandingScore': 40, 'rmUnderstandingScore': 40, 'customerAppreciationValue': 50, 'rmKnowledgeScore': 50, 'overallCallQualityScore': 90}, {'UUID': 'CUS99399-30-003', 'country': 'in', 'customerid': 'C28212', 'RelationshipID': 'R4831', 'Customername': 'Scott Mclean', 'mail': 'barbaramora@example.com', 'phone': '578-290-0578x50263', 'age': 60, 'id': 3, 'activestatus': '4hrs ago', 'Quick Hint': 'Sell-1', 'infer': 'Missed Lead:1', 'category': 'Citi Private Client', 'category-count': 8, 'Score': 'Recommended', 'rmAdvisoryScore': 80, 'customerUnderstandingScore': 50, 'rmUnderstandingScore': 90, 'customerAppreciationValue': 30, 'rmKnowledgeScore': 50, 'overallCallQualityScore': 30}, {'UUID': 'CUS65572-30-004', 'country': 'jp', 'customerid': 'C17328', 'RelationshipID': 'R3063', 'Customername': 'Brian Parker', 'mail': 'benjamindelgado@example.net', 'phone': '9649240668', 'age': 31, 'id': 4, 'activestatus': '4 days ago', 'Quick Hint': 'Sell-3', 'infer': 'Missed Lead:1', 'category': 'Citi Private Bank', 'category-count': 5, 'Score': 'Recommended', 'rmAdvisoryScore': 60, 'customerUnderstandingScore': 80, 'rmUnderstandingScore': 80, 'customerAppreciationValue': 70, 'rmKnowledgeScore': 40, 'overallCallQualityScore': 40}, {'UUID': 'CUS16317-30-005', 'country': 'br', 'customerid': 'C18170', 'RelationshipID': 'R6019', 'Customername': 'Patricia Nichols', 'mail': 'upearson@example.com', 'phone': '001-972-229-0606x4397', 'age': 87, 'id': 5, 'activestatus': '4 days ago', 'Quick Hint': 'Hold-2', 'infer': 'Follow-up:4', 'category': 'Citi Private Bank', 'category-count': 3, 'Score': 'Recommended', 'rmAdvisoryScore': 40, 'customerUnderstandingScore': 60, 'rmUnderstandingScore': 40, 'customerAppreciationValue': 40, 'rmKnowledgeScore': 90, 'overallCallQualityScore': 60}, {'UUID': 'CUS66025-30-006', 'country': 'in', 'customerid': 'C39349', 'RelationshipID': 'R9905', 'Customername': 'Judy Davis', 'mail': 'stephenmiller@example.com', 'phone': '(884)413-4889', 'age': 54, 'id': 6, 'activestatus': '4hrs ago', 'Quick Hint': 'Hold-2', 'infer': 'Completed:3', 'category': 'Citi Private Client', 'category-count': 7, 'Score': 'Not Recommended', 'rmAdvisoryScore': 30, 'customerUnderstandingScore': 70, 'rmUnderstandingScore': 80, 'customerAppreciationValue': 60, 'rmKnowledgeScore': 30, 'overallCallQualityScore': 60}, {'UUID': 'CUS76420-30-007', 'country': 'it', 'customerid': 'C92396', 'RelationshipID': 'R3503', 'Customername': 'Sarah Ponce', 'mail': 'dmartin@example.org', 'phone': '+1-528-571-9211x95903', 'age': 26, 'id': 7, 'activestatus': '4hrs ago', 'Quick Hint': 'Sell-3', 'infer': 'Potential Lead:2', 'category': 'Citi Private Bank', 'category-count': 0, 'Score': 'Recommended', 'rmAdvisoryScore': 30, 'customerUnderstandingScore': 90, 'rmUnderstandingScore': 70, 'customerAppreciationValue': 50, 'rmKnowledgeScore': 70, 'overallCallQualityScore': 80}, {'UUID': 'CUS99309-30-008', 'country': 'br', 'customerid': 'C20109', 'RelationshipID': 'R9996', 'Customername': 'Brenda Jefferson', 'mail': 'iadams@example.net', 'phone': '435-701-7517x80133', 'age': 51, 'id': 8, 'activestatus': '4 days ago', 'Quick Hint': 'Buy-5', 'infer': 'Missed Lead:1', 'category': 'Citi Private Bank', 'category-count': 9, 'Score': 'Not Recommended', 'rmAdvisoryScore': 60, 'customerUnderstandingScore': 70, 'rmUnderstandingScore': 60, 'customerAppreciationValue': 80, 'rmKnowledgeScore': 30, 'overallCallQualityScore': 60}, {'UUID': 'CUS79649-30-009', 'country': 'us', 'customerid': 'C63542', 'RelationshipID': 'R112', 'Customername': 'Brenda Castillo', 'mail': 'tina13@example.net', 'phone': '001-811-967-6471x726', 'age': 31, 'id': 9, 'activestatus': 'Online - MBOL', 'Quick Hint': 'Sell-3', 'infer': 'Potential Lead:2', 'category': 'Citi Private Bank', 'category-count': 3, 'Score': 'Recommended', 'rmAdvisoryScore': 80, 'customerUnderstandingScore': 50, 'rmUnderstandingScore': 60, 'customerAppreciationValue': 80, 'rmKnowledgeScore': 30, 'overallCallQualityScore': 70}]


dummt = [
    {'country': 'us', 'name': 'Sarah Willie', 'category':'Citi Gold' ,
     'phone' :'(850) 834-3764',
     'mail' : 'sarahwillie@gmail.com',
     'infer' : 'Missed',
     'category-count': "1",
     'activestatus' : 'Online - MBOL',
     "id":1},
    {"id":2, 'country': 'hk', 'name': 'Wills Turner', 'category':'Citi Private Bank', 'category-count': "1", 'phone' :'(850) 834-3764', 'mail' : 'sarahwillie@gmail.com', 'infer' : 'Missed   ', 'activestatus' : '5hrs Ago     '},
    {"id":3, 'country': 'it', 'name': 'Chris Lukash', 'category':'Citi Private Client','category-count': "2", 'phone' :'(850) 834-3764', 'mail' : 'sarahwillie@gmail.com', 'infer' : 'Potential', 'activestatus' : '10hrs Ago    '},
    {"id":4, 'country': 'cn', 'name': 'Pilpe Mateos', 'category':'Citi Gold','category-count': "3", 'phone' :'(850) 834-3764', 'mail' : 'sarahwillie@gmail.com', 'infer' : 'Potential', 'activestatus' : '1 Month Ago  '},
]

sample_transcript = """
{"uuid": "f8a6b2b1-73e9-4512-b7f7-92b53425084f", "transcripted": "Speaker 2: Good morning, Sarah. How can I assist you today?\nSpeaker 1: Hey Samantha. I'm interested in exploring investment options, but I'm more comfortable with bonds.\nSpeaker 2: I understand bonds are a safe choice, but have you considered diversifying your portfolio with a mutual fund? We have a solid mutual fund low-volatility Equity portfolio that offers High returns and quarterly dividends. It has a 70% spread in the US Equity market and 30% in fixed-income. It has been performing well in the market for a long time and it's a good fun to start investing.\nSpeaker 1: I'm not sure about mutual funds. I've always preferred bonds because they feel safer to me\nSpeaker 2: While bonds are safe. Your portfolio is already heavily invested in them diversifying with this mutual fund could balance your Investments and potentially yield higher returns the US market portion provides growth potential while the fixed-income part offers stability. \nSpeaker 1: I see the point But I'll have to think about it Bonds just feel more secure to me.\nSpeaker 2: I understand it's important to feel secure in your Investments take your time. But remember that diversifying can protect your portfolio from Market volatility and enhance overall returns if you have any questions or need more information, I'm here to help.", "score": "20%", "scoreReason": "The banker is recommending and not enforcing client to invest in Mutual Funds. Words like 'consider' and 'could' indicates a recommendation tone.", "actionable": "Potential Lead", "clientRequested": "BND:Bonds:BUY:", "orderarray": [{"productType": "MF", "productName": "low-volatility Equity portfolio", "amount": ""}],"customerAppreciationValue": 30, "customerUnderstandingScore": 30, "overallCallQualityScore": 50, "rmAdvisoryScore": 70, "rmKnowledgeScore": 60, "rmUnderstandingScore": 70}
"""

generation_config = {
    "max_output_tokens": 8192,
    "temperature": 1,
    "top_p": 0.95,
}

safety_settings = {
    generative_models.HarmCategory.HARM_CATEGORY_HATE_SPEECH: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
    generative_models.HarmCategory.HARM_CATEGORY_HARASSMENT: generative_models.HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
}
progress_value=0

@callback(
    Output("dialog", "open"),
    [Input({"type":"viewdetail", "index":ALL}, "n_clicks"),
     Input("close", "n_clicks")]
)
def dialogopen(n_click, n_click_2):
    if isinstance(ctx.triggered_id, dict) and ctx.triggered_id["type"] == "viewdetail":
        return True
    elif isinstance(ctx.triggered_id, str) and ctx.triggered_id == "close":
        return False
    else:
        return False
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


def score(rmAdvisoryScore,customerUnderstandingScore,rmUnderstandingScore,customerAppreciationValue,rmKnowledgeScore,overallCallQualityScore):
    scores = {
        'rmAdvisoryScore': rmAdvisoryScore,
        'customerUnderstandingScore': customerUnderstandingScore,
        'rmUnderstandingScore': rmUnderstandingScore,
        'customerAppreciationValue': customerAppreciationValue,
        'rmKnowledgeScore': rmKnowledgeScore,
        'overallCallQualityScore': overallCallQualityScore
    }

    # Define categories and values
    categories = list(scores.keys())
    values = list(scores.values())
    values.append(values[0])
    categories.append(categories[0])
    # Create the radar chart
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=categories,
        fill='toself',
        name='Call Quality Scores'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=False
    )

    return fig


# def livetracker(transcript):
#     encoded_image = base64.b64encode(open('assets/mic.svg', 'rb').read()).decode()
#     # transcript['transcripted'].replace( /(?:\r\n|\r|\n)/g, '<br>')
#
#     conversations = str(transcript['transcripted']).split("\n")
#
#     transcript_ = md.Paper(elevation=3, style={"position": "relative", "width": "auto", "height": "280px"}, children=[
#         # {"uuid":"", "transcripted" : "", "score":"", "actionable" :"", "orderarray" : ""},
#
#         md.Typography("UUID: " + transcript['uuid'], style={"padding": "20px"}),
#
#         md.Card(children=[md.Typography(conversation) for conversation in conversations],
#                 style={"padding-top": "10px", "padding-bottom": "10px", 'maxHeight': '60%', 'overflow': 'auto'}),
#         md.Icon(className="bi bi-mic-fill"),
#
#         # md.TableContainer(children=[
#         #     md.TableHead(transcript['uuid'], style={"padding":"2px"}),
#         #     md.TableBody(children=[md.TableRow(transcript['transcripted'], style={"padding":"2px", 'maxHeight': '40px', 'overflow': 'auto'}),
#         #                            ]),
#         #     md.TableFooter(
#         #         html.Img(src="data:image/png;base64,{}".format(encoded_image), height="2rem", width="auto"))
#         # ])
#     ])
#     # logo = md.TableContainer(children=[md.TableRow(children=[md.TableCell(style={"background-color": "green"}, height="10px", width="20px"), md.TableCell(children=[md.Icon(className="bi bi-record2", style={"color":"black"})],style={"background-color": "yellow"}, height="10px", width="20px"), md.TableCell(style={"background-color": "red"}, height="10px", width="20px")])])
#     return dbc.Row([dbc.Col(md.Paper(dcc.Graph(style={"position": "relative", "width": "280px", "height": "280px"},
#                                                figure=score(transcript['score'])), elevation=3), md=3),
#                     dbc.Col(transcript_, md=9)])

def parse_conversations(conversations):
    parsed_conversations = []
    for line in conversations:
        if ": " in line:
            speaker, text = line.split(": ", 1)
            parsed_conversations.append({"Speaker": speaker, "text": text})
    return parsed_conversations
def livetracker( transcript):
    encoded_image = base64.b64encode(open('assets/mic.svg', 'rb').read()).decode()

    transcript = transcript.replace("json", "").replace("`","")
    print(transcript)
    transcript = json.loads(transcript, strict=False)

    conversations = transcript['transcripted'].split("\n")
    parsed_conversations = parse_conversations(conversations)

    print(parsed_conversations)
    chat_display = [create_chat_bubble(conv["Speaker"], conv["text"]) for conv in parsed_conversations]
    transcript_ = md.Paper(elevation=4, style={"position": "relative", "width": "300","height": "500px"}, children=[
        md.Typography("Google's Transcripted Text: UUID"+transcript['uuid'], style={"padding":"20px"}),
        dbc.Container(
            dbc.Card(
                dbc.CardBody(chat_display),
                style={"padding": "10px", "background-color": "#f7f7f7", "border-radius": "10px", "margin-top": "20px",'maxHeight': '400px', 'overflow': 'auto'}
            ),
            fluid=True
        )
        # md.Card(children=[md.Typography(conversation) for conversation in conversations], style={"padding-top":"10px", "padding-bottom": "10px",  "padding-left": "20px",  'maxHeight': '100%', 'overflow': 'auto'}),
        # md.Icon(className="bi bi-mic-fill"),
    ])
    return dbc.Row([ dbc.Col(md.Paper(dcc.Graph(style={"position": "relative", "width": "450px","height": "500px"}, figure=score(transcript["rmAdvisoryScore"],transcript["customerUnderstandingScore"],transcript["rmUnderstandingScore"],transcript["customerAppreciationValue"],transcript["rmKnowledgeScore"],transcript["overallCallQualityScore"])), elevation=5), md=5),dbc.Col(transcript_, md=7)])


def create_chat_bubble(speaker, text):
    if speaker == "Speaker 1":
        return dbc.Row(
            dbc.Col(
                html.Div([
                    html.Strong(speaker, style={"color": "blue"}),
                    html.P(text, style={"margin": 0})
                ], style={"background-color": "#e1f5fe", "padding": "10px", "border-radius": "10px",
                          "max-width": "70%"}),
                width={"size": 10, "offset": 0},
                style={"margin-top": "10px"}
            )
        )
    else:
        return dbc.Row(
            dbc.Col(
                html.Div([
                    html.Strong(speaker, style={"color": "green"}),
                    html.P(text, style={"margin": 0})
                ], style={"background-color": "#e8f5e9", "padding": "10px", "border-radius": "10px",
                          "max-width": "70%", "margin-left": "auto"}),
                width={"size": 10, "offset": 2},
                style={"margin-top": "10px"}
            )
        )

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

def _customer_list(customers: list) -> md.TableContainer:
    return md.TableContainer(
        children=[
            md.Table(
                style={"minWidth": "650"},
                children=[
            md.TableHead(
                children=[
                    md.TableRow(
                        children=[
                        md.TableCell("Country"),
                        md.TableCell("Customer ID"),
                        md.TableCell("Customer Name"),
                        md.TableCell("Customer Age"),
                        md.TableCell("Contact Details"),
                        md.TableCell("Last Conduct"),
                        md.TableCell("Active Status"),
                        md.TableCell("Actions")]
                    )
                ]

            ),
            md.TableBody(
                children=[
                    md.TableRow(
                        children=[
                        md.TableCell(md.Avatar(src="https://flagcdn.com/h80/"+customerinfo['country']+".png")),
                        md.TableCell(md.Typography(customerinfo['customerid'], style={'font-size' : '14px'}),),
                        md.TableCell(
                            children=[
                            md.Typography(customerinfo['Customername'], style={'font-size' : '14px'}),
                            #md.ListItemText(primary=customerinfo['name'],
                            #                style={"padding-left": "20px"}, ),
                            md.Chip(label=customerinfo['category'], style={'height': '20px', 'font-size' : '10px'}),
                            md.Chip(label=str(customerinfo['category-count'])+" - Relationships", style={'height': '20px','font-size' : '10px','padding-left':'4px'})
                            ]
                        ),
                            md.TableCell(md.Typography(customerinfo['age'], style={'font-size': '14px'}), ),
                        md.TableCell(
                            children=[
                            md.Typography("Mobile: " +customerinfo['phone'], style={'font-size': '14px'}),
                            md.Typography("Mail: " + customerinfo['mail'], style={'font-size': '14px'}),
                            ]
                        ),
                        md.TableCell(
                            md.Typography(customerinfo['infer'], style={'font-size': '14px'}),
                            #md.ListItemText(secondary=customerinfo['infer'])
                        ),
                        md.TableCell(
                            md.Typography(customerinfo['activestatus'], style={'font-size': '14px'}),
                            #md.ListItemText(secondary=customerinfo['activestatus']),
                        ),
                    md.TableCell(
                        md.Button("View Details", id={"type": "viewdetail", "index": customerinfo['id']})
                    ) ]
                    ) for customerinfo in customers
                ]
            )
            ])
        ]
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
            children=[md.Box(style={'position': 'relative', },
                             children=[
                                 md.Typography(text.split(":")[0], variant="h6"),
                                 #md.CircularProgress(variant="determinate", size="8rem", value=80, color="primary"),

                                 ],
                             ),
                      md.Box(style={'position': 'relative', 'display': 'inline-flex'},
                             children=[
                                 md.ImageListItem(),
                                 img, md.Typography(text.split(":")[1], style={
                                 "font-size": "2.125rem"
                             }),])

                      ],
            style={

            "padding-top": "10px",
            "padding": "10px",
                "height": "100px",
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

total_customer_img = dash.html.Img(src=app.get_asset_url("total-number-of-users.png"), style={"height":"2.125rem", "width":"2.125rem"})
potential_leads_img = dash.html.Img(src=app.get_asset_url("leads.png"), style={"height":"2.125rem", "width":"2.125rem"})
missed_leads_img = dash.html.Img(src=app.get_asset_url("missed.svg"), style={"height":"2.125rem", "width":"2.125rem"})
fullfiled_img = dash.html.Img(src=app.get_asset_url("fulfill.png"), style={"height":"2.125rem", "width":"2.125rem"})


def header_component(name, id):
    title = html.H6(name, style={"margin-top": 5, "padding-top": "10px", "padding-bottom": "10px"})
    if id == "1":
        logo = html.Header("RM Logged In: RM09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    elif id == "3":
        logo = html.Header("Customer: CUS09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    elif id == "2":
        return dbc.Row([dbc.Col([title, md.Button("Call Live", id="callrecord1")], md=8)])
    elif id == "4":
        return dbc.Row([dbc.Col([title, md.Button("Call Live", id="callrecord", style={"marginTop": "-20px"}),
                                 html.Audio(id='audio-player', controls=True, src='',
                                            style={"horizontal-align": "right", "max-width": "100%",
                                                   "height": "35px"}), ], md=12)])
    else:
        return dbc.Row([dbc.Col(title, md=8)])

def earlier_conversations_component():
    columnDefs = [
        {"field": "UUID", "cellRenderer": "CheckboxRenderer", "tooltipField": "Customername",
         "tooltipComponentParams": {"showDelay": 100}},
        {"headerName": "Play", "field": "Play", "maxWidth": 20, "sortable": False, "filter": False},
        {"field": "Customername", "cellRenderer": "FlagsCellRenderer"},
        {"field": "CustomerID"},
        {"field": "RelationshipID"},
        {"field": "Date", "headerName": "Last Call Date"},
        {"field": "Actionable", "cellRenderer": "Button", "cellRendererParams": {"className": "btn btn-success"}},
        {"field": "Quick Hint"},
        {"field": "Score"}
    ]
    rowData = [
        {"Actionable": "Potential Lead:2", "CustomerID": "C652", "Customername": "Charles Rodriguez",
         "Date": "2023-08-05 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R9544", "Score": "Not Recommended",
         "UUID": "CUS31660-30-000", "country": "it", "customerAppreciationValue": 40, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 90, "rmKnowledgeScore": 90, "rmUnderstandingScore": 70},
        {"Actionable": "Lost Lead:5", "CustomerID": "C65099", "Customername": "Tammy Hatfield",
         "Date": "2024-06-15 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R4547", "Score": "Recommended",
         "UUID": "CUS38334-30-001", "country": "jp", "customerAppreciationValue": 80, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 80, "rmKnowledgeScore": 30, "rmUnderstandingScore": 80},
        {"Actionable": "Missed Lead:1", "CustomerID": "C87337", "Customername": "Tommy Stevens",
         "Date": "2024-07-08 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R1453", "Score": "Recommended",
         "UUID": "CUS10708-30-002", "country": "br", "customerAppreciationValue": 80, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 50, "rmKnowledgeScore": 80, "rmUnderstandingScore": 90},
        {"Actionable": "Lost Lead:5", "CustomerID": "C89591", "Customername": "Jean Gordon",
         "Date": "2023-03-18 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R8257", "Score": "Recommended",
         "UUID": "CUS46427-30-003", "country": "de", "customerAppreciationValue": 90, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 90, "rmKnowledgeScore": 80, "rmUnderstandingScore": 50},
        {"Actionable": "Lost Lead:5", "CustomerID": "C5300", "Customername": "Jason Brown",
         "Date": "2023-06-25 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R4755", "Score": "Not Recommended",
         "UUID": "CUS89481-30-004", "country": "au", "customerAppreciationValue": 60, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 70, "rmKnowledgeScore": 70, "rmUnderstandingScore": 70},
        {"Actionable": "Missed Lead:1", "CustomerID": "C97160", "Customername": "Stephen Barker",
         "Date": "2024-01-08 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R5463", "Score": "Recommended",
         "UUID": "CUS38012-30-005", "country": "us", "customerAppreciationValue": 40, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 60, "rmKnowledgeScore": 50, "rmUnderstandingScore": 60},
        {"Actionable": "Missed Lead:1", "CustomerID": "C97895", "Customername": "Jeffrey Simpson",
         "Date": "2023-08-03 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R455", "Score": "Recommended",
         "UUID": "CUS72502-30-006", "country": "it", "customerAppreciationValue": 70, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 40, "rmKnowledgeScore": 30, "rmUnderstandingScore": 60},
        {"Actionable": "Follow-up:4", "CustomerID": "C20703", "Customername": "Gary Owen",
         "Date": "2023-01-10 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R103", "Score": "Recommended",
         "UUID": "CUS80704-30-007", "country": "jp", "customerAppreciationValue": 60, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 30, "rmKnowledgeScore": 90, "rmUnderstandingScore": 80},
        {"Actionable": "Follow-up:4", "CustomerID": "C69910", "Customername": "Troy Lam", "Date": "2023-02-24 00:00:00",
         "Quick Hint": "Buy-8", "RelationshipID": "R8145", "Score": "Not Recommended", "UUID": "CUS84215-30-008",
         "country": "fr", "customerAppreciationValue": 30, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 60, "rmKnowledgeScore": 50, "rmUnderstandingScore": 30},
        {"Actionable": "Follow-up:4", "CustomerID": "C78825", "Customername": "Tiffany Johnson",
         "Date": "2023-09-10 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R4590", "Score": "Recommended",
         "UUID": "CUS54702-30-009", "country": "it", "customerAppreciationValue": 80, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 60, "rmKnowledgeScore": 50, "rmUnderstandingScore": 60},
        {"Actionable": "Potential Lead:2", "CustomerID": "C3202", "Customername": "Jeffery Brown",
         "Date": "2023-11-26 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R3865", "Score": "Not Recommended",
         "UUID": "CUS33381-30-010", "country": "us", "customerAppreciationValue": 90, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 80, "rmAdvisoryScore": 70, "rmKnowledgeScore": 50, "rmUnderstandingScore": 40},
        {"Actionable": "Missed Lead:1", "CustomerID": "C99464", "Customername": "Krystal Gross",
         "Date": "2024-06-06 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R3496", "Score": "Recommended",
         "UUID": "CUS26454-30-011", "country": "sg", "customerAppreciationValue": 30, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 60, "rmKnowledgeScore": 50, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C36632", "Customername": "Troy Johnson",
         "Date": "2024-04-23 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R7942", "Score": "Not Recommended",
         "UUID": "CUS31821-30-012", "country": "cn", "customerAppreciationValue": 90, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 80, "rmKnowledgeScore": 70, "rmUnderstandingScore": 80},
        {"Actionable": "Lost Lead:5", "CustomerID": "C52527", "Customername": "Olivia Rocha",
         "Date": "2023-11-02 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R6861", "Score": "Recommended",
         "UUID": "CUS67145-30-013", "country": "cn", "customerAppreciationValue": 40, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 60, "rmKnowledgeScore": 40, "rmUnderstandingScore": 90},
        {"Actionable": "Missed Lead:1", "CustomerID": "C70685", "Customername": "Madeline Hoffman",
         "Date": "2023-06-22 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R1165", "Score": "Not Recommended",
         "UUID": "CUS57962-30-014", "country": "in", "customerAppreciationValue": 60, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 90, "rmKnowledgeScore": 90, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C57596", "Customername": "Kelli Cook",
         "Date": "2024-04-21 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R9620", "Score": "Recommended",
         "UUID": "CUS47075-30-015", "country": "cn", "customerAppreciationValue": 70, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 60, "rmKnowledgeScore": 60, "rmUnderstandingScore": 60},
        {"Actionable": "Missed Lead:1", "CustomerID": "C4384", "Customername": "Michael Berry",
         "Date": "2023-08-23 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R6141", "Score": "Recommended",
         "UUID": "CUS16775-30-016", "country": "fr", "customerAppreciationValue": 50, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 60, "rmKnowledgeScore": 30, "rmUnderstandingScore": 50},
        {"Actionable": "Lost Lead:5", "CustomerID": "C16949", "Customername": "Cynthia Vincent",
         "Date": "2024-05-03 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R1773", "Score": "Not Recommended",
         "UUID": "CUS72916-30-017", "country": "us", "customerAppreciationValue": 60, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 70, "rmKnowledgeScore": 80, "rmUnderstandingScore": 70},
        {"Actionable": "Potential Lead:2", "CustomerID": "C2906", "Customername": "Julie Hunt",
         "Date": "2023-08-13 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R4427", "Score": "Not Recommended",
         "UUID": "CUS57265-30-018", "country": "jp", "customerAppreciationValue": 70, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 40, "rmKnowledgeScore": 60, "rmUnderstandingScore": 80},
        {"Actionable": "Completed:3", "CustomerID": "C36798", "Customername": "Richard Kirk",
         "Date": "2023-08-20 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R4664", "Score": "Recommended",
         "UUID": "CUS53257-30-019", "country": "fr", "customerAppreciationValue": 40, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 90, "rmKnowledgeScore": 70, "rmUnderstandingScore": 30},
        {"Actionable": "Completed:3", "CustomerID": "C1224", "Customername": "Christina Wong DVM",
         "Date": "2023-07-19 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R563", "Score": "Not Recommended",
         "UUID": "CUS52789-30-020", "country": "br", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 80, "rmKnowledgeScore": 80, "rmUnderstandingScore": 30},
        {"Actionable": "Lost Lead:5", "CustomerID": "C55304", "Customername": "Christopher Mccormick",
         "Date": "2023-08-10 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R4278", "Score": "Recommended",
         "UUID": "CUS72162-30-021", "country": "in", "customerAppreciationValue": 90, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 90, "rmKnowledgeScore": 30, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C48159", "Customername": "Carly Gibbs",
         "Date": "2023-05-20 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R7139", "Score": "Not Recommended",
         "UUID": "CUS73446-30-022", "country": "cn", "customerAppreciationValue": 40, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 80, "rmKnowledgeScore": 40, "rmUnderstandingScore": 40},
        {"Actionable": "Missed Lead:1", "CustomerID": "C65883", "Customername": "Diane Bishop",
         "Date": "2023-05-22 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R3550", "Score": "Not Recommended",
         "UUID": "CUS32949-30-023", "country": "us", "customerAppreciationValue": 50, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 70, "rmKnowledgeScore": 60, "rmUnderstandingScore": 60},
        {"Actionable": "Missed Lead:1", "CustomerID": "C16329", "Customername": "Peter Roberts",
         "Date": "2023-11-28 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R7287", "Score": "Not Recommended",
         "UUID": "CUS57170-30-024", "country": "br", "customerAppreciationValue": 60, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 90, "rmKnowledgeScore": 60, "rmUnderstandingScore": 90},
        {"Actionable": "Missed Lead:1", "CustomerID": "C45005", "Customername": "Aaron Walker",
         "Date": "2023-07-19 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R6935", "Score": "Not Recommended",
         "UUID": "CUS70590-30-025", "country": "de", "customerAppreciationValue": 30, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 80, "rmAdvisoryScore": 60, "rmKnowledgeScore": 60, "rmUnderstandingScore": 40},
        {"Actionable": "Follow-up:4", "CustomerID": "C47312", "Customername": "Brandon Strickland",
         "Date": "2023-08-03 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R7200", "Score": "Not Recommended",
         "UUID": "CUS6468-30-026", "country": "us", "customerAppreciationValue": 70, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 90, "rmKnowledgeScore": 80, "rmUnderstandingScore": 90},
        {"Actionable": "Potential Lead:2", "CustomerID": "C14380", "Customername": "Jacqueline Charles",
         "Date": "2023-11-04 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R3664", "Score": "Not Recommended",
         "UUID": "CUS86443-30-027", "country": "jp", "customerAppreciationValue": 90, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 60, "rmKnowledgeScore": 30, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C27966", "Customername": "Angela Edwards",
         "Date": "2023-11-30 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R6945", "Score": "Recommended",
         "UUID": "CUS60839-30-028", "country": "cn", "customerAppreciationValue": 60, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 60, "rmKnowledgeScore": 40, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C36582", "Customername": "Janet Pham",
         "Date": "2023-08-24 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R9411", "Score": "Not Recommended",
         "UUID": "CUS53029-30-029", "country": "jp", "customerAppreciationValue": 80, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 80, "rmKnowledgeScore": 50, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C67814", "Customername": "Pamela Escobar",
         "Date": "2024-07-02 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R7093", "Score": "Recommended",
         "UUID": "CUS262-30-030", "country": "au", "customerAppreciationValue": 80, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 50, "rmKnowledgeScore": 80, "rmUnderstandingScore": 40},
        {"Actionable": "Missed Lead:1", "CustomerID": "C1977", "Customername": "John Freeman",
         "Date": "2023-01-28 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R4757", "Score": "Recommended",
         "UUID": "CUS9503-30-031", "country": "de", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 40, "rmKnowledgeScore": 90, "rmUnderstandingScore": 30},
        {"Actionable": "Follow-up:4", "CustomerID": "C20590", "Customername": "Debra Robinson",
         "Date": "2024-05-10 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R8671", "Score": "Not Recommended",
         "UUID": "CUS2712-30-032", "country": "it", "customerAppreciationValue": 80, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 90, "rmKnowledgeScore": 40, "rmUnderstandingScore": 60},
        {"Actionable": "Completed:3", "CustomerID": "C76025", "Customername": "Jordan Greene",
         "Date": "2023-02-27 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R4807", "Score": "Not Recommended",
         "UUID": "CUS59463-30-033", "country": "br", "customerAppreciationValue": 40, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 40, "rmKnowledgeScore": 30, "rmUnderstandingScore": 70},
        {"Actionable": "Follow-up:4", "CustomerID": "C74435", "Customername": "Kristin Bryant",
         "Date": "2023-12-27 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R9737", "Score": "Not Recommended",
         "UUID": "CUS772-30-034", "country": "de", "customerAppreciationValue": 70, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 50, "rmKnowledgeScore": 70, "rmUnderstandingScore": 90},
        {"Actionable": "Completed:3", "CustomerID": "C46135", "Customername": "Anna Schroeder",
         "Date": "2023-10-21 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R8460", "Score": "Not Recommended",
         "UUID": "CUS88892-30-035", "country": "br", "customerAppreciationValue": 50, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 80, "rmKnowledgeScore": 30, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C65408", "Customername": "Mr. James Cruz",
         "Date": "2023-08-12 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R8866", "Score": "Not Recommended",
         "UUID": "CUS66769-30-036", "country": "fr", "customerAppreciationValue": 60, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 90, "rmKnowledgeScore": 60, "rmUnderstandingScore": 70},
        {"Actionable": "Follow-up:4", "CustomerID": "C12608", "Customername": "Frank Armstrong",
         "Date": "2023-12-08 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R3249", "Score": "Recommended",
         "UUID": "CUS17017-30-037", "country": "au", "customerAppreciationValue": 40, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 50, "rmKnowledgeScore": 80, "rmUnderstandingScore": 80},
        {"Actionable": "Lost Lead:5", "CustomerID": "C69248", "Customername": "Sandra Manning",
         "Date": "2024-02-22 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R3873", "Score": "Not Recommended",
         "UUID": "CUS69375-30-038", "country": "au", "customerAppreciationValue": 50, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 70, "rmKnowledgeScore": 60, "rmUnderstandingScore": 40},
        {"Actionable": "Missed Lead:1", "CustomerID": "C11019", "Customername": "Christopher Johnson",
         "Date": "2024-06-08 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R9984", "Score": "Not Recommended",
         "UUID": "CUS93647-30-039", "country": "sg", "customerAppreciationValue": 60, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 80, "rmAdvisoryScore": 90, "rmKnowledgeScore": 50, "rmUnderstandingScore": 90},
        {"Actionable": "Lost Lead:5", "CustomerID": "C38774", "Customername": "Elizabeth Garrett",
         "Date": "2023-06-30 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R5896", "Score": "Recommended",
         "UUID": "CUS47164-30-040", "country": "in", "customerAppreciationValue": 50, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 40, "rmKnowledgeScore": 60, "rmUnderstandingScore": 50},
        {"Actionable": "Potential Lead:2", "CustomerID": "C30477", "Customername": "Sarah King",
         "Date": "2023-07-01 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R7081", "Score": "Recommended",
         "UUID": "CUS71349-30-041", "country": "br", "customerAppreciationValue": 60, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 90, "rmKnowledgeScore": 80, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C52193", "Customername": "Robin Young",
         "Date": "2023-09-07 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R3151", "Score": "Not Recommended",
         "UUID": "CUS50692-30-042", "country": "cn", "customerAppreciationValue": 70, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 40, "rmKnowledgeScore": 30, "rmUnderstandingScore": 60},
        {"Actionable": "Follow-up:4", "CustomerID": "C10815", "Customername": "Charles Haynes",
         "Date": "2024-02-16 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R9802", "Score": "Not Recommended",
         "UUID": "CUS25254-30-043", "country": "br", "customerAppreciationValue": 70, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 40, "rmKnowledgeScore": 90, "rmUnderstandingScore": 80},
        {"Actionable": "Missed Lead:1", "CustomerID": "C58049", "Customername": "Steven Wilson",
         "Date": "2024-04-17 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R227", "Score": "Recommended",
         "UUID": "CUS60921-30-044", "country": "de", "customerAppreciationValue": 70, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 40, "rmKnowledgeScore": 80, "rmUnderstandingScore": 90},
        {"Actionable": "Completed:3", "CustomerID": "C84855", "Customername": "Derek Hall",
         "Date": "2023-10-08 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R2714", "Score": "Recommended",
         "UUID": "CUS16137-30-045", "country": "de", "customerAppreciationValue": 50, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 30, "rmKnowledgeScore": 30, "rmUnderstandingScore": 90},
        {"Actionable": "Follow-up:4", "CustomerID": "C94763", "Customername": "Patrick Powell",
         "Date": "2023-09-13 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R8485", "Score": "Recommended",
         "UUID": "CUS59442-30-046", "country": "it", "customerAppreciationValue": 90, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 30, "rmKnowledgeScore": 60, "rmUnderstandingScore": 40},
        {"Actionable": "Lost Lead:5", "CustomerID": "C92676", "Customername": "Michael Hernandez",
         "Date": "2023-02-18 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R5435", "Score": "Recommended",
         "UUID": "CUS91192-30-047", "country": "de", "customerAppreciationValue": 80, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 70, "rmKnowledgeScore": 80, "rmUnderstandingScore": 30},
        {"Actionable": "Potential Lead:2", "CustomerID": "C60238", "Customername": "Christopher Clark",
         "Date": "2024-06-01 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R5493", "Score": "Recommended",
         "UUID": "CUS67090-30-048", "country": "it", "customerAppreciationValue": 50, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 40, "rmKnowledgeScore": 80, "rmUnderstandingScore": 80},
        {"Actionable": "Potential Lead:2", "CustomerID": "C32282", "Customername": "George Simpson",
         "Date": "2023-07-05 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R2811", "Score": "Not Recommended",
         "UUID": "CUS31390-30-049", "country": "sg", "customerAppreciationValue": 60, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 30, "rmKnowledgeScore": 40, "rmUnderstandingScore": 30},
        {"Actionable": "Completed:3", "CustomerID": "C67439", "Customername": "Briana Wilkins",
         "Date": "2024-04-08 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R80", "Score": "Recommended",
         "UUID": "CUS93193-30-050", "country": "fr", "customerAppreciationValue": 90, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 50, "rmKnowledgeScore": 30, "rmUnderstandingScore": 70},
        {"Actionable": "Missed Lead:1", "CustomerID": "C2483", "Customername": "Lisa Price",
         "Date": "2023-12-31 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R5863", "Score": "Not Recommended",
         "UUID": "CUS86070-30-051", "country": "fr", "customerAppreciationValue": 90, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 40, "rmKnowledgeScore": 70, "rmUnderstandingScore": 60},
        {"Actionable": "Potential Lead:2", "CustomerID": "C43699", "Customername": "April Anderson",
         "Date": "2023-06-30 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R5784", "Score": "Recommended",
         "UUID": "CUS51855-30-052", "country": "us", "customerAppreciationValue": 50, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 60, "rmKnowledgeScore": 90, "rmUnderstandingScore": 30},
        {"Actionable": "Follow-up:4", "CustomerID": "C62775", "Customername": "Jennifer Andersen",
         "Date": "2023-04-12 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R7803", "Score": "Not Recommended",
         "UUID": "CUS42662-30-053", "country": "cn", "customerAppreciationValue": 90, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 50, "rmKnowledgeScore": 70, "rmUnderstandingScore": 60},
        {"Actionable": "Follow-up:4", "CustomerID": "C68148", "Customername": "Kenneth Harrison",
         "Date": "2023-05-12 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R8435", "Score": "Recommended",
         "UUID": "CUS55870-30-054", "country": "in", "customerAppreciationValue": 50, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 80, "rmKnowledgeScore": 90, "rmUnderstandingScore": 50},
        {"Actionable": "Lost Lead:5", "CustomerID": "C28346", "Customername": "Theodore Kelly",
         "Date": "2024-04-10 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R1167", "Score": "Recommended",
         "UUID": "CUS17613-30-055", "country": "fr", "customerAppreciationValue": 90, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 90, "rmKnowledgeScore": 50, "rmUnderstandingScore": 80},
        {"Actionable": "Missed Lead:1", "CustomerID": "C55351", "Customername": "Roger Sullivan",
         "Date": "2023-02-07 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R2282", "Score": "Recommended",
         "UUID": "CUS93751-30-056", "country": "it", "customerAppreciationValue": 80, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 60, "rmKnowledgeScore": 70, "rmUnderstandingScore": 30},
        {"Actionable": "Completed:3", "CustomerID": "C87732", "Customername": "Larry Williams",
         "Date": "2023-01-05 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R6617", "Score": "Recommended",
         "UUID": "CUS68339-30-057", "country": "jp", "customerAppreciationValue": 70, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 50, "rmKnowledgeScore": 70, "rmUnderstandingScore": 70},
        {"Actionable": "Completed:3", "CustomerID": "C99972", "Customername": "Jonathan Patterson",
         "Date": "2023-05-22 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R2881", "Score": "Recommended",
         "UUID": "CUS37026-30-058", "country": "sg", "customerAppreciationValue": 50, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 60, "rmKnowledgeScore": 50, "rmUnderstandingScore": 70},
        {"Actionable": "Completed:3", "CustomerID": "C67867", "Customername": "Dustin Johnson",
         "Date": "2024-06-28 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R5142", "Score": "Not Recommended",
         "UUID": "CUS46049-30-059", "country": "au", "customerAppreciationValue": 60, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 80, "rmKnowledgeScore": 80, "rmUnderstandingScore": 80},
        {"Actionable": "Lost Lead:5", "CustomerID": "C37773", "Customername": "Tina Lamb",
         "Date": "2024-01-26 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R1632", "Score": "Not Recommended",
         "UUID": "CUS51371-30-060", "country": "fr", "customerAppreciationValue": 70, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 80, "rmKnowledgeScore": 70, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C8754", "Customername": "Thomas Nash",
         "Date": "2023-04-26 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R9582", "Score": "Recommended",
         "UUID": "CUS3645-30-061", "country": "sg", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 50, "rmKnowledgeScore": 80, "rmUnderstandingScore": 80},
        {"Actionable": "Completed:3", "CustomerID": "C90852", "Customername": "Willie Foster",
         "Date": "2023-02-02 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R7539", "Score": "Not Recommended",
         "UUID": "CUS98114-30-062", "country": "cn", "customerAppreciationValue": 40, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 90, "rmKnowledgeScore": 40, "rmUnderstandingScore": 90},
        {"Actionable": "Lost Lead:5", "CustomerID": "C18405", "Customername": "Cory Sullivan",
         "Date": "2023-04-13 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R5371", "Score": "Recommended",
         "UUID": "CUS60468-30-063", "country": "br", "customerAppreciationValue": 70, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 90, "rmKnowledgeScore": 30, "rmUnderstandingScore": 30},
        {"Actionable": "Missed Lead:1", "CustomerID": "C23549", "Customername": "Harold Harrison",
         "Date": "2023-05-19 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R633", "Score": "Recommended",
         "UUID": "CUS85137-30-064", "country": "it", "customerAppreciationValue": 60, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 90, "rmKnowledgeScore": 50, "rmUnderstandingScore": 90},
        {"Actionable": "Missed Lead:1", "CustomerID": "C94453", "Customername": "Rodney Bolton",
         "Date": "2023-09-19 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R4028", "Score": "Not Recommended",
         "UUID": "CUS13443-30-065", "country": "us", "customerAppreciationValue": 90, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 30, "rmKnowledgeScore": 60, "rmUnderstandingScore": 80},
        {"Actionable": "Lost Lead:5", "CustomerID": "C21707", "Customername": "Yolanda Golden",
         "Date": "2024-07-29 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R6675", "Score": "Recommended",
         "UUID": "CUS51410-30-066", "country": "de", "customerAppreciationValue": 60, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 40, "rmKnowledgeScore": 40, "rmUnderstandingScore": 50},
        {"Actionable": "Lost Lead:5", "CustomerID": "C72844", "Customername": "Tammy Taylor",
         "Date": "2023-02-16 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R5131", "Score": "Recommended",
         "UUID": "CUS61036-30-067", "country": "sg", "customerAppreciationValue": 90, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 40, "rmKnowledgeScore": 60, "rmUnderstandingScore": 80},
        {"Actionable": "Potential Lead:2", "CustomerID": "C53177", "Customername": "Gregory Jackson",
         "Date": "2023-11-23 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R913", "Score": "Recommended",
         "UUID": "CUS94806-30-068", "country": "jp", "customerAppreciationValue": 60, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 70, "rmKnowledgeScore": 30, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C5687", "Customername": "Sara Robinson",
         "Date": "2023-02-07 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R9922", "Score": "Recommended",
         "UUID": "CUS83121-30-069", "country": "fr", "customerAppreciationValue": 50, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 30, "rmKnowledgeScore": 70, "rmUnderstandingScore": 40},
        {"Actionable": "Follow-up:4", "CustomerID": "C82986", "Customername": "Sheena Hardy",
         "Date": "2024-05-28 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R9008", "Score": "Recommended",
         "UUID": "CUS80304-30-070", "country": "us", "customerAppreciationValue": 80, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 70, "rmKnowledgeScore": 30, "rmUnderstandingScore": 80},
        {"Actionable": "Missed Lead:1", "CustomerID": "C52772", "Customername": "Logan Johnson",
         "Date": "2023-08-20 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R3690", "Score": "Not Recommended",
         "UUID": "CUS93615-30-071", "country": "cn", "customerAppreciationValue": 70, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 40, "rmKnowledgeScore": 70, "rmUnderstandingScore": 50},
        {"Actionable": "Missed Lead:1", "CustomerID": "C25481", "Customername": "Destiny Carter",
         "Date": "2024-02-05 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R7967", "Score": "Recommended",
         "UUID": "CUS6216-30-072", "country": "de", "customerAppreciationValue": 50, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 80, "rmAdvisoryScore": 70, "rmKnowledgeScore": 90, "rmUnderstandingScore": 90},
        {"Actionable": "Follow-up:4", "CustomerID": "C44107", "Customername": "Carla Rowe",
         "Date": "2024-01-10 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R9467", "Score": "Not Recommended",
         "UUID": "CUS83331-30-073", "country": "us", "customerAppreciationValue": 80, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 50, "rmKnowledgeScore": 50, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C77969", "Customername": "Brittany Perez",
         "Date": "2023-06-25 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R4045", "Score": "Not Recommended",
         "UUID": "CUS56259-30-074", "country": "jp", "customerAppreciationValue": 70, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 30, "rmKnowledgeScore": 40, "rmUnderstandingScore": 70},
        {"Actionable": "Potential Lead:2", "CustomerID": "C57266", "Customername": "Robert Bradford",
         "Date": "2023-09-23 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R4419", "Score": "Recommended",
         "UUID": "CUS67803-30-075", "country": "fr", "customerAppreciationValue": 80, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 90, "rmKnowledgeScore": 60, "rmUnderstandingScore": 40},
        {"Actionable": "Potential Lead:2", "CustomerID": "C60538", "Customername": "Tammy Burton",
         "Date": "2023-10-03 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R4652", "Score": "Recommended",
         "UUID": "CUS95604-30-076", "country": "sg", "customerAppreciationValue": 50, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 90, "rmKnowledgeScore": 80, "rmUnderstandingScore": 70},
        {"Actionable": "Potential Lead:2", "CustomerID": "C56752", "Customername": "Carlos Gonzalez Jr.",
         "Date": "2024-07-15 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R2508", "Score": "Not Recommended",
         "UUID": "CUS64276-30-077", "country": "us", "customerAppreciationValue": 60, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 80, "rmKnowledgeScore": 90, "rmUnderstandingScore": 30},
        {"Actionable": "Missed Lead:1", "CustomerID": "C22534", "Customername": "Thomas Nguyen",
         "Date": "2023-08-08 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R2408", "Score": "Recommended",
         "UUID": "CUS97572-30-078", "country": "br", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 80, "rmKnowledgeScore": 50, "rmUnderstandingScore": 30},
        {"Actionable": "Follow-up:4", "CustomerID": "C44687", "Customername": "Sarah Walker",
         "Date": "2024-04-30 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R505", "Score": "Recommended",
         "UUID": "CUS95334-30-079", "country": "cn", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 30, "rmKnowledgeScore": 60, "rmUnderstandingScore": 80},
        {"Actionable": "Missed Lead:1", "CustomerID": "C35298", "Customername": "Kelly Adams",
         "Date": "2023-05-27 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R8980", "Score": "Not Recommended",
         "UUID": "CUS12157-30-080", "country": "cn", "customerAppreciationValue": 40, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 90, "rmKnowledgeScore": 60, "rmUnderstandingScore": 90},
        {"Actionable": "Missed Lead:1", "CustomerID": "C13144", "Customername": "Matthew Fleming",
         "Date": "2024-01-16 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R4728", "Score": "Not Recommended",
         "UUID": "CUS33972-30-081", "country": "au", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 30, "rmKnowledgeScore": 60, "rmUnderstandingScore": 50},
        {"Actionable": "Completed:3", "CustomerID": "C88437", "Customername": "Daniel Calderon",
         "Date": "2023-12-09 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R8024", "Score": "Recommended",
         "UUID": "CUS54758-30-082", "country": "us", "customerAppreciationValue": 80, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 80, "rmAdvisoryScore": 40, "rmKnowledgeScore": 60, "rmUnderstandingScore": 30},
        {"Actionable": "Missed Lead:1", "CustomerID": "C94630", "Customername": "Carmen Mitchell",
         "Date": "2024-04-14 00:00:00", "Quick Hint": "Buy-1", "RelationshipID": "R2366", "Score": "Not Recommended",
         "UUID": "CUS18080-30-083", "country": "us", "customerAppreciationValue": 50, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 60, "rmKnowledgeScore": 90, "rmUnderstandingScore": 50},
        {"Actionable": "Missed Lead:1", "CustomerID": "C10445", "Customername": "Rhonda Cummings",
         "Date": "2023-01-01 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R9673", "Score": "Not Recommended",
         "UUID": "CUS76176-30-084", "country": "au", "customerAppreciationValue": 40, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 50, "rmAdvisoryScore": 50, "rmKnowledgeScore": 70, "rmUnderstandingScore": 40},
        {"Actionable": "Follow-up:4", "CustomerID": "C82002", "Customername": "Peter Jordan",
         "Date": "2024-06-27 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R677", "Score": "Not Recommended",
         "UUID": "CUS19263-30-085", "country": "in", "customerAppreciationValue": 70, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 80, "rmKnowledgeScore": 90, "rmUnderstandingScore": 30},
        {"Actionable": "Follow-up:4", "CustomerID": "C7524", "Customername": "Philip Robinson",
         "Date": "2024-05-04 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R5739", "Score": "Not Recommended",
         "UUID": "CUS27768-30-086", "country": "it", "customerAppreciationValue": 60, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 60, "rmKnowledgeScore": 40, "rmUnderstandingScore": 70},
        {"Actionable": "Lost Lead:5", "CustomerID": "C93438", "Customername": "Sharon Long",
         "Date": "2023-07-01 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R3286", "Score": "Not Recommended",
         "UUID": "CUS53069-30-087", "country": "in", "customerAppreciationValue": 60, "customerUnderstandingScore": 50,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 70, "rmKnowledgeScore": 40, "rmUnderstandingScore": 30},
        {"Actionable": "Follow-up:4", "CustomerID": "C34452", "Customername": "Veronica Wong",
         "Date": "2023-09-18 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R2375", "Score": "Recommended",
         "UUID": "CUS31843-30-088", "country": "us", "customerAppreciationValue": 50, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 60, "rmKnowledgeScore": 60, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C28176", "Customername": "Rebecca Roberts DDS",
         "Date": "2024-06-21 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R9850", "Score": "Not Recommended",
         "UUID": "CUS11346-30-089", "country": "fr", "customerAppreciationValue": 30, "customerUnderstandingScore": 60,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 30, "rmKnowledgeScore": 50, "rmUnderstandingScore": 40},
        {"Actionable": "Follow-up:4", "CustomerID": "C22086", "Customername": "Jason Mills",
         "Date": "2023-10-07 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R231", "Score": "Recommended",
         "UUID": "CUS34443-30-090", "country": "de", "customerAppreciationValue": 90, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 70, "rmKnowledgeScore": 30, "rmUnderstandingScore": 50},
        {"Actionable": "Potential Lead:2", "CustomerID": "C66160", "Customername": "Morgan Kim",
         "Date": "2023-06-28 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R6562", "Score": "Not Recommended",
         "UUID": "CUS13482-30-091", "country": "cn", "customerAppreciationValue": 60, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 50, "rmKnowledgeScore": 90, "rmUnderstandingScore": 70},
        {"Actionable": "Potential Lead:2", "CustomerID": "C31236", "Customername": "Erica Chavez",
         "Date": "2023-05-31 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R4599", "Score": "Not Recommended",
         "UUID": "CUS66722-30-092", "country": "de", "customerAppreciationValue": 60, "customerUnderstandingScore": 40,
         "overallCallQualityScore": 80, "rmAdvisoryScore": 30, "rmKnowledgeScore": 40, "rmUnderstandingScore": 70},
        {"Actionable": "Follow-up:4", "CustomerID": "C31537", "Customername": "Jose Munoz",
         "Date": "2024-05-15 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R2448", "Score": "Recommended",
         "UUID": "CUS43264-30-093", "country": "cn", "customerAppreciationValue": 90, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 30, "rmKnowledgeScore": 70, "rmUnderstandingScore": 40},
        {"Actionable": "Completed:3", "CustomerID": "C6035", "Customername": "Jennifer Romero",
         "Date": "2023-01-07 00:00:00", "Quick Hint": "Buy-5", "RelationshipID": "R6923", "Score": "Not Recommended",
         "UUID": "CUS52365-30-094", "country": "br", "customerAppreciationValue": 60, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 80, "rmKnowledgeScore": 40, "rmUnderstandingScore": 50},
        {"Actionable": "Follow-up:4", "CustomerID": "C17807", "Customername": "Bryan Jackson",
         "Date": "2024-05-30 00:00:00", "Quick Hint": "Sell-3", "RelationshipID": "R7126", "Score": "Not Recommended",
         "UUID": "CUS12812-30-095", "country": "fr", "customerAppreciationValue": 90, "customerUnderstandingScore": 90,
         "overallCallQualityScore": 70, "rmAdvisoryScore": 90, "rmKnowledgeScore": 90, "rmUnderstandingScore": 70},
        {"Actionable": "Completed:3", "CustomerID": "C95008", "Customername": "Katherine Thompson",
         "Date": "2024-01-12 00:00:00", "Quick Hint": "Buy-8", "RelationshipID": "R8589", "Score": "Recommended",
         "UUID": "CUS30914-30-096", "country": "au", "customerAppreciationValue": 70, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 60, "rmAdvisoryScore": 80, "rmKnowledgeScore": 30, "rmUnderstandingScore": 50},
        {"Actionable": "Completed:3", "CustomerID": "C78363", "Customername": "Marcus Jenkins",
         "Date": "2023-12-10 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R7847", "Score": "Recommended",
         "UUID": "CUS5502-30-097", "country": "in", "customerAppreciationValue": 30, "customerUnderstandingScore": 80,
         "overallCallQualityScore": 30, "rmAdvisoryScore": 40, "rmKnowledgeScore": 70, "rmUnderstandingScore": 80},
        {"Actionable": "Completed:3", "CustomerID": "C13181", "Customername": "Wesley Oconnor",
         "Date": "2023-12-12 00:00:00", "Quick Hint": "Hold-2", "RelationshipID": "R3346", "Score": "Not Recommended",
         "UUID": "CUS1084-30-098", "country": "us", "customerAppreciationValue": 60, "customerUnderstandingScore": 30,
         "overallCallQualityScore": 90, "rmAdvisoryScore": 80, "rmKnowledgeScore": 80, "rmUnderstandingScore": 80},
        {"Actionable": "Missed Lead:1", "CustomerID": "C93514", "Customername": "Xavier Price",
         "Date": "2023-04-30 00:00:00", "Quick Hint": "Sell-1", "RelationshipID": "R8670", "Score": "Not Recommended",
         "UUID": "CUS32948-30-099", "country": "fr", "customerAppreciationValue": 30, "customerUnderstandingScore": 70,
         "overallCallQualityScore": 40, "rmAdvisoryScore": 80, "rmKnowledgeScore": 80, "rmUnderstandingScore": 60}
    ]
    return dag.AgGrid(
        id="styling-selections",
        className="ag-theme-quartz-dark",
        columnSize="sizeToFit",
        columnDefs=columnDefs,
        rowData=rowData,
        defaultColDef={"flex": 1, "sortable": True, "filter": True},
        style={"height": "250px", "width": "100%"},
        dashGridOptions={'pagination': True, 'paginationPageSize': 10,
                         "animateRows": True, 'cacheQuickFilter': True,
                         "groupDisplayType": "groupRows",
                         "rowGroupPanelShow": "always",
                         "domLayout": "autoHeight",
                         "enableRangeSelection": True,
                         'groupDefaultExpanded': 1,
                         'suppressDragLeaveHidesColumns': True,
                         'groupIncludeFooter': True,
                         'groupIncludeTotalFooter': True
                         }
    )

def transcribe_audio_with_speaker_diarization(gcs_uri):
    global progress_value
    progress_value = progress_value + 10
    print('Connecting Google Speech Client')
    client = speech.SpeechClient()
    print("Connecting to Google Cloud...")
    audio = speech.RecognitionAudio(uri=gcs_uri)
    print("Retrieved Audio from Google Cloud.")
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
        enable_speaker_diarization=True,
        diarization_speaker_count=2,
        enable_automatic_punctuation=True
    )
    print("Transcription Started.")
    progress_value = progress_value + 10
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=600)
    progress_value = progress_value + 10
    print("Transcription Ended.")
    result = response.results[-1]
    words_info = result.alternatives[0].words

    speaker_tag = 0
    transcript = ""

    for word_info in words_info:
        if word_info.speaker_tag != speaker_tag:
            speaker_tag = word_info.speaker_tag
            transcript += f"\nSpeaker {speaker_tag}: "

        transcript += f"{word_info.word} "

    return transcript.strip()
def generate(content):
    print(f"BEFORE GENERATING... THE CONTENT>....{content}")
    vertexai.init(project="main-basis-430303-p0", location="us-central1")
    model = GenerativeModel(
        "gemini-1.5-pro-001",
    )
    template_order_checking = """
  You will be provided with conversation of banker and customer. Based on the conversation you have to assume Speaker as Banker or Customer.

  Here are some jargons and their meaning.
  product type - Type of investment product. example: Stock, Bond, Mutual Funds, Structured notes, ETFs, Insurance, Security brokerage, etc.
  transaction type - Type of the transaction or order. example: BUY , execute,invest, order, booking, interest, purchase, SELL, SWITCH, etc.
  BUY is also called invest, order, booking, interest, purchase, execute.
  MF - Mutual Fund.
  SB - Security Brokerage.
  BND - Bonds.
  SN - Structured Notes.

  Please find out what investment product the customer want to buy or sell from the above conversation and provide the product names or codes in the following format: <Product name or code>:<product type>:<transaction type>:<no. of units> or <amount>,...
  If all information in the JSON is available then provide output in JSON format with key answer.

  Also, check if there was any cross product type buy or sell was requested by the client. Highlight that potential lead in your summary.

  Provide me in the below format. 

  Create uuid as a unique number based on the current timestamp and include it in uuid json as value.
  Possible values of actionable are 'No Action', 'Potential Lead', 'Order Requested'.
  score should be based on the words used for enforcement rather than recommendation. This should be in percentage value only. Do not provide any further description
  scoreReason should explain the reason why the score above was computed. This should highlight the words used in the conversation.
  clientRequested should be the product details which the customer was requesting to buy. 
  orderarray element will be an array of orders with potential orders that could have been bought by the cclient in the conversation. It can be more than 1 order, so build the JSON in an array format with multiple orders.
  rmAdvisoryScore will be advisory score for the RM.
  customerUnderstandingScore will be score based on Customer's understanding.
  rmUnderstandingScore will be based on RM's understanding on customer's need.
  customerAppreciationValue will be customer's happy index with respect to the conversaton
  rmKnowledgeScore will be RM's knowledge on the product he is recommending or the customer has requested.
  overallCallQualityScore will be the average based on the above scores.

  JSON structure: {"uuid":"", "transcripted" : """ + content + """, "score":"","scoreReason":"", "actionable" :"", "clientRequested":"", "orderarray" : [{"productType":"","productName":"", "amount":""},{"productType":"","productName":"", "amount":""},{"productType":"","productName":"", "amount":""}], "rmAdvisoryScore": "","customerUnderstandingScore": "","rmUnderstandingScore": "","customerAppreciationValue": "","rmKnowledgeScore": "","overallCallQualityScore": ""}
  """

    # print(template_order_checking)

    responses = model.generate_content(
        f" {template_order_checking} ",
        generation_config=generation_config,
        safety_settings=safety_settings,
        stream=True,
    )

    response_text = ""
    for response in responses:
        response_text += response.text

    return response_text
def analyze_call_logs_main(flow):
    # initialize the input variable
    # flow = 'negative'
    if (flow == 'record'):
        test_text = ''
        # Initialize recognizer
        recognizer = sr.Recognizer()

        # Use the microphone as the source for input
        with sr.Microphone() as source:
            print("Listening...")
            recognizer.adjust_for_ambient_noise(source)
            audio_data = recognizer.listen(source)
            print("Recognizing...")

            # Recognize speech using Google's Speech-to-Text API
            try:
                test_text = recognizer.recognize_google(audio_data)
            except sr.UnknownValueError:
                print("Google Speech Recognition could not understand the audio")
            except sr.RequestError as e:
                print(f"Could not request results from Google Speech Recognition service; {e}")
    elif (flow == 'negative'):
        print('loading wav file from GCS')
        test_text = transcribe_audio_with_speaker_diarization('gs://ct-transcript-bucket1/potential-lead.wav')
    else:
        test_text = transcribe_audio_with_speaker_diarization('bonds_sale_sara-samantha.wav')

    # test_text='My name is Joseph and I am the author of this code.'
    print("#################################################\n\n")
    print(f"Transcription:\n{test_text}")
    print("\n\n#################################################\n\n")
    print("Generating.....\n\n")
    return generate(test_text)

app.layout = dbc.Container(
    fluid=True,
    style={"--bs-gutter-x": "0rem"},
    children=[
        md.Paper(square=True,
                 children=[
                     md.Grid(style={"flexGrow": "2"}, container=True, xs=12, children=[
                         md.Grid(item=True, xs=1, children=[
                             md.Icon(className="bi bi-c-square-fill", style={'height': '40px', 'color': '#FFFFFF'}),
                             # md.Typography("RM Conversation Dashbord", variant="h4", style={"width": "90%","color": "#3338FF"})
                         ], style={'max-width': '2.33333%'}),
                         md.Grid(item=True, xs=6, children=[
                             md.Typography("RM Calls Dashboard", variant="h6",
                                           style={"width": "90%", "color": "#FFFFFF", 'text-align': 'left',
                                                  'vertical-align': 'middle', 'padding-left': '10px',
                                                  'font-size': '25px'})
                         ]),
                         md.Grid(item=True, xs=3, children=[

                         ]),
                         md.Grid(item=True, xs=1, children=[
                             md.Avatar(src="https://flagcdn.com/h80/sg.png",
                                       style={"bgcolor": "#3368FF", "float": "right", }),
                             md.Icon(className="bi bi-bell-fill", style={"color": "white", "height": "2em"})
                         ]),
                         md.Grid(item=True, xs=1, children=[
                             md.Icon(className="bi bi-box-arrow-right",
                                     style={"color": "white", "float": "right", "height": "2em"}),

                         ]),
                     ])], style={"background-color": "#1a3347", "padding": "10px", "height": "80px"}),
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
                    children=[_make_grid_item(s) for s in [("Total Customers:10",total_customer_img), ("Potential Leads:12",potential_leads_img), ("Missed Leads:5",missed_leads_img), ("Fulfilled:10",fullfiled_img)]]

                ),
                md.Paper(
                    style={
                        "width": "100%",
                        "padding": "10px",
                        "position": "relative",
                        "backgroundColor": "#ffffff",
                    },
                    children=[
                        _customer_list(customers),
                    ]
                )
            ],
        ),
        md.Dialog(
            id="dialog",
            open=False,
            fullScreen=True,
            fullWidth=True,
            children=[md.DialogTitle("Analyse Voice Conversation"),
                      md.DialogContent(children=[
dbc.Container(
    fluid=True,
    children=[
        md.DialogActions(
                        md.Button("Close", id="close")
                      ),
        #header_component("RM Dashboard", "1"),
        html.Hr(),
        header_component("Customer Conversation Portal", "4"),
        earlier_conversations_component(),
        html.Div(children=[md.Paper(id='output-div', style={"display": "block"}), md.Button("Analyse", id="analyse")],
                 style={"display": "block", "margin-top": "300px"}),
        dcc.Interval(id='progress-interval', interval=1 * 1000, n_intervals=0, disabled=True),
        dbc.Progress(id="progress-bar", value=0, max=100, style={"height": "20px", "marginTop": "10px"}),

        html.Hr(),
        html.Div(id="livetracker"),
        dbc.Spinner(html.Div(id="loading-component", style={'display': 'none'})),
        dcc.Store(id="store-conversation", data="")
    ],
)
                      ]),
                      ]

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
    Output('audio-player', 'src'),
    Input('styling-selections', 'cellClicked'),
    prevent_initial_call=True
)
def play_audio_on_click(cell):
    # Print the cell object for debugging purposes
    print("Cell object:", cell)

    # Check if 'cell' and its nested keys exist
    if cell and 'colId' in cell:
        if cell['colId'] == 'Play':
            return '/assets/Potential lead.wav'

@app.callback(
    [Output('progress-interval', 'disabled'),
     Output('progress-interval', 'n_intervals'),
     Output('progress-bar', 'value'),
     Output('livetracker', 'children'),
     Output('loading-component', 'children'),
     Output('analyse', 'disabled')],
    [Input('analyse', 'n_clicks'),
     Input('progress-interval', 'n_intervals'),
     Input("callrecord", "n_clicks")],
    prevent_initial_call=True
)
def update_components(n_clicks, n_intervals, n_clicks1):
    global progress_value
    ctx = dash.callback_context

    if not ctx.triggered:
        return dash.no_update

    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]
    if trigger_id == 'analyse' or trigger_id == 'progress-interval':

        transcript = sample_transcript
        # transcript = analyze_call_logs_main('negative')
        # Handle progress updates
        if n_intervals is not None:
            if progress_value >= 100:
                return True, 0, 100, livetracker(transcript), None, False
            progress_value += 40  # Update progress value
            return False, n_intervals, progress_value, "Processing...", None, True

        # Handle the "Analyse" button click
        if n_clicks and n_intervals == 0:
            progress_value = 0  # Reset progress
            # Use your actual analysis function or sample transcript
            # Disable the "Analyse" button after click to prevent multiple submissions
            return False, 0, progress_value, livetracker(transcript), dbc.Spinner("Processing..."), True
    elif trigger_id == 'callrecord' or trigger_id == 'progress-interval':
        # transcript = sample_transcript
        transcript = analyze_call_logs_main('record')
        # Handle progress updates
        if n_intervals is not None:

            if progress_value >= 100:
                return True, 0, 100, "Completed...", None, False  # Re-enable the button when complete
            progress_value += 40  # Update progress value
            return False, n_intervals, progress_value, "Listening...", None, True

        # Handle the "Analyse" button click
        if n_clicks1 and n_intervals == 0:
            progress_value = 0  # Reset progress
            # Use your actual analysis function or sample transcript
            # Disable the "Analyse" button after click to prevent multiple submissions
            return False, 0, progress_value, livetracker(transcript), dbc.Spinner("Processing..."), True

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update
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

if __name__ == "__main__":
    app.run_server(debug=True)
