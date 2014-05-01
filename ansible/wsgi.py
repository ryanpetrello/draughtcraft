if __name__ == "__main__":
    from pecan.deploy import deploy
    app = deploy('/opt/web/draughtcraft/src/config.py')
    app.run()
