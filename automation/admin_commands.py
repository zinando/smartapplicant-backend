from .models import WebhookEvent
import inspect

event: WebhookEvent = None  # Global variable to hold the event context
def get_business_info():
    # Placeholder for actual implementation
    if event:
        biz_info = event.tenant.business_details if event.tenant else {}
        if biz_info:
            info_str = "\n\n".join(f"{key}: {value}" for key, value in biz_info.items())
            return f"Business Information:\n{info_str}"
    return "Business info retrieved."

def command_map() -> dict:
    return {
        "get business info": get_business_info,
        # "send message to customer": send_message_to_customer,
        # "show product info": show_product_info,
        # "update product info": update_product_info,
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
    if func and len(inspect.getfullargspec(func).args) == 0:
        response = func()
    elif func:
        response = "We are processing your message."
    else:
        response = "Unknown command"
    return response