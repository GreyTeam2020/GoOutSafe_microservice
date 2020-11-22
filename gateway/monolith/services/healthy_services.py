from flask import current_app
from monolith.utils.http_utils import HttpUtils
from monolith.app_constant import USER_MICROSERVICE_URL, BOOKING_MICROSERVICE_URL
from monolith.model import UserModel

from datetime import datetime, timedelta
from sqlalchemy import extract

from monolith.services import UserService
from monolith.tests.utils import get_user_with_id
from monolith.app_constant import *


class HealthyServices:
    """
    This class is a service that has inside it all the component
    to make all REST call with other services about healthy authority
    """

    @staticmethod
    def report_positive():
        # bind filter params...
        url = "{}/positive".format(USER_MICROSERVICE_URL)
        response = HttpUtils.make_get_request(url)
        users = response["result"]
        list_user = []
        for user in users:
            new_user = UserModel()
            new_user.fill_from_json(user)
            list_user.append(new_user)
        return list_user

    @staticmethod
    def mark_positive(user_email: str = "", user_phone: str = "") -> str:
        # bind filter params...
        if user_email is not None:
            key = "email"
            value = user_email
        elif user_phone is not None:
            key = "phone"
            value = user_phone
        else:
            return None
        url = "{}/mark/{}/{}".format(USER_MICROSERVICE_URL, key, value)
        response = HttpUtils.make_get_request(url)

        """
        TODO: chiamata contact
        esempio risposta API contact
        {
           "friends":["aaa@aaa.it","bbbb@bbb.it","bbbb@bbb.it"],
           "contacts":["","",""],
           "past_restaurants":["","",""],
           "reservation_restaurants":["","",""]
        }
        la risposta viene mandata come request body al email_microservice per notificare i contatti 
        il servizio prende le 4 liste, per ognuna cicla ed invia una mail ad ogni indirizzo
        
        ELEIMINARE, SONO LE VECCHIE CHIAMATE PER INVIO EMAIL, VENGONO MESSE IN email_microservice
         DispatcherMessage.send_message(
                    NEW_COVID_TO_RESTAURANT_BOOKING,
                    [
                        q_owner.email,
                        q_owner.firstname,
                        q_user.email,
                        restaurant.name,
                    ],
                )
        

         DispatcherMessage.send_message(
            NEW_POSITIVE_WAS_IN_RESTAURANT,
            [
                owner.email,
                owner.firstname,
                str(reservation.reservation_date),
                restaurant.name,
            ],
        )


         DispatcherMessage.send_message(
            EMAIL_TO_FRIEND,
            [friend, str(reservation.reservation_date), restaurant.name],
        )

        DispatcherMessage.send_message(
            NEW_POSITIVE_CONTACT,
            [
                thisuser.email,
                thisuser.firstname,
                contact.reservation_date,
                restaurant.name,
            ],
        )


         DispatcherMessage.send_message(
            EMAIL_TO_FRIEND,
            [
                friend,
                str(contact.reservation_date),
                restaurant.name,
            ],
        )
        """

        return response

    @staticmethod
    def unmark_positive(user_email: str, user_phone: str) -> str:
        """
        This method mark the a people as positive on db
        :param user_email:
        :param user_phone:
        :return: return a message
        """
        if user_email == "" and user_phone == "":
            return "Insert an email or a phone number"

        if user_email != "":
            body = str({"key": "email", "value": user_email})
        else:
            body = str({"key": "phone", "value": user_phone})

        URL = USER_MICROSERVICE_URL + "/unmark"

        response = HttpUtils.make_put_request(URL, body)

        if response is None:
            return "An error occurs"

        if response[1] == 400:
            return "An error occurs, please try again"

        if response[1] == 404:
            if response[0] == "User not found":
                return "The customer is not registered"
            elif response[0] == "User not positive":
                return "The user is not Covid-19 positive"

        if response[1] == 200:
            return ""

        return "Error"


    
    def search_contacts_for_email(user_email: str, user_phone: str):

        contact_users_GUI = []
        """
            per contatti non ancora positivi:
            contact_users_GUI.append(
                [
                    user.id,
                    user.firstname + " " + user.lastname,
                    str(user.dateofbirth).split()[0],
                    user.email,
                    user.phone,
                ]
            )
        """

        pass



    def search_contacts_for_email(user_email: str, user_phone: str):
        '''{
           "friends":["aaa@aaa.it","bbbb@bbb.it","bbbb@bbb.it"],
           "contacts":["","",""],
           "past_restaurants":["","",""],
           "reservation_restaurants":["","",""]
        }'''

        if user_email == "" and user_phone == "":
            return "Insert an email or a phone number"

        friends = []
        contacts = []
        past_restaurants = []
        future_restaurants = []

        if user_email != "":
            URL = USER_MICROSERVICE_URL + "/positiveinfo/email/"+str(user_email)
        else:
            URL = USER_MICROSERVICE_URL + "/positiveinfo/phone/"+str(user_phone)

        #check if the user exists
        #check if the user is positive (get also date of marking) (API)
        response = HttpUtils.make_get_request(URL)
        if response is None:
            return "Error, please try again"

        if response == "User not found":
            return "The customer is not registered"
        elif response == "Information not found":
            return "The user is not Covid-19 positive"
        elif response == "Bad Request":
            return "Error"

        #now we have the information about the positivity of the user in response
        date_marking = response["from_date"]
        user_id = response["user_id"]
        
        #start to check contacts
        #API: get all reservation of the customer between date_marking and date_marking -14
        URL = BOOKING_MICROSERVICE_URL + "?user_id="+str(user_id)+"&fromDate="+str(date_marking)+"&toDate="+str(date_marking - timedelta(days=14))
        reservations_customer = HttpUtils.make_get_request(URL)
        
        if reservations_customer != "No Reservations":
            
            #API: get all reservations between date_marking and date_m -14
            URL = BOOKING_MICROSERVICE_URL + "?&fromDate="+str(date_marking)+"&toDate="+str(date_marking - timedelta(days=14))
            all_reservations = HttpUtils.make_get_request(URL)
        
            '''
            for each reservation of the client
            get friend's email of the positive customer
            SEND EMAIL (ADD TO JSON)

            find in all reservations all res with same day and time
            get user id of reservation (contact)
            API: get user email and name of the contact
            get friend of the contact
            SEND EMAIL (ADD TO JSON)

            get restaurant id of the reservation
            API restaurant: get info (owner_email) of the restaurant
            SEND EMAIL (ADD TO JSON)
            '''
        
        #API booking: get all future booking of the customer
        URL = BOOKING_MICROSERVICE_URL + "?user_id="+str(user_id)+"&fromDate="+str(date_marking))
        future_reservations = HttpUtils.make_get_request(URL)
        
        """
        get all restaurants (API)
        for each future reservation
            use restaurant.id to get owner_email from list of restaurants
            SEND EMAIL (ADD TO JSON)
        """