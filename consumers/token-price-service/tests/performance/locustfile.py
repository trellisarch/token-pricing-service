from locust import FastHttpUser, task


class WalletUser(FastHttpUser):

    @task
    def token_list(self):
        self.client.post("/tokens/")
