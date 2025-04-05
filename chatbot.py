import time
import streamlit as st
from data import search_flights
from booking import confirm_booking

def generate_response(user_input, chain, df):
    # Ensure state is initialized
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
    if "available_flights" not in st.session_state:
        st.session_state.available_flights = []
    if "filtered_flights" not in st.session_state:
        st.session_state.filtered_flights = []
    if "selected_flight" not in st.session_state:
        st.session_state.selected_flight = None

    details = st.session_state.booking_details
    flights = st.session_state.available_flights
    filtered_flights = st.session_state.filtered_flights
    details_str = f"Departure: {details['departure_city']}, Destination: {details['destination']}, Date: {details['travel_date']}, Airline: {details['airline']}, Class: {details['seating_class']}, Flight ID: {details['flight_id']}, Name: {details.get('user_name')}, Email: {details.get('user_email')}"
    dataset_context = "\n".join([f"Flight {row['Flight_ID']}: {row['Departure_City']} to {row['Destination']} on {row['Travel_Date']}, {row['Airline']}, {row['Seating_Class']}, {row['Departure_Time']}, Rs. {row['Price']}" for _, row in df.iterrows()]) if not df.empty else "No dataset loaded"
    context = f"""Current Booking Details: {details_str}
Available Flights: {flights if flights else 'No flights searched yet.'}
Filtered Flights: {filtered_flights if filtered_flights else 'No filtered flights yet.'}
Dataset (40 flights): {dataset_context}
Chat History: {st.session_state.memory.buffer}
User Input: {user_input}
"""

    # Debug logs
    st.write(f"DEBUG: User Input: {user_input}")
    st.write(f"DEBUG: Current Booking Details: {details}")
    if df is None or df.empty:
        st.write("DEBUG: ERROR: Dataset (df) is empty or not loaded!")
        return "Flight data not found. Please check data source."

    if "cancel" in user_input.lower():
        return reset_booking(details)

    # Handle "book me a flight from X to Y" with or without date
    if "book me a flight from" in user_input.lower() and "to" in user_input.lower():
        return handle_from_to_input(user_input, details, chain, context, df)

    # Step-by-step flow only if prior steps are incomplete
    if not details["departure_city"]:
        return handle_departure_city(user_input, details, chain, context)
    if not details["destination"]:
        return handle_destination(user_input, details, chain, context)
    if not details["travel_date"]:
        return handle_travel_date(user_input, details, df, chain, context)
    
    # Search flights if not already done
    if not flights and details["travel_date"]:
        flights = search_flights(details["departure_city"], details["destination"], details["travel_date"], df)
        st.session_state.available_flights = flights if flights else []
        if not flights:
            return "No flights available on this date. Please try another date."

    if not details["airline"]:
        return handle_airline(user_input, details, chain, context)
    if not details["seating_class"]:
        return handle_seating_class(user_input, details, df, chain, context)
    if not details["flight_id"]:
        return handle_flight_id(user_input, details, df, chain, context)
    if not details.get("user_name"):
        return handle_user_name(user_input, details, chain, context)
    if not details.get("user_email"):
        response = handle_user_email(user_input, details, chain, context)
        if "Booking confirmed" in response:
            return response
        return response
    return "All details collected! Anything else I can assist with?"

def reset_booking(details):
    st.session_state.booking_details = {k: None for k in details}
    st.session_state.available_flights = None
    st.session_state.filtered_flights = None
    st.session_state.selected_flight = None
    return "Booking canceled. Please provide your departure city."

def handle_from_to_input(user_input, details, chain, context, df):
    try:
        parts = user_input.lower().split("from")[1].split("to")
        departure_city = parts[0].strip().capitalize()
        destination_part = parts[1].strip()
        
        # List of possible prepositions for date
        date_prepositions = ["on", "at", "for", "in", "to", "by", "during", "after", "before"]
        date_part = None
        destination = None
        
        # Check for date with any preposition
        for prep in date_prepositions:
            if f" {prep} " in destination_part:
                split_parts = destination_part.split(f" {prep} ")
                destination = split_parts[0].strip().capitalize()
                date_part = split_parts[1].strip()
                break
        
        # If no preposition found, assume whole part is destination
        if not date_part:
            destination = destination_part.strip().capitalize()

        # Update details
        details["departure_city"] = departure_city
        details["destination"] = destination
        
        # Process date if provided
        if date_part:
            details["travel_date"] = date_part
            flights = search_flights(details["departure_city"], details["destination"], details["travel_date"], df)
            st.session_state.available_flights = flights if flights else []
            if not flights:
                return "No flights available on this date. Please try another date."
            return "Which airline do you prefer?"
        
        return "When would you like to travel? Please provide the date (YYYY-MM-DD)."
    except:
        return "Please clarify your departure and destination cities, e.g., 'from Chicago to London'."

