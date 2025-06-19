# app.py

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers import StrOutputParser
from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional

# Import our universal file processor
from file_processor import process_uploaded_files

# --- Configuration and Initialization ---
load_dotenv()
st.set_page_config(page_title="Pantry-Powered Date-Night Planner", page_icon="🕯️")

# --- MODEL AND PROMPT SETUP ---
MODEL_NAME = "gemini-1.5-flash"
prompt_template = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            Act like a world-renowned, imaginative, and romantically intuitive date night planner with 20+ years of experience. You specialize in turning ordinary pantry items—whether shared through typed messages, PDFs, text files, or even image uploads—into extraordinary, intimate evenings.

            Your role is to be the user's magical behind-the-scenes designer, crafting every detail of their dream date night: the food, the ambiance, the connection, and the atmosphere. You take pride in making every moment feel bespoke and unforgettable.

            MULTIMODAL INTELLIGENCE:
            - If the user input contains: **"Content from uploaded file:"**, you MUST prioritize and base the plan on that content.
            - If the user provides an **uploaded image**, you must extract and analyze all visible ingredient labels or recognizable food items.
            - If the input is direct text, analyze the message normally.
            - Always **combine** all sources into a unified ingredient list before planning.

            YOUR STEP-BY-STEP STRATEGY:
            1. Extract and synthesize all ingredients from every available source: text, files, and images.
            2. Identify the best romantic dish (or dishes) that can be made using these ingredients.
            3. If it elevates the recipe, suggest up to two optional but common pantry ingredients.
            4. Design the ambiance: lighting, music, and decor ideas tailored for a cozy, romantic home setting.
            5. Recommend a meaningful or playful icebreaker or activity that sparks conversation or intimacy.
            6. Present your full plan in the structured, emoji-enhanced Markdown format shown below.
            7. End your plan with the question: 
               **"How does this sound for your date night? Feel free to ask for changes to any part of the plan—the recipe, the music, anything at all!"**
            8. Wait for user feedback and improve the plan iteratively until the user replies with something like: **"Yes, this is perfect!"**
            9. Upon final confirmation, respond with a short, warm, celebratory closing—never generate a new plan at this point.

            MEMORY & INTERACTION RULES:
            - Use the chat history to track evolving preferences (e.g., dietary restrictions, spice levels, cheese preferences, lighting tone, etc.).
            - Ask thoughtful, open-ended questions to clarify or expand on vague user input.
            - Do NOT repeat suggestions unless explicitly requested.
            - Remember everything about the current session until it’s completed.

            FORMATTING & STYLE (ALWAYS USE THIS STRUCTURE):
            - 🍽️ **Recipe Suggestion**: [Name of the dish]
              • **Ingredients Identified**: 
                - [Ingredient 1 from any source]\n
                - [Ingredient 2...]\n
                - [Ingredient 3...]\n
              • **Optional Additions**: [Optional 1], [Optional 2]
              • **Preparation Steps**:
                1. [Step one]\n
                2. [Step two]\n
                3. [Step three]\n
            - 🎶 **Ambiance**: [Music genre or playlist idea]
            - 🕯️ **Decor**: [Lighting mood, aesthetic details, props]
            - 💬 **Icebreaker**: [Fun game, meaningful prompt, or playful challenge]

            STYLE REQUIREMENTS:
            - Always use **Markdown** formatting with bold headers.
            - Start each preparation step on a **new line with a number**.
            - Maintain a **charming, inviting, poetic tone**—as if you’re designing a fairytale evening for two.

            Take a deep breath and work on this problem step-by-step.
            """
        ),
        MessagesPlaceholder(variable_name="chat_history"),
        ("human", "{input}"),
    ]
)


llm = ChatGoogleGenerativeAI(model=MODEL_NAME, temperature=0.7)
chain = prompt_template | llm | StrOutputParser()

# --- Session State Management ---
def initialize_session_state():
    """Initializes session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = [
            AIMessage(content="Hello! What ingredients do you have? Upload photos, text files, or PDFs!"),
        ]
    if "conversation_active" not in st.session_state:
        st.session_state.conversation_active = True

initialize_session_state()

# --- Core Response Generation Function ---
def generate_ai_response(user_prompt: str, image_parts: Optional[List[Dict[str, Any]]] = None, extracted_text: str = ""):
    """
    Handles AI response generation. It can take text, images, or both.
    This single function now powers all AI interactions.
    """
    with st.spinner("Crafting your response..."):
        # 1. Construct the multimodal input for the LLM
        prompt_parts = []
        if extracted_text:
            prompt_parts.append({"type": "text", "text": "--- Text from Uploaded Files ---\n" + extracted_text})
        if user_prompt:
             prompt_parts.append({"type": "text", "text": user_prompt})
        if image_parts:
            for image in image_parts:
                prompt_parts.append({"type": "image", "source": image})

        # 2. Add user message to history and invoke the chain
        st.session_state.chat_history.append(HumanMessage(content=user_prompt))
        ai_response = chain.invoke({
            "chat_history": st.session_state.chat_history,
            "input": prompt_parts,
        })
        st.session_state.chat_history.append(AIMessage(content=ai_response))

# --- UI Rendering ---
st.title("🕯️ Pantry-Powered Date-Night Planner")

# Display chat history
for message in st.session_state.chat_history:
    avatar = "🕯️" if isinstance(message, AIMessage) else "👤"
    with st.chat_message(name="AI" if isinstance(message, AIMessage) else "Human", avatar=avatar):
        st.markdown(message.content)


# --- Main Application Flow ---
if st.session_state.conversation_active:
    
    if len(st.session_state.chat_history) > 1:
        st.write("Need some ideas?")
        cols = st.columns(3)
        suggestions = {
            "Yes, this is perfect!": { "is_conclusive": True },
            "Suggest a different recipe": { "is_conclusive": False },
            "Change the ambiance": { "is_conclusive": False },
        }
        
        buttons = [
            cols[0].button(list(suggestions.keys())[0], use_container_width=True),
            cols[1].button(list(suggestions.keys())[1], use_container_width=True),
            cols[2].button(list(suggestions.keys())[2], use_container_width=True)
        ]

        for i, (prompt, props) in enumerate(suggestions.items()):
            if buttons[i]:
                if props["is_conclusive"]:
                    st.session_state.conversation_active = False # End the conversation
                generate_ai_response(prompt)
                st.rerun()
                
    # --- Input form for active conversation ---
    with st.form(key="input_form", clear_on_submit=True):
        uploaded_files = st.file_uploader(
            "Upload ingredients (images, txt, pdf)",
            type=["txt", "pdf", "png", "jpg", "jpeg"],
            accept_multiple_files=True,
            label_visibility="collapsed"
        )
        user_prompt = st.text_input("What would you like to do?", key="chat_input")
        submit_button = st.form_submit_button(label="Plan my date!")

    if submit_button and (user_prompt or uploaded_files):
        text_from_files, image_data = process_uploaded_files(uploaded_files)
        # Use the primary user prompt, or a default if only files are uploaded
        prompt_for_ai = user_prompt or "Please create a plan based on the attached file(s)."
        generate_ai_response(prompt_for_ai, image_data, text_from_files)
        st.rerun()
        
else:
    # --- Conversation Ended State ---
    st.success("Enjoy your magical date night! ✨")
    if st.button("Start a New Plan"):
        st.session_state.clear() # Clear the entire session for a fresh start
        st.rerun()