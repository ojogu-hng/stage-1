import hashlib

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import Strings
from src.error import AlreadyExist, NotFoundError
from src.log import setup_logger
from src.schema import ParsedFilters, InterpretedQuery, NLPFiltering, SuccessResponse

# Set up logger
logger = setup_logger(__name__, "service.log")


class NaturalLanguageParser:
    def parse_query(self, query: str) -> ParsedFilters:
        parsed_filters = ParsedFilters()
        query_lower = query.lower()
        logger.info(f"Parsing query_lower: '{query_lower}'") # DEBUG

        if "palindrome" in query_lower:
            parsed_filters.is_palindrome = True
        if "not palindrome" in query_lower or "non-palindrome" in query_lower:
            parsed_filters.is_palindrome = False

        if "single word" in query_lower:
            parsed_filters.word_count = 1
        
        # Basic length parsing (e.g., "length greater than 5")
        if "length greater than" in query_lower:
            try:
                parts = query_lower.split("length greater than")
                min_length_str = parts[1].strip().split(" ")[0]
                parsed_filters.min_length = int(min_length_str)
            except (ValueError, IndexError):
                logger.warning(f"Could not parse min_length from query: {query}")
        
        if "length less than" in query_lower:
            try:
                parts = query_lower.split("length less than")
                max_length_str = parts[1].strip().split(" ")[0]
                parsed_filters.max_length = int(max_length_str)
            except (ValueError, IndexError):
                logger.warning(f"Could not parse max_length from query: {query}")

        # Basic contains character parsing (e.g., "contains 'a'")
        logger.info(f'Checking for "contains \'" in {query_lower!r}: {"contains \'" in query_lower}')

        if "contains '" in query_lower:
            try:
                start_index = query_lower.find("contains '") + len("contains '")
                end_index = query_lower.find("'", start_index)
                if start_index != -1 and end_index != -1:
                    parsed_filters.contains_character = query_lower[start_index:end_index]
                    logger.info(f"Parsed contains_character (with quotes): {parsed_filters.contains_character}") # DEBUG
            except (ValueError, IndexError):
                logger.warning(f"Could not parse contains_character from query (with quotes): {query}")
        # Removed the 'elif "contains" in query_lower:' block for now to simplify debugging.

        logger.info(f"Final Parsed filters before return: {parsed_filters.model_dump_json()}") # DEBUG
        return parsed_filters


class StringService:
    def __init__(self):
        pass

    def length(self, value: str):
        # Number of characters in the string
        count = 0
        for _ in value:
            count = count + 1
        return count

    def is_palindrome(self, value: str) -> bool:
        """
        Boolean indicating if the string reads the same forwards and backwards (case-insensitive)
        """
        value_lower = value.lower()
        reversed_text = "".join(reversed(value_lower))
        return value_lower == reversed_text

    def unique_characters(self, value: str):
        # Count of distinct characters in the string
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

    def sha256_hash(self, value: str):
        # SHA-256 hash of the string for unique identification
        hash_value = hashlib.sha256(value.encode()).hexdigest()
        return hash_value

    def character_frequency_map(self, value: str):
        # Object/dictionary mapping each character to its occurrence count
        char_map = {}
        for char in value:
            char_map[char] = char_map.get(char, 0) + 1
        return char_map

    def create_string(self, value: str):
        pass


# Create an instance of StringService
string_service = StringService()


