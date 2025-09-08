from datetime import datetime, date
from typing import Literal

Season = Literal["Vinter", "Vår", "Sommer", "Høst"]

def get_current_season(location: str = "Norway") -> Season:
    """
    Determine the current season based on astronomical definitions.
    
    For Norway (and northern hemisphere), seasons are defined as:
    - Vår (Spring): From spring equinox to summer solstice (Mar 20/21 - Jun 20/22)
    - Sommer (Summer): From summer solstice to autumn equinox (Jun 20/22 - Sep 22/23)
    - Høst (Autumn): From autumn equinox to winter solstice (Sep 22/23 - Dec 21/22)
    - Vinter (Winter): From winter solstice to spring equinox (Dec 21/22 - Mar 20/21)
    
    Args:
        location: Location for seasonal calculation. Currently only supports "Norway".
    
    Returns:
        Season name in Norwegian
    """
    if location.lower() != "norway":
        raise NotImplementedError("Currently only supports Norway location")
    
    today = date.today()
    year = today.year
    month = today.month
    day = today.day
    
    # Approximate dates for Norwegian seasons (northern hemisphere)
    # Spring equinox: March 20/21
    # Summer solstice: June 20/21/22  
    # Autumn equinox: September 22/23
    # Winter solstice: December 21/22
    
    # Spring (Vår): March 20/21 to June 20/21
    if (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
        return "Vår"
    
    # Summer (Sommer): June 21/22 to September 22/23
    elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 22):
        return "Sommer"
    
    # Autumn (Høst): September 22/23 to December 21/22
    elif (month == 9 and day >= 22) or month in [10, 11] or (month == 12 and day < 21):
        return "Høst"
    
    # Winter (Vinter): December 21/22 to March 19/20
    else:
        return "Vinter"


def get_season_for_date(target_date: date, location: str = "Norway") -> Season:
    """
    Determine the season for a specific date.
    
    Args:
        target_date: The date to check
        location: Location for seasonal calculation. Currently only supports "Norway".
    
    Returns:
        Season name in Norwegian
    """
    if location.lower() != "norway":
        raise NotImplementedError("Currently only supports Norway location")
    
    month = target_date.month
    day = target_date.day
    
    # Spring (Vår): March 20/21 to June 20/21
    if (month == 3 and day >= 20) or month in [4, 5] or (month == 6 and day < 21):
        return "Vår"
    
    # Summer (Sommer): June 21/22 to September 22/23
    elif (month == 6 and day >= 21) or month in [7, 8] or (month == 9 and day < 22):
        return "Sommer"
    
    # Autumn (Høst): September 22/23 to December 21/22
    elif (month == 9 and day >= 22) or month in [10, 11] or (month == 12 and day < 21):
        return "Høst"
    
    # Winter (Vinter): December 21/22 to March 19/20
    else:
        return "Vinter"