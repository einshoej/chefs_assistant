"""
Fun cooking-themed spinner messages for loading screens
Similar to SimCity's entertaining loading messages
"""

import random

SPINNER_MESSAGES = [
    # Kitchen Prep & Equipment
    "Sharpening the knives...",
    "Preheating the oven...",
    "Calibrating taste sensors...",
    "Warming up the spatula...",
    "Polishing the pots...",
    "Tuning the kitchen timer...",
    "Oiling the pan...",
    "Testing the smoke alarm...",
    "Arranging the spice rack...",
    "Cleaning the cutting board...",
    "Untangling the whisk...",
    "Charging the flavor batteries...",
    "Defrosting the freezer...",
    "Adjusting the heat...",
    "Lubricating the can opener...",
    "Sterilizing the spoons...",
    "Checking oven temperature...",
    "Aligning the measuring cups...",
    "Sanitizing the surfaces...",
    "Activating kitchen mode...",
    
    # Ingredient Humor
    "Convincing onions not to cry...",
    "Teaching pasta to swim...",
    "Waking up the yeast...",
    "Negotiating with vegetables...",
    "Interviewing tomatoes...",
    "Motivating the dough to rise...",
    "Calming the boiling water...",
    "Encouraging eggs to cooperate...",
    "Sweet-talking the sugar...",
    "Reasoning with rice...",
    "Befriending the butter...",
    "Consulting with carrots...",
    "Persuading peppers to behave...",
    "Taming wild mushrooms...",
    "Domesticating free-range herbs...",
    "Counseling confused corn...",
    "Educating the eggplant...",
    "Training the turnips...",
    "Disciplining the dill...",
    "Organizing the oregano...",
    
    # Chef Actions
    "Putting on chef's hat...",
    "Tasting for science...",
    "Practicing knife skills...",
    "Perfecting the flip...",
    "Channeling inner chef...",
    "Summoning culinary spirits...",
    "Consulting the food gods...",
    "Reading tea leaves...",
    "Meditating on flavors...",
    "Achieving kitchen zen...",
    "Embracing the chaos...",
    "Finding inner peace...",
    "Becoming one with spatula...",
    "Entering the flavor zone...",
    "Activating chef mode...",
    "Downloading recipe data...",
    "Uploading taste preferences...",
    "Synchronizing with stove...",
    "Establishing kitchen dominance...",
    "Asserting culinary authority...",
    
    # Kitchen Mishaps & Humor
    "Cleaning flour explosion...",
    "Rescuing burnt toast...",
    "Apologizing to smoke detector...",
    "Hiding kitchen disasters...",
    "Denying any explosions...",
    "Blaming the cat...",
    "Pretending nothing happened...",
    "Sweeping under the rug...",
    "Opening all windows...",
    "Calling fire department...",
    "Ordering pizza backup...",
    "Googling 'how to cook'...",
    "Watching cooking tutorials...",
    "Taking cooking notes...",
    "Learning from mistakes...",
    "Trying again...",
    "Third time's the charm...",
    "Improvising wildly...",
    "Making it up...",
    "Winging it professionally...",
    
    # Food Puns & Wordplay
    "Whisking you well...",
    "Lettuce begin...",
    "Having a grate time...",
    "Feeling souper...",
    "Living on the wedge...",
    "Raisin the bar...",
    "Going against the grain...",
    "Spicing things up...",
    "Stirring up trouble...",
    "Beating expectations...",
    "Mixing it up...",
    "Rolling with it...",
    "Keeping it fresh...",
    "Serving looks...",
    "Plating perfection...",
    "Dishing out goodness...",
    "Cooking up storms...",
    "Baking miracles...",
    "Grilling and chilling...",
    "Simmering down...",
    
    # Recipe & Cooking Process
    "Decoding grandma's handwriting...",
    "Translating recipe ancient texts...",
    "Converting to metric...",
    "Calculating portions...",
    "Adjusting for altitude...",
    "Factoring in hunger level...",
    "Allowing flavors to mingle...",
    "Marinating in creativity...",
    "Reducing complexity...",
    "Infusing with love...",
    "Seasoning to perfection...",
    "Balancing the flavors...",
    "Harmonizing ingredients...",
    "Orchestrating the meal...",
    "Composing flavor symphony...",
    "Conducting kitchen orchestra...",
    "Fine-tuning the recipe...",
    "Optimizing taste parameters...",
    "Maximizing deliciousness...",
    "Achieving peak flavor...",
    
    # More Kitchen Fun
    "Bribing the timer...",
    "Hypnotizing the herbs...",
    "Convincing salt to behave...",
    "Teaching garlic manners...",
    "Training the thermometer...",
    "Negotiating with noodles...",
    "Disciplining the dishwasher...",
    "Exercising the egg beater...",
    "Massaging the meat...",
    "Serenading the soufflé...",
    "Tickling the taste buds...",
    "Romancing the rosemary...",
    "Dancing with the dumplings...",
    "Wrestling with wraps...",
    "Juggling jalapeños...",
    "Balancing the batter...",
    "Flirting with flavors...",
    "Courting the cucumber...",
    "Wooing the wok...",
    "Charming the cheese...",
    
    # Professional Chef Mode
    "Assuming chef position...",
    "Engaging taste protocol...",
    "Initializing flavor matrix...",
    "Loading culinary database...",
    "Scanning ingredient inventory...",
    "Calculating taste ratios...",
    "Analyzing flavor profiles...",
    "Processing recipe algorithms...",
    "Compiling cooking instructions...",
    "Executing kitchen commands...",
    "Running taste tests...",
    "Validating recipe integrity...",
    "Optimizing cook times...",
    "Buffering deliciousness...",
    "Streaming flavor data...",
    "Caching taste memories...",
    "Debugging burnt offerings...",
    "Patching recipe errors...",
    "Updating spice versions...",
    "Backing up dinner plans..."
]


def get_random_spinner_message():
    """
    Return a random cooking-themed spinner message
    
    Returns:
        str: A fun cooking-themed loading message
    """
    return random.choice(SPINNER_MESSAGES)


def get_spinner_message_count():
    """
    Return the total number of available spinner messages
    
    Returns:
        int: Number of available messages
    """
    return len(SPINNER_MESSAGES)