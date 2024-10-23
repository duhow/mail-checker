#!/usr/bin/env python3

from flask import Flask, request, jsonify
from mail_checker.validator import Validator
import os

app = Flask(__name__)

checks_done = 0

@app.route('/health')
def health_check():
  return jsonify({'status': 'healthy'}), 200

@app.route('/metrics')
def metrics():
  global checks_done

  return (
    "# HELP mail_checker_requests The number of email checks done\n"
    "# TYPE mail_checker_requests counter\n"
    f"mail_checker_requests {checks_done}\n"
  ), 200, {'Content-Type': 'text/plain'}

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

  global checks_done
  checks_done += 1

  validator = Validator(email)
  validator.run()

  return jsonify(validator.dict)

if __name__ == '__main__':
    debug_mode = os.getenv('DEBUG', 'False').lower() in ['true', '1', 't', 'y', 'yes']
    app.run(host='0.0.0.0', debug=debug_mode)