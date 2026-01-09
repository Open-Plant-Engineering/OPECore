#ifndef SESSIONMANAGER_HPP
#define SESSIONMANAGER_HPP

#include <string>
#include <vector>
#include <set>

class SessionManager {
public:
    explicit SessionManager(const std::string& repoPath);

    // 1. Clone project (delegates to GitWrapper)
    static bool cloneProject(const std::string& remoteUrl,
                             const std::string& localPath,
                             std::string& errorMessage);

    // 2. Create new JSON with unique ID under relativeDir (inside repo)
    // returns relative path like "configs/12345.json"
    std::string createJsonWithUniqueId(const std::string& relativeDir,
                                       const std::string& initialJsonText,
                                       std::string& errorMessage);

    // 3–4. Modify attribute using hostname-based working copy
    // newValueAsJson must be valid JSON text (e.g. "123", "\"foo\"", "{...}")
    bool modifyAttribute(const std::string& relativeJsonPath,
                         const std::string& key,
                         const std::string& newValueAsJson,
                         std::string& errorMessage);

    // 5–6. Finalize work:
    //  - applies safe changes back into original
    //  - rejects conflicting keys in rejectedKeys
    bool finalizeSession(const std::string& relativeJsonPath,
                         std::vector<std::string>& rejectedKeys,
                         std::string& errorMessage);
    // NEW: Git integration
    bool commitFile(const std::string& relativeJsonPath,
                    const std::string& message,
                    std::string& errorMessage);

    // NEW: Cleanup APIs
    std::set<std::string> listActiveUsers() const;
    bool cleanupUser(const std::string& user);
    bool cleanupAllUsers();
    
    const std::string& getRepoPath() const { return repoPath; }

private:
    std::string repoPath;
    std::string hostname;

    // Path helpers
    std::string makeAbsolute(const std::string& relative) const;
    static std::string joinPaths(const std::string& base, const std::string& sub);
    static std::string extractDirectory(const std::string& path);
    static std::string extractFilename(const std::string& path);
    // Locking helpers
    bool isLockedByOther(const std::string& lockFile, std::string& lockedBy);
    bool acquireLock(const std::string& lockFile, std::string& errorMessage);
    bool releaseLock(const std::string& lockFile);
    std::string lockFileRelative(const std::string& relativeJsonPath) const;

    // working: <dir>/<hostname>_<basename>
    std::string workingRelative(const std::string& relativeJsonPath) const;
    // base: <dir>/.base_<hostname>_<basename>
    std::string baseRelative(const std::string& relativeJsonPath) const;

    // Utilities
    static std::string generateUniqueId();
    static std::string getHostname();
};

#endif // SESSIONMANAGER_HPP