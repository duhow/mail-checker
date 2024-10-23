#!/usr/bin/env python3

from flask import Flask, request, jsonify
from mail_checker.validator import Validator

app = Flask(__name__)

@app.route('/check', methods=['POST', 'GET'])
def check_email():
  if request.method == 'POST':
    if request.is_json:
      data = request.get_json()
    else:
      data = request.form
    email = data.get('email')
  elif request.method == 'GET':
    email = request.args.get('email')
  
  if not email:
    return jsonify({'error': 'Email is required'}), 400
  
  validator = Validator(email)
  validator.run()

  return jsonify(validator.dict)

if __name__ == '__main__':
    app.run(debug=True)