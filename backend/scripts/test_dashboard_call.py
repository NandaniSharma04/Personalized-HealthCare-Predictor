import urllib.request, urllib.error

def main():
    url = 'http://127.0.0.1:8001/api/users/me/dashboard'
    token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzg2NzA4MDU5fQ.6WzPz6zlv7YLeSPL1eB1om3xoecQkj1peEtGaxnrCWc'
    req = urllib.request.Request(url, headers={'Authorization': f'Bearer {token}'})
    try:
        with urllib.request.urlopen(req, timeout=5) as r:
            print('STATUS', r.status)
            print(r.read().decode())
    except urllib.error.HTTPError as e:
        print('HTTP ERROR', e.code)
        try:
            print(e.read().decode())
        except Exception:
            pass
    except Exception as e:
        print('ERR', e)

if __name__ == '__main__':
    main()
