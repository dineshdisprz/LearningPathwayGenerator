import streamlit as st
import os
import json
from openai import AzureOpenAI
from pydantic import BaseModel
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from typing import List
import os
import json
from openai import AzureOpenAI
from pydantic import BaseModel
from typing import List, Optional, Dict
from pydantic import BaseModel, Field
from typing import List
import requests
# Set your Azure OpenAI API key
os.environ["AZURE_OPENAI_API_KEY"] = '1dfeeaf8f4e945e5a461f82fd08169b3'

# Initialize AzureOpenAI client
client = AzureOpenAI(
    api_version="2023-07-01-preview",
    azure_endpoint="https://disprz-originals.openai.azure.com/",
    api_key=os.environ["AZURE_OPENAI_API_KEY"]
)

# Define the function schema for the output format you want
class SkillLists(BaseModel):
    skill_name: str = Field(..., alias='skill_name', description='Skill Name')
    subskills: List[str] = Field(..., description='List of subskills for the skill')  # Correctly use List[str] for array of strings
    desired_level: str = Field(..., alias='desired_level', description='Desired level of the skill')

class LearningPathway(BaseModel):
    Module_Title: str = Field(..., alias='Module_Title', description='Title of the Module: eg(Introduction to Mercedes-Benz and its product lineup.)')
    intervention_type: str = Field(..., alias='intervention_type', description='Intervention type: eg (Classroom training), (On-the-job training)')
    Content:  str = Field(..., description='Detailed description of the content to be covered in the intervention')  # Correctly use List[str] for array of strings
    skill_names: List[str] = Field(..., alias='skill_names', description='Skills covered in the intervention')

class ExtractedInfo(BaseModel):
    skillList: List[SkillLists] = Field(..., description='List of skills with their subskills and desired level')
    LearningPathwayList: List[LearningPathway] = Field(..., description='List of Learning Pathway content with their intervention type, content and skills addresses')

# Define the function to fetch completion using Azure OpenAI API
def get_completion(objective):
    prompt = f"""
            You are a learning designer working at the L&D department  company. Your job is to design a learning pathway to meet a particular objective given below. You need to break down the objective into constituent skills, desired levels at these skills and design a series of interventions (each intervention can be a type given below). 
            <Objective>
            {objective}
            </Objective>
            <Learning Intervention Types>
            1. Classroom training - (can be in-person or virtual) of 3 hours
            2. Self-paced Learning - Content of between 10-15 minutes from content created for the company
            3. Micro-learning - from content available online including sites like Coursera or YouTube or podcast
            4. Quiz - (answering a multiple choice question)
            5. Conversational Practice assessment  - (where the person speaks to an AI bot in a simulated customer scenario and gives feedback at the end)
            6. On-the-job training - (where a buddy or an evaluator evaluates the advisor on a series of steps)
            7. Manager assessment
            8. Social Post - Making a social post on the intranet
            </Learning Intervention Types>
            The chosen learning intervention type should be Classroom training, Self-paced Learning, Micro-learning, Quiz, Conversational Practice assessment, On-the-job training, Manager assessment, Social Post
            """
    messages = [{"role": "user", "content": prompt}]
    
    # Call the OpenAI function for learning pathway design with the schema for structured output
    response = client.chat.completions.create(
        model="GPT4o",
        messages=messages,
        temperature=0.5,
               functions=[{
            "name": "Learning_Pathway_Designer",
            "parameters": ExtractedInfo.model_json_schema()
        }],
        function_call={"name": "Learning_Pathway_Designer"}
    )
    # Process the response to return it in the required structured format
    return response.choices[0].message.function_call.arguments

# Sample call to get completion and output the learning pathway
class checkpointlists(BaseModel):
    checkpoint_name: str = Field(..., alias='checkpoint_name', description='Name of the checkpoint')
    question_name: str = Field(..., alias='question_name', description='Question name in the checkpoint')

class ExtractedInfo1(BaseModel):
    checkpointbasedquestions: List[checkpointlists] = Field(..., description='List of questions with checkpoints name')

