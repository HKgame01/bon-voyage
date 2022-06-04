import time
from configparser import ConfigParser
from os import access, path
import json

from duffel_api import Duffel

# for multiple passengers we can call this function multiple times for each passenger

"""
ERRORS: 
duffel_api.http_client.ApiError: airline_error: Requested offer is no longer available: Please select another offer, or create a new offer request to get the latest availability.
idk how to fix this

FIX:
Custom error in errors.errors.py for airline_error
STILL NEED TO IMPLEMENT
"""

def bookFlight():
    config = ConfigParser() # Create a config parser object
    config.read(path.join("config", "config.ini")) # Read the config file
    client = Duffel(access_token=config['duffel']['access_token'])  # Create a new instance of the API

    # Get all flights from the API and print the results to the console
    destination = input("\nDestination?\n").strip()
    origin = input("\nFrom where?\n").strip()
    departure_date = input("\nDate of departure? (YYYY-MM-DD)\n").strip()   # if data is before current date, throws duffel_api.http_client.ApiError: validation_error: Invalid date: Field 'departure_date' must be after yyyy-mm-dd

    print("\nSearching flights...")
    time.sleep(1) # limit API calls to 1 per second to avoid rate limiting

    # Get all flights from the API
    slices = [
        {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
        },
    ]
    # Get all flights from the API
    offer_request = (
        client.offer_requests.create()
        .passengers([{"type": "adult"}])
        .slices(slices)
        .return_offers()
        .execute()
    )
    offers = offer_request.offers   # Get the list of offers
    #print(offers)

    for idx, offer in enumerate(offers): # Print the results to the console 
        print(
            f"{idx + 1}. {offer.owner.name} flight departing at "
            + f"{offer.slices[0].segments[0].departing_at} "    # offer.slices[0].segments[0].departing_at is a datetime object
            + f"{offer.total_amount} {offer.total_currency}"    # offer.total_amount is the price of the flight
        )
    # Get the user's choice
    offer_index = input("\nSelect the flight number you wish to book\n").strip()
    given_name = input("\nWhat is your first name?\n").strip()
    family_name = input("\nWhat is your surname?\n").strip() # validation_error: Invalid length: Field 'family_name' should be at least 2 character(s) long
    dob = input("\nWhat is your date of birth? (YYYY-MM-DD)\n").strip() # must be in yyyy-mm-dd format. solution: create a calendar object in the flask backend and use the datepicker to select the date
    title = input("\nWhat is your title? (mr, ms, mrs, miss)\n").strip() # dr and other surnames are not supported by api calls
    gender = input("\nWhat is your gender? (m, f)\n").strip()   # other genders are not supported by api calls
    phone_number = input("\nWhat is your phone number? (+XX)\n").strip()
    email = input("\nWhat is your email address?\n").strip()
    bags = input("\nHow Many bags?\n").strip()
    
    '''    
print(f'\n{offers[int(offer_index) - 1].owner.name} \n{offers[int(offer_index) - 1].slices[0].segments[0].departing_at}'
          f'\n{offers[int(offer_index) - 1].total_amount} \n{offers[int(offer_index) - 1].total_currency}'
          f'\n{offers[int(offer_index) - 1].tax_amount} \n{offers[int(offer_index) - 1].base_amount}'
          f'\n{offers[int(offer_index) - 1].slices[0].destination.city_name}\n{offers[int(offer_index) - 1].slices[0].origin.city_name}')
    '''
    print(f"\nHang tight! Booking offer {offer_index}...")
    time.sleep(1) # artificial delay to show the user the progress
    
    selected_offer = offers[int(offer_index) - 1]   # Get the selected offer
    payments = [    # Create a payment object
        {
            "currency": selected_offer.total_currency,  # USD
            "amount": selected_offer.total_amount,
            "type": "balance",
        }
    ]
    passengers = [ # Create a passenger object
        {
            "phone_number": phone_number,
            "email": email,
            "title": title,
            "gender": gender,
            "family_name": family_name,
            "given_name": given_name,
            "born_on": dob,
            "id": offer_request.passengers[0].id,
        }
    ]

    try:
        order = ( # Create an order object
            client.orders.create()
            .payments(payments)
            .passengers(passengers)
            .selected_offers([selected_offer.id])
            .execute()
        )
    except:
        # recursion to try again is api calls are rate limited or create an error for the user
        print('Sorry, something went wrong. Please try again. \n')
        bookFlight()
        
    # Print the results to the console
    """    
    print(f"\nPerfect! Your flight has been booked.\n"
          f"\nYour Flight Info:\n"
          f"Order Number: {order.booking_reference}\n"
          f"Flight Name: {offers[int(offer_index) - 1].owner.name}\n"
          f"Departure Date: {offers[int(offer_index) - 1].slices[0].segments[0].departing_at}\n"
          f"Flying from {offers[int(offer_index) - 1].slices[0].origin.city_name} to {offers[int(offer_index) - 1].slices[0].destination.city_name}\n"
          f"Subtotal: {offers[int(offer_index) - 1].base_amount}\n"
          f"Tax: {offers[int(offer_index) - 1].tax_amount}\n"
          f"Total: {offers[int(offer_index) - 1].total_amount}\n"
          "Thank you for using *APP_NAME*!\n")
    """
          
          
    sqlEndpoint = { 
        "order_number": order.booking_reference,
        "flight_name": offers[int(offer_index) - 1].owner.name,
        "departure_date": offers[int(offer_index) - 1].slices[0].segments[0].departing_at,
        "origin": offers[int(offer_index) - 1].slices[0].origin.city_name,
        "destination": offers[int(offer_index) - 1].slices[0].destination.city_name,
        "bags = ": bags,
        "subtotal": (offers[int(offer_index) - 1].base_amount) + 25*int(bags),
        "tax": offers[int(offer_index) - 1].tax_amount,
        "Total": ((offers[int(offer_index) - 1].base_amount) + 25*int(bags)) + (offers[int(offer_index) - 1].tax_amount)
    }
    
    # add code to insert the data into the sql database

