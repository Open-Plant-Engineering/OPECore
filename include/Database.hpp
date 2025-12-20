#pragma once

#include <soci/soci.h>
#include <memory>
#include <string>

enum class DbBackend
{
    SQLite,
    MySQL
};

class Database
{
public:
    Database(DbBackend backend,
             const std::string& connectionString);

    void initSchema();

    // CRUD operations
    void createUser(const std::string& name, int age);
    bool readUserByName(const std::string& name, int& idOut, int& ageOut);
    void updateUserAge(const std::string& name, int newAge);
    void deleteUser(const std::string& name);

private:
    DbBackend backend_;
    std::unique_ptr<soci::session> session_;
};