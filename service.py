import hashlib


class StringService():
    def __init__(self):
        pass
    
    def length(self, value:str):
        #Number of characters in the string
        count = 0
        for _ in value:
            count = count + 1
        return count
             
    
    def is_palindrome(self, value: str) -> bool:
        """
        Boolean indicating if the string reads the same forwards and backwards (case-insensitive)
        """
        value_lower = value.lower()
        reversed_text = ''.join(reversed(value_lower))
        return value_lower == reversed_text
    
    def unique_characters(self, value:str):
        #Count of distinct characters in the string
        unique_characters = set(value.replace(" ", ""))  # ignore spaces
        count = len(unique_characters)
        return count
    
    def word_count(self, text: str) -> int:
        count = 0
        in_word = False

        for ch in text:
            if ch.isspace():
                # We hit a space → end of a word
                in_word = False
            elif not in_word:
                # We found the start of a new word
                count += 1
                in_word = True

        return count
    
    def sha256_hash(self, value:str):
        #SHA-256 hash of the string for unique identification
        hash_value = hashlib.sha256(value.encode()).hexdigest() 
        return hash_value
    
    def character_frequency_map(self, value: str):
        # Object/dictionary mapping each character to its occurrence count
        char_map = {}
        for char in value:
            char_map[char] = char_map.get(char, 0) + 1
        return char_map
    
    def create_string(self, value:str):
        pass 
    
    
# Create an instance of StringService
string_service = StringService()

# Test string to use
test_string = "Hello World"
palindrome = "Madam"

# Test all methods
print("Testing length:", string_service.length(test_string))
print("Testing is_palindrome:", string_service.is_palindrome(palindrome))
print("Testing unique_characters:", string_service.unique_characters(test_string))
print("Testing word_count:", string_service.word_count(test_string))
print("Testing sha256_hash:", string_service.sha256_hash(test_string))
print("Testing character_frequency_map:", string_service.character_frequency_map(test_string))


class StringCRUD():
    def __init__(self, string_service: StringService):
        self.string_service = StringService()
        