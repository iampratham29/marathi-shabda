
# marathi-shabda

Check README_English.md for more information in English.

मराठी शब्दांचे विश्लेषण करणारी, deterministic आणि पूर्णपणे offline Python लायब्ररी

## marathi-shabda म्हणजे काय?

`marathi-shabda` ही मराठी शब्दांचे विश्लेषण करण्यासाठी तयार केलेली production-quality Python लायब्ररी आहे.
ही लायब्ररी शब्दाचा मूळ शब्द (lemma), शब्दकोशातील अर्थ, आणि रूपवैज्ञानिक माहिती (विभक्ती, शब्दप्रकार, काळ) ओळखते.

## वैशिष्ट्ये

- विभक्ती लावलेल्या शब्दातून मूळ शब्द (lemma) काढणे  
- मराठी ↔ इंग्रजी शब्दकोश शोध  
- शब्दप्रकार (नाम, क्रियापद, विशेषण) ओळख  
- Roman मराठी इनपुट सपोर्ट (pani → पाणी)  
- पूर्णपणे offline – इंटरनेट किंवा API लागत नाही  

## Installation

pip install marathi-shabda

## Usage (उदाहरण)

from marathi_shabda import get_lemma

result = get_lemma("पाण्यावर")
print(result.lemma)

## Offline Guarantee

ही लायब्ररी पूर्णपणे offline चालते.
कोणतेही network request, telemetry किंवा API key लागत नाही.

## मर्यादा

- एकावेळी एकच शब्द
- वाक्य पातळीवर विश्लेषण नाही
- काही दुर्मिळ शब्दांमध्ये ambiguity

## License

ही लायब्ररी शैक्षणिक व non-commercial वापरासाठी मोफत आहे.
Commercial वापरासाठी वेगळा license आवश्यक आहे.

## Contributors

- Prathmesh Santosh Choudhari
- Vedangi Deepak Deshpande
- Siddhant Akash Bobde
