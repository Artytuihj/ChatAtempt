import threading
from App.client.main import MainApp as App


app1 = App()
app2 = App()

threading.Thread(target=app1.app.exec(), daemon=True).start()
threading.Thread(target=app2.app.exec(), daemon=True).start()