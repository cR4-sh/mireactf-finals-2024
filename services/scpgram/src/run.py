import app.main as main

if __name__ == '__main__':
    main.socketio.run(main.app, port=8000, host="0.0.0.0", allow_unsafe_werkzeug=True)
