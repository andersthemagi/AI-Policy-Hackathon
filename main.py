import streamlit as st
import os
from dotenv import load_dotenv
from openai import OpenAI
from streamlit_pills import pills

load_dotenv()

OPENAI_API_KEY=os.getenv("OPENAI_API_KEY")
ASSISTANT_ID=os.getenv("ASSISTANT_ID")

AVAILABLE_STANDARDS = [
    "SIT EF 120 | Metric | Percentage workloads cloud hosted -- SIT EF 120-1 | Metric | Percentage cloud-hosted by provider",
    """SIT EF 110 	Topic 	Technology infrastructure energy consumption (include electricity, heating, cooling) 	GRI 302-1, 3; SASB TC-IM-130a.1, TC-SI-130a.1; ESRS E1; SDG 7, 9, 13, 17
    SIT EF 110-1 	Platform 	Owned/on-premises
    SIT EF 110-1.a 	Metric 	kWh consumption by location, time of day, per end user (include EF 111-1.a, 112-1, 113-1.a)
    SIT EF 110-1.b 	Metric 	Percentage renewable """,
    """SIT EF 130 	Metric 	Lifecycle energy consumption IT products and services (include electricity, heating, cooling) 	GRI 302-1, 3; ESRS E1; SDG 7, 9, 13, 17
    SDG Ambition Benchmark(s):
    SIT EF 130-1 	Metric 	Percentage products and services having an extraordinarily high workload
    SIT EF 130-2 	Metric 	Percentage products and services on renewable energy
    SIT EF 130-3 	Metric 	Percentage eligible products and services hosted/delivered by third parties
    """
]

client = OpenAI(
    api_key=OPENAI_API_KEY
)

st.empty()

# initialize user state variable
if 'user_state' not in st.session_state:
    st.session_state.user_state = "start"

def main():
    st.title("Pan - Your SMART Sustainability Expert")

    st.markdown("""
    Using OpenAI, we cross-reference a given Global Reporting Index (GRI) report with specific standards from SustainableIT to determine measurable goals and impact. The goal is less to identify a specific goal but rather ensure these goals are actually SMART (Specific, Measureable, Achievable, Relevant, and Time-Bound).
    """)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("The assistant created for this purpose, Pan, is focused on cross-reference and identifying specific components of goals listed to determine efficacy. Pan acts as a guide rather than a dictator, advising on where a user might improve the wording. As you can imagine, Pan is a reference to the Greek God of the same name, who acts to a certain extent like the bridge between humans and nature.")
    with col2:
        st.image("./static/pan.png")

    st.markdown("""
    A user might use a tool like this to evaluate a companies progress towards specified goals. A company might also self-asses in order to fine-tune their content to provide the best information regarding their initiatives, assuming they aren't incentivized to be vague.
                
    Built for the AI Policy Hackathon on the AI in Sustainability Track, Technical Focus.
                
    Created by Andres Sepulveda Morales (andres@redmage.cc)
    """)

    with st.expander("More on the SustainableIT Standards"):
        st.markdown("You can see a full list of standards at [sustainableit.org.](https://www.sustainableit.org/standards/it-esg-standards)")
        st.write(AVAILABLE_STANDARDS)

    if 'file_upload_disabled' not in st.session_state:
        st.session_state.file_upload_disabled = False

    file_container = st.container(border=True)
    with file_container:
        st.markdown("Sample PDF File: [GIV_2021_GRISustainabilityReport.pdf](app/static/GIV_2021_GRISustainabilityReport.pdf)")

    uploaded_file = st.button("\"Upload File\"", type="primary", disabled=st.session_state.file_upload_disabled)

    if uploaded_file:
        st.session_state.file_upload_disabled = True

        initialize_assistant()

