import base64
import os
from textwrap import dedent
import json
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
import os
import speech_recognition as sr
import vertexai
import vertexai.preview.generative_models as generative_models
from google.cloud import aiplatform
from google.cloud import speech_v1p1beta1 as speech
from google.cloud import storage
from google.cloud.aiplatform.gapic.schema import predict
from vertexai.generative_models import GenerativeModel


@callback(
    Output("livetracker", "children"),
     Input("analyse", "n_clicks"),
    config_prevent_initial_callbacks=True,
)
def livetrackerupdate(n_clicks):
    if ctx.triggered_id == "analyse":
        print("Catch")
        #transcript = {"uuid": "1701334308754", "transcripted": "Speaker 2: Good morning, Sarah. How can I assist you today? Hey \nSpeaker 1: Samantha. I'm interested in exploring investment options, but I'm more comfortable with bonds. \nSpeaker 2: I understand bonds are a safe choice, but have you considered diversifying your \nSpeaker 1: portfolio with a mutual \nSpeaker 2: fund? We have a solid mutual fund low-volatility Equity portfolio that offers High returns and quarterly dividends. It has a 70% spread in the US Equity market and 30% in fixed-income. It has been performing well in the market for a long time and it's a good fun to start investing. I'm not \nSpeaker 1: sure about mutual funds. I've always preferred bonds because they feel safer to me while \nSpeaker 2: bonds are safe. Your portfolio is already heavily invested in them diversifying with this mutual fund could balance your Investments and potentially yield higher Returns the US market portion provides growth potential while the fixed-income part offers stability. \nSpeaker 1: I see the point But I'm worried about the risks involved with mutual funds. \nSpeaker 2: It's natural to be cautious. However, this mutual fund is managed by top experts who carefully select the investment the fixed-income part helps mitigate risk ensuring that your investment remains relatively stable. \nSpeaker 1: I'm still hesitant. I like the predictability of bonds predictability is important but \nSpeaker 2: so is growth by investing solely in bonds. You might miss out on higher returns. This mutual fund is designed to give you the best of both worlds growth from the US market and stability from fixed-income. I'll have to think about it \nSpeaker 1: bonds just feel more secure to me. \nSpeaker 2: I understand. It's important to feel secure in your Investments take your time. But remember that diversifying can protect your portfolio from Market volatility and enhance overall returns if you have any questions or need more information, I'm here to help.", "score": "60%", "scoreReason": "The banker is trying to persuade the customer to invest in Mutual funds by highlighting the benefits like 'High returns', 'quarterly dividends', 'performing well in the market', 'balance your investments', 'potentially yield higher returns', 'growth potential' etc.  The customer is hesitant and wants to stick with bonds. ", "actionable": "Potential Lead", "clientRequested": "BND:Bonds:BUY:", "orderarray": [{"productType": "MF", "productName": "low-volatility Equity portfolio", "amount":""}]}
        transcript = analyze_call_logs_main('negative')
        #print(transcript)
        return livetracker(transcript)
    else:
        return None

# @callback(
#     Output("livetracker", "children"),
#      Input("callrecord", "n_clicks"),
#     config_prevent_initial_callbacks=True,
# )
# def livetrackerupdate1(n_clicks):
#     if ctx.triggered_id == "callrecord":
#         print("Catch")
#         #transcript = {"uuid": "1701334308754", "transcripted": "Speaker 2: Good morning, Sarah. How can I assist you today? Hey \nSpeaker 1: Samantha. I'm interested in exploring investment options, but I'm more comfortable with bonds. \nSpeaker 2: I understand bonds are a safe choice, but have you considered diversifying your \nSpeaker 1: portfolio with a mutual \nSpeaker 2: fund? We have a solid mutual fund low-volatility Equity portfolio that offers High returns and quarterly dividends. It has a 70% spread in the US Equity market and 30% in fixed-income. It has been performing well in the market for a long time and it's a good fun to start investing. I'm not \nSpeaker 1: sure about mutual funds. I've always preferred bonds because they feel safer to me while \nSpeaker 2: bonds are safe. Your portfolio is already heavily invested in them diversifying with this mutual fund could balance your Investments and potentially yield higher Returns the US market portion provides growth potential while the fixed-income part offers stability. \nSpeaker 1: I see the point But I'm worried about the risks involved with mutual funds. \nSpeaker 2: It's natural to be cautious. However, this mutual fund is managed by top experts who carefully select the investment the fixed-income part helps mitigate risk ensuring that your investment remains relatively stable. \nSpeaker 1: I'm still hesitant. I like the predictability of bonds predictability is important but \nSpeaker 2: so is growth by investing solely in bonds. You might miss out on higher returns. This mutual fund is designed to give you the best of both worlds growth from the US market and stability from fixed-income. I'll have to think about it \nSpeaker 1: bonds just feel more secure to me. \nSpeaker 2: I understand. It's important to feel secure in your Investments take your time. But remember that diversifying can protect your portfolio from Market volatility and enhance overall returns if you have any questions or need more information, I'm here to help.", "score": "60%", "scoreReason": "The banker is trying to persuade the customer to invest in Mutual funds by highlighting the benefits like 'High returns', 'quarterly dividends', 'performing well in the market', 'balance your investments', 'potentially yield higher returns', 'growth potential' etc.  The customer is hesitant and wants to stick with bonds. ", "actionable": "Potential Lead", "clientRequested": "BND:Bonds:BUY:", "orderarray": [{"productType": "MF", "productName": "low-volatility Equity portfolio", "amount":""}]}
#         transcript = analyze_call_logs_main('record')
#         #print(transcript)
#         return livespeaker(transcript)
#     else:
#         return None

