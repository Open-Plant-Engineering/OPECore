import os
import json
import time

# Import your pybind11 modules
import py_GitWrapper
import py_JsonCRUD
import py_SessionManager


def print_header(title):
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def main():
    # ---------------------------------------------------------
    # 1. Clone repository
    # ---------------------------------------------------------
    print_header("1. Cloning repository")

    remote_url = "https://github.com/your/repo.git"
    local_path = "/tmp/test_repo"

    if not os.path.exists(local_path):
        os.makedirs(local_path, exist_ok=True)

    err = ""
    ok = py_GitWrapper.cloneRepository(remote_url, local_path, err)
    if not ok:
        print("Clone failed:", err)
        return
    print("Clone successful")

    # ---------------------------------------------------------
    # 2. Create SessionManager
    # ---------------------------------------------------------
    print_header("2. Creating SessionManager")

    session = py_SessionManager.SessionManager(local_path)
    print("SessionManager created for:", session.getRepoPath())

    # ---------------------------------------------------------
    # 3. Create new JSON file with unique ID
    # ---------------------------------------------------------
    print_header("3. Creating new JSON file")

    initial_data = json.dumps({
        "name": "TestObject",
        "value": 10,
        "status": "new"
    })

    err = ""
    relative_path = session.createJsonWithUniqueId("data", initial_data, err)
    if not relative_path:
        print("Failed to create JSON:", err)
        return

    print("Created JSON file:", relative_path)

    # ---------------------------------------------------------
    # 4. Modify attribute (creates working + base copies)
    # ---------------------------------------------------------
    print_header("4. Modifying attribute")

    err = ""
    ok = session.modifyAttribute(relative_path, "value", "123", err)
    if not ok:
        print("Modify failed:", err)
        return

    print("Attribute modified in working copy")

    # ---------------------------------------------------------
    # 5. Modify another attribute
    # ---------------------------------------------------------
    print_header("5. Modifying another attribute")

    err = ""
    ok = session.modifyAttribute(relative_path, "status", "\"updated\"", err)
    if not ok:
        print("Modify failed:", err)
        return

    print("Second attribute modified")

    # ---------------------------------------------------------
    # 6. Finalize session (merge working → original)
    # ---------------------------------------------------------
    print_header("6. Finalizing session")

    rejected = []
    err = ""
    ok = session.finalizeSession(relative_path, rejected, err)

    if not ok:
        print("Finalize failed:", err)
        return

    if rejected:
        print("Some keys were rejected due to conflicts:", rejected)
    else:
        print("Finalize successful — no conflicts")

    print_header("TEST COMPLETE")


if __name__ == "__main__":
    main()