# # Define the function to fetch completion using Azure OpenAI API
def get_completion1(content):
    prompt = f"""
        Create a series of checkpoint-based questions for an on-the-job training session. The training will evaluate an advisor on {content}. This content will change depending on the specific skills or processes being assessed in each session. The session should include checkpoints that assess the advisor's ability to perform various tasks, resolve problems, or follow processes effectively, based on the focus of the training. There can be mutliple questions for a single checkpoint as well. The questions should be actionable and evaluative, focusing on measurable actions or outcomes, and so avoid asking questions that would have avoid subjective or yes/no answers. Just ask questions which an reviewer could rate on a scale of 1-5. Avoid asking questions starting with a did like - Did the advisor confirm their understanding, etc
        """
    messages = [{"role": "user", "content": prompt}]
    
    # Call the OpenAI function for learning pathway design with the schema for structured output
    response = client.chat.completions.create(
        model="GPT4o",
        messages=messages,
        temperature=0.5,
               functions=[{
            "name": "onthejobtraining",
            "parameters": ExtractedInfo1.model_json_schema()
        }],
        function_call={"name": "onthejobtraining"}
    )
    # Process the response to return it in the required structured format
    return response.choices[0].message.function_call.arguments
# Function to get the access token
def get_access_token():
    url = 'https://appsvc-qa.disprz.com/authenticationservice/auth/service/token'
    headers = {
        'accept': 'text/plain',
        'ApiKey': 'oOYEQjw0OFQ6HF4kHFFgjx',
        'Content-Type': 'application/json'
    }
    data = {
        "region": "qa"
    }

    response = requests.post(url, headers=headers, json=data)
    if response.status_code == 200:
        response_json = response.json()
        return response_json.get("token")  
    else:
        raise Exception(f"Failed to get access token: {response.status_code} {response.text}")

# Function to call OJTs using POST
def call_ojts(title):
    url = 'https://appsvc-qa.disprz.com/ojtservice/v1/ojts'
    headers = {
        'Access-Token': 'yRxeW0VB3uvyFTFq+eGoqXnArMq+P8SvSH+RDNwv0CSbxHg8k3dFiNR/GwS+CfeZhHQLFxXVrL6LVRXd/XaBSMivzZbxYDU8wVJhHa8vpXZc6wktKiCk5O0d/QeYiQLAgQbswE+LYSBzlBoj665C0ZIeEk9waC/TZ49OcKr13stGyYtgEKL9KSNN52+zfyNeAP7qMHVboWi8T9PH+g7W86951RYA0aW+IgOrsev3t26PmEtAu0ZtgflIx1i2o2PADJ4hjuzPv7FSjCSLrZlSyoHSuqjjK+2TUh26S1+IQYWf23K5BVhngFysRPaiHduROM5wymweNuTcDsg32hNJxi6TQ1GktraKR+o792whY+InQhCdpYp6MR395CjeMuIm',
        'Content-Type': 'application/json'
    }
    payload = {
  "name": title,
  "description": "sample",
  "image": "Content/LXPProQA/Files/b94755ae-0aaa-485b-82de-e83d836a4b0a/1737628005403",
  "venue": "Dubai",
  "location": {
    "locationName": "Dubai",
    "latitude": 0,
    "longitude": 0
  },
  "objectives": "On-the-job Training",
  "dueInDays": 0,
  "status": 0,
  "passSetting": {
    "passCriteria": 0,
    "reAttemptAfter": 0,
    "watchDuration": 0,
    "isGrading": True,
    "retryAttemptsCount": 0
  },
  "isOpenToPeers": True,
  "duration": "string",
  "certificateDetails": {
    "isCertificateEnabled": True,
    "certificateDesignId": 0
  },
  "cloneMetaData": {
    "parentId": 0,
    "cloneStatus": 0
  },
  "skillIds": [
    0
  ]
}

    response = requests.post(url, headers=headers, json=payload)
    print(response.status_code)
    if response.status_code == 201:
        ojtid=response.text

    return ojtid

