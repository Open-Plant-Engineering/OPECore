#ifndef DATABASE_HPP
#define DATABASE_HPP

#include <string>
#include <vector>

// Generic interface
class IDatabase {
public:
    virtual ~IDatabase() = default;

    virtual bool connect(const std::string& connStr) = 0;
    virtual bool createTable(const std::string& tableName) = 0;
    virtual bool insert(const std::string& tableName,
                        const std::string& name,
                        int age) = 0;
    virtual std::vector<std::string> read(const std::string& tableName) = 0;
    virtual bool update(const std::string& tableName,
                        int id,
                        const std::string& name,
                        int age) = 0;
    virtual bool remove(const std::string& tableName, int id) = 0;
};

#endif // DATABASE_HPP