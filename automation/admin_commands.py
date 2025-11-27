from .models import WebhookEvent
import inspect
import re
import logging
from .helpers import save_cache, delete_cache, get_pending_requests

logger = logging.getLogger(__name__)

event: WebhookEvent = None  # Global variable to hold the event context

def __extract_business_info_from_message(text="") -> str:
        if not text:
            if event:
                text = event.message or ""
        # extract line with single hash (#)
        line = re.search(r'^#(.*)', text)
        if line:
            line_text = line.group(1).strip().lower()
            return line_text.replace(" ", "_").strip()
        return ""
        
def get_business_info():
    # Placeholder for actual implementation
    response = []
    if event:
        biz_info = event.tenant.business_details if event.tenant else {}
        if biz_info:
            info_str = "\n\n".join(f"{key}: {value}" for key, value in biz_info.items())
            
            response.append(f"Business Information:\n{info_str}")
            response.append("""
                            You can update business info using the 'update business info' command. Example:
                            \n'##update business info
                            \n#name
                            \n*New Name
                            \nNote:\n- Use double hash (##) to specify the command, single hash (#) to specify the info you want to update, and single asterisks (*) to indicate the new values.
                            \n- For simple business info (like name, address, description, ceo, use marketing), you can update multiple info with their corresponding new values in one command.
                            \n- For more complex business info (like admin contacts, faq, working hours, image data, services, products), you can update only one info at a time.
                            """)
            return response
    return "Business info retrieved."

def fetch_customers():
    # Placeholder for actual implementation
    if event and event.tenant:
        customers = event.tenant.customers or []
        if customers:
            customer_list = ", ".join(str(customer) for customer in customers)
            return f"Here is the lis of Customers for {event.tenant.name}:\n\n{customer_list}"
    return "No customers found."

def update_simple_business_info():
    """This is used to update simple business info such as:
    - name
    - address
    - description
    - ceo
    - use marketing

    E.g '##update business info
    #name
    *New Name

    #address
    *New Address'

    Logic:
    1. extract key-value pairs from the message
    2. check if the corresponding key exists and has a simple type (str, bool)
    3. update the business details with the new values if valid
    4. return error message for invalid fields
    """
    updated = []
    not_updated = []
    # Extract the business info from the event message
    if event and event.tenant:
        message_text = event.message or ""
        lines = [line for line in message_text.splitlines() if line.strip()]
        logger.info(f"Updating simple business info with lines: {lines}")
        biz_info = event.tenant.business_details or {}
        info_line = lines[1:]  # Skip the first line which is the command
        i = 0
        while i < len(info_line):
            line = info_line[i]
            if line.startswith("#"):
                biz_info_key = __extract_business_info_from_message(line)
                if biz_info_key in biz_info and isinstance(biz_info[biz_info_key], (str, bool)):
                    logger.info(f"Processing key: {biz_info_key}")
                    if i + 1 < len(lines[1:]) and lines[1:][i + 1].startswith("*"):
                        biz_info_value = lines[1:][i + 1].lstrip("*").strip()
                        # Convert to appropriate type
                        if biz_info_key == "use_marketing":
                            biz_info_value = biz_info_value.lower() in ["true", "1", "yes"]
                        biz_info[biz_info_key] = biz_info_value
                        updated.append(biz_info_key)
                        i += 2
                    else:
                        not_updated.append(biz_info_key)
                        i += 1
                else:
                    logger.info(f"Key {biz_info_key} not found or invalid type.")
                    not_updated.append(biz_info_key)
                    i += 1
            else:
                logger.info(f"Invalid line format: {line}")
                not_updated.append(line.strip())
                i += 1
        if updated:
            event.tenant.business_details = biz_info
            event.tenant.save()
            message = "Business info updated for: " + ", ".join(updated) if updated else ""
            if not_updated:
                message += "\nThese fields were not updated (missing value): " + ", ".join(not_updated)
            return message.strip()
        else:
            return "No valid business info fields found to update."
    return "Failed to update business info."

