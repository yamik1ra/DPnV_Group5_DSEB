"""
decode.py
--------------------------------
Module to decode FBI Hate Crime BH + IR fields using inline dictionaries.

Usage:
    from src.decode import decode_all
    df_bh_dec, df_ir_dec = decode_all(df_bh, df_ir)
"""
import pandas as pd

# ----------------------------------------------------
# DICTIONARIES FOR DECODING
# ----------------------------------------------------
# State Codes
STATE_CODES = {
    '50': ('AK', 'Alaska'), '01': ('AL', 'Alabama'), '54': ('AS', 'American Samoa'),
    '02': ('AZ', 'Arizona'), '03': ('AR', 'Arkansas'), '04': ('CA', 'California'),
    '52': ('CZ', 'Canal Zone'), '05': ('CO', 'Colorado'), '06': ('CT', 'Connecticut'),
    '08': ('DC', 'District of Columbia'), '07': ('DE', 'Delaware'), '09': ('FL', 'Florida'),
    '10': ('GA', 'Georgia'), '55': ('GM', 'Guam'), '51': ('HI', 'Hawaii'),
    '14': ('IA', 'Iowa'), '11': ('ID', 'Idaho'), '12': ('IL', 'Illinois'),
    '13': ('IN', 'Indiana'), '15': ('KS', 'Kansas'), '16': ('KY', 'Kentucky'),
    '17': ('LA', 'Louisiana'), '20': ('MA', 'Massachusetts'), '19': ('MD', 'Maryland'),
    '18': ('ME', 'Maine'), '21': ('MI', 'Michigan'), '22': ('MN', 'Minnesota'),
    '24': ('MO', 'Missouri'), '23': ('MS', 'Mississippi'), '25': ('MT', 'Montana'),
    '26': ('NB', 'Nebraska'), '32': ('NC', 'North Carolina'), '33': ('ND', 'North Dakota'),
    '28': ('NH', 'New Hampshire'), '29': ('NJ', 'New Jersey'), '30': ('NM', 'New Mexico'),
    '27': ('NV', 'Nevada'), '31': ('NY', 'New York'), '34': ('OH', 'Ohio'),
    '35': ('OK', 'Oklahoma'), '36': ('OR', 'Oregon'), '37': ('PA', 'Pennsylvania'),
    '53': ('PR', 'Puerto Rico'), '38': ('RI', 'Rhode Island'), '39': ('SC', 'South Carolina'),
    '40': ('SD', 'South Dakota'), '41': ('TN', 'Tennessee'), '42': ('TX', 'Texas'),
    '43': ('UT', 'Utah'), '62': ('VI', 'Virgin Islands'), '45': ('VA', 'Virginia'),
    '44': ('VT', 'Vermont'), '46': ('WA', 'Washington'), '48': ('WI', 'Wisconsin'),
    '47': ('WV', 'West Virginia'), '49': ('WY', 'Wyoming')
}

# Geographic Divisions & Regions
COUNTRY_DIVISIONS = {
    '0': ('Possessions', ['54', '52', '55', '53', '62']),
    # Region 1 - NORTH EAST
    '1': ('New England', ['06', '18', '20', '28', '38', '44']),
    '2':( 'Middle Atlantic', ['29', '31', '37']),
    # Region 2 - NORTH CENTRAL
    '3': ('East North Central', ['12', '13', '21', '34', '48']),
    '4': ('West North Central', ['14', '15', '22', '24', '26', '33', '40']),
    # Region 3 - SOUTH
    '5': ('South Atlantic', ['07', '08', '09', '10', '19', '32']),
    '6': ('East South Central', ['01', '16', '23', '41']),
    '7': ('West South Central', ['03', '17', '35', '42']),
    # Region 4 - WEST
    '8': ('Mountain', ['02', '05', '11', '25', '27', '30', '43', '49']),
    '9': ('Pacific', ['50', '04', '51', '36', '46'])
}
COUNTRY_REGIONS = {
    '0': 'Possessions', '1': 'Northeast', '2': 'North Central', 
    '3': 'South', '4': 'West'
}
JUDICIAL_REGION = {
    'N': 'Northern',
    'S': 'Southern',
    'E': 'Eastern',
    'W': 'Western',
    'M': 'Middle',
    'C': 'Central',
    'A': 'All of the state'
}

