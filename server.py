from flask import Flask, request

app = Flask(__name__)

@app.route('/slack/events', methods=['POST'])
def slack_events():
    print("🔥 Slack route HIT")
    print("Headers:", request.headers)
    print("Body:", request.data)
    return '', 200

@app.route('/test', methods=['GET'])
def test():
    return "🚀 It works", 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 3000))
    app.run(host='0.0.0.0', port=port)
