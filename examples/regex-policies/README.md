# Regex Policies

This example represents web book library whose resources are protected by "Amazon AWS IAM"-like policies 
defined with `vakt`'s regex policies (String-based Policies in `vakt` nomenclature).

All the policies here are defined with string or regular expression.

Interaction between client and server is done via HTTP.

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
