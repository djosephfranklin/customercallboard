import base64
import json
import os
import threading
import time

import dash
import dash_ag_grid as dag
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import materialdashboard as md
import openai
import plotly.graph_objects as go
from dash import callback, ctx
from dash.dependencies import Input, Output, State
import logging
import speech_recognition as sr
import vertexai
import vertexai.preview.generative_models as generative_models
from google.cloud import aiplatform
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.cloud.aiplatform.gapic.schema import predict
from vertexai.generative_models import GenerativeModel

# Authentication
openai.api_key = os.getenv("OPENAI_KEY")

os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="/Users/josephdevaraj/Documents/MTech DSE/Final Project/AudioLogAnalysis/main-basis-430303-p0-fcb81ceab729.json"

gen_content=''

# Define app
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
server = app.server

# Load images
IMAGES = {"Philippe": app.get_asset_url("Philippe.jpg")}

COUNTRY_CODES = {
    "Ireland": "ie",
    "Luxembourg": "lu",
    "Belgium": "be",
    "Spain": "es",
    "France": "fr",
    "Germany": "de",
    "Sweden": "se",
    "Italy": "it",
    "India":"in",
    "Singapore":"sg",
    "Malaysia":"ma",
    "Hong Kong":"hk",
    "Taiwan":"tw",
    "China":"cn",
    "Greece": "gr",
    "Iceland": "is",
    "Portugal": "pt",
    "Malta": "mt",
    "Norway": "no",
    "Brazil": "br",
    "Argentina": "ar",
    "Colombia": "co",
    "Peru": "pe",
    "Venezuela": "ve",
    "Uruguay": "uy",
    "United States":"us"
}


# Helper Functions
def score_indicator(scoreValue):
    score = int(scoreValue.strip('%'))
    fig = go.Figure(go.Indicator(
        domain={'x': [0, 1], 'y': [0, 1]},
        value=score,
        mode="gauge+number+delta",
        title={'text': "Enforcement Score"},
        gauge={
            'axis': {'range': [None, 100]},
            'steps': [
                {'range': [0, 40], 'color': "green"},
                {'range': [40, 60], 'color': "yellow"},
                {'range': [60, 100], 'color': "red"}
            ],
            'threshold': {
                'line': {'color': "red", 'width': 4},
                'thickness': 0.75,
                'value': score
            }
        }
    ))
    return fig

def parse_transcript(transcript):
    transcript = transcript.replace("json", "").replace("`", "")
    return json.loads(transcript, strict=False)

def transcript_card(transcript_data):
    conversations = transcript_data['transcripted'].split("\n")
    return md.Paper(
        elevation=3,
        style={"position": "relative", "width": "auto", "height": "280px"},
        children=[
            md.Typography("UUID: " + transcript_data['uuid'], style={"padding": "20px"}),
            md.Card(
                children=[md.Typography(conversation) for conversation in conversations],
                style={"padding-top": "10px", "padding-bottom": "10px", 'maxHeight': '60%', 'overflow': 'auto'}
            ),
            md.Icon(className="bi bi-mic-fill"),
        ]
    )

def live_tracker_layout(transcript):
    parsed_transcript = parse_transcript(transcript)
    return dbc.Row([
        dbc.Col(md.Paper(dcc.Graph(style={"position": "relative", "width": "280px", "height": "280px"},
                                    figure=score_indicator(parsed_transcript['score'])), elevation=3), md=3),
        dbc.Col(transcript_card(parsed_transcript), md=9)
    ])

