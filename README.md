# 📨 Mail Checker

A small Flask application to check the email provided, return score and determine if it's valid or not.

This app can detect:

* common pattern typos and make domain suggestions (eg. `gemail.com`)
* some **Disposable Email Addresses** (DEA) - aka temporal emails
* domains used on public email services
* domains that do not exist (checks DNS records) or cannot receive emails

### Usage

Call endpoint `GET /check?email=your@email.com` or `POST /check` with JSON `{"email": "your@email.com"}`.

Alternatively, execute `app.py your@email.com` to check one single address.

```sh
curl -H  "Content-Type: application/json" localhost:5000/check --data '{"email": "whatever@abaot.com"}'
```

```json
{
  "disposable": true,
  "email": "whatever@abaot.com",
  "reasons": [
    "Suspicious Tempmail"
  ],
  "score": 0,
  "valid": false
}
```
