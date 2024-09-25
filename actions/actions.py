# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

# from typing import Any, Text, Dict, List

# from rasa_sdk import Action, Tracker # type: ignore
# from rasa_sdk.executor import CollectingDispatcher # type: ignore

from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker  # type: ignore
from rasa_sdk.executor import CollectingDispatcher  # type: ignore
from rasa_sdk.events import SlotSet  
import mysql.connector

class OrderPlantAction(Action):

    def name(self) -> Text:
        return "action_order_plant"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        dispatcher.utter_message(text="Sure, which kind of plant would you like to order? Answer in format: I want to order plantname")

        return []

class ExtractPlantEntity(Action):

    def name(self) -> Text:
        return "action_extract_plant_entity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        plant_entity = next(tracker.get_latest_entity_values('plant'), None)

        if plant_entity:
            dispatcher.utter_message(text=f"You have selected {plant_entity} as your plant choice, please enter how many of them? You can order from [50 - 500] of them.")
            return [SlotSet("selected_plant", plant_entity)]
        else:
            dispatcher.utter_message(text="I am sorry, I could not detect the plant choice. Please specify the plant you would like to order.")
        return []

class QuantityOrderAction(Action):

    def name(self) -> Text:
        return "action_provide_quantity"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        quantity_entity = next(tracker.get_latest_entity_values('quantity'), None)
        
        if quantity_entity:
            try:
                quantity = int(quantity_entity)
                
                if 49 < quantity <= 500:
                    dispatcher.utter_message(text=f"You want to order {quantity_entity}. Now please provide me with your email address!")
                    return [SlotSet("selected_quantity", quantity_entity)]
                else:
                    dispatcher.utter_message(text="I am sorry, we only offer quantities between 50 and 500.")
                    
            except ValueError:
                dispatcher.utter_message(text="I am sorry, the quantity provided is not valid. Please enter a valid number between 50 and 500.")
        else:
            dispatcher.utter_message(text="I am sorry, we couldn't detect the quantity. Please provide a valid quantity between 50 and 500.")
        
        return []

class EmailOrderAction(Action):

    def name(self) -> Text:
        return "action_provide_email"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        email_entity = next(tracker.get_latest_entity_values('email'), None)
       
        if email_entity:
            dispatcher.utter_message(text=f"Thank you for your email {email_entity}. Now please provide me with your address in format: Street streetname!")
            return [SlotSet("selected_email", email_entity)]
        else:
            dispatcher.utter_message(text="I am sorry, check your email again.")
        return []

class AddressOrderAction(Action):

    def name(self) -> Text:
        return "action_provide_address"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
        address_entity = next(tracker.get_latest_entity_values('address'), None)
       
        if address_entity:
            dispatcher.utter_message(text=f"Your delivery address is {address_entity}. Tell me do you want to order anything else, in case that you want first complete this first order then, second?")
            return [SlotSet("selected_address", address_entity)]
        else:
            dispatcher.utter_message(text="I am sorry, I do not recognize the address. Please, provide it to me again.")
        return []