def update_complex_dict_type_business_info():
    """This is used to update complex dict type business info like admin contacts.
    E.g '##update business info
    #admin contacts

    *order=2348567890
    *support=234987654321
    *delivery=234722334455'
    """
    updated = []
    not_updated = []
    biz_info_value = {}
    if event and event.tenant:
        message_text = event.message or ""
        lines = [line for line in message_text.splitlines() if line.strip()]
        biz_info = event.tenant.business_details or {}
        if lines and len(lines) > 2:
            info_line = lines[1:]  # Skip the first line which is the command
            if info_line[0].startswith("#"):
                biz_info_key = __extract_business_info_from_message(info_line[0])
                if biz_info_key in biz_info and isinstance(biz_info[biz_info_key], dict):
                    for line in info_line[1:]:  # Skip the first line
                        if "=" in line and line.startswith("*"):
                            key, value = line.lstrip("*").split("=", 1)
                            biz_info_value[key.strip().lower()] = value.strip()
                            updated.append(key.strip().lower())
                        else:
                            not_updated.append(line.strip())
                else:
                    not_updated.append(biz_info_key)
            else:
                return "Invalid command format. Please ensure to specify the business info key with a single hash (#)."
        if biz_info_value:
            # you need to process admin contact list here if key is admin_contacts: remove old ones from cache and add new ones
            if biz_info_key == "admin_contacts":
                cache_key = f"{event.tenant.waba_phone_number_id}_admin_contacts"
                # remove old admin contacts from cache
                delete_cache(cache_key)
                # add new admin contacts to cache
                admin_contacts = [value for key, value in biz_info_value.items()]
                if admin_contacts:
                    save_cache(cache_key, list(set(admin_contacts)), timeout=None)
                    
            biz_info[biz_info_key] = biz_info_value
            event.tenant.business_details = biz_info
            event.tenant.save()
            message = "Business info updated for : " + ", ".join(updated) if updated else ""
            if not_updated:
                message += "\nThese fields were not updated (invalid format): " + ", ".join(not_updated)
            return message.strip() 

    return "Failed to update admin contacts."

def update_complex_list_dict_type_business_info():
    """This is used to update list of dict type business info like:
    - image data
    - faq
    - working hours
    E.g '##update business info
    #faq
    *question=What is your return policy?
    *answer=You can return any item within 30 days of purchase.
    *question=What are your working hours?
    *answer=Monday to Friday, 9am to 5pm.

    steps:
    1. extract the business info key from the command string
    2. check if the key exists in the business details
    3. parse the lines to extract key-value pairs
    4. check if key already exists and update it; else add new
    """
    updated = []
    not_updated = []
    if event and event.tenant:
        message_text = event.message or ""
        lines = [line for line in message_text.splitlines() if line.strip()]
        biz_info = event.tenant.business_details or {}
        info_lines = lines[1:]  # Skip the first line which is the command
        if info_lines and info_lines[0].startswith("#"):
            biz_info_key = __extract_business_info_from_message(info_lines[0])
            if biz_info_key in biz_info and isinstance(biz_info[biz_info_key], list):
                biz_info_value = biz_info.get(biz_info_key, [])
                keys_in_value = [i for x in biz_info_value if isinstance(x, dict) for i in x.keys()]
                current_dict = {}
                for line in info_lines[1:]:  # Skip the first line
                    if "=" in line and line.startswith("*"):
                        key, value = line.lstrip("*").split("=", 1)
                        if key in keys_in_value:
                            # update existing dict
                            for item in biz_info_value:
                                if key in item:
                                    item[key] = value.strip()
                                    updated.append(key.strip().lower())
                        else:
                            current_dict[key.strip().lower()] = value.strip()
                            updated.append(key.strip().lower())
                        # if current_dict has data, append it to biz_info_value
                        if current_dict:
                            biz_info_value.append(current_dict)
                            current_dict = {}
                    else:
                        not_updated.append(line.strip())
                if biz_info_value:
                    biz_info[biz_info_key] = biz_info_value
                    event.tenant.business_details = biz_info
                    event.tenant.save()
                    message = "Business info updated for : " + ", ".join(updated) if updated else ""
                    if not_updated:
                        message += "\nThese fields were not updated (invalid format): " + ", ".join(not_updated)
                    return message.strip()  
    return "Failed to update business info."

