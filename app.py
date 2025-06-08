import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Pantry-Powered Date-Night Planner", page_icon="🕯️")
st.title("🕯️ Pantry-Powered Date-Night Planner")
st.write("Tell me what's in your pantry, and I'll craft the perfect romantic date night for you!")


prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You are a seasoned date planner with 20 years of experience and a flair for romance. 
            A user has provided the following pantry items: [User's List]. 
            Your task is to craft a romantic date night plan utilizing these ingredients. 
            If a particular recipe requires one or two additional items to enhance its appeal, suggest them. 
            Ensure the plan is intimate, creative, and tailored to a cozy evening at home.
            
            Maintain a dynamic memory of the user's preferences and context of suggestions and the user's real-time feedback, including dietary restrictions, 
            desired ambiance, and any feedback on previous suggestions and details like spice level, dish type, cheese preference, added sides, ambiance tone, 
            and satisfaction status. If the user modifies their preferences or requests adjustments, update the plan accordingly. 
            Always ensure that the evolving plan aligns with the user's vision for their date night. 
            Only mark the date-night ‘complete’ when the user explicitly confirms they are delighted. 
            
            To curate the perfect date night:
            1.	Analyze the provided pantry items.
            2.	Identify potential recipes that can be crafted using these items.
            3.	If beneficial, suggest up to two additional ingredients to elevate the dish.
            4.	Design an ambiance plan, including lighting, music, and decor suggestions.
            5.	Propose an engaging icebreaker or activity to enhance the evening.
            6.	Compile all elements into a cohesive, romantic date night plan.
            7.	Ask an open-ended follow-up: 'Would you like anything adjusted in the recipe, ambiance, music, or flow?’ 
            8.	If changes are requested, apply them, update the plan, and repeat the process. 
            9.	Continue until the user says, ‘Yes, this is perfect!’ 
            10.	Think step-by-step. Don’t be Lazy. Research before Answer.

            Present the date night plan in the following format:
            🍽️ Recipe Suggestion: [Dish Name]
            •	Ingredients: [List]
            •	Preparation Steps: [Step-by-step guide]
                    1. [Step 1]
                    2. [Step 2]
                    3. [Step 3]
                    4. [Step 4]
            Note: the preparation steps should be in a numbered list format, Not in paragraphs. Give it one by one.
            🎶 Ambiance: [Music genre or playlist suggestion]
            🕯️ Decor: [Lighting and decor tips]
            💬 Icebreaker: [Conversation starter or activity]
            
            Ensure the tone is warm, inviting, and tailored to create a memorable evening.
            After presenting the plan, always ask for feedback with a phrase like:
            ‘Is this exactly what you envisioned for your perfect date night? If you’d like any tweaks—say the word: recipes, lighting, music, etc.
            —I’m happy to refine it until it’s just right.'
            """
        ),
       
        MessagesPlaceholder(variable_name="chat_history"),
        
        ("human", "{input}"),
    ]
)

llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.7)
agent_chain = LLMChain(
    llm=llm,
    prompt=prompt_template,
    memory=ConversationBufferMemory(memory_key="chat_history", return_messages=True),
    verbose=True
)

# --- NEW: Function to handle AI response generation ---
def generate_ai_response(user_input):
    """Invokes the agent chain and updates the chat history."""
    with st.spinner("Crafting your perfect date night..."):
        ai_response = agent_chain.invoke({"input": user_input})

    st.session_state.chat_history.append(HumanMessage(content=user_input))
    st.session_state.chat_history.append(AIMessage(content=ai_response["text"]))

# --- Initialize Streamlit Session State ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = [
        AIMessage(content="Hello! What ingredients do you have in your pantry for our romantic date night?"),
    ]
if "conversation_active" not in st.session_state:
    st.session_state.conversation_active = True


# --- Display Chat History ---
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("AI", avatar="🕯️"):
            st.markdown(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("Human", avatar="👤"):
            st.markdown(message.content)


# --- NEW: UI Logic for Active vs. Completed Conversation ---
if st.session_state.conversation_active:
    # --- User Input Text Box ---
    user_prompt = st.chat_input("e.g., Onion, Milk, Eggs, Cheese, .....")
    if user_prompt:
        generate_ai_response(user_prompt)
        st.rerun()

    # --- Suggested Reply Buttons ---
    # Only show suggestions if there's more than one message (i.e., after the initial greeting)
    if len(st.session_state.chat_history) > 1:
        st.write("Here are some ideas:")
        cols = st.columns(3)
        suggestions = [
            "Yes, this is perfect!",
            "Suggest a different recipe",
            "Change the ambiance",
        ]
        
        # This is the "end conversation" button
        if cols[0].button(suggestions[0], use_container_width=True):
            st.session_state.conversation_active = False # End the conversation
            generate_ai_response(suggestions[0])
            st.rerun()

        # These are feedback buttons
        if cols[1].button(suggestions[1], use_container_width=True):
            generate_ai_response(suggestions[1])
            st.rerun()

        if cols[2].button(suggestions[2], use_container_width=True):
            generate_ai_response(suggestions[2])
            st.rerun()
else:
    # --- Conversation Ended State ---
    st.success("Enjoy your magical date night! ✨")
    if st.button("Start a new plan"):
        # Reset the session state to start over
        st.session_state.chat_history = [
            AIMessage(content="Hello! What ingredients do you have in your pantry for our romantic date night?"),
        ]
        st.session_state.conversation_active = True
        st.rerun()