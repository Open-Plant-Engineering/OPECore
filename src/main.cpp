#include <iostream>
#include "OpeDbCore.h"
#include <sqlite3.h>
#include "JsonCRUD.hpp"
#include "GitWrapper.hpp"
#include "Database.hpp"

int JsonCRUDMain();
void testGitWrapper(const std::string& repoPath);
int TestDB();

int main() {
    TestDB();
    std::string repoPath = "/workspaces/OPECore/libgit2";
    testGitWrapper(repoPath);

    JsonCRUDMain();
    
    OpeDbCore app;

    app.dbFilePath = "C:\\db\\db.db";
    app.OpenDbConnection();

    std::string createTable = "CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT);";
    std::string insertData = "INSERT INTO items (name) VALUES ('Book'), ('Pen');";

    if (!app.execute(createTable)) {
        std::cerr << "Failed to create table: " << app.getLastError() << std::endl;
        return 1;
    }

    if (!app.execute(insertData)) {
        std::cerr << "Failed to insert data: " << app.getLastError() << std::endl;
        return 1;
    }
    
    std::cout << "Demo app ran successfully!" << std::endl;
    return 0;
}

// Example usage
int JsonCRUDMain() {
    JsonCRUD crud("data.json");

    // Create
    crud.create("user1", {{"name", "Alice"}, {"age", 25}});
    crud.create("user2", {{"name", "Bob"}, {"age", 30}});

    // Read
    std::cout << "User1: " << crud.read("user1") << std::endl;

    // Update
    crud.update("user1", {{"name", "Alice"}, {"age", 26}});

    // Delete
    crud.remove("user2");

    // Print all
    crud.printAll();

    return 0;
}

void testGitWrapper(const std::string& repoPath) {
    GitWrapper git(repoPath);

    std::cout << "=== Testing GitWrapper on repo: " << repoPath << " ===\n";

    // 1. Create a new branch
    if (git.gitCreateBranch("test-branch")) {
        std::cout << "Branch 'test-branch' created successfully.\n";
    } else {
        std::cout << "Failed to create branch.\n";
    }

    // 2. Rename the branch
    if (git.gitRenameBranch("test-branch", "renamed-branch")) {
        std::cout << "Branch renamed to 'renamed-branch'.\n";
    } else {
        std::cout << "Failed to rename branch.\n";
    }

    // 3. Pull (fetch only in our simplified wrapper)
    if (git.gitPull("origin", "main")) {
        std::cout << "Pull (fetch) completed.\n";
    } else {
        std::cout << "Pull failed.\n";
    }

    // 4. List modified files
    auto modified = git.getModifiedFiles();
    if (!modified.empty()) {
        std::cout << "Modified files:\n";
        for (const auto& f : modified) {
            std::cout << " - " << f << "\n";
        }
    } else {
        std::cout << "No modified files detected.\n";
    }

    // 5. Reset (soft example)
    if (git.gitReset("HEAD~1", "soft")) {
        std::cout << "Soft reset to HEAD~1 completed.\n";
    } else {
        std::cout << "Reset failed.\n";
    }

    // Hard reset to HEAD~1
    if (git.gitReset("HEAD~1", "hard")) {
        std::cout << "Hard reset to HEAD~1 completed.\n";
    } else {
        std::cout << "Hard reset failed.\n";
    }

    // 6. Stash
    if (git.gitStash("Test stash")) {
        std::cout << "Changes stashed successfully.\n";
    } else {
        std::cout << "Stash failed.\n";
    }

    // Create branch first
    git.gitCreateBranch("temp-branch");

    // Delete branch
    if (git.gitDeleteBranch("temp-branch")) {
        std::cout << "Branch deletion test passed.\n";
    } else {
        std::cout << "Branch deletion test failed.\n";
    }
}

#include "Database.hpp"

int TestDB() {
    try
    {
        // ----- Choose backend -----
        // 1) SQLite example
        DbBackend backend = DbBackend::SQLite;
        std::string connStr = "soci_demo.db"; // SQLite file

        // 2) MySQL example (uncomment to use)
        // DbBackend backend = DbBackend::MySQL;
        // std::string connStr =
        //     "db=testdb user=root password=1234 host=127.0.0.1";

        Database db(backend, connStr);
        db.initSchema();

        std::string name = "Alice";
        int age = 30;

        std::cout << "== CREATE ==" << std::endl;
        db.createUser(name, age);

        std::cout << "== READ ==" << std::endl;
        int idOut = 0, ageOut = 0;
        if (db.readUserByName(name, idOut, ageOut))
        {
            std::cout << "User found: id=" << idOut
                      << ", name=" << name
                      << ", age=" << ageOut << std::endl;
        }
        else
        {
            std::cout << "User not found" << std::endl;
        }

        std::cout << "== UPDATE ==" << std::endl;
        db.updateUserAge(name, 31);
        if (db.readUserByName(name, idOut, ageOut))
        {
            std::cout << "After update: id=" << idOut
                      << ", name=" << name
                      << ", age=" << ageOut << std::endl;
        }

        std::cout << "== DELETE ==" << std::endl;
        db.deleteUser(name);
        if (!db.readUserByName(name, idOut, ageOut))
        {
            std::cout << "User deleted successfully." << std::endl;
        }
    }
    catch (const std::exception& ex)
    {
        std::cerr << "Error: " << ex.what() << '\n';
        return 1;
    }

    return 0;
}