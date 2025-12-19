#ifndef JSONCRUD_HPP
#define JSONCRUD_HPP

#include <string>
#include <nlohmann/json.hpp>

using json = nlohmann::json;

class JsonCRUD {
private:
    std::string filename;
    json data;

    void load();
    void save();

public:
    explicit JsonCRUD(const std::string& file);

    // CRUD operations
    void create(const std::string& key, const json& value);
    json read(const std::string& key);
    void update(const std::string& key, const json& value);
    void remove(const std::string& key);

    // Utility
    void printAll();
};

#endif // JSONCRUD_HPP