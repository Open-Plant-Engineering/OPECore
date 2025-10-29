#include "OpeDbCore.h"
#include <iostream>

OpeDbCore::OpeDbCore() { }

void OpeDbCore::OpenDbConnection() {
    if (sqlite3_open(dbFilePath.c_str(), &db) != SQLITE_OK) {
        lastError = sqlite3_errmsg(db);
        db = nullptr;
    }
}

OpeDbCore::~OpeDbCore() {
    if (db) {
        sqlite3_close(db);
    }
}

bool OpeDbCore::execute(const std::string& sql) {
    char* errMsg = nullptr;
    int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        lastError = errMsg ? errMsg : "Unknown error";
        sqlite3_free(errMsg);
        return false;
    }
    return true;
}

std::string OpeDbCore::getLastError() const {
    return lastError;
}