@callback(
    Output("popup", "open"),
    Input("od", "n_clicks")
)
def openPopUp(n_clicks):
    if  ctx.triggered_id == "od":
        return True
    else:
        return False

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

def livespeaker( transcript):
    encoded_image = base64.b64encode(open('assets/mic.svg', 'rb').read()).decode()
    #transcript['transcripted'].replace( /(?:\r\n|\r|\n)/g, '<br>')
    #print(type(transcript))

    transcript = transcript.replace("json", "").replace("`","")
    print(transcript)
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

def Header(name, app, id):
    title = html.H4(name, style={"margin-top": 5, "padding-top": "10px"})
    if id == "1":
        logo = html.H4("RM Logged In: RM09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    if id == "3":
        logo = html.H4("Customer: CUS09651", style={"margin-top": 5, "padding-top": "10px"})
        return dbc.Row([dbc.Col(title, md=8), dbc.Col(logo, md=4)])
    if id == "2":
        return dbc.Row([dbc.Col(children=[title, md.Button("Call Live", id="callrecord")], md=8)])
    else:
        return dbc.Row([dbc.Col(title, md=8)])

def EarlierConversations(name, app):
    title = html.H5(name, style={"margin-top": 5, "padding-top": "10px"} )
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
        #  "Score": "Recommended"
        #  },
        {"UUID": "CUS01234-30-003",
         "CustomerID": "CUS01234",
         "Date": "30-July-2024",
         "PLAYBACK": "PLAYBACK-001.wav",
         "Orders": "4",
         "Quick Hint": "Buy-1",
         "Actionable": "Missed Lead:1",
         "Score": "Recommended"
         },
        {"UUID": "CUS01234-30-003",
         "CustomerID": "CUS01234",
         "Date": "30-July-2024",
         "PLAYBACK": "PLAYBACK-001.wav",
         "Orders": "4",
         "Quick Hint": "Buy-8",
         "Actionable": "Potential Lead:2",
         "Score": "Recommended"
         },
        {"UUID": "CUS01234-30-002",
         "CustomerID": "CUS01234",
         "Date": "30-July-2024",
         "PLAYBACK": "PLAYBACK-001.wav",
         "Orders": "4",
         "Quick Hint": "Sell-1",
         "Actionable": "Completed:3",
         "Score": "Recommended"
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
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
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

app.layout = dbc.Container(
    fluid=True,
    children=[
        Header("RM Conversation Tracker", app, "1"),
        html.Hr(),
        Header("Customer in Live : CUS02012", app, "2"),
        html.Div(id="livetracker"),
        html.Hr(),
        Header("Conversation History", app, "4"),
        html.Div(children=[md.Button("Analyse", id="analyse"), md.Button("Order Details", id= "od")]),
        EarlierConversations("Conversation History", app),
        dcc.Store(id="store-conversation", data=""),
        md.Dialog(fullScreen=False, maxWidth="xl", fullWidth=True, id="popup", open=False,
                  children=[
                      md.DialogTitle("id")
                  ]
                  ),
        conversation,
        controls,
        dbc.Spinner(html.Div(id="loading-component")),
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


os.environ["GOOGLE_APPLICATION_CREDENTIALS"] ="/Users/josephdevaraj/Documents/MTech DSE/Final Project/AudioLogAnalysis/main-basis-430303-p0-fcb81ceab729.json"

gen_content=''

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

def transcribe_audio1(audio_file_path):
    client = speech.SpeechClient()
    with open(audio_file_path, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=48000,
        language_code="en-US",
    )

    response = client.recognize(config=config, audio=audio)
    transcript = ''
    for result in response.results:
        transcript += result.alternatives[0].transcript
    return transcript

def analyze_text_with_vertex_ai(project_id, endpoint_id, location, text):
    aiplatform.init(project=project_id, location=location)
    endpoint = aiplatform.Endpoint(endpoint_id=endpoint_id)

    instance = predict.instance.TextClassificationPredictionInstance(content=text).to_value()
    instances = [instance]
    parameters = predict.params.TextClassificationPredictionParams().to_value()

    prediction = endpoint.predict(instances=instances, parameters=parameters)
    return prediction

def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
    """Uploads a file to the bucket."""
    # Initialize a client
    storage_client = storage.Client()

    # Get the bucket
    bucket = storage_client.bucket('ct-transcript-bucket1')

    # Create a blob (object) in the bucket
    blob = bucket.blob('potential-lead.wav')

    # Upload the file to GCS
    blob.upload_from_filename('Potential lead.wav')

    print(f"File {source_file_name} uploaded to {destination_blob_name}.")

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

if __name__ == "__main__":
    app.run_server(debug=True)
