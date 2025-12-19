#include "Database.hpp"
#include <mysql/mysql.h>
#include <iostream>

class MySQLDatabase : public IDatabase {
private:
    MYSQL* conn;

public:
    MySQLDatabase() : conn(mysql_init(nullptr)) {}
    ~MySQLDatabase() {
        if (conn) mysql_close(conn);
    }

    bool connect(const std::string& connStr) override {
        // connStr format: host;user;password;db
        auto host = "localhost";
        auto user = "root";
        auto pass = "password";
        auto db   = "testdb";

        if (!mysql_real_connect(conn, host, user, pass, db, 3306, nullptr, 0)) {
            std::cerr << "MySQL connection failed: " << mysql_error(conn) << "\n";
            return false;
        }
        return true;
    }

    bool createTable(const std::string& tableName) override {
        std::string query = "CREATE TABLE IF NOT EXISTS " + tableName +
                            " (id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50), age INT)";
        return mysql_query(conn, query.c_str()) == 0;
    }

    bool insert(const std::string& tableName, const std::string& name, int age) override {
        std::string query = "INSERT INTO " + tableName + " (name, age) VALUES('" + name + "'," + std::to_string(age) + ")";
        return mysql_query(conn, query.c_str()) == 0;
    }

    std::vector<std::string> read(const std::string& tableName) override {
        std::vector<std::string> results;
        std::string query = "SELECT id, name, age FROM " + tableName;
        if (mysql_query(conn, query.c_str()) == 0) {
            MYSQL_RES* res = mysql_store_result(conn);
            MYSQL_ROW row;
            while ((row = mysql_fetch_row(res))) {
                results.push_back(std::string(row[0]) + " | " + row[1] + " | " + row[2]);
            }
            mysql_free_result(res);
        }
        return results;
    }

    bool update(const std::string& tableName, int id, const std::string& name, int age) override {
        std::string query = "UPDATE " + tableName + " SET name='" + name + "', age=" + std::to_string(age) +
                            " WHERE id=" + std::to_string(id);
        return mysql_query(conn, query.c_str()) == 0;
    }

    bool remove(const std::string& tableName, int id) override {
        std::string query = "DELETE FROM " + tableName + " WHERE id=" + std::to_string(id);
        return mysql_query(conn, query.c_str()) == 0;
    }
};