# Agency Types & Population Groups
AGENCY_INDICATORS = {
    '1': 'City', '2': 'County', '3': 'University of Colleges',
    '4': 'State Police', '5': 'Local Police', # e.g. airport police, railroad police, hospital marshals, etc.
    '6': 'State Agency Enforcement Unit',
    '7': 'Tribal / BIA Agencies', # Tribal police or Bureau of Indian Affairs Police
    '8': "Federal Agency"
}
POPULATION_GROUPS = {
    '0': 'Possessions', '1A': 'Cities 1,000,000+', '1B': 'Cities 500,000-999,999',
    '1C': 'Cities 250,000-499,999', '2': 'Cities 100,000-249,999',
    '3': 'Cities 50,000-99,999', '4': 'Cities 25,000-49,999',
    '5': 'Cities 10,000-24,999', '6': 'Cities 2,500-9,999', '7': 'Cities <2,500',
    '8A': 'Non-MSA Counties 100,000+', '8B': 'Non-MSA Counties 25,000-99,999',
    '8C': 'Non-MSA Counties 10,000-24,999', '8D': 'Non-MSA Counties <10,000',
    '8E': 'Non-MSA State Police', '9A': 'MSA Counties 100,000+',
    '9B': 'MSA Counties 25,000-99,999', '9C': 'MSA Counties 10,000-24,999',
    '9D': 'MSA Counties <10,000', '9E': 'MSA State Police'
}

# UCR Offense Codes
UCR_OFFENSE_CODES = {
    '200': 'Arson',
    # Assault
    '13A': 'Aggravated Assault', '13B': 'Simple Assault', '13C': 'Intimidation',
    '510': 'Bribery',
    '220': 'Burglary/Breaking and Entering',
    '250': 'Counterfeiting/Forgery',
    '290': 'Destruction/Damage/Vandalism of Property',
    '35A': 'Drug/Narcotic Violations', '35B': 'Drug Equipment Violations',
    '270': 'Embezzlement', '210': 'Extortion/Blackmail',
    # Fraud Offenses
    '26A': 'False Pretenses/Swindle/Confidence Game',
    '26B': 'Credit Card/Automatic Teller Machine Fraud', '26C': 'Impersonation',
    '26D': 'Welfare Fraud', '26E': 'Wire Fraud', 
    '26F': 'Identity Theft','26G': 'Hacking/Computer Invasion',
    # Gambling Offenses
    '39A': 'Betting/Wagering', '39B': 'Operating/Promoting/Assisting Gambling',
    '39C': 'Gambling Equipment Violations', '39D': 'Sports Tampering',
    # Homicide
    '09A': 'Murder/Non-negligent Manslaughter', '09B': 'Negligent Manslaughter',
    '09C': 'Justifiable Homicide', # Not a Crime
    # Human Trafficking
    '64A': 'Human Trafficking, Commercial Sex Acts',
    '64B': 'Human Trafficking, Involuntary Servitude',
    '100': 'Kidnapping/Abduction',
    # Larceny/Theft
    '23A': 'Pocket-picking', '23B': 'Purse-snatching', '23C': 'Shoplifting',
    '23D': 'Theft from Building',  '23E': 'Theft from Coin-Operated Machine or Device',
    '23F': 'Theft from Motor Vehicle', '23G': 'Theft of Motor Vehicle Parts/Accessories',
    '23H': 'Other Larceny',
    '240': 'Motor Vehicle Theft',
    '370': 'Pornography/Obscene Material',
    # Prostitution Offenses
    '40A': 'Prostitution', '40B': 'Assisting or Promoting Prostitution', 
    '40C': 'Purchasing Prostitution',
    '120': 'Robbery',
    # Sex Offenses - Forcible
    '11A': 'Rape', '11B': 'Sodomy', '11C': 'Sexual Assault With An Object',
    '11D': 'Fondling (Indecent Liberties/Child Molestation)',
    # Sex Offenses - Non-forcible
    '36A': 'Incest', '36B': 'Statutory Rape',
    '280': 'Stolen Property Offenses (Receiving, Selling, Etc.)',
    '520': 'Weapon Law Violations',
    '720': 'Animal Cruelty'
}

