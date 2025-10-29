#pragma once

// Session Management System is implimented
#ifndef SQLITE_ENABLE_SESSION
    #define SQLITE_ENABLE_SESSION
#endif

#ifndef SQLITE_ENABLE_PREUPDATE_HOOK
    #define SQLITE_ENABLE_PREUPDATE_HOOK
#endif

#include <string>
#include "sqlite3.h"
#include "OpeSessionManager.hpp"

class OpeDbCore {
public:
    OpeDbCore();
    ~OpeDbCore();

    OpeSessionManager manager;
    std::string dbFilePath;
    void OpenDbConnection();
    bool execute(const std::string& sql);
    std::string getLastError() const;
    sqlite3* db;
private:
    std::string lastError;

};