class StringCRUD:
    def __init__(self, db: AsyncSession):
        self.string_service = StringService()
        self.db = db

    async def check_if_string_exist(self, string_value: str):
        stmt = select(Strings).where(Strings.value == string_value)
        result = await self.db.execute(stmt)
        string = result.scalars().first()
        if string:
            logger.info(f"String '{string_value}' found in database.")
        else:
            logger.info(f"String '{string_value}' not found in database.")
        return string

    async def create_string(self, string_value: str):
        try:
            string = await self.check_if_string_exist(string_value)
            if string:
                logger.warning(
                    f"Attempted to create existing string: '{string_value}'."
                )
                raise AlreadyExist(f"'{string_value}' already exists")

            logger.info(f"Calculating properties for new string: '{string_value}'.")
            length = self.string_service.length(string_value)
            is_palindrome = self.string_service.is_palindrome(string_value)
            unique_character = self.string_service.unique_characters(string_value)
            word_count = self.string_service.word_count(string_value)
            hash = self.string_service.sha256_hash(string_value)
            freq_map = self.string_service.character_frequency_map(string_value)

            new_string = Strings(
                value=string_value,
                length=length,
                is_palindrome=is_palindrome,
                unique_characters=unique_character,
                word_count=word_count,
                sha256_hash=hash,
                character_frequency_map=freq_map,
            )
            self.db.add(new_string)
            await self.db.commit()
            logger.info(f"New string '{new_string.value}' created successfully.")
            return new_string
        except AlreadyExist as e:
            logger.error(f"Failed to create string: {e}")
            raise
        except Exception as e:
            logger.error(
                f"An unexpected error occurred while creating string '{string_value}': {str(e)}"
            )
            raise

    async def fetch_one_string(
        self,
        string_value: str,
    ):
        logger.info(f"Fetching string '{string_value}'.")
        stmt = select(Strings).where(Strings.value == string_value)

        result = await self.db.execute(stmt)
        string = result.scalars().first()

        if string:
            logger.info(f"String '{string_value}' found matching criteria.")
            return string
        else:
            logger.warning(
                f"String '{string_value}' not found or does not match criteria."
            )
            raise NotFoundError(
                f"String '{string_value}' not found or does not match criteria."
            )


    async def fetch_all_strings_with_filtering(
        self,
        is_palindrome: bool = None,
        min_length: int = None,
        max_length: int = None,
        word_count: int = None,
        contains_character: str = None,
    ):
        logger.info(
            f"Fetching all strings with filters: is_palindrome={is_palindrome}, min_length={min_length}, max_length={max_length}, word_count={word_count}, contains_character='{contains_character}'."
        )
        stmt = select(Strings)

        if is_palindrome is not None:
            stmt = stmt.where(Strings.is_palindrome == is_palindrome)
        if min_length is not None:
            stmt = stmt.where(Strings.length >= min_length)
        if max_length is not None:
            stmt = stmt.where(Strings.length <= max_length)
        if word_count is not None:
            stmt = stmt.where(Strings.word_count == word_count)
        if contains_character is not None:
            stmt = stmt.where(Strings.value.ilike(f"%{contains_character}%"))

        result = await self.db.execute(stmt)
        strings = result.scalars().all()

        logger.info(f"Found {len(strings)} strings matching the criteria.")
        return strings

    async def delete_string(self, string_value: str):
        logger.info(f"Attempting to delete string: '{string_value}'.")
        string = await self.check_if_string_exist(string_value)
        if not string:
            logger.warning(
                f"Attempted to delete non-existent string: '{string_value}'."
            )
            raise NotFoundError(f"String '{string_value}' not found.")

        await self.db.delete(string)
        await self.db.commit()
        logger.info(f"String '{string_value}' deleted successfully.")
        return {"message": f"String '{string_value}' deleted successfully."}

    async def filter_strings_by_natural_language(self, query: str):
        logger.info(f"Filtering strings by natural language query: '{query}'.")
        parser = NaturalLanguageParser()
        parsed_filters = parser.parse_query(query)

        stmt = select(Strings)

        if parsed_filters.is_palindrome is not None:
            stmt = stmt.where(Strings.is_palindrome == parsed_filters.is_palindrome)
        if parsed_filters.min_length is not None:
            stmt = stmt.where(Strings.length >= parsed_filters.min_length)
        if parsed_filters.max_length is not None:
            stmt = stmt.where(Strings.length <= parsed_filters.max_length)
        if parsed_filters.word_count is not None:
            stmt = stmt.where(Strings.word_count == parsed_filters.word_count)
        if parsed_filters.contains_character is not None:
            stmt = stmt.where(Strings.value.ilike(f"%{parsed_filters.contains_character}%"))

        result = await self.db.execute(stmt)
        strings = result.scalars().all()

        # Convert ORM objects to Pydantic models for response
        response_data = [
            SuccessResponse(
                id=str(s.sha256_hash),
                value=s.value,
                properties={
                    "length": s.length,
                    "is_palindrome": s.is_palindrome,
                    "unique_characters": s.unique_characters,
                    "word_count": s.word_count,
                    "sha256_hash": s.sha256_hash,
                    "character_frequency_map": s.character_frequency_map,
                },
                created_at=s.created_at,
            )
            for s in strings
        ]

        interpreted_query = InterpretedQuery(original=query, parsed_filters=parsed_filters)
        
        logger.info(f"Found {len(strings)} strings matching the natural language query.")
        return NLPFiltering(data=response_data, count=len(response_data), interpreted_query=interpreted_query)
