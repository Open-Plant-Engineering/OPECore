import json
import time


class LeaderWorker:
    def __init__(self, log, queue, claims, leader):
        self.log = log
        self.queue = queue
        self.claims = claims
        self.leader = leader

    def process_once(self):
        """
        Process one batch of requests
        """
        if not self.leader.is_leader():
            return

        files = self.queue.list_requests()

        for fname in files:
            try:
                path = self.queue.mark_processing(fname)

                with open(path, "r") as f:
                    req = json.load(f)

                ok = self.handle(req)

                if ok:
                    self.queue.mark_done(path)
                else:
                    self.queue.mark_failed(path)

            except Exception as e:
                print("Error:", e)

    def loop(self):
        """
        Continuous processing
        """
        while True:
            self.process_once()
            time.sleep(0.1)

    # 🔥 CORE: command dispatcher
    def handle(self, req: dict) -> bool:
        action = req.get("action")

        if action == "claim":
            return self.claims.claim(
                req["user"],
                req["path"],
                req["type"]
            )

        elif action == "release":
            self.claims.release(
                req["user"],
                req["path"]
            )
            return True

        elif action == "append":
            data = json.dumps(req["data"]).encode()
            self.log.append(data)
            return True

        return False

    def loop(self):
        while True:
            if self.leader.is_leader():
                self.leader.heartbeat()   # ✅ critical
                self.process_once()

            time.sleep(0.5)
