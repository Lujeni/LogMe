## LogMe:
Very simply app for real-time log monitoring in your browser.
LogMe watch log files (reader.py) for changes, send new log messages to the server (logme.py), which broadcasts to web clients.

## Powered:
`gevent`
`socket.IO`
`zeromq`
`bootstrap`

## Quick install:
### Step 1: Install library require.
```
pip install -r requirements.txt
```

### Step 2: Launch the broker / App front.
```
python logme.py
```

### Step 3: Launch the reader(s).
```
python reader.py -f /var/log/emerge.log -h localhost -p 6666
python reader.py -f /var/log/http/error.log -h localhost -p 6666
```