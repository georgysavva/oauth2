from core import services, config

app = services.initialize_wsgi()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=config.DEV_SERVER_PORT)
