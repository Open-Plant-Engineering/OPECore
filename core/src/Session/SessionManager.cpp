#include "Session/SessionManager.hpp"
#include "Git/GitWrapper.hpp"
#include "JSON/JsonCRUD.hpp"
#include <fstream>
#include <filesystem>
#include <random>
#include <chrono>
#include <stdexcept>

#if defined(_WIN32)
    #include <windows.h>
#else
    #include <unistd.h>
#endif

namespace fs = std::filesystem;

// ----- ctor -----

SessionManager::SessionManager(const std::string& repoPath_)
    : repoPath(repoPath_), hostname(getHostname()) {
    if (!fs::exists(repoPath) || !fs::is_directory(repoPath)) {
        throw std::runtime_error("Repository path does not exist or is not a directory: " + repoPath);
    }
}

// ----- clone -----

bool SessionManager::cloneProject(const std::string& remoteUrl,
                                  const std::string& localPath,
                                  std::string& errorMessage) {
    return GitWrapper::cloneRepository(remoteUrl, localPath, errorMessage);
}

// ----- create JSON with unique ID -----

std::string SessionManager::createJsonWithUniqueId(const std::string& relativeDir,
                                                   const std::string& initialJsonText,
                                                   std::string& errorMessage) {
    std::string id = generateUniqueId();

    std::string dirAbs = makeAbsolute(relativeDir);
    if (!fs::exists(dirAbs)) {
        fs::create_directories(dirAbs);
    }

    std::string filename = id + ".json";
    std::string relPath = relativeDir.empty()
                          ? filename
                          : joinPaths(relativeDir, filename);
    std::string absPath = makeAbsolute(relPath);

    if (!JsonCRUD::createFile(absPath, initialJsonText, errorMessage)) {
        return {};
    }

    return relPath;
}

// ----- modify attribute via working copy -----
bool SessionManager::modifyAttribute(const std::string& relativeJsonPath,
                                     const std::string& key,
                                     const std::string& newValueAsJson,
                                     std::string& errorMessage) {
    std::string lockRel = lockFileRelative(relativeJsonPath);
    std::string lockAbs = makeAbsolute(lockRel);

    // Acquire lock
    if (!acquireLock(lockAbs, errorMessage)) {
        return false;
    }

    // Continue with existing logic
    std::string originalAbs = makeAbsolute(relativeJsonPath);
    std::string workingRel  = workingRelative(relativeJsonPath);
    std::string baseRel     = baseRelative(relativeJsonPath);

    std::string workingAbs  = makeAbsolute(workingRel);
    std::string baseAbs     = makeAbsolute(baseRel);

    if (!JsonCRUD::ensureBaseAndWorking(originalAbs, baseAbs, workingAbs, errorMessage)) {
        return false;
    }

    return JsonCRUD::modifyAttributeInWorking(workingAbs, key, newValueAsJson, errorMessage);
}

// ----- finalize session -----

bool SessionManager::finalizeSession(const std::string& relativeJsonPath,
                                     std::vector<std::string>& rejectedKeys,
                                     std::string& errorMessage) {
    std::string lockRel = lockFileRelative(relativeJsonPath);
    std::string lockAbs = makeAbsolute(lockRel);

    // Must own the lock
    std::string lockedBy;
    if (isLockedByOther(lockAbs, lockedBy)) {
        errorMessage = "Cannot finalize. File is locked by: " + lockedBy;
        return false;
    }

    // Continue with existing logic
    std::string originalAbs = makeAbsolute(relativeJsonPath);
    std::string workingRel  = workingRelative(relativeJsonPath);
    std::string baseRel     = baseRelative(relativeJsonPath);

    std::string workingAbs  = makeAbsolute(workingRel);
    std::string baseAbs     = makeAbsolute(baseRel);

    bool ok = JsonCRUD::finalizeWorkingCopy(originalAbs, baseAbs, workingAbs,
                                            rejectedKeys, errorMessage);

    // If no conflicts → release lock
    if (ok && rejectedKeys.empty()) {
        releaseLock(lockAbs);
    }

    return ok;
}

// ----- Lock file helpers -----
std::string SessionManager::makeAbsolute(const std::string& relative) const {
    if (fs::path(relative).is_absolute()) {
        return relative;
    }
    return (fs::path(repoPath) / relative).lexically_normal().string();
}

std::string SessionManager::joinPaths(const std::string& base, const std::string& sub) {
    if (base.empty()) return sub;
    return (fs::path(base) / sub).lexically_normal().string();
}

std::string SessionManager::extractDirectory(const std::string& path) {
    return fs::path(path).parent_path().string();
}

std::string SessionManager::extractFilename(const std::string& path) {
    return fs::path(path).filename().string();
}

std::string SessionManager::workingRelative(const std::string& relativeJsonPath) const {
    std::string dir  = extractDirectory(relativeJsonPath);
    std::string file = extractFilename(relativeJsonPath);

    std::string name = hostname + "_" + file;
    return dir.empty() ? name : joinPaths(dir, name);
}

std::string SessionManager::baseRelative(const std::string& relativeJsonPath) const {
    std::string dir  = extractDirectory(relativeJsonPath);
    std::string file = extractFilename(relativeJsonPath);

    std::string name = ".base_" + hostname + "_" + file;
    return dir.empty() ? name : joinPaths(dir, name);
}

