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

        if response is None :
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


    
    def search_contacts(user_email: str, user_phone: str):

        if user_email == "" and user_phone == "":
            return "Insert an email or a phone number"

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

        contact_users_GUI = []

        #now we have the information about the positivity of the user in response
        date_marking = response["from_date"]
        user_id = response["user_id"]
        
        #start to check contacts
        #API: get all reservation of the customer between date_marking and date_marking -14
        URL = BOOKING_MICROSERVICE_URL + "?user_id="+str(user_id)+"&fromDate="+str(date_marking)+"&toDate="+str(date_marking - timedelta(days=14))
        reservations_customer = HttpUtils.make_get_request(URL)
        
        i=1

        if reservations_customer != "No Reservations":
            
            #API: get all reservations between date_marking and date_m -14
            URL = BOOKING_MICROSERVICE_URL + "?&fromDate="+str(date_marking)+"&toDate="+str(date_marking - timedelta(days=14))
            all_reservations = HttpUtils.make_get_request(URL)
            
            for reservation in reservations_customer:

                restaurant_id = reservation["table"]["restaurant"]["id"]

                start =  datetime.strptime(reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ")
                end = datetime.strptime(reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ")

                for one_reservation in all_reservations:
                    
                    restaurant_id_contact = one_reservation["table"]["restaurant"]["id"]

                    if restaurant_id_contact != restaurant_id:
                        #are not in the same restaurant
                        continue

                    start_contact =  datetime.strptime(one_reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ")
                    end_contact = datetime.strptime(one_reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ")


                    #if people are in the same restaurant in the same day
                    if(
                        start.year != start_contact.year or
                        start.month != start_contact.month or
                        start.day != start_contact.day 
                    ):
                        continue

                    URL = RESTAURANTS_MICROSERVICE_URL + "/" + str(restaurant_id)+ "/openings"
                    openings = HttpUtils.make_get_request(URL)

                    if start.weekday() == 0:
                        dayNumber = 6
                    else:
                        dayNumber = start.weekday()-1

                    restaurant_hours = []

                    for opening in openings["openings"]:
                        if opening["week_day"] == dayNumber:
                            restaurant_hours.append(datetime.strptime(opening["open_lunch"], "%H:%M"))
                            restaurant_hours.append(datetime.strptime(opening["close_lunch"], "%H:%M"))
                            restaurant_hours.append(datetime.strptime(opening["open_dinner"], "%H:%M"))
                            restaurant_hours.append(datetime.strptime(opening["close_dinner"], "%H:%M"))

                    #if people are in the restaurant at lunch or dinner
                    if (
                        (
                            restaurant_hours[0].hour <= start.hour and
                            restaurant_hours[0].hour <= start_contact.hour and
                            restaurant_hours[0].minute <= start.minute and
                            restaurant_hours[0].minute <= start_contact.minute and

                            restaurant_hours[1].hour >= end.hour and
                            restaurant_hours[1].hour >= end_contact.hour and
                            restaurant_hours[1].minute >= end.minute and
                            restaurant_hours[1].minute >= end_contact.minute 
                        ) or (
                            restaurant_hours[2].hour <= start.hour and
                            restaurant_hours[2].hour <= start_contact.hour and
                            restaurant_hours[2].minute <= start.minute and
                            restaurant_hours[2].minute <= start_contact.minute and

                            restaurant_hours[3].hour >= end.hour and
                            restaurant_hours[3].hour >= end_contact.hour and
                            restaurant_hours[3].minute >= end.minute and
                            restaurant_hours[3].minute >= end_contact.minute 

                        )

                    ):
                        #people are in the same restaurant at lunch

                        #if they are in the same time 
                        if not ( 
                            (
                                start_contact < start and 
                                end_contact < start
                            ) or (
                                start_contact > end and 
                                end_contact > end
                            )
                        ):
                            #they are contacts!

                            #API: get user email and name of the contact
                            URL = USER_MICROSERVICE_URL +"/"+str(one_reservation["customer_id"])
                            user = HttpUtils.make_get_request(URL)
                             
                            contact_users_GUI.append(
                                [
                                    i,
                                    user["firstname"] + " " + user["lastname"],
                                    user["dateofbirth"],
                                    user["email"],
                                    user["phone"]
                                ]
                            )
                            i += 1

        return contact_users_GUI


    def search_contacts_for_email(user_email: str, user_phone: str):

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
        
            
            for reservation in reservations_customer:

                restaurant_id = reservation["table"]["restaurant"]["id"]

                URL = RESTAURANTS_MICROSERVICE_URL + "/" + str(restaurant_id)
                restaurant = HttpUtils.make_get_request(URL)
                if restaurant is not None:
                    past_restaurants.add({
                        "email" : restaurant["owner_email"],
                        "name" : restaurant["name"],
                        "date" : start
                    })

                '''
                RSERVATION DOESN'T RETURN EMAIL OF FRIENDS

                get friend's email of the positive customer
                SEND EMAIL (ADD TO JSON)
                '''

                start =  datetime.strptime(reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ")
                end = datetime.strptime(reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ")

                for one_reservation in all_reservations:
                    
                    restaurant_id_contact = one_reservation["table"]["restaurant"]["id"]

                    if restaurant_id_contact != restaurant_id:
                        #are not in the same restaurant
                        continue

                    start_contact =  datetime.strptime(one_reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ")
                    end_contact = datetime.strptime(one_reservation["reservation_end"], "%Y-%m-%dT%H:%M:%SZ")


                    #if people are in the same restaurant in the same day
                    if(
                        start.year != start_contact.year or
                        start.month != start_contact.month or
                        start.day != start_contact.day 
                    ):
                        continue

                    URL = RESTAURANTS_MICROSERVICE_URL + "/" + str(restaurant_id)+ "/openings"
                    openings = HttpUtils.make_get_request(URL)

                    if start.weekday() == 0:
                        dayNumber = 6
                    else:
                        dayNumber = start.weekday()-1

                    restaurant_hours = []

                    for opening in openings["openings"]:
                        if opening["week_day"] == dayNumber:
                            restaurant_hours.append(datetime.strptime(opening["open_lunch"], "%H:%M"))
                            restaurant_hours.append(datetime.strptime(opening["close_lunch"], "%H:%M"))
                            restaurant_hours.append(datetime.strptime(opening["open_dinner"], "%H:%M"))
                            restaurant_hours.append(datetime.strptime(opening["close_dinner"], "%H:%M"))

                    #if people are in the restaurant at lunch or dinner
                    if (
                        (
                            restaurant_hours[0].hour <= start.hour and
                            restaurant_hours[0].hour <= start_contact.hour and
                            restaurant_hours[0].minute <= start.minute and
                            restaurant_hours[0].minute <= start_contact.minute and

                            restaurant_hours[1].hour >= end.hour and
                            restaurant_hours[1].hour >= end_contact.hour and
                            restaurant_hours[1].minute >= end.minute and
                            restaurant_hours[1].minute >= end_contact.minute 
                        ) or (
                            restaurant_hours[2].hour <= start.hour and
                            restaurant_hours[2].hour <= start_contact.hour and
                            restaurant_hours[2].minute <= start.minute and
                            restaurant_hours[2].minute <= start_contact.minute and

                            restaurant_hours[3].hour >= end.hour and
                            restaurant_hours[3].hour >= end_contact.hour and
                            restaurant_hours[3].minute >= end.minute and
                            restaurant_hours[3].minute >= end_contact.minute 

                        )

                    ):
                        #people are in the same restaurant at lunch

                        #if they are in the same time 
                        if not ( 
                            (
                                start_contact < start and 
                                end_contact < start
                            ) or (
                                start_contact > end and 
                                end_contact > end
                            )
                        ):
                            #they are contacts!

                            #API: get user email and name of the contact
                            URL = USER_MICROSERVICE_URL +"/"+str(one_reservation["customer_id"])
                            user = HttpUtils.make_get_request(URL)
                             
                            contacts.append({
                                "email" : user["email"],
                                "name" : user["firstname"],
                                "restaurant_name" : restaurant["name"],
                                "date" : start
                            })

                            '''
                            get friend of the contact
                            SEND EMAIL (ADD TO JSON)
                            '''

                
        if user_email != "":
            customer_email = user_email
        else:
            URL = USER_MICROSERVICE_URL +"/"+str(user_id)
            user = HttpUtils.make_get_request(URL)
            customer_email = user["email"]
        

        #API booking: get all future booking of the customer
        URL = BOOKING_MICROSERVICE_URL + "?user_id="+str(user_id)+"&fromDate="+str(date_marking)
        future_reservations = HttpUtils.make_get_request(URL)
        
        for future_reservation in future_reservations:
            date =  datetime.strptime(reservation["reservation_date"], "%Y-%m-%dT%H:%M:%SZ")   

            restaurant_id = future_reservation["table"]["restaurant"]["id"]
            URL = RESTAURANTS_MICROSERVICE_URL + "/" + str(restaurant_id)
            restaurant = HttpUtils.make_get_request(URL)
            if restaurant is not None:
                future_restaurants.append({
                    "email" : restaurant["owner_email"],
                    "name" : restaurant["name"],
                    "date" : date,
                    "customer_email" : customer_email
                })


        return {
           "friends": friends,
           "contacts": contacts,
           "past_restaurants":past_restaurants,
           "reservation_restaurants":future_restaurants
        } 