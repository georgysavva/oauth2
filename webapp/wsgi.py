from core import services

app = services.initialize_wsgi()

if __name__ == '__main__':
    app.run()