// ----- utilities -----
std::string SessionManager::lockFileRelative(const std::string& relativeJsonPath) const {
    std::string dir  = extractDirectory(relativeJsonPath);
    std::string file = extractFilename(relativeJsonPath);

    std::string lockName = file + ".lock";

    return dir.empty() ? lockName : joinPaths(dir, lockName);
}

bool SessionManager::isLockedByOther(const std::string& lockFileAbs, std::string& lockedBy) {
    if (!fs::exists(lockFileAbs)) {
        return false;
    }

    std::ifstream in(lockFileAbs);
    if (!in.is_open()) {
        lockedBy = "unknown";
        return true; // treat unreadable lock as locked
    }

    std::getline(in, lockedBy);
    return lockedBy != hostname;
}

bool SessionManager::acquireLock(const std::string& lockFileAbs, std::string& errorMessage) {
    std::string lockedBy;
    if (isLockedByOther(lockFileAbs, lockedBy)) {
        errorMessage = "File is currently locked by: " + lockedBy;
        return false;
    }

    // If lock exists but belongs to us → OK
    if (fs::exists(lockFileAbs)) {
        return true;
    }

    // Create lock file
    std::ofstream out(lockFileAbs);
    if (!out.is_open()) {
        errorMessage = "Failed to create lock file: " + lockFileAbs;
        return false;
    }

    out << hostname << "\n";
    out << std::chrono::system_clock::now().time_since_epoch().count() << "\n";
    return true;
}

bool SessionManager::releaseLock(const std::string& lockFileAbs) {
    std::error_code ec;
    fs::remove(lockFileAbs, ec);
    return !fs::exists(lockFileAbs);
}

// ----- utilities -----

std::string SessionManager::generateUniqueId() {
    auto now = std::chrono::system_clock::now().time_since_epoch();
    auto millis = std::chrono::duration_cast<std::chrono::milliseconds>(now).count();

    std::random_device rd;
    std::mt19937_64 gen(rd());
    std::uniform_int_distribution<unsigned long long> dist;

    unsigned long long randVal = dist(gen);

    char buf[64];
    std::snprintf(buf, sizeof(buf), "%lld_%016llx",
                  static_cast<long long>(millis),
                  static_cast<unsigned long long>(randVal));
    return std::string(buf);
}

std::string SessionManager::getHostname() {
#if defined(_WIN32)
    char buf[MAX_COMPUTERNAME_LENGTH + 1];
    DWORD size = sizeof(buf);
    if (GetComputerNameA(buf, &size)) {
        return std::string(buf, size);
    }
    return "unknown_host";
#else
    char buf[256];
    if (gethostname(buf, sizeof(buf)) == 0) {
        buf[sizeof(buf) - 1] = '\0';
        return std::string(buf);
    }
    return "unknown_host";
#endif
}


// ------------------------------------------------------------
// NEW: Commit finalized JSON file
// ------------------------------------------------------------
bool SessionManager::commitFile(const std::string& relativeJsonPath,
                                const std::string& message,
                                std::string& errorMessage)
{
    GitWrapper git(repoPath);
    return git.commitFile(relativeJsonPath, message, errorMessage);
}

// ------------------------------------------------------------
// NEW: List active users
// ------------------------------------------------------------
std::set<std::string> SessionManager::listActiveUsers() const {
    std::set<std::string> users;

    for (auto& p : fs::recursive_directory_iterator(repoPath)) {
        if (!p.is_regular_file()) continue;

        std::string name = p.path().filename().string();

        // working copy: <hostname>_<file>
        auto pos = name.find('_');
        if (pos != std::string::npos && !name.starts_with(".base_")) {
            users.insert(name.substr(0, pos));
        }

        // base copy: .base_<hostname>_<file>
        if (name.starts_with(".base_")) {
            std::string rest = name.substr(6);
            auto pos2 = rest.find('_');
            if (pos2 != std::string::npos)
                users.insert(rest.substr(0, pos2));
        }

        // lock file: <file>.lock
        if (name.ends_with(".lock")) {
            std::ifstream in(p.path());
            std::string lockedBy;
            if (in.is_open() && std::getline(in, lockedBy))
                users.insert(lockedBy);
        }
    }

    return users;
}

// ------------------------------------------------------------
// NEW: Cleanup one user
// ------------------------------------------------------------
bool SessionManager::cleanupUser(const std::string& user) {
    for (auto& p : fs::recursive_directory_iterator(repoPath)) {
        if (!p.is_regular_file()) continue;

        std::string name = p.path().filename().string();

        if (name.starts_with(user + "_") ||
            name.starts_with(".base_" + user + "_"))
        {
            fs::remove(p.path());
            continue;
        }

        if (name.ends_with(".lock")) {
            std::ifstream in(p.path());
            std::string lockedBy;
            if (in.is_open() && std::getline(in, lockedBy)) {
                if (lockedBy == user)
                    fs::remove(p.path());
            }
        }
    }

    return true;
}

// ------------------------------------------------------------
// NEW: Cleanup all users
// ------------------------------------------------------------
bool SessionManager::cleanupAllUsers() {
    for (auto& p : fs::recursive_directory_iterator(repoPath)) {
        if (!p.is_regular_file()) continue;

        std::string name = p.path().filename().string();

        if (name.find('_') != std::string::npos ||
            name.starts_with(".base_") ||
            name.ends_with(".lock"))
        {
            fs::remove(p.path());
        }
    }

    return true;
}