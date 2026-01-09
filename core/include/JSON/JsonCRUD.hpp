#ifndef JSONCRUD_HPP
#define JSONCRUD_HPP

#include <string>
#include <vector>
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

    // Basic CRUD on the main file
    void create(const std::string& key, const json& value);
    json read(const std::string& key);
    void update(const std::string& key, const json& value);
    void remove(const std::string& key);
    void printAll();

    // ---------- New: static helpers for SessionManager ----------

    // Create a new JSON file with given initial data (as JSON text or empty = "{}")
    static bool createFile(const std::string& filename,
                           const std::string& initialJsonText,
                           std::string& errorMessage);

    // Ensure base and working copies exist:
    //   baseFilename: snapshot file (used as "base")
    //   workingFilename: editable copy
    // If they don't exist, they are created from originalFilename.
    static bool ensureBaseAndWorking(const std::string& originalFilename,
                                     const std::string& baseFilename,
                                     const std::string& workingFilename,
                                     std::string& errorMessage);

    // Modify a single attribute in working file (value is JSON text, e.g. `"foo"` or `123` or `{...}`)
    static bool modifyAttributeInWorking(const std::string& workingFilename,
                                         const std::string& key,
                                         const std::string& newValueAsJson,
                                         std::string& errorMessage);

    // Finalize:
    //  - Reads base, original, working
    //  - Does three-way merge per key
    //  - Writes merged result back to originalFilename
    //  - Fills rejectedKeys for conflicting keys
    //  - Optionally deletes base/working if no conflicts
    static bool finalizeWorkingCopy(const std::string& originalFilename,
                                    const std::string& baseFilename,
                                    const std::string& workingFilename,
                                    std::vector<std::string>& rejectedKeys,
                                    std::string& errorMessage);
};

#endif // JSONCRUD_HPP