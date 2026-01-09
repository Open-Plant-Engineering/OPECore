#ifndef GITWRAPPER_HPP
#define GITWRAPPER_HPP

#include <string>
#include <vector>
#include <git2.h>

class GitWrapper {
public:
    explicit GitWrapper(const std::string& repoPath);
    ~GitWrapper();

    // Core Git operations
    bool gitPull(const std::string& remote = "origin", const std::string& branch = "main");
    bool gitPush(const std::string& remote = "origin", const std::string& branch = "main");
    bool gitMerge(const std::string& branch);
    bool gitCreateBranch(const std::string& branch);
    bool gitRenameBranch(const std::string& oldName, const std::string& newName);
    bool gitRebase(const std::string& branch);
    bool gitStash(const std::string& message = "WIP");
    bool gitReset(const std::string& commit = "HEAD~1", const std::string& mode = "hard");
    bool gitDeleteBranch(const std::string& branch);
    
    // File operations
    bool addFile(const std::string& filePath);
    bool removeFile(const std::string& filePath);
    bool stageAll();

    // Commit operations
    bool commitFile(const std::string& filePath,
                    const std::string& message,
                    std::string& errorMessage);

    bool commitAll(const std::string& message,
                   std::string& errorMessage);

    // Listing
    std::vector<std::string> listBranches();
    std::vector<std::string> listTags();
    std::vector<std::string> logHistory(int maxCount = 20);


    static bool cloneRepository(const std::string& remoteUrl,
                                const std::string& localPath,
                                std::string& errorMessage);

    // Utility
    std::vector<std::string> getModifiedFiles();
    bool checkoutBranch(const std::string& branch);
private:
    git_repository* repo;
    std::string repoPath;
};

#endif // GITWRAPPER_HPP