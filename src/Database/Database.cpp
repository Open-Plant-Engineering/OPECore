#include "Database.hpp"

#include <soci/sqlite3/soci-sqlite3.h>
#include <soci/mysql/soci-mysql.h>

#include <iostream>

Database::Database(DbBackend backend,
                   const std::string& connectionString)
    : backend_(backend)
{
    switch (backend_)
    {
    case DbBackend::SQLite:
        session_ = std::make_unique<soci::session>(
            soci::sqlite3, connectionString);
        break;

    case DbBackend::MySQL:
        session_ = std::make_unique<soci::session>(
            soci::mysql, connectionString);
        break;
    }

    if (!session_ || !session_->is_connected())
    {
        throw std::runtime_error("Failed to open database session");
    }
}

void Database::initSchema()
{
    if (backend_ == DbBackend::SQLite)
    {
        *session_ << "CREATE TABLE IF NOT EXISTS users ("
                     "id INTEGER PRIMARY KEY AUTOINCREMENT, "
                     "name TEXT, "
                     "age INTEGER)";
    }
    else // MySQL
    {
        *session_ << "CREATE TABLE IF NOT EXISTS users ("
                     "id INT AUTO_INCREMENT PRIMARY KEY, "
                     "name VARCHAR(100), "
                     "age INT)";
    }
}

void Database::createUser(const std::string& name, int age)
{
    *session_ << "INSERT INTO users(name, age) VALUES(:name, :age)",
        soci::use(name), soci::use(age);
}

bool Database::readUserByName(const std::string& name,
                              int& idOut, int& ageOut)
{
    soci::indicator idInd, ageInd;
    soci::statement st = (session_->prepare <<
        "SELECT id, age FROM users WHERE name = :name",
        soci::use(name),
        soci::into(idOut, idInd),
        soci::into(ageOut, ageInd)
    );

    st.execute(true); // fetch first row

    if (st.got_data() && idInd == soci::i_ok && ageInd == soci::i_ok)
        return true;

    return false;
}

void Database::updateUserAge(const std::string& name, int newAge)
{
    *session_ << "UPDATE users SET age = :age WHERE name = :name",
        soci::use(newAge), soci::use(name);
}

void Database::deleteUser(const std::string& name)
{
    *session_ << "DELETE FROM users WHERE name = :name",
        soci::use(name);
}