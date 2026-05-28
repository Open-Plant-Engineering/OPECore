import json
import time


class LeaderWorker:
    def __init__(self, log, queue, claims, leader, idempotency, state_store=None):
        self.log = log
        self.queue = queue
        self.claims = claims
        self.leader = leader
        self.idempotency = idempotency
        self.state_store = state_store

        # ✅ recover stuck files on startup
        self.queue.recover_stuck()

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

                request_id = req.get("request_id")

                # ✅ Skip duplicate execution
                if request_id and self.idempotency.is_processed(request_id):
                    self.queue.mark_done(path)
                    continue

                ok = self.handle(req)

                if ok:
                    if request_id:
                        self.idempotency.mark_processed(request_id)

                    self.queue.mark_done(path)
                else:
                    self.queue.mark_failed(path)

            except Exception as e:
                print("Worker error:", e)

    def loop(self):
        while True:
            if self.leader.is_leader():
                self.leader.heartbeat()  # ✅ keep lease alive
                self.process_once()

            time.sleep(0.5)

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

        elif action == "set":
            entry = {
                "op": "SET",
                "path": req["path"],
                "value": req["value"]
            }

            data = json.dumps(entry).encode()

            # ✅ write to log
            self.log.append(data)

            # ✅ update in-memory state instantly
            if self.state_store:
                self.state_store.apply_record(data)

            return True
        
        elif action == "delete":
            entry = {
                "op": "DELETE",
                "path": req["path"]
            }

            data = json.dumps(entry).encode()

            self.log.append(data)

            if self.state_store:
                self.state_store.apply_record(data)

            return True

        return False