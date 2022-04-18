# import libraries for the DAS
from xlwt import Workbook
import xlwt
from logging import debug
import dash
import dash_html_components as html
import dash_bootstrap_components as dbc
import dash_leaflet as dl
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import dash_daq as daq
from numpy.core.fromnumeric import var
import plotly
import plotly.graph_objects as go
from flask import request
import flask
import plotly.express as px
import datetime as dt
import requests


# List for the X axis
X = [0]
# List for the Y axis
Y = [0]
# Variable distance will store and update the distance recevied from the ultrasonic sensor
distance = 0

# GraduatedBar used for displaying the battery level

bar = daq.GraduatedBar(
    className="bar",
    id="my-bar",
    color={"gradient": True, "ranges": {
        "#4bbf73": [0, 25], "#ed9d2b": [25, 75], "#d9534f": [75, 100]}},
    showCurrentValue=False,
    value=50,
    step=5,
    min=0,
    max=100,
    label="Battery",
)

# Gauge created displaying the speed of the aircraft
gauge2 = daq.Gauge(
    id='speed',
    color={"gradient": True, "ranges": {
        "green": [0, 5], "yellow": [5, 10], "red": [10, 15]}},
    value=0,
    label='Speed(m/s)',
    showCurrentValue=True,
    max=15,
    min=0,
    className='g2',
    units='m/s',
    size=200,
)

# Geographical map for displaying the location of the aircraft

# Rotated custom marker.
iconUrl = "https://dash-leaflet.herokuapp.com/assets/icon_plane.png"

marker = dict(rotate=True, markerOptions=dict(
    icon=dict(iconUrl=iconUrl, iconAnchor=[16, 16])))


patterns = [dict(repeat='10', dash=dict(pixelSize=2, pathOptions=dict(color='#000', weight=1, opacity=0.2))),
            dict(offset='16%', repeat='20%', marker=marker)]


polyline = dl.Polyline(positions=[[18.5532, 73.8040], [18.5534, 73.8042], [18.5536, 73.8044], [18.5538, 73.8046], [18.5540, 73.8048], [18.5542, 73.8050], [18.5545, 73.8052],
                                  [18.5547, 73.8054], [18.5549, 73.8056], [18.5585, 73.8085], [18.5595, 73.8095], [18.5605, 73.8105], [18.5610, 73.8110]])

marker_pattern = dl.PolylineDecorator(children=polyline, patterns=patterns)

map_fig = dl.Map([dl.TileLayer(), marker_pattern],
                 zoom=15, center=(18.5575, 73.8075), style={'width': '400px', 'height': '330px'}, className="map")

# FPV Video Feed

webcam = html.Img(
    id="mycam", src="http://127.0.0.1:3003/video_feed", className="video")

alert4 = dbc.Toast(
    [html.H1("Green Zone")],
    id="simple-toast-4",
    header="Success",
    icon="success",
    className="alert1",
    dismissable=True,
)

alert3 = dbc.Toast(
    [html.H1("Yellow Zone")],
    id="simple-toast-3",
    header="Warning",
    icon="warning",
    className="alert1",
    dismissable=True,
)

alert2 = dbc.Toast(
    [html.H1("Red Zone")],
    id="simple-toast-2",
    header="Danger",
    icon="danger",
    className="alert1",
    dismissable=True,
)

alert1 = dbc.Toast(
    [html.H1("Arduino Not Connected!")],
    id="simple-toast-1",
    header="Danger",
    icon="danger",
    className="alert1",
    dismissable=True,
)

# Display the Altitude of the aircraft

led = daq.LEDDisplay(
    id='my-LED-display',
    label="Altitude(feet)",
    value="00.00",
    size=96,
    className="led",
    color="#4bbf73"
)


server = flask.Flask(__name__)
app = dash.Dash(__name__, server=server,
                external_stylesheets=[dbc.themes.BOOTSTRAP])

# padding for the page content
CONTENT_STYLE = {
    "transition": "margin-left .5s",
    "margin-left": "2rem",
    "margin-right": "2rem",
    "padding": "2rem 1rem",
}

content = html.Div(id="page-content", children=[], style=CONTENT_STYLE)

navbar = dbc.NavbarSimple(
    children=[
        dbc.Col(
            html.Img(src=app.get_asset_url('logo white.png'), className="logo"), className='logo-div'),
        dbc.Row(children=[
            dbc.Col(dbc.NavLink("Dashboard",
                                href="/", active="exact"), className="dashboard"),
            dbc.Col(dbc.NavLink("Playback", href="/page-1",
                    active="exact"), className="playback"),
        ])
    ],
    color="dark",
    dark=True,
    className="nav",
    links_left=True,
)


# app layout
app.layout = html.Div([
    dcc.Location(id="url"),
    html.Div(
        children=[navbar, content]
    )
])


text_input_1 = html.Div(
    [
        dbc.Input(id="input1", placeholder="Latitude", type="number"),
        html.Br(),
        html.P(id="output1"),
    ]
)

text_input_2 = html.Div(
    [
        dbc.Input(id="input2", placeholder="Longitude", type="number"),
        html.Br(),
        html.P(id="output2"),
    ]
)


@app.callback(Output("output1", "children"), [Input("input1", "value")])
def output_text(value):
    return value


@app.callback(Output("output2", "children"), [Input("input2", "value")])
def output_text(value):
    return value


# Workbook is created
wb = Workbook()