def initialize_assistant():
        
    write_to_chat("assistant", "Initializing assistant...")    

    # Create instance of Pan
    my_assistant = client.beta.assistants.retrieve(ASSISTANT_ID)

    write_to_chat("assistant", "Uploading GRI report...")  

    # Create Vector Store
    vector_store = client.beta.vector_stores.create(name="GRI_Report_Data")

    file_paths = ["./static/GIV_2021_GRISustainabilityReport.pdf"]
    file_streams = [open(path, "rb") for path in file_paths]

    # Add files to vector store 
    file_batch = client.beta.vector_stores.file_batches.upload_and_poll(
        vector_store_id = vector_store.id,
        files = file_streams
    )

    # Update Assistant to include Vector Store 
    my_assistant = client.beta.assistants.update(
        assistant_id = my_assistant.id,
        description="""
        You are an AI evaluator for SustainableIT, a 501 (c)(6) nonprofit organization (NPO) led by technology executives who will advance sustainability around the world through technology leadership.  You excel at cross-referencing given Global Reporting Initiative (GRI) reports with SustainableIT standards. 

        You are critical and willing to say what needs to be said regarding the efficacy of goals, no matter how rude.
        """,
        instructions="""
        The user will give a standard or set of standards to cross-reference between on the file uploaded.

        Restate the standard given. Provide analysis on efficacy of goals regarding said standard. Summarize the efficacy of the goal with a rating out of 5. When possible, provide both positive and constructive feedback utilizing the SMART Goal method regarding the standards you are evaluating and whether an organization is meeting them. You MUST utilize the SMART Goal method to break down aspects of goals for easy legibility by human readers. 
        """,
        temperature=0.1,
        tool_resources = {
            "file_search" : {
                "vector_store_ids": [vector_store.id]
            }
        }
    )

    if 'assistant' not in st.session_state:
        st.session_state.assistant = my_assistant

    write_to_chat("assistant", "Intializing conversation thread...")
    # Create Thread
    comm_thread = client.beta.threads.create()

    if 'thread_id' not in st.session_state:
        st.session_state.thread_id = comm_thread.id 
    
    write_to_chat("assistant","Ready for action! What would you like to know about this report?")

    standard_options = st.selectbox(
        "Select a standard dialogue option to ask:", 
        options=AVAILABLE_STANDARDS, 
        index=None,
        placeholder="Select an option...",
        on_change=update_state_to_query_model,
        key="standard_options"
    )
        
            

def update_state_to_query_model():
    st.session_state.user_state = "query_model"

def write_to_chat(type, content):
    avatar_path = "./static/pan.png" if type == "assistant" else None
    with st.chat_message(type, avatar=avatar_path ):
        st.write(content)

@st.dialog("Conclusion")
def conclusion_dialog():
    st.markdown("""
    Through this example, we've shown that an LLM can assist in evaluating the efficacy of goals set in sustainability and cross-referencing different standards.
                
    In a full solution, one might want a multi-agent system to handle specific facets of standards (environment, social, government, etc.) to be able to finer tune outputs and evaluation critera.
    """)
    if st.button("Run Again"):
        st.rerun()

def handle_query():
    option_str = str(st.session_state.standard_options)
    print(f"option_str = {option_str}")
    
    # Create Message for Assistant 

    write_to_chat("assistant", "Initializing message object...")

    query_msg = client.beta.threads.messages.create(
        thread_id = st.session_state.thread_id,
        role="user",
        content=option_str
    )
    print(f"Message: {query_msg}")

    write_to_chat("assistant", "Running query...")
    
    run_query = client.beta.threads.runs.create_and_poll(
        thread_id = st.session_state.thread_id,
        assistant_id=st.session_state.assistant.id
    )

    # Hold while Run is processed by assistant api
    while run_query.status in ["queued", "in_progress"]:
        run_query = client.beta.threads.runs.retrieve(
            thread_id=st.session_state.thread_id,
            run_id=run_query.id
        )

    write_to_chat("assistant", "Query finished. Rendering...")

    all_messages = client.beta.threads.messages.list(
        thread_id=st.session_state.thread_id
    )

    write_to_chat("user", query_msg.content[0].text.value)
    write_to_chat("asssistant", all_messages.data[0].content[0].text.value)

    conclusion_dialog()

# Start App Flow

user_state = st.session_state.user_state

if user_state == "start":
    main()
elif user_state == "query_model":
    handle_query()  
  
    