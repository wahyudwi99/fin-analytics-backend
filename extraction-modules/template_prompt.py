template_statement_extractor="""
Extract information within this image and return the result with the following format below:
```
{
    "column_1": ["val_1", "val_2", "val_3"],
    "column_2": ["val_1", "val_2", "val_3"],
    "column_3": ["val_1", "val_2", "val_3"]
}
```
IMPORTANT NOTES:
1. Extract all detail transactions within the document. If there are 5 columns in that document, extract information for 5 those columns, if
there are 10 columns, extract information for those 10 columns.
2. The things within triple backticks are the examples, don't copy it for result.
3. Replace "column" with the name you found within the document.
4. If you found several tables with different column names, just input those columns on the result and use null if the value is empty.
"""


template_prompt_new = """
Extract information within the input image and return the result with the following format below:
```
{
    "table_1": {
        "column_1": ["val_1", "val_2", "val_3"],
        "column_2": ["val_1", "val_2", "val_3"],
        "column_3": ["val_1", "val_2", "val_3"]
    },
    "table_2": {
        "column_1": ["val_1", "val_2", "val_3"],
        "column_2": ["val_1", "val_2", "val_3"],
        "column_3": ["val_1", "val_2", "val_3"]
    }
}
```

IMPORTANT NOTES:
1. The things within triple backticks are the examples, don't copy it for result.
2. Replace "column" with the name you found within the document.
3. Ensure every column in every table contains the same list length.
"""