# add_sheet is used to create sheet.
sheet1 = wb.add_sheet('Sheet 1')
value = []
sheet1.write(0, 0, 'Reading')
sheet1.write(0, 1, 'Distance')


# callback function generated for the ultrasonic sensor data updation in the following :

# Speed Gauge(In reality IMU data)
# Graduated bar(In reality Battery Level)
# LED Display()
i = 1


@app.callback(
    Output('simple-toast-4', 'is_open'),
    Output('simple-toast-3', 'is_open'),
    Output('simple-toast-2', 'is_open'),
    Output('simple-toast-1', 'is_open'),
    Output('speed', 'value'),
    Output('my-bar', 'value'),
    Output('my-LED-display', 'value'),
    Input("timing", "n_intervals"),
)
def update(n_intervals):
    try:
        global i
        global distance
        distance = float(distance)
        if (distance == (-1)):
            return False, False, False, True, 0, 0, 0
        elif (distance != (-1)):
            time = dt.datetime.now().strftime('%H:%M:%S')
            sheet1.write(i, 0, time)
            sheet1.write(i, 1, distance)
            wb.save('DAS_GUI.xls')
            i = i+1
            if distance < 400:
                ledDistance = "0%.2f" % round(distance, 2)
                return True, False, False, False, distance, distance, ledDistance
            elif (400 <= distance < 1000):
                ledDistance = "%.2f" % round(distance, 2)
                return False, True, False, False, distance, distance, ledDistance
            else:
                ledDistance = "%.2f" % round(distance, 2)
                return False, False, True, False, distance, distance, ledDistance

    except:
        return False, False, False, True, 0, 0, "00.00"

# call back function for displaying the alert when boolean value is True for the Boolean Switch


@app.callback(
    Output('my-LED-display', 'color'),
    Output("switch", "disabled"),
    Input("switch", "on"),
)
def open_toast(n):
    if n == None:
        return "#4bbf73", False
    if n == True:
        return "#ff0000", True
    else:
        return "#4bbf73", False

# call back function for plotting the live data of the altitude under the playback function
# temporarily we are updating the ultrasonic data,in reality we will display the altitude


@app.callback(Output('live-graph', 'figure'),
              [Input('graph-update', 'n_intervals')])
def update_graph_scatter(input_data):
    global distance
    global X
    global Y

    data = plotly.graph_objs.Scatter(
        x=list(X),
        y=list(Y),
        name='Scatter',
        mode='lines+markers',
    )

    return {'data': [data], 'layout': go.Layout(xaxis=dict(range=[min(X), max(X)]),
                                                yaxis=dict(range=[min(Y), max(Y)]), xaxis_title="Count",
                                                yaxis_title="Altitude(feet)",
                                                )}


record_button = dbc.Button("Record", color="success",
                           className="button", id="example-button", n_clicks=0)


v = True


@app.callback(
    Output("example-button", "color"),
    Output("example-button", "value"),
    Input("example-button", "n_clicks")
)
def on_button_click(n):
    global v
    if n == None:
        return "success", "Record"
    if v:
        v = False
        return "success", "Record"
    else:
        requests.get("http://127.0.0.1:3003/video_record",
                     json={'video': True})
        print("GOT REQUEST")
        v = True
        return "danger", "Record"


@app.callback(

    Output("page-content", "children"),
    [Input("url", "pathname")]
)
def render_page_content(pathname):

    # Layout for the dashboard page
    if pathname == "/":
        return [
            html.Div(
                children=[
                    dbc.Row(
                        children=[
                            dbc.Col(webcam, className="video-col"),
                            dbc.Col(map_fig, className="map-div"),
                            dbc.Col(
                                children=[
                                    dbc.Row(gauge2),
                                    dbc.Row(bar, className="bar")
                                ], className="g2-div")
                        ]
                    ),
                    dbc.Row(
                        children=[

                            dbc.Col(children=[
                                    dbc.Row(record_button,
                                            className="button-div"), dbc.Row(html.H4("Start"), className="heading1"), dbc.Row(text_input_1, className="text_input_1"), dbc.Row(text_input_2, className="text_input_2"), dbc.Row(html.H4("End"), className="heading1"), dbc.Row(text_input_1, className="text_input_3"), dbc.Row(text_input_2, className="text_input_4")
                                    ]),

                            dbc.Col(led, className="led-div"),
                            dbc.Col(
                                children=[dbc.Row(alert1, className="alert-div"), dbc.Row(alert2, className="alert-div"), dbc.Row(alert3, className="alert-div"), dbc.Row(alert4, className="alert-div"), ]),


                        ]
                    ),

                    dcc.Interval(id="timing", interval=1000, n_intervals=0)

                ])]

    # Layout for the playback page
    elif pathname == "/page-1":
        return [
            html.H1('Altitude Playback',
                    style={'textAlign': 'center'}),
            html.Div(
                [

                    dcc.Graph(id='live-graph', animate=False,
                              className='my-plot'),
                    dcc.Interval(
                        id='graph-update',
                        interval=3*1000
                    ),
                ]
            )
        ]

#  route for POSTING the Arduino data to the server


@ server.route('/data', methods=['POST'])
def publish():
    global distance
    global X
    global Y
    if request.method == 'POST':
        try:
            result = request.get_json()
            distance = result['value']
            X.append(X[-1]+1)
            Y.append(float(distance))
            return "Sent:"+distance

        except Exception as e:
            print(e)
            return "error"


if __name__ == '__main__':
    app.run_server()
