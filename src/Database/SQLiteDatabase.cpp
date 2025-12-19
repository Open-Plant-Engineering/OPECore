#include "Database.hpp"
#include <sqlite3.h>
#include <iostream>

class SQLiteDatabase : public IDatabase {
private:
    sqlite3* db;

public:
    SQLiteDatabase() : db(nullptr) {}
    ~SQLiteDatabase() {
        if (db) sqlite3_close(db);
    }

    bool connect(const std::string& connStr) override {
        // connStr = path to SQLite file
        if (sqlite3_open(connStr.c_str(), &db) != SQLITE_OK) {
            std::cerr << "SQLite connection failed: " << sqlite3_errmsg(db) << "\n";
            return false;
        }
        return true;
    }

    bool createTable(const std::string& tableName) override {
        std::string query = "CREATE TABLE IF NOT EXISTS " + tableName +
                            " (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, age INTEGER)";
        return sqlite3_exec(db, query.c_str(), nullptr, nullptr, nullptr) == SQLITE_OK;
    }

    bool insert(const std::string& tableName, const std::string& name, int age) override {
        std::string query = "INSERT INTO " + tableName + " (name, age) VALUES('" + name + "'," + std::to_string(age) + ")";
        return sqlite3_exec(db, query.c_str(), nullptr, nullptr, nullptr) == SQLITE_OK;
    }

    std::vector<std::string> read(const std::string& tableName) override {
        std::vector<std::string> results;
        std::string query = "SELECT id, name, age FROM " + tableName;
        sqlite3_stmt* stmt;
        if (sqlite3_prepare_v2(db, query.c_str(), -1, &stmt, nullptr) == SQLITE_OK) {
            while (sqlite3_step(stmt) == SQLITE_ROW) {
                int id = sqlite3_column_int(stmt, 0);
                const char* name = reinterpret_cast<const char*>(sqlite3_column_text(stmt, 1));
                int age = sqlite3_column_int(stmt, 2);
                results.push_back(std::to_string(id) + " | " + name + " | " + std::to_string(age));
            }
        }
        sqlite3_finalize(stmt);
        return results;
    }

    bool update(const std::string& tableName, int id, const std::string& name, int age) override {
        std::string query = "UPDATE " + tableName + " SET name='" + name + "', age=" + std::to_string(age) +
                            " WHERE id=" + std::to_string(id);
        return sqlite3_exec(db, query.c_str(), nullptr, nullptr, nullptr) == SQLITE_OK;
    }

    bool remove(const std::string& tableName, int id) override {
        std::string query = "DELETE FROM " + tableName + " WHERE id=" + std::to_string(id);
        return sqlite3_exec(db, query.c_str(), nullptr, nullptr, nullptr) == SQLITE_OK;
    }
};