def update_complex_list_string_type_business_info():
    """This is used to update list string type business info like 
    - services
    - products
    - customers
    E.g '##update services
    *service one
    *service two
    *service three'
    """
    updated = []
    not_updated = []
    if event and event.tenant:
        message_text = event.message or ""
        lines = [line for line in message_text.splitlines() if line.strip()]
        biz_info = event.tenant.business_details or {}
        info_lines = lines[1:]  # Skip the first line which is the command
        if info_lines and info_lines[0].startswith("#"):
            biz_info_key = __extract_business_info_from_message(info_lines[0])
            if biz_info_key in biz_info and isinstance(biz_info[biz_info_key], list):
                biz_info_value = []
                for line in info_lines[1:]:  # Skip the first line
                    if line.startswith("*"):
                        value = line.lstrip("*").strip()
                        biz_info_value.append(value)
                        updated.append(value)
                    else:
                        not_updated.append(line.strip())
                if biz_info_value: 
                    biz_info[biz_info_key] = biz_info_value
                    event.tenant.business_details = biz_info
                    event.tenant.save()
                    message = "Business info updated for : " + ", ".join(updated) if updated else ""
                    if not_updated:
                        message += "\nThese fields were not updated (invalid format): " + ", ".join(not_updated)
                    return message.strip()
    return "Failed to update business info."

def add_new_simple_business_info(key: str, value):
    """This is used to add new simple business info such as:
    - name
    - address
    - description
    - ceo
    - use marketing

    E.g '##add new business info
    #name
    *New Name

    #address
    *New Address'

    Logic:
    1. extract key-value pairs from the message
    2. check if the corresponding key exists and has a simple type (str, bool)
    3. add the business details with the new values if valid
    4. return error message for invalid fields
    """
    if event and event.tenant:
        biz_info = event.tenant.business_details or {}
        if key not in biz_info:
            biz_info[key] = value
            event.tenant.business_details = biz_info
            event.tenant.save()
            return f"Business info added for: {key}"
        else:
            return f"Business info for {key} already exists. Use update command to modify it."
    return "Failed to add business info."

def add_new_dict_business_info(key: str, value: dict):
    """This is used to add new dict type business info such as:
    - admin contacts

    E.g '##add new business info
    #admin contacts

    *order=2348567890
    *support=234987654321
    *delivery=234722334455'

    Logic:
    1. extract key-value pairs from the message
    2. check if the corresponding key exists and has a dict type
    3. add the business details with the new values if valid
    4. return error message for invalid fields
    """
    if event and event.tenant:
        biz_info = event.tenant.business_details or {}
        if key not in biz_info:
            biz_info[key] = value
            event.tenant.business_details = biz_info
            event.tenant.save()
            return f"Business info added for: {key}"
        else:
            return f"Business info for {key} already exists. Use update command to modify it."
    return "Failed to add business info."

def add_new_list_string_business_info(key: str, value: list):
    """This is used to add new list of strings type business info such as:
    - services
    - products
    - customers

    E.g '##add new business info
    #services
    *service one
    *service two
    *service three'

    Logic:
    1. extract key-value pairs from the message
    2. check if the corresponding key exists and has a list of strings type
    3. add the business details with the new values if valid
    4. return error message for invalid fields
    """
    if event and event.tenant:
        biz_info = event.tenant.business_details or {}
        if key not in biz_info:
            biz_info[key] = value
            event.tenant.business_details = biz_info
            event.tenant.save()
            return f"Business info added for: {key}"
        else:
            return f"Business info for {key} already exists. Use update command to modify it."
    return "Failed to add business info."

def add_new_list_dict_business_info(key: str, value: list):
    """This is used to add new list of dicts type business info such as:
    - faq
    - image data

    E.g '##add new business info
    #faq
    *question=What is your return policy?
    *answer=You can return any item within 30 days of purchase.
    *question=What are your working hours?
    *answer=Monday to Friday, 9am to 5pm.'

    Logic:
    1. extract key-value pairs from the message
    2. check if the corresponding key exists and has a list of dicts type
    3. add the business details with the new values if valid
    4. return error message for invalid fields
    """
    # check that value is a list of dicts
    if not all(isinstance(item, dict) for item in value):
        return "Invalid value type. Expected a list of dictionaries."
    
    if event and event.tenant:
        biz_info = event.tenant.business_details or {}
        if key not in biz_info:
            biz_info[key] = value
            event.tenant.business_details = biz_info
            event.tenant.save()
            return f"Business info added for: {key}"
        else:
            return f"Business info for {key} already exists. Use update command to modify it."
    return "Failed to add business info."

