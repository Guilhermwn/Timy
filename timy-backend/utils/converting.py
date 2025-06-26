import base64

with open("mygui.json") as f:
    data = f.read().encode("utf-8")

encoded = base64.b64encode(data)

with open("credentials.txt", "w") as f:
    f.write(encoded.decode())
