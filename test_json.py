import json


with open('data/input/functions_definition.json') as file:
    json_content = json.load(file)

print(json_content)
print(type(json_content[0]['parameters']))
