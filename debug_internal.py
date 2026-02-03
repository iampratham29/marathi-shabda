from marathi_shabda.dictionary import DictionaryAdapter

def check_debug():
    adapter = DictionaryAdapter()
    
    for word in ["मुल", "मूल", "मुलगा"]:
        exists = adapter.exists(word)
        print(f"Exists '{word}': {exists}")
        if exists:
            entries = adapter.lookup_by_devanagari(word)
            print(f"Entries for '{word}': {entries}")

if __name__ == "__main__":
    check_debug()