def handle_departure_city(user_input, details, chain, context):
    if not user_input.strip():
        return "Please provide your departure city."
    details["departure_city"] = user_input.capitalize()
    if not details["destination"]:
        return "Please provide your destination city."
    return "When would you like to travel? Please provide the date (YYYY-MM-DD)."

def handle_destination(user_input, details, chain, context):
    if not user_input.strip():
        return "Please provide your destination city."
    details["destination"] = user_input.capitalize()
    if not details["travel_date"]:
        return "When would you like to travel? Please provide the date (YYYY-MM-DD)."
    return "Which airline do you prefer?"

def handle_travel_date(user_input, details, df, chain, context):
    date_input = user_input.strip()
    if not date_input:
        return "When would you like to travel? Please provide the date (YYYY-MM-DD)."
    details["travel_date"] = date_input
    flights = search_flights(details["departure_city"], details["destination"], details["travel_date"], df)
    st.session_state.available_flights = flights if flights else []
    if not flights:
        return "No flights available on this date. Please try another date."
    return "Which airline do you prefer?"

def handle_airline(user_input, details, chain, context):
    if "no" in user_input.lower() and "preference" in user_input.lower():
        details["airline"] = None
        return "What seating class do you want – Economy, Business, or First?"
    if not user_input.strip():
        return "Which airline do you prefer?"
    details["airline"] = user_input.capitalize()
    return "What seating class do you want – Economy, Business, or First?"

def handle_seating_class(user_input, details, df, chain, context):
    if not user_input.strip():
        return "What seating class do you want – Economy, Business, or First?"
    details["seating_class"] = user_input.capitalize()
    flights = st.session_state.available_flights
    if flights:
        filtered_flights = [f for f in flights if 
                           (not details["airline"] or f["Airline"].lower() == details["airline"].lower()) and 
                           f["Seating_Class"].lower() == details["seating_class"].lower()]
        st.session_state.filtered_flights = filtered_flights if filtered_flights else flights  # Fallback to all flights if no match
        flight_list = "\n".join([f"- {f['Flight_ID']} - {f['Departure_Time']} - Rs. {f['Price']}" for f in st.session_state.filtered_flights])
        return f"Here are your options: {flight_list}. Enter the flight ID to book."
    return "No flights available. Try another date or destination."

def handle_flight_id(user_input, details, df, chain, context):
    if not user_input.strip():
        return "Please enter a flight ID from the list."
    flights = st.session_state.filtered_flights or st.session_state.available_flights
    if flights:
        selected_flight = next((f for f in flights if f["Flight_ID"].lower() == user_input.lower()), None)
        if selected_flight:
            details["flight_id"] = selected_flight["Flight_ID"]
            st.session_state.selected_flight = selected_flight
            return "Please provide your name to confirm the booking."
        flight_ids = [f["Flight_ID"] for f in flights]
        return f"Invalid flight ID. Choose from: {', '.join(flight_ids[:4])}."
    return "No flights available to choose from. Try another airline, class, or date."

def handle_user_name(user_input, details, chain, context):
    if not user_input.strip():
        return "Please provide your name to confirm the booking."
    details["user_name"] = user_input.capitalize()
    return "Please provide your email to confirm the booking."

def handle_user_email(user_input, details, chain, context):
    if not user_input.strip():
        return "Please provide your email to confirm the booking."
    details["user_email"] = user_input
    selected_flight = st.session_state.selected_flight
    if selected_flight:
        return confirm_booking(selected_flight, details)
    return "Something went wrong. Please start over with your departure city."

def update_context(details, user_input):
    details_str = f"Departure: {details['departure_city']}, Destination: {details['destination']}, Date: {details['travel_date']}, Airline: {details['airline']}, Class: {details['seating_class']}, Flight ID: {details['flight_id']}, Name: {details.get('user_name')}, Email: {details.get('user_email')}"
    return f"""Current Booking Details: {details_str}
Available Flights: {st.session_state.available_flights if st.session_state.available_flights else 'No flights found.'}
Filtered Flights: {st.session_state.filtered_flights if st.session_state.filtered_flights else 'No filtered flights found.'}
Chat History: {st.session_state.memory.buffer}
User Input: {user_input}
"""

def retry_with_backoff(func, max_retries=3, initial_delay=10):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if "rate_limit_exceeded" in str(e) and "413" in str(e):
                st.write(f"Rate limit exceeded. Retrying in {initial_delay} seconds...")
                time.sleep(initial_delay)
                initial_delay *= 2
            else:
                raise e
    raise Exception("Max retries exceeded.")