def create_checkpoints(ojtid, checkpoint_data):
    url = 'https://appsvc-qa.disprz.com/ojtservice/v1/ojts/checkpoints'
    headers = {
        'Access-Token': 'yRxeW0VB3uvyFTFq+eGoqXnArMq+P8Sv9o3Ad7Vz+VIk4w5EoB83z/H399BjU7B8hHQLFxXVrL6LVRXd/XaBSMivzZbxYDU8wVJhHa8vpXZc6wktKiCk5O0d/QeYiQLAgQbswE+LYSBzlBoj665C0ZIeEk9waC/TZ49OcKr13stGyYtgEKL9KSNN52+zfyNeAP7qMHVboWi8T9PH+g7W86951RYA0aW+IgOrsev3t26PmEtAu0ZtgflIx1i2o2PADJ4hjuzPv7GM1jfwt2npK0Dv9+YDIylwUh26S1+IQYWf23K5BVhngFysRPaiHduROM5wymweNuTcDsg32hNJxi6TQ1GktraKR+o792whY+InQhCdpYp6MR395CjeMuIm',
        'Content-Type': 'application/json'
    }

    # Initialize the base payload structure
    payload = {
        "ojtId": ojtid,
        "name": "OJT-Final-Test-Agent",
        "type": 5,
        "evaluationId": 0,
        "evaluationRunId": 0,
        "questions": []
    }

    # Loop through checkpoint data to add questions dynamically
    for item in checkpoint_data:
        question_data = {
            "checkPointId": 0,
            "question": item["question_name"],  # Get question name from JSON
            "questionType": 1,
            "questionSubType": 0,
            "isMandatory": True,
            "isEvidenceRequired": False,
            "ifResponseEnabled": False,
            "points": 5,
            "references": [],
            "choices": [],
            "groupName": item["checkpoint_name"],  # Set group name from checkpoint name
            "localeText": "",
            "ruleType": None,
            "ruleInput": None,
            "pointer": ""
        }
        # Append each dynamically created question to the payload's "questions" list
        payload["questions"].append(question_data)

    # Make the API call
    response = requests.post(url, headers=headers, json=payload)
    return response.status_code


if "page" not in st.session_state:
    st.session_state.page = "main"

if st.session_state.page == "main":
    # Set page configuration
    st.set_page_config(page_title="Learning Pathway Designer", layout="wide")
    logo_url = 'disprz_reverse.png' 
    left_co, cent_co=st.columns([1, 1.3])
    with cent_co:
        st.image(logo_url, width=200)
    
    st.markdown(
    f"""
    <style>
    .outer-container {{
        background-color: #212751; /* Outer container background */
        padding: 0px 0;
    }}
    .logo {{
        max-width: 200px; /* Adjust the logo size as needed */
        margin-bottom: 20px; /* Add spacing below the logo */
    }}
    .inner-container {{
        background-color: #1A1A45; /* Inner container background */
        padding: 30px;
        border-radius: 10px;
        width: 60%;
        margin: auto;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
        text-align: center; /* Center all content */
        border: 2px solid #787982; /* Border width, style, and color */
        margin-bottom: 45px;
    }}
    .title {{
        font-size: 32px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 20px;
    }}
    .subtitle {{
        font-size: 16px;
        color: #cccccc;
        margin-bottom: 20px;
    }}
    .divider {{
        height: 2px;
        background-color: #787982; /* Blue color */
        margin: 20px 0;
        margin-bottom: 60px;
    }}
    .skill-box {{
        background-color: #1f2f56; /* Dark blue background */
        color: white; /* White text color */
        font-size: 18px; /* Font size */
        font-weight: 500; /* Semi-bold font */
        padding: 10px 20px; /* Padding inside the box */
        border-radius: 8px; /* Rounded corners */
        display: inline-block; /* Inline block to center */
        margin-bottom: 20px; /* Add spacing below */
    }}
    .skill-box span {{
        font-weight: 700; /* Bold font for key terms */
        color: #4b9dfd; /* Highlighted blue color */
    }}
    .content {{
        font-size: 18px;
        color: #ffffff;
        margin-bottom: 20px;
    }}
    .content1 {{
        font-size: 18px;
        color: #ffffff;
        margin-bottom: 60px;
    }}
    .project-title {{
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }}
    .overview-title {{
        font-size: 22px;
        font-weight: bold;
        color: #ffffff;
        margin-bottom: 10px;
    }}
    .overview {{
        font-size: 18px;
        color: #ffffff;
        margin-bottom: 30px;
    }}
    .button-container {{
        text-align: center;
        margin-top: 30px;
    }}
    </style>
    <div class="outer-container">
        <div class="inner-container">
            <div class="title">✨ Learning Pathway Designer</div>
            <div class="subtitle">Welcome! Provide your learning objective, and let the agent design a tailored learning pathway for you.</div>
            <div class="divider"></div>
    </div>
    """,
    unsafe_allow_html=True,
)
    st.markdown(
                        """
                        <style>
                    button[kind="primary"] {
        display: block;
        width: 150px;
        height: 50px;
        padding: 10px;
        background-color: #40E0D0; /* Turquoise Green */
        color: black;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        cursor: pointer;
        margin: 0 auto; /* Center the button horizontally */
        margin-top: -140px;
    }
                        </style>
                        """, unsafe_allow_html=True
                    )
    if st.button("Let's Begin ➟", type="primary"):
        st.session_state.page = "welcome"
        st.rerun()