# Bias Motivation Codes
BIAS_MOTIVATION_CODES = {
    # Race/Ethnicity
    '11': 'Anti-White', '12': 'Anti-Black or African American',
    '13': 'Anti-American Indian/Alaska Native', '14': 'Anti-Asian',
    '15': 'Anti-Multiple Races, Group', '16': 'Anti-Native Hawaiian/Pacific Islander',
    '31': 'Anti-Arab', '32': 'Anti-Hispanic or Latino',
    '33': 'Anti-Other Race/Ethnicity/Ancestry',
    # Religion
    '21': 'Anti-Jewish', '22': 'Anti-Catholic', '23': 'Anti-Protestant',
    '24': 'Anti-Islamic (Muslim)', '25': 'Anti-Other Religion',
    '26': 'Anti-Multiple Religions, Group', '27': 'Anti-Atheism/Agnosticism',
    '28': 'Anti-Church of Jesus Christ (LDS)', '29': "Anti-Jehovah's Witness",
    '81': 'Anti-Eastern Orthodox', '82': 'Anti-Other Christian',
    '83': 'Anti-Buddhist', '84': 'Anti-Hindu', '85': 'Anti-Sikh',
    # Sexual Orientation
    '41': 'Anti-Gay (Male)', '42': 'Anti-Lesbian',
    '43': 'Anti-LGBTQ+ (Mixed Group)', '44': 'Anti-Heterosexual',
    '45': 'Anti-Bisexual',
    # Disability
    '51': 'Anti-Physical Disability', '52': 'Anti-Mental Disability',
    # Gender & Gender Identity
    '61': 'Anti-Male', '62': 'Anti-Female',
    '71': 'Anti-Transgender', '72': 'Anti-Gender Non-Conforming'
}
BIAS_CATEGORIES = {
    'Race/Ethnicity': ['11', '12', '13', '14', '15', '16', '31', '32', '33'],
    'Religion': ['21', '22', '23', '24', '25', '26', '27', '28', '29', 
                 '81', '82', '83', '84', '85'],
    'Sexual Orientation': ['41', '42', '43', '44', '45'],
    'Disability': ['51', '52'],
    'Gender': ['61', '62'],
    'Gender Identity': ['71', '72']
}

# Location Codes
LOCATION_CODES = {
    '01': "Air/Bus/Train Terminal", '02': 'Bank/Savings and Loan',
    '03': 'Bar/Nightclub', '04': 'Church/Synagogue/Temple',
    '05': 'Commercial/Office Building', '06': 'Construction Site',
    '07': 'Convenience Store', '08': 'Department/Discount Store',
    '09': "Drug Store/Dr.'s Office/Hospital", '10': 'Field/Woods',
    '11': 'Government/Public Building', '12': 'Grocery/Supermarket',
    '13': 'Highway/Road/Alley', '14': 'Hotel/Motel/Etc.',
    '15': 'Jail/Prison', '16': 'Lake/Waterway', '17': 'Liquor Store',
    '18': 'Parking Lot/Garage', '19': 'Rental Storage Facility',
    '20': 'Residence/Home', '21': 'Restaurant', '22': 'School/College',
    '23': 'Service/Gas Station', '24': 'Specialty Store (TV, Fur, Etc.)',
    '25': 'Other/Unknown', '37': 'Abandoned/Condemned Structure',
    '38': 'Amusement Park', '39': 'Arena/Stadium/Fairgrounds/Coliseum',
    '40': 'ATM Separate from Bank', '41': 'Auto Dealership New/Used',
    '42': 'Camp/Campground', '44': 'Daycare Facility',
    '45': 'Dock/Wharf/Freight/Modal Terminal', '46': 'Farm Facility',
    '47': 'Gambling Facility/Casino', '48': 'Industrial Site',
    '49': 'Military Installation', '50': 'Park/Playground',
    '51': 'Rest Area', '52': 'School - College/University',
    '53': 'School - Elementary/Secondary', '54': 'Shelter - Mission/Homeless',
    '55': 'Shopping Mall', '56': 'Tribal Lands', '57': 'Community Center',
    '58': 'Cyberspace'
}

# Victim & Offender Characteristics
VICTIM_TYPES = {
    'I': 'Individual', 'B': 'Business', 'F': 'Financial Institution',
    'G': 'Government', 'R': 'Religious Organization', 'S': 'Society/Public',
    'O': 'Other', 'U': 'Unknown'
}
OFFENDER_RACE_CODES = {
    'W': 'White', 'B': 'Black or African American',
    'I': 'American Indian/Alaska Native', 'A': 'Asian',
    'M': 'Group of Multiple Races', 'P': 'Native Hawaiian/Other Pacific Islander',
    'U': 'Unknown'
}
OFFENDER_ETHNICITY_CODES = {
    'H': 'Hispanic or Latino', 'N': 'Not Hispanic or Latino', 'M': 'Multiple Ethnicities', 'U': 'Unknown'
}

