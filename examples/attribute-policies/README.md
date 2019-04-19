# Attribute Policies

This example represents a tiny Github clone whose resources are protected by 
policies (Rule-based Policies in `vakt` nomenclature) defined with rules for various entity attributes 
or entire entities.

Interaction between client and server is done via remote procedure calls with the use of Pyro.


Install deps:
```bash
python3 -m pip install -r requirements.txt
```


Run server:
```bash
python3 server.py
```

Check access with client:
```bash
python3 client.py
```

Client should run assertions and respond with "Everything works fine" message.