elif st.session_state.page == "welcome":
    st.markdown(
        '<div style="text-align: center; margin-top: -55px; "><img src="https://raw.githubusercontent.com/abishekmadisprz/figmatotestcase/master/.streamlit/static/disprz_reverse.png" width="200"></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """
        <div style="text-align: center; font-family: 'Source Sans Pro', sans-serif; font-size: 30px; font-weight: 650; margin-bottom: 15px; margin-top: -10px;">
        ✨ Learning Pathway Designer ✨
        </div>
        """,
        unsafe_allow_html=True,
    )
    container2 = st.container(border=True)
    container2.markdown(
                    """
                    <div style="font-family: 'Source Sans Pro', sans-serif; font-size:20px; font-weight: 700; margin-bottom: -15px;">✍️ Input Learning Objective:</div>
                    """,
                    unsafe_allow_html=True,
                )
    st.markdown(
    """
    <style>
    /* Target the Streamlit text area */
    div[data-testid="stTextArea"] {
        margin-top: -20px; /* Remove or reduce top margin */
    }

    /* Optional: Add padding to the text area itself */
    textarea {
        padding: 10px; /* Adjust padding inside the text area */
        border: 1px solid #ccc; /* Optional: Customize the border */
        border-radius: 5px; /* Optional: Add rounded corners */
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Render the text area
    user_answer = container2.text_area("", placeholder="E.g., To onboard a new sales advisor at an auto dealership that sells premium cars from Mercedes. At the end of the pathway, the advisor should be able to meet a customer and make a sale of the car's flagship model E class.", height=120)
    container2.markdown(
                        """
                        <style>
        button[kind="primary"] {
        display: block;
        font-family: 'Source Sans Pro', sans-serif;
        width: 250px;
        height: 50px;
        padding: 10px;
        background-color: #40E0D0; /* Turquoise Green */
        color: black;
        border: none;
        border-radius: 5px;
        font-size: 16px;
        font-weight: bold; /* Bold text */
        text-align: center;
        cursor: pointer;
        margin: 0 auto; /* Center the button horizontally */
        margin-top: -15px;
    }
                        </style>
                        """, unsafe_allow_html=True
                    )
                    # Button to submit the answer
    # Initialize session state for the buttons
    if "show_expander" not in st.session_state:
        st.session_state.show_expander = False
    if "success_message" not in st.session_state:
        st.session_state.success_message = False
    if "skillList" not in st.session_state:
        st.session_state.skillList = None    
    
    if container2.button("Create Pathway", type="primary", use_container_width=True):
        st.session_state.show_expander = True
        output = get_completion(user_answer)
        st.session_state.skillList = json.loads(output)
    
    skillList = st.session_state.skillList
    if skillList and 'skillList' in skillList:
        skills_data = skillList['skillList']
        learning_pathway_data = skillList['LearningPathwayList']
    else:
        skills_data = []
        learning_pathway_data = []
    

    if st.session_state.show_expander:
        output = get_completion(user_answer)
        container3=st.container(border=True)
        container3.markdown(
                    """
                    <div style="font-family: 'Source Sans Pro', sans-serif; font-size:20px; font-weight: 700; margin-left: 2px; margin-bottom: 15px;">💡Key Skills and Desired Proficiency</div>
                    """,
                    unsafe_allow_html=True,
                )
        skills_data = skillList['skillList']
        num_columns = len(skills_data)
        columns = container3.columns(num_columns)
        
        for idx, skill in enumerate(skills_data):
            with columns[idx]:
                st.markdown(
                    """
                    <style>
                    .st-emotion-cache-u2rxv6 {
                        font-family: 'Source Sans Pro', sans-serif;
                        font-size: 15px;
                        font-weight: 400;
                        color: #40E0D0;
                    }
                    st-emotion-cache-1fstc0 {
                    border: 1px solid #40E0D0;
                    }
                    </style>
                    """,
                    unsafe_allow_html=True,
                )
                with st.expander(f"{skill['skill_name']}", expanded=False):  # Expander for each skill
                    st.markdown(f"**Desired Level 💼:**  {skill['desired_level']}")
                    st.markdown("**Subskills  🛠️:**")
                    for subskill in skill['subskills']:
                        st.markdown(f"- {subskill}")
        container3.markdown(
                """
                <style>
                .divider {
                    border-top: 1px solid #787982;
                    margin: 2px 0;
                }
                </style>
                """,
                unsafe_allow_html=True,
            )
        container3.markdown("<div class='divider'></div>", unsafe_allow_html=True)
    if st.session_state.show_expander:
        container3.markdown(
                    """
                    <div style="font-family: 'Source Sans Pro', sans-serif; font-size:20px; font-weight: 700; margin-left: 2px; margin-bottom: 15px;">🚀 Proposed Learning Pathway</div>
                    """,
                    unsafe_allow_html=True,
                )
        for i, module in enumerate(learning_pathway_data, start=1):
            # Display the step number and title
            container3.markdown(
                f"""
                <div style="font-family: 'Source Sans Pro', sans-serif; font-size:20px; font-weight: 700; margin-left: 2px; margin-bottom: 15px;">Pitstop {i}: {module['Module_Title']} - ( {module['intervention_type']} )</div>
                """,
                unsafe_allow_html=True,
            )

            # Create a unique key per expander to track the success message
            success_key = f"success_message_{i}"

            # Initialize the success state for this button if not already in session_state
            if success_key not in st.session_state:
                st.session_state[success_key] = False

            # Create an expander for the current module
            with container3.expander(f"Create {module['intervention_type']}"):
                st.write(f"**Intervention Type 🛠️:** {module['intervention_type']}")
                st.write(f"**Content 📚 :** {module['Content']}")
                st.write(f"**Skills Covered 💡:** {', '.join(module['skill_names'])}")

                st.markdown("""
                <style>
                .element-container:has(#button-after) + div button {
                    width: 250px;
                    height: 50px;
                    padding: 10px;
                    border: 2px solid yellow;

                    margin-top: -15px;
                    color: white; /* Text color */
                }
                /* Hover effect */
                .element-container:has(#button-after) + div button:hover {
                    background-color: yellow; /* Darker yellow on hover */
                    color: black;
                }
                </style>
                """, unsafe_allow_html=True)

                st.markdown('<span id="button-after"></span>', unsafe_allow_html=True)

                # "Create" button inside the expander
                if st.button(f"Create {module['intervention_type']}", key=f"create_button_{i}"):
                    st.session_state[success_key] = True  

                # Check if the button has been clicked and display appropriate results
                if st.session_state[success_key]:
                    if module['intervention_type']=='On-the-job training':
                        response=call_ojts(str(module['Module_Title']))
                        ojts_no=int(response)
                        checklists = get_completion1(str(module['Content']))
                        final_checkpoint = json.loads(checklists)
                        final_load_checkpoint = final_checkpoint['checkpointbasedquestions']
                        create_checkpoints(ojts_no, final_load_checkpoint)
                        st.success(f"The {module['intervention_type']} has been successfully created. You can view it here:  https://qa.disprz.com/#!/t/trainerprogramsview/microExperiences/{ojts_no}")
                    else:
                        st.warning(f"Unable to create {module['intervention_type']} at the moment. Please try again later.")
                    st.session_state[success_key] = False