def header_component(name, id):
    title = html.Header(name, style={"margin-top": 5, "padding-top": "10px"})
    if id == "1":
        logo = html.Header("RM Logged In: RM09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    elif id == "3":
        logo = html.Header("Customer: CUS09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    elif id == "2":
        return dbc.Row([dbc.Col([title, md.Button("Call Live", id="callrecord")], md=8)])
    else:
        return dbc.Row([dbc.Col(title, md=8)])

def earlier_conversations_component():
    columnDefs = [
        {"field": "UUID", "cellRenderer":"CheckboxRenderer","tooltipField": "Customername","tooltipComponentParams": {"showDelay": 100}},
        {"field": "Customername", "cellRenderer": "FlagsCellRenderer"},
        {"field": "CustomerID"},
        {"field": "RelationshipID"},
        {"field": "Date", "headerName":"Last Call Date"},
        {"field": "Actionable", "cellRenderer": "Button", "cellRendererParams": {"className": "btn btn-success"}},
        {"field": "Quick Hint"},
        {"field": "Score"}
    ]
    rowData = [
        {"UUID": "CUS01234-30-003", "country":"sg", "CustomerID": "CUS01234", "RelationshipID":"R1324", "Customername":"John Smith", "Date": "30-July-2024",
         "Quick Hint": "Buy-1", "Actionable": "Missed Lead:1", "Score": "Recommended"},
        {"UUID": "CUS01234-30-003",  "country":"it", "CustomerID": "CUS03412", "RelationshipID":"R1325","Customername":"Will Turner","Date": "30-July-2024",
         "Quick Hint": "Buy-8", "Actionable": "Potential Lead:2", "Score": "Recommended"},
        {"UUID": "CUS01234-30-002", "country":"fr",  "CustomerID": "CUS01431", "RelationshipID":"R1326","Customername":"Philip Mathew", "Date": "30-July-2024",
         "Quick Hint": "Sell-1", "Actionable": "Completed:3", "Score": "Recommended"}
    ]
    return dag.AgGrid(
        id="styling-selections",
        className="ag-theme-quartz-dark",
        columnSize="sizeToFit",
        columnDefs=columnDefs,
        rowData=rowData,
        defaultColDef={"resizable": True, "sortable": True, "filter": True},
        dashGridOptions={"animateRows": True, 'cacheQuickFilter': True}
    )

def textbox_component(text, box="AI", name="Philippe"):
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
        thumbnail = html.Img(src=IMAGES["Philippe"], style={"border-radius": 50, "height": 36, "margin-right": 5, "float": "left"})
        textbox = dbc.Card(text, style=style, body=True, color="light", inverse=False)
        return html.Div([thumbnail, textbox])
    else:
        raise ValueError("Incorrect option for `box`.")

def _make_grid_item(size: int) -> md.Grid:
    return md.Grid(
        # Children components should have the `item=True` attribute.
        item=True,
        # The size (in number of columns) of the item can be set depending on the screen size (xs, sm, md, lg, xl).
        # The size for each screen size can be set, or some can be left unspecified.
        # In this case, only `xs` is used, which means that the layout will always be the same, independently of the
        # screen size (hence will be unresponsive).
        xs=size,
        children=[_make_paper_item(f"Size {size}")],
    )


def _make_paper_item( text: str) -> md.Paper:
    return md.Paper(
        children=[text],
        style={
            "padding": "20px",
            "height" : "200px",
            "textAlign": "center",
            "backgroundColor": "#eeeeee",
        },
    )

progress_value = 0

# Layout
app.layout = dbc.Container(
    fluid=True,
    children=[
        header_component("RM Dashboard", "1"),
        html.Hr(),
        header_component("Customer Conversation Portal", "4"),

        earlier_conversations_component(),
        html.Div(id='output-div'),
        html.Div(children=[md.Button("Analyse", id="analyse")]),
        html.Div(id="livetracker"),
        dbc.Spinner(html.Div(id="loading-component", style={'display': 'none'})),
        dcc.Interval(id='progress-interval', interval=1 * 1000, n_intervals=0, disabled=True),
        dbc.Progress(id="progress-bar", value=0, max=100, style={"height": "30px", "marginTop": "10px"}),
        html.Hr(),
        dcc.Store(id="store-conversation", data=""),
        md.Dialog(fullScreen=False, maxWidth="xl", fullWidth=True, id="popup", open=False, children=[md.DialogTitle("id")]),
        html.Div(id="display-conversation", style={"overflow-y": "auto", "display": "flex", "height": "calc(90vh - 132px)", "flex-direction": "column-reverse"}),
        dbc.Spinner(html.Div(id="loading-component", style={'display': 'none'})),
        dbc.InputGroup(
            children=[
                md.IconButton(),
                dbc.Input(id="user-input", placeholder="Write to the chatbot...", type="text"),
                md.Icon(className="bi bi-mic-fill", id="record"),
                dbc.Button("Submit", id="submit"),
            ]
        ),

    ],
)


# Create logger.
logger = logging.getLogger("app")

# Callbacks

@app.callback(
    [Output('progress-interval', 'disabled'),
     Output('progress-interval', 'n_intervals'),
     Output('progress-bar', 'value'),
     Output('livetracker', 'children'),
     Output('loading-component', 'children')],
     [Input('analyse', 'n_clicks'),
     Input('progress-interval', 'n_intervals')],
    prevent_initial_call=True
)
def update_components(n_clicks, n_intervals):
    global progress_value

    # Handle the "Analyse" button click
    if n_clicks:
        progress_value = 0  # Reset progress
        # Start the analysis process
        transcript = analyze_call_logs_main('negative')
        # Return initial values
        return False, 0, progress_value, livetracker(transcript), dbc.Spinner("Processing...")

    # Handle progress updates
    if n_intervals is not None:
        if progress_value >= 100:
            return True, 0, progress_value, "Analysis Complete", None  # Disable interval and show completion message
        progress_value += 1  # Update progress value
        return False, n_intervals, progress_value, "Processing...", None

    return dash.no_update, dash.no_update, dash.no_update, dash.no_update, dash.no_update

def long_running_task():
    global progress_value
    # Simulate progress update
    for i in range(0, 101, 10):
        time.sleep(1)  # Simulate time-consuming task
        progress_value = i

def livetracker( transcript):
    encoded_image = base64.b64encode(open('assets/mic.svg', 'rb').read()).decode()
    #transcript['transcripted'].replace( /(?:\r\n|\r|\n)/g, '<br>')
    #print(type(transcript))

    transcript = transcript.replace("json", "").replace("`","")
    #print(transcript)
    transcript = json.loads(transcript, strict=False)

    conversations = transcript['transcripted'].split("\n")
    print(transcript)
    transcript_ = md.Paper(elevation=3, style={"position": "relative", "width": "auto","height": "280px"}, children=[
       #{"uuid":"", "transcripted" : "", "score":"", "actionable" :"", "orderarray" : ""},

        md.Typography("UUID: "+transcript['uuid'], style={"padding":"20px"}),

        md.Card(children=[md.Typography(conversation) for conversation in conversations], style={"padding-top":"10px", "padding-bottom": "10px", 'maxHeight': '60%', 'overflow': 'auto'}),
        md.Icon(className="bi bi-mic-fill"),

        # md.TableContainer(children=[
        #     md.TableHead(transcript['uuid'], style={"padding":"2px"}),
        #     md.TableBody(children=[md.TableRow(transcript['transcripted'], style={"padding":"2px", 'maxHeight': '40px', 'overflow': 'auto'}),
        #                            ]),
        #     md.TableFooter(
        #         html.Img(src="data:image/png;base64,{}".format(encoded_image), height="2rem", width="auto"))
        # ])
    ])
    #logo = md.TableContainer(children=[md.TableRow(children=[md.TableCell(style={"background-color": "green"}, height="10px", width="20px"), md.TableCell(children=[md.Icon(className="bi bi-record2", style={"color":"black"})],style={"background-color": "yellow"}, height="10px", width="20px"), md.TableCell(style={"background-color": "red"}, height="10px", width="20px")])])
    return dbc.Row([ dbc.Col(md.Paper(dcc.Graph(style={"position": "relative", "width": "280px","height": "280px"}, figure=score(transcript['score'])), elevation=3), md=3),dbc.Col(transcript_, md=9)])

# @app.callback(
#     Output("popup", "open"),
#     Input("od", "n_clicks"),
# )
# def open_popup(n_clicks):
#     if ctx.triggered_id == "od":
#         return True
#     return False

@app.callback(
    Output("display-conversation", "children"),
    Input("store-conversation", "data")
)
def update_display(chat_history):
    return [textbox_component(x, box="user") if i % 2 == 0 else textbox_component(x, box="AI") for i, x in enumerate(chat_history.split("<split>")[:-1])]

@app.callback(
    Output("user-input", "value"),
    [Input("submit", "n_clicks"), Input("user-input", "n_submit")],
)
def clear_input(n_clicks, n_submit):
    return ""

def generate(content):
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
  JSON structure: {"uuid":"", "transcripted" : """+content+""", "score":"","scoreReason":"", "actionable" :"", "clientRequested":"", "orderarray" : [{"productType":"","productName":"", "amount":""},{"productType":"","productName":"", "amount":""},{"productType":"","productName":"", "amount":""}]
  """

  #print(template_order_checking)

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


def transcribe_audio(audio_file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(audio_file_path) as source:
        audio = recognizer.record(source)
    try:
        text = recognizer.recognize_google(audio)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")
        return None

def transcribe_audio_with_speaker_diarization(gcs_uri):
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
    operation = client.long_running_recognize(config=config, audio=audio)
    response = operation.result(timeout=600)
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
def analyze_call_logs_main(flow):
    # initialize the input variable
    #flow = 'negative'
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

def score(scoreValue):
    score = int(scoreValue.strip('%'))
    scoreValue = score
    fig = go.Figure(go.Indicator(
        domain = {'x': [0, 1], 'y': [0, 1]},
        value = scoreValue,
        mode = "gauge+number+delta",
        title = {'text': "Enforcement Score"},
        gauge = {'axis': {'range': [None, 100]},
                 'steps' : [
                     {'range': [0, 40], 'color': "green"},
                     {'range': [40, 60], 'color': "yellow"},
                 {'range': [60, 100], 'color': "red"}],
                 'threshold' : {'line': {'color': "red", 'width': 4}, 'thickness': 0.75, 'value': scoreValue}}))
    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
