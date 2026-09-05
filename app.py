from pathlib import Path
import html
import time
import streamlit as st

from src.chatbot import SmartFAQEngine
from src.faq_manager import add_faq, delete_faq, load_faqs, update_faq

# =========================================================
# CONFIG
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
DATA_PATH = BASE_DIR / "data" / "faqs.csv"

st.set_page_config(
    page_title="SmartFAQ",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# CSS
# =========================================================

st.markdown(
    """
    <style>
    @import url(
        'https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap'
    );

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }

    .stApp {
        background:
            radial-gradient(circle at 10% 0%, rgba(118,87,255,.12), transparent 28%),
            radial-gradient(circle at 90% 10%, rgba(59,130,246,.10), transparent 26%),
            #f7f8fc;
    }

    .block-container {
        max-width: 1500px;
        padding-top: 1.3rem;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0b1020, #101936);
    }

    [data-testid="stSidebar"] * {
        color: #e8ecf8 !important;
    }

    .brand {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 4px 22px;
    }

    .brand-icon {
        width: 44px;
        height: 44px;
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #7c5cff, #3182f6);
        font-size: 22px;
        box-shadow: 0 12px 30px rgba(80,70,220,.35);
    }

    .brand-title {
        font-size: 20px;
        font-weight: 800;
    }

    .brand-sub {
        font-size: 10px;
        opacity: .65;
    }

    .hero {
        border-radius: 24px;
        padding: 28px 30px;
        color: white;
        background:
            radial-gradient(circle at 80% 20%, rgba(255,255,255,.20), transparent 22%),
            linear-gradient(135deg, #111936, #26377b 55%, #6948d9);
        box-shadow: 0 20px 55px rgba(29,40,92,.18);
        margin-bottom: 20px;
    }

    .hero h1 {
        margin: 0;
        font-size: 32px;
        letter-spacing: -1px;
    }

    .hero p {
        margin: 8px 0 0;
        color: #dfe5ff;
    }

    .online {
        display: inline-flex;
        gap: 7px;
        align-items: center;
        margin-top: 16px;
        padding: 7px 11px;
        border: 1px solid rgba(255,255,255,.16);
        border-radius: 999px;
        background: rgba(255,255,255,.08);
        font-size: 12px;
    }

    .dot {
        color: #6ee7b7;
    }

    .stat, .chat-card, .info-card {
        background: rgba(255,255,255,.88);
        border: 1px solid rgba(148,163,184,.18);
        border-radius: 18px;
        padding: 17px;
        box-shadow: 0 8px 30px rgba(15,23,42,.05);
    }

    .stat-label {
        color: #64748b;
        font-size: 12px;
        font-weight: 600;
    }

    .stat-value {
        color: #111827;
        font-size: 25px;
        font-weight: 800;
        margin-top: 4px;
    }

    .chat-card {
        padding: 22px;
        border-radius: 24px;
    }

    .msg-row {
        display: flex;
        margin: 13px 0;
    }

    .msg-row.user {
        justify-content: flex-end;
    }

    .avatar {
        width: 36px;
        height: 36px;
        flex: 0 0 36px;
        border-radius: 12px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: #e0e7ff;
        margin-right: 9px;
    }

    .bubble {
        max-width: 78%;
        padding: 13px 16px;
        border-radius: 18px;
        font-size: 14px;
        line-height: 1.55;
    }

    .bot .bubble {
        background: #f4f6fb;
        border: 1px solid #e9edf5;
        color: #172033;
        border-top-left-radius: 5px;
    }

    .user .bubble {
        background: linear-gradient(135deg, #7157f7, #3b82f6);
        color: white;
        border-top-right-radius: 5px;
    }

    .meta {
        font-size: 11px;
        color: #7b8799;
        margin-top: 7px;
    }

    .badge {
        display: inline-block;
        padding: 4px 9px;
        border-radius: 999px;
        background: #ede9fe;
        color: #5b42c7;
        font-size: 11px;
        font-weight: 700;
    }

    .match {
        margin-top: 10px;
        padding: 10px 12px;
        border-left: 3px solid #7657ff;
        background: white;
        border-radius: 10px;
        color: #475569;
        font-size: 12px;
    }

    .section-title {
        font-size: 17px;
        font-weight: 800;
        color: #111827;
        margin: 8px 0 12px;
    }

    div.stButton > button {
        border-radius: 12px;
        font-weight: 600;
        background: linear-gradient(135deg, #7157f7, #3b82f6);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# SESSION STATE
# =========================================================

defaults = {
    "messages": [],
    "answered": 0,
    "confidence_values": [],
    "admin_mode": False,
}

for key, value in defaults.items():
    if key not in st.session_state:
        st.session_state[key] = value

# =========================================================
# CHATBOT
# =========================================================

try:
    if "engine" not in st.session_state:
        st.session_state.engine = SmartFAQEngine(DATA_PATH)

    engine = st.session_state.engine

except Exception as error:
    st.error(f"SmartFAQ could not load: {error}")
    st.stop()

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown(
        """
        <div class="brand">
            <div class="brand-icon">🤖</div>
            <div>
                <div class="brand-title">SmartFAQ</div>
                <div class="brand-sub">INTELLIGENT STUDENT SUPPORT</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("### FAQ Categories")

    categories = ["All"] + list(engine.categories())

    selected_category = st.radio(
        "Filter",
        categories,
        label_visibility="collapsed",
    )

    st.markdown("### Suggested Questions")

    # Load FAQ data
    faq_df = load_faqs(DATA_PATH)

    # ---------------------------------------------------------
    # Suggestions based on selected category
    # ---------------------------------------------------------

    if selected_category == "All":

        suggestions = [
            "What is the admission process?",
            "What scholarships are available?",
            "How can I check my exam schedule?",
            "What is the minimum attendance requirement?",
            "Are hostel facilities available?",
        ]

    else:

        category_faqs = faq_df[
            faq_df["category"]
            .astype(str)
            .str.strip()
            .str.lower()
            == selected_category.strip().lower()
        ]

        suggestions = (
            category_faqs["question"]
            .dropna()
            .astype(str)
            .drop_duplicates()
            .head(5)
            .tolist()
        )


    # ---------------------------------------------------------
    # Display suggestion buttons
    # ---------------------------------------------------------

    if suggestions:

        for i, question in enumerate(suggestions):

            if st.button(
            question,
            key=f"suggestion_{selected_category}_{i}",
            use_container_width=True,
            ):

                st.session_state.pending_question = question
                st.rerun()

    else:
        st.caption(
        "No suggested questions available for this category."
        )

    st.markdown("---")

    st.markdown("### About")

    st.caption(
        "SmartFAQ is a local NLP retrieval system using "
        "NLTK, TF-IDF and cosine similarity. "
        "No OpenAI API or paid API is required."
    )

    if st.button(
        "⚙️ FAQ Management",
        use_container_width=True,
    ):

        st.session_state.admin_mode = True
        st.rerun()


    # ---------------------------------------------------------
    # HOME BUTTON
    # ---------------------------------------------------------

    if st.session_state.admin_mode:

        if st.button(
            "🏠 Home",
            use_container_width=True,
        ):

            st.session_state.admin_mode = False
            st.rerun()

# =========================================================
# hero
# =========================================================

st.markdown(
    """
        <h1>SmartFAQ</h1>
        <p>Your Intelligent Student Support Assistant</p>

        <div class="online">
            <span class="dot">●</span>
            AI Online · Local NLP Engine
        </div>
    """,
    unsafe_allow_html=True,
)

# =========================================================
# STATISTICs
# =========================================================

avg_confidence = (
    sum(st.session_state.confidence_values)
    / len(st.session_state.confidence_values)
    if st.session_state.confidence_values
    else 0
)

stats = engine.stats(
    answered_count=st.session_state.answered,
    avg_confidence=avg_confidence,
)

stat_data = [
    ("Total FAQs", stats["total_faqs"]),
    ("Categories", stats["categories"]),
    ("Questions Answered", stats["questions_answered"]),
    ("Average Confidence", f'{stats["avg_confidence"]:.0%}'),
]

cols = st.columns(4)

for col, (label, value) in zip(cols, stat_data):
    with col:
        st.markdown(
            f"""
            <div class="stat">
                <div class="stat-label">{html.escape(str(label))}</div>
                <div class="stat-value">{html.escape(str(value))}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

st.write("")

# =========================================================
# admin panel
# =========================================================

if st.session_state.admin_mode:

    st.markdown(
        '<div class="section-title">⚙️ FAQ Management</div>',
        unsafe_allow_html=True,
    )

    tabs = st.tabs(
        ["View & Search", "Add FAQ", "Edit FAQ", "Delete FAQ"]
    )

    # -----------------------------------------------------
    # VIEW
    # -----------------------------------------------------

    with tabs[0]:

        df = load_faqs(DATA_PATH)

        search = st.text_input(
            "Search FAQs",
            placeholder="Search question, answer or category...",
        )

        if search:
            mask = df.astype(str).apply(
                lambda col: col.str.contains(
                    search,
                    case=False,
                    na=False,
                )
            ).any(axis=1)

            df = df[mask]

        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
        )

    # -----------------------------------------------------
    # ADD
    # -----------------------------------------------------

    with tabs[1]:

        with st.form("add_faq_form", clear_on_submit=True):

            question = st.text_input("Question")
            answer = st.text_area("Answer", height=120)

            category = st.selectbox(
                "Category",
                list(engine.categories()) + ["Other"],
            )

            submit = st.form_submit_button(
                "Add FAQ",
                use_container_width=True,
            )

            if submit:

                if not question.strip() or not answer.strip():
                    st.warning("Question and answer are required.")

                else:
                    add_faq(
                        DATA_PATH,
                        question.strip(),
                        answer.strip(),
                        category,
                    )

                    engine.reload()
                    st.success("FAQ added successfully.")
                    time.sleep(.3)
                    st.rerun()

    # -----------------------------------------------------
    # EDIT
    # -----------------------------------------------------

    with tabs[2]:

        df = load_faqs(DATA_PATH)

        if len(df):

            index = st.number_input(
                "FAQ row number",
                min_value=0,
                max_value=len(df) - 1,
                value=0,
                step=1,
            )

            row = df.iloc[int(index)]

            with st.form("edit_faq_form"):

                question = st.text_input(
                    "Question",
                    value=str(row["question"]),
                )

                answer = st.text_area(
                    "Answer",
                    value=str(row["answer"]),
                    height=120,
                )

                category = st.text_input(
                    "Category",
                    value=str(row["category"]),
                )

                submit = st.form_submit_button(
                    "Save Changes",
                    use_container_width=True,
                )

                if submit:

                    if not all(
                        [
                            question.strip(),
                            answer.strip(),
                            category.strip(),
                        ]
                    ):
                        st.warning("All fields are required.")

                    else:
                        update_faq(
                            DATA_PATH,
                            int(index),
                            question.strip(),
                            answer.strip(),
                            category.strip(),
                        )
                        engine.reload()
                        st.success("FAQ updated successfully.")
                        time.sleep(.3)
                        st.rerun()

        else:
            st.info("No FAQs available to edit.")

    # -----------------------------------------------------
    # DELETE
    # -----------------------------------------------------

    with tabs[3]:

        df = load_faqs(DATA_PATH)

        if len(df):

            index = st.number_input(
                "FAQ row number to delete",
                min_value=0,
                max_value=len(df) - 1,
                value=0,
                step=1,
                key="delete_idx",
            )

            st.warning(
                
                f'You are about to delete: '
                f'"{df.iloc[int(index)]["question"]}"'
            )

            if st.button(
                "Delete FAQ",
                type="primary",
                use_container_width=True,
            ):

                delete_faq(DATA_PATH, int(index))
                engine.reload()

                st.success("FAQ deleted successfully.")
                time.sleep(.3)
                st.rerun()

        else:
            st.info("No FAQs available to delete.")

    st.divider()

# =========================================================
# CHAT
# =========================================================

chat_col, info_col = st.columns([2.25, 1], gap="large")

# =========================================================
# CHAT AREA
# =========================================================

with chat_col:

    st.markdown(
        '<div class="section-title">💬 Ask SmartFAQ</div>',
        unsafe_allow_html=True,
    )

    st.markdown(
        '<div class="chat-card">',
        unsafe_allow_html=True,
    )

    if not st.session_state.messages:

        st.markdown(

            """
            <div style="padding:25px;text-align:center;color:#64748b">
                <div style="font-size:40px">🤖</div>
                <h3 style="color:#1f2937">
                    How can I help you today?
                </h3>
                <div>
                    Ask about admissions, fees, exams,
                    scholarships, placements, hostel,
                    attendance, library and more.
                </div>

            </div>
            """,
            unsafe_allow_html=True,
        )

    for message in st.session_state.messages:

        content = html.escape(str(message["content"]))

        if message["role"] == "user":

            st.markdown(

                f"""
                <div class="msg-row user">
                    <div class="bubble">{content}</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        else:

            category = html.escape(str(message["category"]))
            matched = html.escape(
                str(message["matched_question"])
            )

            confidence = float(message["confidence"])

            st.markdown(

                f"""<div class="msg-row bot">
                    <div class="avatar">🤖</div>
                    <div>
                        <div class="bubble">
                            {content}
                        </div>
                        <div class="meta">
                            <span class="badge">
                                {category}
                            </span>
                            &nbsp;
                            Confidence:
                            <b>{confidence:.0%}</b>
                        </div>
                        <div class="match">
                            <b>Matched Question:</b>
                            {matched}
                        </div>
                    </div>
                </div>""",
                unsafe_allow_html=True,
            )

    st.markdown("</div>", unsafe_allow_html=True)

# =========================================================
# INPUT
# =========================================================

pending = st.session_state.pop(
    "pending_question",
    None,
)

typed_question = st.chat_input(
    "Ask a question about student support..."
)

question = typed_question or pending

# =========================================================
# PROCESS QUESTION
# =========================================================

if question:

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question,
        }
    )

    with st.spinner("SmartFAQ is analyzing your question..."):

        result = engine.ask(
            question,
            selected_category,
        )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "confidence": result["confidence"],
            "category": result["category"],
            "matched_question": result["matched_question"],
        }
    )

    if result["status"] == "matched":

        st.session_state.answered += 1

        st.session_state.confidence_values.append(
            result["confidence"]
        )

    st.rerun()

# =========================================================
# RIGHT INFORMATION PANEL
# =========================================================

with info_col:

    st.markdown(
        '<div class="section-title">How it works</div>',
        unsafe_allow_html=True,
    )

    st.info(
        "Your question is cleaned with NLTK, converted "
        "into TF-IDF vectors, compared with FAQs using "
        "cosine similarity, and evaluated using "
        "confidence thresholds."
    )

    st.markdown(
        '<div class="section-title">Confidence</div>',
        unsafe_allow_html=True,
    )

    confidence_cards = [
        ("≥ 70%", "Confident answer"),
        ("45–69%", "May help"),
        ("< 45%", "Fallback response"),
    ]

    for value, description in confidence_cards:

        st.markdown(
            f"""
            <div class="stat" style="margin-bottom:10px">
                <b>{value}</b><br>
                <span style="color:#64748b">
                    {description}
                </span>
            </div>
            """,
            unsafe_allow_html=True,
        )