def add_new_business_info():
    """This is used to add new business info.
    Logic:
    1. extract the business info key from the command string
    2. check if it exists in the business info
       i. if it exists, return an error message
       ii. if it does not exist, got to step 3
    3. determine its value type by checking the patter of texts after the command line. Must have keys prefixed with hash and values prefixed with asterisks.
        i. if each key is followed by one value which does not have = sign, it is a simple type (str, bool)
        ii. if each key is followed by multiple values which do not have = sign, it is a list of strings
        iii. if each key is followed by multiple key-value pairs with = sign, it is a list of dicts
        iv. if each key is followed by single key-value pairs with = sign, it is a dict
    4. call the appropriate add function based on the determined type
    """
    if event and event.tenant:
        biz_info = event.tenant.business_details or {}
        lines = [line for line in (event.message or "").splitlines() if line.strip()]
        info_line = lines[1:]  # Skip the first line which is the command
        if info_line and len(info_line) > 1:
            new_item = {}
            for line in info_line:
                if line.startswith("#") and not new_item:
                    biz_info_key = __extract_business_info_from_message(line)
                    if biz_info_key not in biz_info:
                        # determine type by checking next lines
                        next_lines = info_line[1:]
    return "we are still working on this feature"

def update_business_info():
    """This is used to select the business info update function to use based on the command string
    command string.
    Logic:
    1. extract the business info key from the command string
    2. check if it exists in the business info
       i. if it exists, check its type and call the appropriate update function
       ii. if it does not exist, return an error message
    """
    
    if event and event.tenant:
        lines = [line for line in (event.message or "").splitlines() if line.strip()]
        info_line = lines[1:]  # Skip the first line which is the command
        if info_line and info_line[0].startswith("#"):
            biz_info_key = __extract_business_info_from_message(info_line[0])
            biz_info = event.tenant.business_details or {}
            if biz_info_key in biz_info:
                biz_info_value = biz_info[biz_info_key]
                if isinstance(biz_info_value, dict):
                    return update_complex_dict_type_business_info()
                elif isinstance(biz_info_value, list):
                    # check if list of dicts or list of strings
                    if all(isinstance(item, dict) for item in biz_info_value):
                        return update_complex_list_dict_type_business_info()
                    elif all(isinstance(item, str) for item in biz_info_value):
                        return update_complex_list_string_type_business_info()
                else:
                    return update_simple_business_info()
            else:
                return f"No existing {biz_info_key} found to update. Use double hash (##) to specify the command, single hash (#) to specify what you want to update, and single akstericks to indicate the new values. E.g '\n##update business info \n#name \n*New Name \n#address \n*New Address' etc"
    return "Failed to update business info."

def fetch_pending_requests():
    """This fetches all pending requests associated with the admin contact"""
    if event and event.tenant:
        request_key = f"{event.tenant.waba_phone_number_id}_{event.sender_id}_pending_requests"
        pending_requests = get_pending_requests(request_key) or []
        result = ""
        if pending_requests:
            for p in pending_requests:
                result += f"{p.get('customer_id')} : {p.get('request')}\n"
        else: 
            result = "No pending requests at this time. Enjoy!"
        return result
    return "Failed to fetch pending requests."


def command_map() -> dict:
    return {
        "get business info": get_business_info,
        "update business info": update_business_info,
        "get customers": fetch_customers,
        "add new business info": add_new_business_info,
        "get pending requests": fetch_pending_requests,
        # "add new product": add_new_product,
        # "get product list": get_product_list,
    }

def process_admin_command(command: str, eventt: WebhookEvent, *args, **kwargs) -> str:
    """
    Process admin commands prefixed with '##'
    Example commands:
    ##update business info
    ##send message to customer
    ##show product info
    ##update product info
    ##add new product
    ##get product list
    """
    global event
    event = eventt  # Assign the event to the global variable
    command_mapp = command_map()
    func = command_mapp.get(command.lower().strip())
    # logger.info(f"Processing admin command: {command}")
    if func and len(inspect.getfullargspec(func).args) == 0:
        response = func()
    elif func:
        response = "We are processing your message."
    else:
        response = ["Unknown command", f"Available commands are:\n{'; '.join(command_mapp.keys())}"]
    return response