# Administrative Codes
DATA_SOURCE_CODES = {
    'D': 'Data entry form', 'F': 'Floppy diskette/Internet e-mail',
    'N': 'NIBRS Incident'
}
ACTIVITY_CODES = {
    'Z': 'Zero-Report (no incident)',
    'I': 'Incident Report submitted',
    '': 'No information submitted'
}
# ----------------------------------------------------
# HELPER FUNCTIONS
# ----------------------------------------------------
def decode_bh(df):
    """Decode all coded fields to human-readable text in Batch Header DataFrame."""
    df = df.copy()
    
    # Decode state
    df['state_name'] = df['state_code'].map(
        lambda x: STATE_CODES.get(x, ('Unknown', 'Unknown'))[1]
    )
    
    # Decode geography
    df['country_region'] = df['country_region'].map(COUNTRY_REGIONS)
    df['country_division'] = df['country_division'].map(
        lambda x: COUNTRY_DIVISIONS.get(x, ('Unknown', []))[0]
    )
    df['judicial_district'] = df['judicial_district'].map(JUDICIAL_REGION)
    
    # Decode agency
    df['agency_indicator'] = df['agency_indicator'].map(AGENCY_INDICATORS)
    df['population_group'] = df['population_group'].map(POPULATION_GROUPS)
    
    # Flags
    df['core_city'] = df['core_city'].map({'Y': True, 'N': False})
    df['nibrs_flag'] = df['nibrs_flag'].map({'A': True, ' ': False, '': False})
    
    for i in range(1,5):
        df[f'state_q{i}_activity'] = df[f'state_q{i}_activity'].map(ACTIVITY_CODES)
        df[f'federal_q{i}_activity'] = df[f'federal_q{i}_activity'].map(ACTIVITY_CODES)
    
    # Rename columns for clarity
    df.rename(columns={'agency_indicator': 'agency_type', 
                       'core_city': 'is_core_city',
                       'nibrs_flag': 'is_nibrs_active'}, inplace=True)
    return df

def decode_offense_flexible(code):
    """Decode UCR offense code with flexible pattern matching."""
    if pd.isna(code) or code == '':
        return 'Unknown'
    if code in UCR_OFFENSE_CODES:
        return UCR_OFFENSE_CODES[code]
    elif str(code).startswith('23') and len(str(code)) == 3:
        return 'All Other Larceny (23H)'
    else:
        return None

def get_bias_category(bias_code):
    """Return bias category for a given code."""
    for category, codes in BIAS_CATEGORIES.items():
        if bias_code in codes:
            return category
    return None

def decode_ir(df):
    """Decode all coded fields to human-readable text in Incident Report DataFrame."""
    df = df.copy()
    
    # Decode state
    df['state_name'] = df['state_code'].map(
        lambda x: STATE_CODES.get(x, ('Unknown', 'Unknown'))[1]
    )
    
    # Decode administrative fields
    df['data_source'] = df['data_source'].map(DATA_SOURCE_CODES).fillna('Unknown')
    
    # Decode offender characteristics
    df['offender_race'] = df['offender_race'].map(OFFENDER_RACE_CODES).fillna('Unknown')
    df['offender_ethnicity'] = df['offender_ethnicity'].map(OFFENDER_ETHNICITY_CODES).fillna('Unknown')
    
    # Decode ten-offense group information
    for i in range(1, 11):
        # Decode offense_code (with flexible pattern matching)
        df[f'ucr_offense_code_{i}'] = df[f'ucr_offense_code_{i}'].apply(decode_offense_flexible)

        df[f'location_code_{i}'] = df[f'location_code_{i}'].map(LOCATION_CODES)
        # Rename coilumn for clarity
        df.rename(columns={f'location_code_{i}': f'location_{i}',
                           f'ucr_offense_code_{i}': f'offense_{i}_cat'}, inplace=True)

        for x in ['a', 'b', 'c', 'd', 'e']:
            df[f'bias_{i}{x}_category'] = df[f'bias_motivation_{i}{x}'].apply(get_bias_category)
            df[f'bias_motivation_{i}{x}'] = df[f'bias_motivation_{i}{x}'].map(BIAS_MOTIVATION_CODES)
        
        # Decode victim types
        df[f'victim_types_{i}'] = df[f'victim_types_{i}'].map(VICTIM_TYPES)
    
    return df

def decode_all(df_bh, df_ir):
    '''Decode both BH and IR in one call.'''
    df_bh_decoded = decode_bh(df_bh.copy())
    df_ir_decoded = decode_ir(df_ir.copy())
    return df_bh_decoded, df_ir_decoded

if __name__ == "__main__":
    print("This module decodes FBI Hate Crime BH and IR records. \nImport and use the decode_all function.")