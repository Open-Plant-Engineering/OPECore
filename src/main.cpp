#include <iostream>
#include "app.h"

int main() {
    OpeCore app;

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