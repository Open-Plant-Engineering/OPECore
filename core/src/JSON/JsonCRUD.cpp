#include "JSON/JsonCRUD.hpp"
#include <fstream>
#include <iostream>
#include <stdexcept>
#include <filesystem>
#include <set>

namespace fs = std::filesystem;

// ---- existing ctor & CRUD ----

JsonCRUD::JsonCRUD(const std::string& file) : filename(file) {
    load();
}

void JsonCRUD::load() {
    std::ifstream in(filename);
    if (!in.is_open()) {
        data = json::object();
        return;
    }
    in >> data;
}

void JsonCRUD::save() {
    std::ofstream out(filename);
    if (!out.is_open()) {
        throw std::runtime_error("Cannot write JSON file: " + filename);
    }
    out << data.dump(4);
}

void JsonCRUD::create(const std::string& key, const json& value) {
    data[key] = value;
    save();
}

json JsonCRUD::read(const std::string& key) {
    if (!data.contains(key)) {
        throw std::runtime_error("Key not found: " + key);
    }
    return data.at(key);
}

void JsonCRUD::update(const std::string& key, const json& value) {
    data[key] = value;
    save();
}

void JsonCRUD::remove(const std::string& key) {
    data.erase(key);
    save();
}

void JsonCRUD::printAll() {
    std::cout << data.dump(4) << std::endl;
}

// ---------- static helpers ----------

bool JsonCRUD::createFile(const std::string& filename,
                          const std::string& initialJsonText,
                          std::string& errorMessage) {
    try {
        json j;
        if (initialJsonText.empty()) {
            j = json::object();
        } else {
            j = json::parse(initialJsonText);
        }
        std::ofstream out(filename);
        if (!out.is_open()) {
            errorMessage = "Failed to open file for write: " + filename;
            return false;
        }
        out << j.dump(4);
        return true;
    } catch (const std::exception& ex) {
        errorMessage = ex.what();
        return false;
    }
}

bool JsonCRUD::ensureBaseAndWorking(const std::string& originalFilename,
                                    const std::string& baseFilename,
                                    const std::string& workingFilename,
                                    std::string& errorMessage) {
    try {
        if (!fs::exists(originalFilename)) {
            errorMessage = "Original JSON file does not exist: " + originalFilename;
            return false;
        }

        json original;
        {
            std::ifstream in(originalFilename);
            if (!in.is_open()) {
                errorMessage = "Failed to open original file: " + originalFilename;
                return false;
            }
            in >> original;
        }

        if (!fs::exists(baseFilename)) {
            std::ofstream baseOut(baseFilename);
            if (!baseOut.is_open()) {
                errorMessage = "Failed to create base file: " + baseFilename;
                return false;
            }
            baseOut << original.dump(4);
        }

        if (!fs::exists(workingFilename)) {
            std::ofstream workOut(workingFilename);
            if (!workOut.is_open()) {
                errorMessage = "Failed to create working file: " + workingFilename;
                return false;
            }
            workOut << original.dump(4);
        }

        return true;
    } catch (const std::exception& ex) {
        errorMessage = ex.what();
        return false;
    }
}

bool JsonCRUD::modifyAttributeInWorking(const std::string& workingFilename,
                                        const std::string& key,
                                        const std::string& newValueAsJson,
                                        std::string& errorMessage) {
    try {
        json working;
        {
            std::ifstream in(workingFilename);
            if (!in.is_open()) {
                errorMessage = "Failed to open working file: " + workingFilename;
                return false;
            }
            in >> working;
        }

        json value = json::parse(newValueAsJson);
        working[key] = value;

        std::ofstream out(workingFilename);
        if (!out.is_open()) {
            errorMessage = "Failed to write working file: " + workingFilename;
            return false;
        }
        out << working.dump(4);
        return true;
    } catch (const std::exception& ex) {
        errorMessage = ex.what();
        return false;
    }
}

static void threeWayMerge(const json& baseJson,
                          const json& originalJson,
                          const json& workingJson,
                          json& mergedOut,
                          std::vector<std::string>& rejectedKeys) {
    mergedOut = originalJson;
    std::set<std::string> allKeys;

    auto collect = [&allKeys](const json& j) {
        if (!j.is_object()) return;
        for (auto it = j.begin(); it != j.end(); ++it) {
            allKeys.insert(it.key());
        }
    };

    collect(baseJson);
    collect(originalJson);
    collect(workingJson);

    for (const auto& key : allKeys) {
        bool inBase     = baseJson.contains(key);
        bool inOriginal = originalJson.contains(key);
        bool inWorking  = workingJson.contains(key);

        json baseVal, origVal, workVal;
        if (inBase)     baseVal  = baseJson.at(key);
        if (inOriginal) origVal  = originalJson.at(key);
        if (inWorking)  workVal  = workingJson.at(key);

        bool changedInWorking =
            (!inBase && inWorking) ||
            (inBase && inWorking && workVal != baseVal);

        bool changedInOriginal =
            (!inBase && inOriginal) ||
            (inBase && inOriginal && origVal != baseVal);

        if (!changedInWorking) {
            continue;
        }

        if (changedInWorking && !changedInOriginal) {
            if (inWorking) {
                mergedOut[key] = workVal;
            } else {
                mergedOut.erase(key);
            }
        } else if (changedInWorking && changedInOriginal) {
            rejectedKeys.push_back(key);
        }
    }
}

bool JsonCRUD::finalizeWorkingCopy(const std::string& originalFilename,
                                   const std::string& baseFilename,
                                   const std::string& workingFilename,
                                   std::vector<std::string>& rejectedKeys,
                                   std::string& errorMessage) {
    try {
        if (!fs::exists(originalFilename) ||
            !fs::exists(baseFilename) ||
            !fs::exists(workingFilename)) {
            errorMessage = "One or more JSON files missing (original/base/working)";
            return false;
        }

        json baseJson, originalJson, workingJson;

        {
            std::ifstream in(baseFilename);
            if (!in.is_open()) { errorMessage = "Cannot open base file"; return false; }
            in >> baseJson;
        }
        {
            std::ifstream in(originalFilename);
            if (!in.is_open()) { errorMessage = "Cannot open original file"; return false; }
            in >> originalJson;
        }
        {
            std::ifstream in(workingFilename);
            if (!in.is_open()) { errorMessage = "Cannot open working file"; return false; }
            in >> workingJson;
        }

        json merged;
        threeWayMerge(baseJson, originalJson, workingJson, merged, rejectedKeys);

        {
            std::ofstream out(originalFilename);
            if (!out.is_open()) {
                errorMessage = "Cannot write merged original file";
                return false;
            }
            out << merged.dump(4);
        }

        if (rejectedKeys.empty()) {
            std::error_code ec;
            fs::remove(baseFilename, ec);
            fs::remove(workingFilename, ec);
        }

        return true;
    } catch (const std::exception& ex) {
        errorMessage = ex.what();
        return false;
    }
}