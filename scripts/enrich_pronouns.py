import os
import sqlite3

# Define the pronouns and their meanings
PRONOUNS = {
    # First Person Singular
    "मी": ["I", "me", "by me"],
    "मला": ["to me", "for me"],
    "माझ्याकडून": ["by me", "from my side"],
    "माझ्याच्याने": ["by me (ability)"],
    "म्या": ["by me (archaic)"],
    "माझ्याशी": ["with me"],
    "माझ्याहून": ["from me", "than me"],
    "माझ्यापेक्षा": ["than me"],
    "माझा": ["my", "mine (masculine)"],
    "माझी": ["my", "mine (feminine)"],
    "माझे": ["my", "mine (neuter/plural)"],
    "माझ्यात": ["in me"],
    
    # First Person Plural
    "आम्ही": ["we", "us", "by us"],
    "आम्हाला": ["to us", "for us"],
    "आमच्याकडून": ["by us", "from our side"],
    "आमच्याच्याने": ["by us (ability)"],
    "आमच्याशी": ["with us"],
    "आमच्याहून": ["from us", "than us"],
    "आमच्यापेक्षा": ["than us"],
    "आमचा": ["our", "ours (masculine)"],
    "आमची": ["our", "ours (feminine)"],
    "आमचे": ["our", "ours (neuter/plural)"],
    "आमच्यात": ["in us"],
    
    # Second Person Singular
    "तू": ["you (singular)", "by you"],
    "तुला": ["to you", "for you"],
    "तुझ्याकडून": ["by you", "from your side"],
    "तुझ्याच्याने": ["by you (ability)"],
    "त्वा": ["by you (archaic)"],
    "तुझ्याशी": ["with you"],
    "तुझ्याहून": ["from you", "than you"],
    "तुझ्यापेक्षा": ["than you"],
    "तुझा": ["your", "yours (masculine)"],
    "तुझी": ["your", "yours (feminine)"],
    "तुझे": ["your", "yours (neuter/plural)"],
    "तुझ्यात": ["in you"],
    
    # Second Person Plural
    "तुम्ही": ["you (plural/respectful)", "by you (plural)"],
    "तुम्हाला": ["to you (plural)", "for you"],
    "तुमच्याकडून": ["by you (plural)", "from your side"],
    "तुमच्याच्याने": ["by you (ability)"],
    "तुमच्याशी": ["with you (plural)"],
    "तुमच्याहून": ["from you (plural)", "than you"],
    "तुमच्यापेक्षा": ["than you (plural)"],
    "तुमचा": ["your", "yours (plural/masculine)"],
    "तुमची": ["your", "yours (plural/feminine)"],
    "तुमचे": ["your", "yours (plural/neuter)"],
    "तुमच्यात": ["in you (plural)"],
    
    # Third Person Singular (Masculine)
    "तो": ["he", "that (masculine)"],
    "त्याला": ["to him", "for him"],
    "त्याने": ["by him"],
    "त्याच्याकडून": ["by him", "from his side"],
    "त्याच्याच्याने": ["by him (ability)"],
    "त्याच्याशी": ["with him"],
    "त्याच्याहून": ["from him", "than him"],
    "त्याच्यापेक्षा": ["than him"],
    "त्याचा": ["his (masculine object)"],
    "त्याची": ["his (feminine object)"],
    "त्याचे": ["his (neuter/plural object)"],
    "त्याच्यात": ["in him"],
    
    # Third Person Singular (Feminine)
    "ती": ["she", "that (feminine)"],
    "तिला": ["to her", "for her"],
    "तिने": ["by her"],
    "तिच्याकडून": ["by her", "from her side"],
    "तिच्याच्याने": ["by her (ability)"],
    "तिच्याशी": ["with her"],
    "तिच्याहून": ["from her", "than her"],
    "तिच्यापेक्षा": ["than her"],
    "तिचा": ["her", "hers (masculine object)"],
    "तिची": ["her", "hers (feminine object)"],
    "तिचे": ["her", "hers (neuter/plural object)"],
    "तिच्यात": ["in her"],
    
    # Third Person Plural
    "ते": ["they (masculine)", "those"],
    "त्या": ["they (feminine)", "those"],
    "ती": ["they (neuter)", "those"],
    "त्यांना": ["to them", "for them"],
    "त्यांनी": ["by them"],
    "त्यांच्याकडून": ["by them", "from their side"],
    "त्यांच्याच्याने": ["by them (ability)"],
    "त्यांच्याशी": ["with them"],
    "त्यांच्याहून": ["from them", "than them"],
    "त्यांच्यापेक्षा": ["than them"],
    "त्यांचा": ["their", "theirs (masculine object)"],
    "त्यांची": ["their", "theirs (feminine object)"],
    "त्यांचे": ["their", "theirs (neuter/plural object)"],
    "त्यांच्यात": ["in them"],

    # Self (Reflexive)
    "स्वतः": ["self", "oneself"],
    "स्वतःला": ["to oneself", "for oneself"],
    "स्वतःने": ["by oneself"],
    "स्वतःकडून": ["by oneself", "from oneself's side"],
    "स्वतःच्याने": ["by oneself (ability)"],
    "स्वतःशी": ["with oneself"],
    "स्वतःहून": ["by oneself", "voluntarily"],
    "स्वतःचा": ["own", "oneself's (masculine object)"],
    "स्वतःची": ["own", "oneself's (feminine object)"],
    "स्वतःचे": ["own", "oneself's (neuter/plural object)"],
    "स्वतःत": ["in oneself"]
}

def escape_sql_string(s):
    if s is None:
        return 'NULL'
    return "'" + s.replace("'", "''") + "'"

def main():
    sql_file = os.path.join("data", "marathi_dictionary.sql")
    
    if not os.path.exists(sql_file):
        print(f"Error: {sql_file} not found.")
        return
        
    print(f"Adding {len(PRONOUNS)} pronoun forms to {sql_file}...")
    
    # Open the SQL file to append the inserts
    with open(sql_file, "a", encoding="utf-8") as f:
        f.write("\n-- PRONOUNS AND INFLECTIONS (Added Automatically) --\n")
        
        for marathi_word, meanings in PRONOUNS.items():
            # Pad meanings to 3 items
            padded_meanings = meanings + [None] * (3 - len(meanings))
            
            key = marathi_word
            m1 = escape_sql_string(marathi_word)
            e1 = escape_sql_string(padded_meanings[0])
            e2 = escape_sql_string(padded_meanings[1])
            e3 = escape_sql_string(padded_meanings[2])
            
            # Schema: Key, Meaning1, Meaning2, Meaning3, Meaning4, user_id, devanagari, pos, definition_mr, source, is_stem
            sql = f"INSERT INTO \"MarathiEnglish\" VALUES({escape_sql_string(key)},{m1},{e1},{e2},{e3},NULL,{m1},'pronoun',NULL,'manual_pronoun',1);\n"
            f.write(sql)
            
    print("Added pronouns to SQL successfully!")

if __name__ == "__main__":
    main()