class ProcessConfirmationAction(Action):

    def name(self) -> Text:
        return "action_process_confirmation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        intent = tracker.latest_message['intent'].get('name')
        
        plant_entity = tracker.get_slot('selected_plant')
        quantity_entity = tracker.get_slot('selected_quantity')
        email_entity = tracker.get_slot('selected_email')
        address_entity = tracker.get_slot('selected_address')

        if intent == 'confirm_order':
            self.save_order_to_db(plant_entity, quantity_entity, email_entity, address_entity)
            message = (
                f"Thank you for confirming your order:\n"
                f"Plant: {plant_entity}\n"
                f"Quantity: {quantity_entity}\n"
                f"Email: {email_entity}\n"
                f"Address: {address_entity}\n"
                "Your order has been placed. A representative will contact you within the next 24 hours."
            )
        elif intent == 'reject_order':
            message = "Your order has been cancelled. If you have any questions, please contact us."
        else:
            message = "I am sorry, I did not understand your response. Please reply with 'yes' to confirm or 'no' to reject."

        dispatcher.utter_message(text=message)
        return []

    def save_order_to_db(self, plant: str, quantity: str, email: str, address: str):
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='',
                database='plant_bot'
            )
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO orders (plant_name, quantity, email, address)
                VALUES (%s, %s, %s, %s)
            ''', (plant, quantity, email, address))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

class LoginProblem(Action):

    def name(self) -> Text:
        return "action_login_problem"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

        email_entity = next(tracker.get_latest_entity_values('email'), None)

        if email_entity:
            try:
                self.save_data_db(email_entity)
                dispatcher.utter_message(text=f"Thank you. Your email {email_entity} has been recorded. We will get in touch with you shortly.")
            except Exception as e:
                dispatcher.utter_message(text="There was an error saving your email. Please try again later.")
                print(f"Error: {e}")
        else:
            dispatcher.utter_message(text="I am sorry to hear that you're having trouble logging in. Please provide your email address so we can assist you.")
        
        return []

    def save_data_db(self, email: str):
        print(f"Saving email: {email}")
        try:
            conn = mysql.connector.connect(
                host='127.0.0.1',
                port=3306,
                user='root',
                password='',
                database='plant_bot'
            )
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO employer_problems (email)
                VALUES (%s)
            ''', (email,))
            conn.commit()
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error: {err}")

# class ConfirmOrderAction(Action):

#     def name(self) -> Text:
#         return "action_confirm_order"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        
#         plant_entity = tracker.get_slot('selected_plant')
#         quantity_entity = tracker.get_slot('selected_quantity')
#         email_entity = tracker.get_slot('selected_email')
#         address_entity = tracker.get_slot('selected_address')

#         if not all([plant_entity, quantity_entity, email_entity, address_entity]):
#             dispatcher.utter_message(text="I am sorry, but some required information is missing. Please provide all necessary details.")
#             return [] 
        
#         self.save_order_to_db(plant_entity, quantity_entity, email_entity, address_entity)

#         message = (
#             f"You have selected the following:\n"
#             f"Plant: {plant_entity}\n"
#             f"Quantity: {quantity_entity}\n"
#             f"Email: {email_entity}\n"
#             f"Address: {address_entity}\n"
#             "Please confirm your order. Do you want to proceed with this order? Expect answer: I confirm or I reject"
#         )

#         dispatcher.utter_message(text=message)

#         return []

#     def save_order_to_db(self, plant: str, quantity: str, email: str, address: str):
#         try:
#             conn = mysql.connector.connect(
#                 host='127.0.0.1',
#                 port=3306,
#                 user='root',
#                 password='',
#                 database='plant_bot'
#             )
#             print("Connection successful")
#             cursor = conn.cursor()
#             cursor.execute('''
#                 INSERT INTO orders (plant_name, quantity, email, address)
#                 VALUES (%s, %s, %s, %s)
#             ''', (plant, quantity, email, address))
#             conn.commit()
#             cursor.close()
#             conn.close()
#         except mysql.connector.Error as err:
#             print(f"Error: {err}")

    
# class ConfirmOrderAction(Action):

#     def name(self) -> Text:
#         return "action_confirm_order"

#     def run(self, dispatcher: CollectingDispatcher,
#             tracker: Tracker,
#             domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:

#         plant_entity = tracker.get_slot('selected_plant')
#         quantity_entity = tracker.get_slot('selected_quantity')
#         email_entity = tracker.get_slot('selected_email')
#         address_entity = tracker.get_slot('selected_address')

#         if not all([plant_entity, quantity_entity, email_entity, address_entity]):
#             dispatcher.utter_message(text="I am sorry, but some required information is missing. Please provide all necessary details.")
#             return []

#         # samo mu pusti sta je do sada narucio
#         message = (
#             f"You have selected the following:\n"
#             f"Plant: {plant_entity}\n"
#             f"Quantity: {quantity_entity}\n"
#             f"Email: {email_entity}\n"
#             f"Address: {address_entity}\n"
#             "Do you want to confirm this order? Please reply with 'I confirm' to confirm or 'I reject' to cancel."
#         )

#         dispatcher.utter_message(text=message)
#         return []