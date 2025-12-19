#include <iostream>
#include "OpeDbCore.h"
#include <sqlite3.h>
#include "JsonCRUD.hpp"

int JsonCRUDMain();

int main() {
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