from fastapi import FastAPI
from .schema import StringInput
from .service import StringService
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

app.post("/strings")
async def create_analyze_string(value:StringInput):
    #takes the string and does the service computation, returns the necccessary values
    pass


app.get("/strings/{string_value}")
#Get Specific String
async def get_string(string_value:str):
    pass


@app.get("/strings")
#Get All Strings with Filtering
async def query_strings(
    is_palindrome: bool = None,
    min_length: int = None,
    max_length: int = None,
    word_count: int = None,
    contains_character: str = None
    ):
        pass
    


@app.get("/strings/filter-by-natural-language")
async def filter_strings_by_query(query: str):
    return {"query": query}

@app.delete("/strings/{string_value}")
async def delete_string(string_value: str):
        # Delete specific string
    pass



# Example Queries to Support:
# "all single word palindromic strings" → word_count=1, is_palindrome=true
# "strings longer than 10 characters" → min_length=11
# "palindromic strings that contain the first vowel" → is_palindrome=true, contains_character=a (or similar heuristic)
# "strings containing the letter z" → contains_character=z