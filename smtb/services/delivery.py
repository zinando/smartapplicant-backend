from smtb.models import SMTBDeliveryCharges, DeliveryType
from django.conf import settings
from api.models import Country, State
import re

def normalize_name(name):
    """
    Normalize a location-like string for comparison:
    - cast to str, strip whitespace
    - lowercase
    - collapse spaces, underscores, and hyphens into a single canonical separator
    """
    name = str(name).strip().lower()
    # treat space, underscore, hyphen as equivalent separators
    name = re.sub(r"[\s_-]+", "_", name)
    return name


def determine_delivery_type(country_id, state_id=None):
    country = Country.objects.filter(
        id=country_id,
        is_active=True
    ).first()

    if not country:
        raise ValueError("Invalid country.")

    if country.country_code != settings.SMTB_HOME_COUNTRY_CODE:
        return DeliveryType.INTERNATIONAL

    if not state_id:
        raise ValueError("State is required for domestic delivery.")

    state = State.objects.filter(
        id=state_id,
        country=country,
        is_active=True
    ).first()

    if not state:
        raise ValueError("Invalid state for the selected country.")

    home_state = State.objects.filter(
        country__country_code=settings.SMTB_HOME_COUNTRY_CODE,
        name__iexact=settings.SMTB_HOME_STATE_NAME,
        is_active=True
    ).first()

    if not home_state:
        raise ValueError("SMTB home state is not configured.")

    if state.id == home_state.id:
        return DeliveryType.INTRASTATE

    return DeliveryType.INTERSTATE

def get_delivery_charge(
    delivery_type,
    country_code,
    state=None,
    city=None,
    location=None
):
    charges = SMTBDeliveryCharges.objects.filter(
        type=delivery_type,
        country=country_code
    )

    if delivery_type == DeliveryType.INTRASTATE:
        charges = charges.filter(state__iexact=state)
        print(charges.first().state)

        search_names = [location, city]

    elif delivery_type == DeliveryType.INTERSTATE:
        search_names = [state]

    elif delivery_type == DeliveryType.INTERNATIONAL:
        # For international, country is the destination country code.
        charges = SMTBDeliveryCharges.objects.filter(
            type=delivery_type
        )
        search_names = [country_code]

    else:
        raise ValueError("Invalid delivery type.")

    search_names = {
        normalize_name(name)
        for name in search_names
        if name
    }

    if not charges.exists():
        return None

    for charge in charges:
        locations = {
            normalize_name(name)
            for name in charge.location_names
            if name
        }
        print(f"matched locations: {locations} vs search_names: {search_names}")

        if search_names & locations:
            return charge.fee

    return None