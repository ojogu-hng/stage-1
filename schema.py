from pydantic import BaseModel
from datetime import datetime
from typing import Dict
from typing import Optional

class StringInput(BaseModel):
    value:str
    
    
class Properties(BaseModel):
    length: int
    is_palindrome: bool
    unique_characters: int
    word_count: int
    sha256_hash: str
    character_frequency_map: Dict[str, int]

class CreateResponse(BaseModel): #for 201 create
    id: str
    value: str
    properties: Properties
    created_at: datetime
    
    
class SuccessResponse(BaseModel): #200 ok: Get Specific String
    id: str
    value: str
    properties: Properties
    created_at: datetime
    
class FiltersApplied(BaseModel):
    is_palindrome: bool
    min_length: int
    max_length: int
    word_count: int
    contains_character: str

class FilteredString(BaseModel): #Get All Strings with Filtering
    data: list[SuccessResponse]
    count: int
    filters_applied: FiltersApplied


class ParsedFilters(BaseModel):
    word_count: Optional[int] = None
    is_palindrome: Optional[bool] = None
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    contains_character: Optional[str] = None

class InterpretedQuery(BaseModel):
    original: str
    parsed_filters: ParsedFilters

class NLPFiltering(BaseModel): 
    data: list[SuccessResponse]
    count: int
    interpreted_query: InterpretedQuery