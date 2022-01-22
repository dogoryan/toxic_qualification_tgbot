import json
def load_data(path: str) -> dict:
    data = None
    try:
        with open(path, 'r') as file:
            data = json.loads(file.read())
    except Exception as e:
        if e == json.JSONDecodeError:
            print('Data is crash')
            exit(1)
    return data

data = load_data('users.json')
print(data)


#if "43254" not in data:
#    data = add_chat(chat_id, data)