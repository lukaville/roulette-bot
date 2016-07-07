class MockBot(object):
    def __init__(self):
        self.messages = []

    def setWebhook(self, **kwargs):
        pass

    def sendMessage(self, user_id, text, **kwargs):
        self.messages.append({
            'user_id': user_id,
            'text': text
        })

    def getUpdates(self, *args, **kwargs):
        return []

    def pop_message(self):
        return self.messages.pop(0)
