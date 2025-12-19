#include "JsonCRUD.hpp"
#include <fstream>
#include <iostream>

// Constructor
JsonCRUD::JsonCRUD(const std::string& file) : filename(file) {
    load();
}

// Load JSON from file
void JsonCRUD::load() {
    std::ifstream inFile(filename);
    if (inFile.is_open()) {
        inFile >> data;
        inFile.close();
    } else {
        data = json::object(); // empty object if file doesn't exist
    }
}

// Save JSON to file
void JsonCRUD::save() {
    std::ofstream outFile(filename);
    if (outFile.is_open()) {
        outFile << data.dump(4); // pretty print
        outFile.close();
    }
}

// CREATE
void JsonCRUD::create(const std::string& key, const json& value) {
    data[key] = value;
    save();
}

// READ
json JsonCRUD::read(const std::string& key) {
    if (data.contains(key)) {
        return data[key];
    }
    return nullptr;
}

// UPDATE
void JsonCRUD::update(const std::string& key, const json& value) {
    if (data.contains(key)) {
        data[key] = value;
        save();
    } else {
        std::cerr << "Key not found: " << key << std::endl;
    }
}

// DELETE
void JsonCRUD::remove(const std::string& key) {
    if (data.contains(key)) {
        data.erase(key);
        save();
    } else {
        std::cerr << "Key not found: " << key << std::endl;
    }
}

// Print all
void JsonCRUD::printAll() {
    std::cout << data.dump(4) << std::endl;
}