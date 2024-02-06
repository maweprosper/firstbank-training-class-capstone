from dash import Dash, html, dcc, callback, Output, Input, State
from dash.dcc import Loading  # Import the Loading component
import requests
import os
from dotenv import load_dotenv
from openai import AzureOpenAI
import time

external_script = ["https://tailwindcss.com/", { "src": "https://cdn.tailwindcss.com"}]
app = Dash(__name__, external_scripts=external_script)
app.scripts.config.serve_locally = True

# Function to generate image from prompt
def generate_image_from_prompt(prompt): 
    try:
        # Get Azure OpenAI Service settings
        load_dotenv()
        api_base = os.getenv("AZURE_OAI_ENDPOINT")
        api_key = os.getenv("AZURE_OAI_KEY")
        api_version = '2023-06-01-preview'

        # Make the initial call to start the job
        url = "{}openai/images/generations:submit?api-version={}".format(api_base, api_version)
        headers= { "api-key": api_key, "Content-Type": "application/json" }
        body = {
            "prompt": prompt,
            "n": 2,
            "size": "512x512"
        }
        submission = requests.post(url, headers=headers, json=body)

        # Get the operation-location URL for the callback
        operation_location = submission.headers['Operation-Location']

        # Poll the callback URL until the job has succeeded
        status = ""
        while (status != "succeeded"):
            time.sleep(3) # wait 3 seconds to avoid rate limit
            response = requests.get(operation_location, headers=headers)
            status = response.json()['status']

        #print(response.json())
        # Get the results
        image_url = response.json()['result']['data'][0]['url']

        # Return the URL for the generated image
        return image_url
    except Exception as ex:
        print(ex)
        return None

# Function to generate prompt using Azure OpenAI
def generate_prompt(value):
    try:
        load_dotenv()
        azure_oai_endpoint = os.getenv("AZURE_OAI_ENDPOINT")
        azure_oai_key = os.getenv("AZURE_OAI_KEY")
        azure_oai_model = os.getenv("AZURE_OAI_MODEL")

        client = AzureOpenAI(
            azure_endpoint = azure_oai_endpoint,
            api_key=azure_oai_key, 
            api_version="2023-05-15"
        )

        response = client.chat.completions.create(
            model=azure_oai_model,
            temperature=0.7,
            max_tokens=120,
            messages=[
                {"role": "system", "content": "You are a DallE prompts generating professional that generates a single prompt"},
                {"role": "user", "content": value}
            ]
        )

        #print(response.choices[0].message.content)

        prompt = response.choices[0].message.content

        #image_url = generate_image_from_prompt(prompt)

        return prompt

    except Exception as ex:
        print(ex)
        return None

# Layout and styling
app.layout = html.Div(style={'height':'100vh','background-image': 'url(assets/picture.jpg)','background-repeat':'none','background-size':'cover', 'padding': '30px'}, children=[
    html.H1(children='GROUP A IMAGE GENERATING APP', style={'margin-top':'20px','text-shadow':'2px 2px 4px rgba(0, 0, 0, 0.5)','font-size':'50px','textAlign': 'center','font-family':'Cursive', 'font-weight':'bold','color':'#ffffff'}),
    dcc.Input(
        id="basic-prompt-input",
        type="text",
        placeholder="Hi, What Image Would You Like to Generate?",
        style={'margin-top':'20px','box-shadow': '-1px 1px 13px 2px rgba(0,0,0,0.49)','display':'block','width': '60%','border':'none', 'margin': '10px auto', 'padding': '10px', 'borderRadius': '10px', 'backgroundColor': '#ffffff', 'color': '#333333'}



    ),
    html.Button('Generate',className='hover:bg-black hover:text-white', id='generate-button', n_clicks=0, style={'font-family': "cursive",'display': 'block', 'margin': '10px auto', 'backgroundColor': '#22a1e6', 'color': 'white', 'padding': '10px 20px', 'border': 'none', 'cursor': 'pointer', 'borderRadius': '15px'}),
    html.Div(id='generated-prompt-output', style={'color':'white','textAlign': 'center', 'margin': '20px 0', 'font-family': "cursive", 'color': "white",'font-size':'25px'}),
    Loading(
        id="loading-output",
        type="circle",
        children=[
            html.Div(id='prompt-output', children='', style={'color':'white','font-weight': 'bold', 'margin-bottom': '10px'}),
            html.Div(id="generated-images-container", style={'display': 'flex', 'flexWrap': 'wrap', 'justifyContent': 'center'})
        ]
    ),
    html.Div(id='loader-overlay', children=[html.Div(className='loader')], style={'display': 'none'})
])

# Callback to generate images
@app.callback(
    Output('generated-images-container', 'children'),
    Output('generated-prompt-output', 'children'),
    Output('loader-overlay', 'style'),
    Input('generate-button', 'n_clicks'),
    State('basic-prompt-input', 'value'),
    prevent_initial_call=True
)
def generate_images(n_clicks, value):
    try:
        start_time = time.time()  # Start measuring time
        prompt = generate_prompt(value)  # Generate prompt
        prompt_output = html.Div(f"Generated Prompt: {prompt}")  # Display generated prompt

        image_urls = []
        # Generate multiple images
        for i in range(2):  # Change 2 to the desired number of images
            image_url = generate_image_from_prompt(prompt)
            image_urls.append(html.Img(src=image_url, style={'width': '450px', 'margin': '10px'}))

        end_time = time.time()  # End time measurement
        loading_time = round(end_time - start_time, 2)  # Calculate loading time

        loader_style = {'display': 'none'}  # Hide loader

        return image_urls, prompt_output, loader_style

    except Exception as ex:
        print(ex)
        return None, None, None

if __name__ == '__main__':
    app.run_server(debug=True)