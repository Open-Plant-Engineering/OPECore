#include "app.h"
#include <iostream>

OpeCore::OpeCore() : db(nullptr) {
    if (sqlite3_open(":memory:", &db) != SQLITE_OK) {
        lastError = sqlite3_errmsg(db);
        db = nullptr;
    }
}

OpeCore::~OpeCore() {
    if (db) {
        sqlite3_close(db);
    }
}

bool OpeCore::execute(const std::string& sql) {
    char* errMsg = nullptr;
    int rc = sqlite3_exec(db, sql.c_str(), nullptr, nullptr, &errMsg);
    if (rc != SQLITE_OK) {
        lastError = errMsg ? errMsg : "Unknown error";
        sqlite3_free(errMsg);
        return false;
    }
    return true;
}

std::string OpeCore::getLastError() const {
    return lastError;
}