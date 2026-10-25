
import streamlit as st

from auth import register_user, login_user
from database import save_search_history
from app import ask_question


# --------------------------------------------------
# 1. PAGE CONFIGURATION
# --------------------------------------------------

st.set_page_config(
    page_title="IncidentTrace AI",
    page_icon="🔍",
    layout="wide"
)


# --------------------------------------------------
# 2. INITIALIZE SESSION STATE
# --------------------------------------------------

if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# 3. LOGIN AND REGISTRATION
# --------------------------------------------------

if not st.session_state.authenticated:

    st.title("🔍 IncidentTrace AI")
    st.subheader("Login or Create Account")

    login_tab, register_tab = st.tabs(
        ["Login", "Register"]
    )

    with login_tab:
        with st.form("login_form"):
            email = st.text_input("Email")

            password = st.text_input(
                "Password",
                type="password"
            )

            login_clicked = st.form_submit_button("Login")

        if login_clicked:
            user, message = login_user(email, password)

            if user:
                st.session_state.authenticated = True
                st.session_state.user = user
                st.session_state.messages = []

                st.success("Login successful!")
                st.rerun()
            else:
                st.error(message)

    with register_tab:
        with st.form("register_form"):
            name = st.text_input("Full name")
            new_email = st.text_input("Email")

            new_password = st.text_input(
                "Password (minimum 8 characters)",
                type="password"
            )

            confirm_password = st.text_input(
                "Confirm password",
                type="password"
            )

            register_clicked = st.form_submit_button(
                "Create Account"
            )

        if register_clicked:
            if new_password != confirm_password:
                st.error("Passwords do not match.")

            else:
                success, message = register_user(
                    name,
                    new_email,
                    new_password
                )

                if success:
                    st.success(message)
                else:
                    st.error(message)

    # Stop here until the user logs in.
    st.stop()



# --------------------------------------------------
# 4. CUSTOM STYLING
# --------------------------------------------------

st.markdown("""
<style>
.stApp {
    background-color: #0b1120;
    color: #f1f5f9;
}

.block-container {
    max-width: 1000px;
    padding-top: 2rem;
}

.chat-message {
    padding: 16px;
    border-radius: 12px;
    margin-bottom: 12px;
    background-color: #172033;
}

/* Normal text input fields */
.stTextInput input {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 10px;
}

/* Chat search/input box */
.stChatInput textarea {
    background-color: #ffffff !important;
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
    caret-color: #000000 !important;
}

/* Placeholder text inside chat input */
.stChatInput textarea::placeholder {
    color: #555555 !important;
    -webkit-text-fill-color: #555555 !important;
    opacity: 1 !important;
}

/* Ensure text remains black while typing */
.stChatInput textarea:focus {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

/* Login and registration input text */
.stTextInput input {
    color: #000000 !important;
    -webkit-text-fill-color: #000000 !important;
}

</style>
""", unsafe_allow_html=True)



# --------------------------------------------------
# 5. APP HEADING
# --------------------------------------------------

st.title("🔍 IncidentTrace AI")
st.caption("IT Outage Investigation Assistant")

st.markdown(
    "Investigate application errors, database issues, "
    "and deployment failures using your knowledge base."
)

user = st.session_state.get("user", {})

if isinstance(user, dict):
    st.caption(
        f"Logged in as: {user.get('full_name', user.get('email', 'User'))}"
    )


# --------------------------------------------------
# 6. SIDEBAR
# --------------------------------------------------

with st.sidebar:
    st.header("IncidentTrace AI")
    st.write("Your AI-powered troubleshooting assistant.")

    st.divider()

    st.subheader("Example questions")

    st.markdown("""
    - Why is my database connection failing?
    - What caused the deployment failure?
    - How can I investigate HTTP 500 errors?
    """)

    if st.button("Clear conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# 7. DISPLAY CURRENT CONVERSATION
# --------------------------------------------------

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])


# --------------------------------------------------
# 8. ASK QUESTION AND GENERATE AI RESPONSE
# --------------------------------------------------

question = st.chat_input("Describe your IT issue...")

if question:

    # Display the question
    with st.chat_message("user"):
        st.markdown(question)

    st.session_state.messages.append({
        "role": "user",
        "content": question
    })

    # Generate the AI response
    with st.chat_message("assistant"):

        with st.spinner(
            "Investigating your issue... "
            "The local AI model may take some time."
        ):
            try:
                answer = ask_question(question)

            except Exception as error:
                answer = f"An error occurred: {error}"

        st.markdown(answer)

    st.session_state.messages.append({
        "role": "assistant",
        "content": answer
    })


    # --------------------------------------------------
    # 9. SAVE QUESTION AND ANSWER TO MYSQL
    # --------------------------------------------------

    current_user = st.session_state.get("user")

    if isinstance(current_user, dict):
        user_id = current_user.get(
            "id",
            current_user.get("user_id")
        )
    else:
        user_id = None

    # Save only when the user ID exists.
    if user_id is not None:

        saved = save_search_history(
            user_id=user_id,
            question=question,
            response=answer
        )

        if saved:
            st.toast("Search saved to history!")
        else:
            st.warning(
                "AI response received, but saving to MySQL failed. "
                "Check the VS Code terminal for the database error."
            )

    else:
        st.warning(
            "Could not find your user ID. "
            "Please check the login_user() function in auth.py."
        )
