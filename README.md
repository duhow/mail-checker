# Mail Checker

A small Flask application to check the email provided, return score and determine if it's valid or not.

### Usage

Call endpoint `GET /check?email=your@email.com` or `POST /check` with JSON `{"email": "your@email.com"}`.

```sh
curl -H  "Content-Type: application/json" --data '{"email": "whatever@abaot.com"}' localhost:5000/check
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