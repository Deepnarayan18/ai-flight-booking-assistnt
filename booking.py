import random
import streamlit as st

def confirm_booking(selected_flight, details):
    # Email validation
    user_email = details.get("user_email", "")
    if not user_email.endswith("@gmail.com"):
        return "Invalid email! Please provide a valid Gmail address (e.g., example@gmail.com) to confirm the booking."

    total_cost = selected_flight["Price"]
    booking_ref = f"FLY{random.randint(100, 999)}"
    booking = {
        "flight_id": selected_flight["Flight_ID"],
        "departure_city": details["departure_city"],
        "destination": details["destination"],
        "travel_date": details["travel_date"],
        "airline": details["airline"],
        "seating_class": details["seating_class"],
        "departure_time": selected_flight["Departure_Time"],
        "price": total_cost,
        "user_name": details["user_name"],
        "user_email": user_email,
        "reference": booking_ref
    }
    st.session_state.bookings.append(booking)
    # Reset state after confirmation
    st.session_state.booking_details = {k: None for k in details}
    st.session_state.available_flights = None
    st.session_state.filtered_flights = None
    st.session_state.selected_flight = None
    confirmation = f"Booking confirmed! Flight {selected_flight['Flight_ID']} from {details['departure_city']} to {details['destination']} at {selected_flight['Departure_Time']} for Rs. {total_cost} (Ref: {booking_ref})."
    return f"{confirmation}\nok enjoy your flight"