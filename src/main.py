from contextlib import asynccontextmanager
from typing import Optional

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession

from src.db import drop_db, get_session, init_db
from src.error import NotFoundError, register_error_handler
from src.schema import (
    CreateResponse,
    FilteredString,
    FiltersApplied,
    Properties,
    StringInput,
    SuccessResponse,
    NLPFiltering, # Added for natural language filtering response
)
from src.service import StringCRUD


def get_string_service(db: AsyncSession = Depends(get_session)):
    return StringCRUD(db=db)


@asynccontextmanager
async def life_span(app: FastAPI):
    # Startup
    try:
        # await drop_db()
        # print("tables dropped")
        await init_db()
        print("tables created")
    except Exception as e:
        print(f"Error during database initialization: {str(e)}")
        raise

    yield  # Application is running

    # Shutdown
    print("server is ending.....")


app = FastAPI(lifespan=life_span)

# register errors
register_error_handler(app)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)


@app.post("/strings")
async def create_analyze_string(
    string_input: StringInput, string_crud: StringCRUD = Depends(get_string_service)
):
    # takes the string and does the service computation, returns the necccessary values
    validated_str = string_input.value
    new_str = await string_crud.create_string(validated_str)
    properties = Properties(
        length=new_str.length,
        is_palindrome=new_str.is_palindrome,
        unique_characters=new_str.unique_characters,
        word_count=new_str.word_count,
        sha256_hash=new_str.sha256_hash,
        character_frequency_map=new_str.character_frequency_map,
    )
    response = CreateResponse(
        id=new_str.sha256_hash,
        value=new_str.value,
        properties=properties,
        created_at=new_str.created_at,
    )
    return response.model_dump()


@app.get("/strings/filter-by-natural-language", response_model=NLPFiltering)
async def filter_strings_by_query(
    query: str, string_crud: StringCRUD = Depends(get_string_service)
):
    return await string_crud.filter_strings_by_natural_language(query=query)



@app.get("/strings/{string_value}")
# Get Specific String
async def get_string(
    string_value: str,
    string_crud: StringCRUD = Depends(get_string_service),
):
    string = await string_crud.fetch_one_string(
        string_value=string_value,
    )
    properties = Properties(
        length=string.length,
        is_palindrome=string.is_palindrome,
        unique_characters=string.unique_characters,
        word_count=string.word_count,
        sha256_hash=string.sha256_hash,
        character_frequency_map=string.character_frequency_map,
    )
    response = CreateResponse(
        id=string.sha256_hash,
        value=string.value,
        properties=properties,
        created_at=string.created_at,
    ) 
    return response.model_dump()




# IMPORTANT: /strings route MUST come BEFORE /strings/{string_value}
@app.get("/strings")
# Get All Strings with Filtering
async def query_strings(
    is_palindrome: Optional[bool] = None,
    min_length: Optional[int] = None,
    max_length: Optional[int] = None,
    word_count: Optional[int] = None,
    contains_character: Optional[str] = None,
    string_crud: StringCRUD = Depends(get_string_service),
):
    strings = await string_crud.fetch_all_strings_with_filtering(
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character,
    )

    response_data = []
    for string in strings:
        properties = Properties(
            length=string.length,
            is_palindrome=string.is_palindrome,
            unique_characters=string.unique_characters,
            word_count=string.word_count,
            sha256_hash=string.sha256_hash,
            character_frequency_map=string.character_frequency_map,
        )
        response_data.append(
            SuccessResponse(
                id=string.sha256_hash,
                value=string.value,
                properties=properties,
                created_at=string.created_at,
            )
        )

    filters_applied = FiltersApplied(
        is_palindrome=is_palindrome,
        min_length=min_length,
        max_length=max_length,
        word_count=word_count,
        contains_character=contains_character,
    )

    return FilteredString(
        data=response_data, count=len(response_data), filters_applied=filters_applied
    ).model_dump()






@app.delete("/strings/{string_value}")
async def delete_string(
    string_value: str, string_crud: StringCRUD = Depends(get_string_service)
):
    try:
        await string_crud.delete_string(string_value)
        return {"message": f"String '{string_value}' deleted successfully."}
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


# Example Queries to Support:
# "all single word palindromic strings" → word_count=1, is_palindrome=true
# "strings longer than 10 characters" → min_length=11
# "palindromic strings that contain the first vowel" → is_palindrome=true, contains_character=a (or similar heuristic)
# "strings containing the letter z" → contains_character=z
