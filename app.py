
import json
import random
import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="AI Murder Mystery", page_icon="🕵️", layout="wide")

# =====================================================
# OPENAI API KEY
# =====================================================
# PASTE YOUR OPENAI API KEY BELOW
# Example:
# sk-xxxxxxxxxxxxxxxxxxxxxxxx
import os

API_KEY = os.getenv("OPENAI_API_KEY")

def get_client():
    if not API_KEY:
        return None
    return OpenAI(api_key=API_KEY)

DEFAULT_CASE = {
    "victim": "Arthur Blackwood",
    "crime_scene": "Old Manor Library",
    "murderer": "Sarah Reed",
    "suspects": [
        {"name":"Sarah Reed","alibi":"I was in the garden.","motive":"Inheritance dispute."},
        {"name":"James Cole","alibi":"I was reading upstairs.","motive":"Business rivalry."},
        {"name":"Emma Stone","alibi":"I was preparing dinner.","motive":"Personal grudge."}
    ],
    "clues":[
        "Muddy footprints near the library door.",
        "A torn will found in the fireplace.",
        "A gardening glove with fresh dirt.",
        "A witness heard an argument.",
        "A pocket watch stopped at 9:15 PM.",
        "A handwritten threat note."
    ],
    "contradictions":[
        {
            "suspect":"Sarah Reed",
            "statement":"I was in the garden all evening.",
            "evidence":"Footprints lead from the library to the garden."
        }
    ]
}

def generate_case():
    client = get_client()
    if client is None:
        return DEFAULT_CASE

    prompt = """
Create a murder mystery. Return ONLY valid JSON.

{
  "victim":"",
  "crime_scene":"",
  "murderer":"",
  "suspects":[
    {"name":"","alibi":"","motive":""}
  ],
  "clues":[""],
  "contradictions":[
    {"suspect":"","statement":"","evidence":""}
  ]
}

Rules:
- exactly 3 suspects
- exactly 1 murderer
- 6 clues
- at least 3 contradictions
- detective-game style
"""
    try:
        response = client.responses.create(
            model="gpt-5",
            input=prompt
        )
        return json.loads(response.output_text)
    except Exception:
        return DEFAULT_CASE

def init_game():
    st.session_state.case = generate_case()
    st.session_state.score = 0
    st.session_state.collected_clues = []
    st.session_state.found_contradictions = []
    st.session_state.game_over = False

if "case" not in st.session_state:
    init_game()

case = st.session_state.case

st.title("🕵️ AI Murder Mystery")
st.caption("Prompts 1–5 Combined: Suspects, Clues, Contradictions, Scoring, OpenAI, Streamlit UI")

with st.sidebar:
    st.header("Detective Panel")
    st.write("Victim:", case["victim"])
    st.write("Crime Scene:", case["crime_scene"])
    st.metric("Score", st.session_state.score)

    if st.button("🔄 New Case"):
        init_game()
        st.rerun()

def rank(score):
    if score >= 200:
        return "Legendary Detective"
    if score >= 150:
        return "Master Detective"
    if score >= 100:
        return "Lead Detective"
    if score >= 50:
        return "Junior Investigator"
    return "Rookie Detective"

col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Crime Scene")
    st.info(case["crime_scene"])

    st.subheader("Investigate")
    if st.button("🔍 Find Clue"):
        remaining = [c for c in case["clues"] if c not in st.session_state.collected_clues]
        if remaining:
            clue = random.choice(remaining)
            st.session_state.collected_clues.append(clue)
            st.session_state.score += 10
            st.success(f"Clue Found: {clue}")
        else:
            st.warning("No more clues available.")

    st.subheader("📋 Collected Clues")
    if st.session_state.collected_clues:
        for clue in st.session_state.collected_clues:
            st.write("•", clue)
    else:
        st.write("No clues collected yet.")

with col2:
    st.subheader("Detective Rank")
    st.success(rank(st.session_state.score))

st.subheader("🧑 Suspects")

cols = st.columns(3)
for i, suspect in enumerate(case["suspects"]):
    with cols[i]:
        st.markdown(f"### {suspect['name']}")
        st.write("**Alibi:**", suspect["alibi"])
        st.write("**Motive:**", suspect["motive"])

st.subheader("⚖️ Find Contradictions")

suspect_choice = st.selectbox(
    "Choose suspect",
    [s["name"] for s in case["suspects"]]
)

if st.button("Check Contradiction"):
    found = False
    for c in case["contradictions"]:
        if c["suspect"] == suspect_choice:
            found = True
            if suspect_choice not in st.session_state.found_contradictions:
                st.session_state.score += 25
                st.session_state.found_contradictions.append(suspect_choice)

            st.error("Contradiction Found!")
            st.write("Statement:", c["statement"])
            st.write("Evidence:", c["evidence"])

    if not found:
        st.info("No contradiction found.")

st.subheader("🎯 Make an Accusation")

accused = st.selectbox(
    "Who is the murderer?",
    [s["name"] for s in case["suspects"]],
    key="accuse"
)

if st.button("Accuse"):
    st.session_state.game_over = True

    if accused == case["murderer"]:
        st.session_state.score += 50
        st.success("Case Solved!")
    else:
        st.error("Wrong Accusation!")

    st.write("Actual Murderer:", case["murderer"])

    st.subheader("Case Report")
    st.write("Victim:", case["victim"])
    st.write("Crime Scene:", case["crime_scene"])
    st.write("Final Score:", st.session_state.score)
    st.write("Rank:", rank(st.session_state.score))
