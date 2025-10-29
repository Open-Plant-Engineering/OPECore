#include <iostream>
#include "app.h"

int main() {
    OpeCore app;

    std::string createTable = "CREATE TABLE users (id INTEGER PRIMARY KEY, name TEXT);";
    std::string insertData = "INSERT INTO users (name) VALUES ('Alice'), ('Bob');";

    if (!app.execute(createTable)) {
        std::cerr << "Error creating table: " << app.getLastError() << std::endl;
        return 1;
    }

    if (!app.execute(insertData)) {
        std::cerr << "Error inserting data: " << app.getLastError() << std::endl;
        return 1;
    }

    std::cout << "SQLite operations completed successfully." << std::endl;
    return 0;
}