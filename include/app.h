#pragma once
#include <string>
#include "sqlite3.h"

class OpeCore {
public:
    OpeCore();
    ~OpeCore();

    bool execute(const std::string& sql);
    std::string getLastError() const;

private:
    sqlite3* db;
    std::string lastError;
};