import streamlit as st
from config import load_config, initialize_llm
from data import load_dataset
from chatbot import generate_response
from langchain.memory import ConversationBufferMemory

def main():
    st.title("Flight Booking Assistant")
    st.write("Hello! Tell me where you'd like to fly, and I'll assist you with booking.")

    api_key = load_config()
    if not api_key:
        return

    df = load_dataset()
    if df is None:
        st.error("Failed to load flight data. Please check the data source.")
        return

    chain = initialize_llm(api_key)
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "booking_details" not in st.session_state:
        st.session_state.booking_details = {
            "departure_city": None,
            "destination": None,
            "travel_date": None,
            "airline": None,
            "seating_class": None,
            "flight_id": None,
            "user_name": None,
            "user_email": None
        }
    if "memory" not in st.session_state:
        st.session_state.memory = ConversationBufferMemory()
    if "bookings" not in st.session_state:
        st.session_state.bookings = []
    if "available_flights" not in st.session_state:
        st.session_state.available_flights = []
    if "filtered_flights" not in st.session_state:
        st.session_state.filtered_flights = []
    if "selected_flight" not in st.session_state:
        st.session_state.selected_flight = None

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    user_input = st.chat_input("Tell me what you need!")
    if user_input:
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.write(user_input)

        bot_reply = generate_response(user_input, chain, df)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        with st.chat_message("assistant"):
            st.write(bot_reply)

if __name__ == "__main__":
    main()