#include <iostream>
#include "OpeDbCore.h"
#include <sqlite3.h>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

int main() {
    json obj;
    obj["name"] = "AVEVA-like app";
    obj["version"] = 1.0;

    // Print JSON
    std::cout << obj.dump(4) << std::endl;

    // Parse JSON string
    std::string input = R"({"status":"active","users":150})";
    json parsed = json::parse(input);

    std::cout << "Status: " << parsed["status"] << std::endl;
    std::cout << "Users: " << parsed["users"] << std::endl;
    
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